"""RF05: reapertura, revalidación y rollback con bases temporales reales."""

import sqlite3
from contextlib import closing
from dataclasses import replace

import pytest

from reservas_lab.dominio import CANCELADA, ConflictoReserva, ErrorPersistencia
from reservas_lab.persistencia import RepositorioSQLite
from reservas_lab.servicio import ServicioReservas

INICIO = "2026-11-10 10:00"
FIN = "2026-11-10 11:00"


def test_reabrir_base_conserva_historial_estados_y_disponibilidad(inventario, ruta_base):
    repo = RepositorioSQLite(ruta_base)
    try:
        servicio = ServicioReservas(inventario, repo)
        primera = servicio.crear("MIC-01", "Persona ficticia A", INICIO, FIN)
        segunda = servicio.crear("MIC-01", "Persona ficticia B", FIN, "2026-11-10 12:00")
        servicio.cancelar(primera.id)
        antes = servicio.historial()
    finally:
        repo.cerrar()
    reabierto = RepositorioSQLite(ruta_base)
    try:
        servicio = ServicioReservas(inventario, reabierto)
        assert servicio.historial() == antes == (replace(primera, estado=CANCELADA), segunda)
        assert servicio.disponible("MIC-01", INICIO, FIN)
        assert not servicio.disponible("MIC-01", FIN, "2026-11-10 12:00")
    finally:
        reabierto.cerrar()


def test_crear_revalida_aunque_la_consulta_previa_estuviera_libre(servicio, inventario, ruta_base):
    assert servicio.disponible("MIC-01", INICIO, FIN)
    otro_repo = RepositorioSQLite(ruta_base)
    try:
        otro_servicio = ServicioReservas(inventario, otro_repo)
        original = otro_servicio.crear("MIC-01", "Persona ficticia B", INICIO, FIN)
        with pytest.raises(ConflictoReserva):
            servicio.crear("MIC-01", "Persona ficticia A", INICIO, FIN)
        assert servicio.historial() == (original,)
    finally:
        otro_repo.cerrar()


def test_fallo_de_insercion_revierte_y_permite_reintentar(servicio, ruta_base):
    # RAISE(FAIL) ocurre después del INSERT: la transacción debe deshacerlo.
    with closing(sqlite3.connect(ruta_base)) as conexion, conexion:
        conexion.execute("""CREATE TRIGGER fallo_insert AFTER INSERT ON reservas
                            BEGIN SELECT RAISE(FAIL, 'fallo de prueba'); END""")
    with pytest.raises(ErrorPersistencia):
        servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN)
    assert servicio.historial() == ()
    assert servicio.disponible("MIC-01", INICIO, FIN)
    with closing(sqlite3.connect(ruta_base)) as conexion, conexion:
        conexion.execute("DROP TRIGGER fallo_insert")
    assert servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN).estado == "ACTIVA"


def test_fallo_de_cancelacion_revierte_cambio_de_estado(servicio, ruta_base):
    original = servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN)
    with closing(sqlite3.connect(ruta_base)) as conexion, conexion:
        conexion.execute("""CREATE TRIGGER fallo_update AFTER UPDATE ON reservas
                            BEGIN SELECT RAISE(FAIL, 'fallo de prueba'); END""")
    with pytest.raises(ErrorPersistencia):
        servicio.cancelar(original.id)
    assert servicio.historial() == (original,)
    assert not servicio.disponible("MIC-01", INICIO, FIN)


def test_fallo_de_commit_no_confirma_insercion(inventario, ruta_base):
    class ConexionConFalloDeCommit(sqlite3.Connection):
        def __exit__(self, tipo, valor, traza):
            if tipo is None:
                super().__exit__(sqlite3.OperationalError, sqlite3.OperationalError(), None)
                raise sqlite3.OperationalError("fallo de commit simulado")
            return super().__exit__(tipo, valor, traza)

    repo = RepositorioSQLite(ruta_base)
    repo.cerrar()
    # Sólo se reemplaza la conexión de esta base temporal, nunca la de producción.
    repo._conexion = sqlite3.connect(ruta_base, factory=ConexionConFalloDeCommit)
    repo._conexion.row_factory = sqlite3.Row
    try:
        servicio = ServicioReservas(inventario, repo)
        with pytest.raises(ErrorPersistencia):
            servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN)
        assert servicio.historial() == ()
    finally:
        repo.cerrar()


def test_base_inaccesible_no_reemplaza_archivos(tmp_path):
    carpeta = tmp_path / "carpeta"
    carpeta.mkdir()
    with pytest.raises(ErrorPersistencia):
        RepositorioSQLite(carpeta)
    assert carpeta.is_dir()
    corrupta = tmp_path / "no-es-sqlite.db"
    contenido = b'contenido original, no es una base SQLite'
    corrupta.write_bytes(contenido)
    with pytest.raises(ErrorPersistencia):
        RepositorioSQLite(corrupta)
    assert corrupta.read_bytes() == contenido


def test_solicitante_se_guarda_como_dato_no_como_sql(servicio):
    nombre = "Persona ficticia '); DROP TABLE reservas; --"
    reserva = servicio.crear("MIC-01", nombre, INICIO, FIN)
    assert servicio.historial() == (reserva,)
    assert reserva.solicitante == nombre
