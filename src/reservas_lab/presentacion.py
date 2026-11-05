"""Mensajes de presentación sin widgets ni validaciones de negocio."""

from dataclasses import dataclass

from .dominio import (
    ConflictoReserva, ErrorInventario, ErrorPersistencia, ErrorValidacion,
    ReservaInexistente, ReservaYaCancelada,
)


@dataclass(frozen=True)
class Mensaje:
    texto: str
    tipo: str = "info"
    campo: str | None = None


def mensaje_error(error: Exception) -> Mensaje:
    if isinstance(error, ErrorValidacion):
        return Mensaje(f"Error: {error}", "error", error.campo)
    if isinstance(error, ConflictoReserva):
        return Mensaje(
            "No disponible: la unidad tiene una reserva activa superpuesta. Elegí otro intervalo o unidad.",
            "aviso", "inicio",
        )
    if isinstance(error, ReservaYaCancelada):
        return Mensaje("La reserva ya estaba cancelada. Se actualizará el historial.")
    if isinstance(error, ReservaInexistente):
        return Mensaje("Error: la reserva ya no está disponible en el historial. Volvé a consultarlo.", "error")
    if isinstance(error, ErrorPersistencia):
        return Mensaje(
            "Error: no se pudo completar la operación con las reservas guardadas. "
            "Volvé a intentarlo. Si continúa, solicitá revisar el archivo de datos.", "error",
        )
    if isinstance(error, ErrorInventario):
        return Mensaje("Error: no se pudo cargar el inventario. Solicitá revisar el archivo de inventario.", "error")
    return Mensaje("Error: no se pudo completar la operación. Volvé a intentarlo; si continúa, solicitá asistencia.", "error")


def mensaje_disponibilidad(disponible: bool) -> Mensaje:
    if disponible:
        return Mensaje("Disponible: la unidad está libre para el intervalo consultado.", "exito")
    return Mensaje("No disponible: hay una reserva activa superpuesta para esa unidad e intervalo.", "aviso")
