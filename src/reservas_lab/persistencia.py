"""Acceso a SQLite. No importa Tkinter ni decide validaciones del formulario."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .dominio import ErrorPersistencia, Reserva, escribir_fecha, leer_fecha


class RepositorioSQLite:
    def __init__(self, ruta: Path):
        self._conexion = None
        try:
            self._conexion = sqlite3.connect(ruta)
            self._conexion.row_factory = sqlite3.Row
            self._conexion.execute("""
                CREATE TABLE IF NOT EXISTS reservas (
                    id TEXT PRIMARY KEY NOT NULL,
                    unidad_id TEXT NOT NULL CHECK (
                        unidad_id IN ('MIC-01', 'MIC-02', 'OSC-01', 'MUL-01', 'FUE-01')
                    ),
                    solicitante TEXT NOT NULL CHECK (length(trim(solicitante)) > 0),
                    inicio TEXT NOT NULL,
                    fin TEXT NOT NULL,
                    estado TEXT NOT NULL CHECK (estado IN ('ACTIVA', 'CANCELADA')),
                    CHECK (inicio < fin)
                )
            """)
        except sqlite3.Error as exc:
            if self._conexion is not None:
                self._conexion.close()
            raise ErrorPersistencia(f"No se pudo abrir la base de reservas: {ruta}") from exc

    def cerrar(self):
        self._conexion.close()

    @contextmanager
    def transaccion(self):
        try:
            # Revalidación e inserción comparten la misma transacción de escritura.
            with self._conexion:
                self._conexion.execute("BEGIN IMMEDIATE")
                yield
        except sqlite3.Error as exc:
            raise ErrorPersistencia("No se pudo guardar la operación; no se confirmó ningún cambio.") from exc

    def _ejecutar(self, sql, parametros=()):
        try:
            return self._conexion.execute(sql, parametros)
        except sqlite3.Error as exc:
            raise ErrorPersistencia("No se pudo acceder a las reservas. Comprobá el archivo de datos.") from exc

    def hay_conflicto(self, unidad_id, inicio, fin) -> bool:
        return self._ejecutar(
            """SELECT 1 FROM reservas
               WHERE unidad_id = ? AND estado = 'ACTIVA'
                 AND ? < fin AND inicio < ? LIMIT 1""",
            (unidad_id, escribir_fecha(inicio), escribir_fecha(fin)),
        ).fetchone() is not None

    def insertar(self, reserva: Reserva):
        self._ejecutar(
            """INSERT INTO reservas (id, unidad_id, solicitante, inicio, fin, estado)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (reserva.id, reserva.unidad_id, reserva.solicitante,
             escribir_fecha(reserva.inicio), escribir_fecha(reserva.fin), reserva.estado),
        )

    def obtener(self, reserva_id: str) -> Reserva | None:
        fila = self._ejecutar("SELECT * FROM reservas WHERE id = ?", (reserva_id,)).fetchone()
        return self._convertir(fila) if fila is not None else None

    def cancelar(self, reserva_id: str):
        self._ejecutar("UPDATE reservas SET estado = 'CANCELADA' WHERE id = ?", (reserva_id,))

    def historial(self) -> tuple[Reserva, ...]:
        filas = self._ejecutar("SELECT * FROM reservas ORDER BY inicio, id").fetchall()
        return tuple(self._convertir(fila) for fila in filas)

    @staticmethod
    def _convertir(fila) -> Reserva:
        return Reserva(
            fila["id"], fila["unidad_id"], fila["solicitante"],
            leer_fecha(fila["inicio"]), leer_fecha(fila["fin"]), fila["estado"],
        )
