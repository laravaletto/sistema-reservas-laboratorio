"""Casos de uso y reglas compartidas, verificables sin abrir ventanas."""

from dataclasses import replace
from uuid import uuid4

from .dominio import (
    CANCELADA, ConflictoReserva, ErrorValidacion, Reserva,
    ReservaInexistente, ReservaYaCancelada, Unidad, leer_fecha,
)
from .persistencia import RepositorioSQLite


class ServicioReservas:
    def __init__(self, inventario: tuple[Unidad, ...], repositorio: RepositorioSQLite):
        self.inventario = inventario
        self._unidades = {unidad.id for unidad in inventario}
        self._repositorio = repositorio

    def _validar_intervalo(self, unidad_id, inicio, fin):
        if not isinstance(unidad_id, str) or unidad_id not in self._unidades:
            raise ErrorValidacion("Seleccioná una unidad existente del inventario.")
        inicio_dt, fin_dt = leer_fecha(inicio), leer_fecha(fin)
        if inicio_dt >= fin_dt:
            raise ErrorValidacion("El inicio debe ser estrictamente anterior al fin.")
        return inicio_dt, fin_dt

    def disponible(self, unidad_id: str, inicio: str, fin: str) -> bool:
        inicio_dt, fin_dt = self._validar_intervalo(unidad_id, inicio, fin)
        return not self._repositorio.hay_conflicto(unidad_id, inicio_dt, fin_dt)

    def crear(self, unidad_id: str, solicitante: str, inicio: str, fin: str) -> Reserva:
        inicio_dt, fin_dt = self._validar_intervalo(unidad_id, inicio, fin)
        if not isinstance(solicitante, str) or not solicitante.strip():
            raise ErrorValidacion("Ingresá un solicitante ficticio que no esté vacío.")
        reserva = Reserva(str(uuid4()), unidad_id, solicitante.strip(), inicio_dt, fin_dt)
        with self._repositorio.transaccion():
            if self._repositorio.hay_conflicto(unidad_id, inicio_dt, fin_dt):
                raise ConflictoReserva("La unidad ya tiene una reserva activa superpuesta.")
            self._repositorio.insertar(reserva)
        return reserva

    def cancelar(self, reserva_id: str) -> Reserva:
        with self._repositorio.transaccion():
            reserva = self._repositorio.obtener(reserva_id)
            if reserva is None:
                raise ReservaInexistente("No existe una reserva con ese identificador.")
            if reserva.estado == CANCELADA:
                raise ReservaYaCancelada("La reserva ya estaba cancelada; no se realizaron cambios.")
            self._repositorio.cancelar(reserva_id)
        return replace(reserva, estado=CANCELADA)

    def historial(self) -> tuple[Reserva, ...]:
        return self._repositorio.historial()
