"""Composición de la aplicación y rutas independientes del directorio actual."""

import sys
from pathlib import Path

from .inventario import cargar_inventario
from .persistencia import RepositorioSQLite
from .presentacion import mensaje_error
from .servicio import ServicioReservas

RAIZ = Path(__file__).resolve().parents[2]
RUTA_INVENTARIO = RAIZ / "data" / "inventario.json"
RUTA_BASE = RAIZ / "data" / "reservas.db"


def main() -> int:
    import tkinter as tk
    from tkinter import messagebox

    from .interfaz import Aplicacion

    raiz = None
    repositorio = None
    try:
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.protocol("WM_DELETE_WINDOW", raiz.quit)
        inventario = cargar_inventario(RUTA_INVENTARIO)
        repositorio = RepositorioSQLite(RUTA_BASE)
        Aplicacion(raiz, ServicioReservas(inventario, repositorio))
        raiz.deiconify()
        raiz.mainloop()
        return 0
    except Exception as exc:
        detalle = (
            "No se pudo abrir la interfaz. Comprobá que Python incluya Tkinter y que haya un escritorio disponible."
            if isinstance(exc, tk.TclError) else mensaje_error(exc).texto
        )
        mensaje = f"No se pudo iniciar el sistema de reservas.\n{detalle}"
        print(mensaje, file=sys.stderr)
        if raiz is not None:
            messagebox.showerror("Error de inicio", mensaje, parent=raiz)
        return 1
    finally:
        if repositorio is not None:
            repositorio.cerrar()
        if raiz is not None:
            raiz.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
