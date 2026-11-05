"""RF02–RF04/RF06: mismas reglas para consultar y crear, sin Tkinter."""

from dataclasses import replace
from uuid import UUID, uuid4

import pytest

from reservas_lab.dominio import (
    ACTIVA, CANCELADA, ConflictoReserva, ErrorValidacion,
    ReservaInexistente, ReservaYaCancelada, escribir_fecha,
)

INICIO = "2026-11-10 10:00"
FIN = "2026-11-10 11:00"


def test_creacion_identidad_normalizacion_e_historial(servicio):
    assert servicio.historial() == ()
    reserva = servicio.crear("MIC-01", "  Persona ficticia A  ", INICIO, FIN)
    otra = servicio.crear("MIC-02", "Persona ficticia A", INICIO, FIN)
    assert UUID(reserva.id).version == 4
    assert str(UUID(reserva.id)) == reserva.id
    assert reserva.id != otra.id
    assert reserva.solicitante == "Persona ficticia A"
    assert reserva.estado == ACTIVA
    assert escribir_fecha(reserva.inicio) == INICIO
    assert escribir_fecha(reserva.fin) == FIN
    assert reserva.inicio.tzinfo is None
    assert set(servicio.historial()) == {reserva, otra}


@pytest.mark.parametrize("unidad", ["XXX-99", "mic-01", "", " MIC-01 ", None])
def test_rechaza_unidad_en_ambos_flujos_sin_cambios(servicio, unidad):
    with pytest.raises(ErrorValidacion):
        servicio.disponible(unidad, INICIO, FIN)
    with pytest.raises(ErrorValidacion):
        servicio.crear(unidad, "Persona ficticia", INICIO, FIN)
    assert servicio.historial() == ()


@pytest.mark.parametrize("solicitante", ["", "   ", "\t\n", None])
def test_rechaza_solicitante_vacio(servicio, solicitante):
    with pytest.raises(ErrorValidacion):
        servicio.crear("MIC-01", solicitante, INICIO, FIN)
    assert servicio.historial() == ()


@pytest.mark.parametrize("fecha", [
    "2026-02-30 10:00", "2026-11-10 24:00", "2026-11-10 10:60",
    "2026-1-10 10:00", "2026-11-1 10:00", "2026-11-10 1:00",
    "2026-11-10 10:0", "2026-11-10T10:00", "2026-11-10 10:00:00",
    "2026-11-10 10:00-03:00", " 2026-11-10 10:00", "2026-11-10 10:00\n",
    "0000-01-01 00:00", "10000-01-01 00:00", "2025-02-29 10:00", "", None,
])
@pytest.mark.parametrize("campo", ["inicio", "fin"])
def test_validacion_temporal_compartida(servicio, fecha, campo):
    inicio, fin = (fecha, FIN) if campo == "inicio" else (INICIO, fecha)
    with pytest.raises(ErrorValidacion):
        servicio.disponible("MIC-01", inicio, fin)
    with pytest.raises(ErrorValidacion):
        servicio.crear("MIC-01", "Persona ficticia", inicio, fin)
    assert servicio.historial() == ()


@pytest.mark.parametrize("inicio, fin", [(INICIO, INICIO), (FIN, INICIO)])
def test_inicio_debe_ser_anterior(servicio, inicio, fin):
    with pytest.raises(ErrorValidacion):
        servicio.disponible("MIC-01", inicio, fin)
    with pytest.raises(ErrorValidacion):
        servicio.crear("MIC-01", "Persona ficticia", inicio, fin)
    assert servicio.historial() == ()


@pytest.mark.parametrize("inicio, fin, disponible", [
    ("09:00", "10:00", True),
    ("11:00", "12:00", True),
    ("10:30", "11:30", False),
    ("09:30", "10:30", False),
    ("10:00", "11:00", False),
    ("10:15", "10:45", False),
    ("09:00", "12:00", False),
    ("10:00", "10:30", False),
    ("10:30", "11:00", False),
])
def test_matriz_intervalos_consulta_y_creacion(servicio, inicio, fin, disponible):
    original = servicio.crear("MIC-01", "Persona ficticia A", INICIO, FIN)
    inicio, fin = f"2026-11-10 {inicio}", f"2026-11-10 {fin}"
    assert servicio.disponible("MIC-01", inicio, fin) is disponible
    assert servicio.historial() == (original,)  # Consultar no modifica datos.
    if disponible:
        nueva = servicio.crear("MIC-01", "Persona ficticia B", inicio, fin)
        assert nueva.estado == ACTIVA
        assert len(servicio.historial()) == 2
    else:
        with pytest.raises(ConflictoReserva):
            servicio.crear("MIC-01", "Persona ficticia B", inicio, fin)
        assert servicio.historial() == (original,)


def test_unidades_distintas_admiten_mismo_intervalo(servicio):
    for unidad in servicio.inventario:
        assert servicio.disponible(unidad.id, INICIO, FIN)
        servicio.crear(unidad.id, "Persona ficticia", INICIO, FIN)
    assert len(servicio.historial()) == 5


def test_cancelar_libera_y_conserva_todos_los_campos(servicio):
    original = servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN)
    assert not servicio.disponible("MIC-01", INICIO, FIN)
    cancelada = servicio.cancelar(original.id)
    assert cancelada == replace(original, estado=CANCELADA)
    assert servicio.disponible("MIC-01", INICIO, FIN)
    assert servicio.historial() == (cancelada,)
    nueva = servicio.crear("MIC-01", "Persona ficticia B", INICIO, FIN)
    assert set(servicio.historial()) == {cancelada, nueva}
    assert not servicio.disponible("MIC-01", INICIO, FIN)


def test_cancelar_inexistente_o_repetir_no_altera_datos(servicio):
    with pytest.raises(ReservaInexistente):
        servicio.cancelar(str(uuid4()))
    assert servicio.historial() == ()
    original = servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN)
    cancelada = servicio.cancelar(original.id)
    with pytest.raises(ReservaYaCancelada):
        servicio.cancelar(original.id)
    assert servicio.historial() == (cancelada,)


@pytest.mark.parametrize("inicio, fin", [
    ("2000-01-01 10:00", "2000-01-01 10:01"),
    ("2024-02-29 23:30", "2024-03-01 01:00"),
    ("0001-01-01 00:00", "9999-12-31 23:59"),
    ("9999-12-31 23:58", "9999-12-31 23:59"),
])
def test_pasado_cruce_de_dia_y_rango_sin_limites_adicionales(servicio, inicio, fin):
    assert servicio.disponible("MIC-01", inicio, fin)
    reserva = servicio.crear("MIC-01", "Persona ficticia", inicio, fin)
    assert escribir_fecha(reserva.inicio) == inicio
    assert escribir_fecha(reserva.fin) == fin
    assert servicio.historial() == (reserva,)


def test_historial_ordenado_por_inicio_y_uuid(servicio):
    tarde = servicio.crear("OSC-01", "Persona ficticia", FIN, "2026-11-10 12:00")
    a = servicio.crear("MIC-01", "Persona ficticia", INICIO, FIN)
    b = servicio.crear("MIC-02", "Persona ficticia", INICIO, FIN)
    servicio.cancelar(tarde.id)
    esperado = tuple(sorted((a, b), key=lambda r: r.id)) + (replace(tarde, estado=CANCELADA),)
    assert servicio.historial() == esperado
