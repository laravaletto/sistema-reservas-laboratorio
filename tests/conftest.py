from pathlib import Path

import pytest

from reservas_lab.inventario import cargar_inventario
from reservas_lab.persistencia import RepositorioSQLite
from reservas_lab.servicio import ServicioReservas

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def inventario():
    return cargar_inventario(RAIZ / "data" / "inventario.json")


@pytest.fixture
def ruta_base(tmp_path):
    return tmp_path / "reservas.db"


@pytest.fixture
def repositorio(ruta_base):
    repo = RepositorioSQLite(ruta_base)
    yield repo
    repo.cerrar()


@pytest.fixture
def servicio(inventario, repositorio):
    return ServicioReservas(inventario, repositorio)
