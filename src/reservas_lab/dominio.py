"""Datos y validación de horas civiles de America/Argentina/Cordoba."""

import re
from dataclasses import dataclass
from datetime import datetime

ACTIVA = "ACTIVA"
CANCELADA = "CANCELADA"
IDS_UNIDADES = frozenset({"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"})


class ErrorReservas(Exception):
    """Error que se puede comunicar al usuario sin cerrar la aplicación."""


class ErrorValidacion(ErrorReservas):
    def __init__(self, mensaje: str, campo: str | None = None):
        super().__init__(mensaje)
        self.campo = campo


class ConflictoReserva(ErrorReservas):
    pass


class ReservaInexistente(ErrorReservas):
    pass


class ReservaYaCancelada(ErrorReservas):
    pass


class ErrorInventario(ErrorReservas):
    pass


class ErrorPersistencia(ErrorReservas):
    pass


@dataclass(frozen=True)
class Unidad:
    id: str
    nombre: str


@dataclass(frozen=True)
class Reserva:
    id: str
    unidad_id: str
    solicitante: str
    inicio: datetime
    fin: datetime
    estado: str = ACTIVA


def leer_fecha(valor: str) -> datetime:
    if not isinstance(valor, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", valor
    ):
        raise ErrorValidacion("Usá el formato exacto AAAA-MM-DD HH:MM; ejemplo: 2026-11-10 10:30.")
    try:
        return datetime.strptime(valor, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise ErrorValidacion("La fecha o la hora no es válida.") from exc


def escribir_fecha(valor: datetime) -> str:
    # strftime puede no rellenar años anteriores a 1000 en todas las plataformas.
    return (
        f"{valor.year:04d}-{valor.month:02d}-{valor.day:02d} "
        f"{valor.hour:02d}:{valor.minute:02d}"
    )
