import json

import pytest

from reservas_lab.__main__ import RAIZ, RUTA_BASE, RUTA_INVENTARIO
from reservas_lab.dominio import ErrorInventario
from reservas_lab.inventario import cargar_inventario


def test_inventario_exacto_y_lectura_sin_modificacion(inventario):
    antes = RUTA_INVENTARIO.read_bytes()
    assert [(u.id, u.nombre) for u in inventario] == [
        ("MIC-01", "Microscopio digital"), ("MIC-02", "Microscopio digital"),
        ("OSC-01", "Osciloscopio"), ("MUL-01", "Multímetro"),
        ("FUE-01", "Fuente de alimentación"),
    ]
    assert cargar_inventario(RUTA_INVENTARIO) == inventario
    assert RUTA_INVENTARIO.read_bytes() == antes


@pytest.mark.parametrize("contenido", [
    b'{', b'\xff', b'{}', b'[]',
    json.dumps([{"id": "MIC-01", "nombre": "Equipo"}] * 5).encode(),
    json.dumps([{"id": "MIC-01", "nombre": " "}] * 5).encode(),
    json.dumps([{"id": [], "nombre": "Equipo"}] * 5).encode(),
    json.dumps([None] * 5).encode(),
])
def test_inventario_invalido_no_se_reemplaza(tmp_path, contenido):
    ruta = tmp_path / "inventario.json"
    ruta.write_bytes(contenido)
    with pytest.raises(ErrorInventario):
        cargar_inventario(ruta)
    assert ruta.read_bytes() == contenido


def test_inventario_ausente_no_se_crea(tmp_path):
    ruta = tmp_path / "ausente.json"
    with pytest.raises(ErrorInventario):
        cargar_inventario(ruta)
    assert not ruta.exists()


def test_rutas_no_dependen_del_directorio_actual(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert RUTA_BASE == RAIZ / "data" / "reservas.db"
    assert cargar_inventario(RUTA_INVENTARIO)
