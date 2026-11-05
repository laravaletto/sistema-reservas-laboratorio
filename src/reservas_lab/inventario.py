"""Lectura del inventario fijo; no contiene operaciones de modificación."""

import json
from pathlib import Path

from .dominio import IDS_UNIDADES, ErrorInventario, Unidad


def cargar_inventario(ruta: Path) -> tuple[Unidad, ...]:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ErrorInventario(f"No se pudo leer el inventario: {ruta}") from exc
    if not isinstance(datos, list) or len(datos) != len(IDS_UNIDADES):
        raise ErrorInventario("El inventario debe contener las cinco unidades del laboratorio.")
    unidades = []
    for dato in datos:
        if (
            not isinstance(dato, dict)
            or set(dato) != {"id", "nombre"}
            or not isinstance(dato["id"], str)
            or not isinstance(dato["nombre"], str)
            or not dato["nombre"].strip()
        ):
            raise ErrorInventario("El inventario contiene una unidad inválida.")
        unidades.append(Unidad(dato["id"], dato["nombre"]))
    if {unidad.id for unidad in unidades} != IDS_UNIDADES:
        raise ErrorInventario("El inventario tiene identificadores incorrectos o repetidos.")
    return tuple(unidades)
