"""Interfaz de escritorio: delega toda regla de negocio al servicio."""

import tkinter as tk
from tkinter import messagebox, ttk

from .dominio import ACTIVA, ErrorReservas, ReservaYaCancelada, escribir_fecha
from .servicio import ServicioReservas


class Aplicacion:
    def __init__(self, raiz: tk.Tk, servicio: ServicioReservas):
        self.raiz = raiz
        self.servicio = servicio
        self._reservas = {}
        self._opciones = {
            f"{unidad.id} — {unidad.nombre}": unidad.id for unidad in servicio.inventario
        }
        raiz.title("Reservas de laboratorio")
        raiz.geometry("1120x720")
        raiz.minsize(900, 620)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)
        marco = ttk.Frame(raiz, padding=16)
        marco.grid(sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(3, weight=1)
        ttk.Label(marco, text="Reservas de laboratorio", font=("Segoe UI", 18, "bold")).grid(sticky="w")
        ttk.Label(
            marco, text="Agenda local · America/Argentina/Cordoba · Usá solicitantes ficticios",
        ).grid(sticky="w", pady=(4, 12))
        self._inventario(marco)
        pestañas = ttk.Notebook(marco)
        pestañas.grid(row=3, sticky="nsew", pady=(12, 0))
        reservas = ttk.Frame(pestañas, padding=16)
        disponibilidad = ttk.Frame(pestañas, padding=16)
        historial = ttk.Frame(pestañas, padding=16)
        for marco_tab, titulo in (
            (reservas, "Reservas"), (disponibilidad, "Disponibilidad"), (historial, "Historial")
        ):
            pestañas.add(marco_tab, text=titulo)
        self._formulario_reservas(reservas)
        self._formulario_disponibilidad(disponibilidad)
        self._historial(historial)
        self._refrescar_historial()
        pestañas.bind("<<NotebookTabChanged>>", self._cambio_pestaña)

    def _inventario(self, marco):
        grupo = ttk.LabelFrame(marco, text="Inventario fijo · sólo lectura", padding=8)
        grupo.grid(row=2, sticky="ew")
        tabla = ttk.Treeview(grupo, columns=("id", "nombre"), show="headings", height=5, selectmode="none")
        tabla.heading("id", text="Unidad")
        tabla.heading("nombre", text="Equipo")
        tabla.column("id", width=100, stretch=False)
        tabla.column("nombre", width=350)
        tabla.pack(fill="x")
        for unidad in self.servicio.inventario:
            tabla.insert("", "end", values=(unidad.id, unidad.nombre))

    def _campos_intervalo(self, marco, con_solicitante=False):
        marco.columnconfigure(1, weight=1)
        unidad = tk.StringVar()
        inicio, fin = tk.StringVar(), tk.StringVar()
        ttk.Label(marco, text="Unidad").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        selector = ttk.Combobox(marco, textvariable=unidad, values=tuple(self._opciones), state="readonly")
        selector.grid(row=0, column=1, sticky="ew", pady=6)
        selector.current(0)
        fila = 1
        solicitante = tk.StringVar()
        if con_solicitante:
            ttk.Label(marco, text="Solicitante ficticio").grid(row=fila, column=0, sticky="w", pady=6)
            ttk.Entry(marco, textvariable=solicitante).grid(row=fila, column=1, sticky="ew", pady=6)
            fila += 1
        for etiqueta, variable in (("Inicio", inicio), ("Fin", fin)):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=6)
            ttk.Entry(marco, textvariable=variable).grid(row=fila, column=1, sticky="ew", pady=6)
            fila += 1
        ttk.Label(
            marco, text="Formato: AAAA-MM-DD HH:MM · Ejemplo: 2026-11-10 10:30",
        ).grid(row=fila, column=0, columnspan=2, sticky="w", pady=8)
        return unidad, solicitante, inicio, fin, fila + 1

    def _formulario_reservas(self, marco):
        self.unidad, self.solicitante, self.inicio, self.fin, fila = self._campos_intervalo(marco, True)
        ttk.Button(marco, text="Crear reserva", command=self._crear).grid(row=fila, column=1, sticky="e", pady=8)

    def _formulario_disponibilidad(self, marco):
        self.unidad_consulta, _, self.inicio_consulta, self.fin_consulta, fila = self._campos_intervalo(marco)
        ttk.Button(marco, text="Consultar disponibilidad", command=self._consultar).grid(
            row=fila, column=1, sticky="e", pady=8,
        )
        self.resultado = tk.StringVar(value="Ingresá un intervalo para consultar.")
        ttk.Label(marco, textvariable=self.resultado, wraplength=760).grid(
            row=fila + 1, column=0, columnspan=2, sticky="w", pady=8,
        )

    def _historial(self, marco):
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)
        self.estado_historial = tk.StringVar()
        ttk.Label(marco, textvariable=self.estado_historial).grid(sticky="w", pady=(0, 8))
        columnas = ("id", "unidad", "solicitante", "inicio", "fin", "estado")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse", height=8)
        for columna, titulo, ancho in zip(
            columnas, ("UUID", "Unidad", "Solicitante", "Inicio", "Fin", "Estado"),
            (280, 85, 160, 145, 145, 110),
        ):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, minwidth=ancho, stretch=False)
        self.tabla.grid(row=1, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        vertical.grid(row=1, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)
        horizontal.grid(row=2, column=0, sticky="ew")
        self.tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.boton_cancelar = ttk.Button(marco, text="Cancelar reserva seleccionada", command=self._cancelar, state="disabled")
        self.boton_cancelar.grid(row=3, column=0, sticky="e", pady=(12, 0))
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar)

    def _crear(self):
        try:
            reserva = self.servicio.crear(
                self._opciones.get(self.unidad.get(), ""), self.solicitante.get(),
                self.inicio.get(), self.fin.get(),
            )
        except ErrorReservas as exc:
            messagebox.showerror("No se pudo crear la reserva", str(exc), parent=self.raiz)
            return
        self.resultado.set("Los datos cambiaron. Volvé a consultar disponibilidad.")
        messagebox.showinfo("Reserva creada", f"Reserva guardada.\nUUID: {reserva.id}", parent=self.raiz)
        self._refrescar_historial()

    def _consultar(self):
        self.resultado.set("")
        try:
            disponible = self.servicio.disponible(
                self._opciones.get(self.unidad_consulta.get(), ""),
                self.inicio_consulta.get(), self.fin_consulta.get(),
            )
        except ErrorReservas as exc:
            messagebox.showerror("No se pudo consultar", str(exc), parent=self.raiz)
            return
        self.resultado.set("Disponible para el intervalo indicado." if disponible else "No disponible: hay una reserva activa superpuesta.")

    def _refrescar_historial(self):
        try:
            reservas = self.servicio.historial()
        except ErrorReservas as exc:
            self.estado_historial.set("No se pudo actualizar el historial.")
            self.boton_cancelar.state(["disabled"])
            messagebox.showerror("Error de lectura", str(exc), parent=self.raiz)
            return
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self._reservas = {reserva.id: reserva for reserva in reservas}
        for reserva in reservas:
            self.tabla.insert("", "end", iid=reserva.id, values=(
                reserva.id, reserva.unidad_id, reserva.solicitante,
                escribir_fecha(reserva.inicio), escribir_fecha(reserva.fin), reserva.estado,
            ))
        self.estado_historial.set(f"{len(reservas)} reservas · activas y canceladas" if reservas else "Todavía no hay reservas.")
        self._seleccionar()

    def _cambio_pestaña(self, _evento):
        self._refrescar_historial()

    def _seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        reserva = self._reservas.get(seleccion[0]) if seleccion else None
        self.boton_cancelar.state(["!disabled"] if reserva and reserva.estado == ACTIVA else ["disabled"])

    def _cancelar(self):
        seleccion = self.tabla.selection()
        reserva = self._reservas.get(seleccion[0]) if seleccion else None
        if reserva is None or reserva.estado != ACTIVA:
            return
        if not messagebox.askyesno("Confirmar cancelación", f"¿Cancelar la reserva {reserva.id}?", parent=self.raiz):
            return
        try:
            self.servicio.cancelar(reserva.id)
        except ReservaYaCancelada as exc:
            messagebox.showinfo("Reserva ya cancelada", str(exc), parent=self.raiz)
        except ErrorReservas as exc:
            messagebox.showerror("No se pudo cancelar", str(exc), parent=self.raiz)
            return
        else:
            messagebox.showinfo("Reserva cancelada", "El intervalo quedó libre y el registro se conserva.", parent=self.raiz)
        self.resultado.set("Los datos cambiaron. Volvé a consultar disponibilidad.")
        self._refrescar_historial()
