"""Punto de entrada: python iniciar.py (no requiere instalar el paquete)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from reservas_lab.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
