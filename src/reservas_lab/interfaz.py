"""Interfaz de escritorio: delega toda regla de negocio al servicio."""

import tkinter as tk
from tkinter import messagebox, ttk

from .dominio import ACTIVA, ReservaYaCancelada, escribir_fecha
from .presentacion import Mensaje, mensaje_disponibilidad, mensaje_error
from .servicio import ServicioReservas


class Aplicacion:
    def __init__(self, raiz: tk.Tk, servicio: ServicioReservas):
        self.raiz = raiz
        self.servicio = servicio
        self._reservas = {}
        self._historial_actualizado = False
        self._mensajes = {}
        self._opciones = {
            f"{unidad.id} — {unidad.nombre}": unidad.id for unidad in servicio.inventario
        }
        raiz.title("Reservas de laboratorio")
        raiz.geometry("1120x720")
        raiz.minsize(900, 620)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)
        estilos = ttk.Style(raiz)
        for nombre, color in (
            ("Exito", "#116329"), ("Error", "#b42318"),
            ("Aviso", "#8a4b00"), ("Info", "#344054"),
        ):
            estilos.configure(f"{nombre}.TLabel", foreground=color)
        marco = ttk.Frame(raiz, padding=16)
        marco.grid(sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(3, weight=1)
        ttk.Label(marco, text="Reservas de laboratorio", font=("Segoe UI", 18, "bold")).grid(sticky="w")
        ttk.Label(
            marco, text="Agenda local · America/Argentina/Cordoba · Usá solicitantes ficticios",
        ).grid(sticky="w", pady=(4, 12))
        self._inventario(marco)
        self.pestañas = pestañas = ttk.Notebook(marco)
        pestañas.grid(row=3, sticky="nsew", pady=(12, 0))
        reservas = ttk.Frame(pestañas, padding=16)
        disponibilidad = ttk.Frame(pestañas, padding=16)
        historial = ttk.Frame(pestañas, padding=16)
        for marco_tab, titulo in (
            (reservas, "Reservas"), (disponibilidad, "Disponibilidad"), (historial, "Historial")
        ):
            pestañas.add(marco_tab, text=titulo, underline=0)
        pestañas.enable_traversal()
        self._formulario_reservas(reservas)
        self._formulario_disponibilidad(disponibilidad)
        self._historial(historial)
        self._focos_pestaña = {
            str(reservas): self._campos_reserva["unidad"],
            str(disponibilidad): self._campos_consulta["unidad"],
            str(historial): self.tabla,
        }
        self._pestaña_historial = str(historial)
        self._refrescar_historial()
        pestañas.bind("<<NotebookTabChanged>>", self._cambio_pestaña)
        raiz.after_idle(self._campos_reserva["unidad"].focus_set)

    def _inventario(self, marco):
        grupo = ttk.LabelFrame(marco, text="Inventario fijo · sólo lectura", padding=8)
        grupo.grid(row=2, sticky="ew")
        tabla = ttk.Treeview(grupo, columns=("id", "nombre"), show="headings", height=5, selectmode="none", takefocus=False)
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
        ttk.Label(marco, text="Unidad (ID y equipo)").grid(row=0, column=0, sticky="w", padx=(0, 16), pady=8)
        selector = ttk.Combobox(marco, textvariable=unidad, values=tuple(self._opciones), state="readonly", takefocus=True)
        selector.grid(row=0, column=1, sticky="ew", pady=6)
        campos = {"unidad": selector}
        fila = 1
        solicitante = tk.StringVar()
        if con_solicitante:
            ttk.Label(marco, text="Solicitante ficticio").grid(row=fila, column=0, sticky="w", pady=6)
            campos["solicitante"] = ttk.Entry(marco, textvariable=solicitante, takefocus=True)
            campos["solicitante"].grid(row=fila, column=1, sticky="ew", pady=8)
            fila += 1
        for campo, etiqueta, variable in (("inicio", "Inicio (fecha y hora)", inicio), ("fin", "Fin (fecha y hora)", fin)):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=8)
            campos[campo] = ttk.Entry(marco, textvariable=variable, takefocus=True)
            campos[campo].grid(row=fila, column=1, sticky="ew", pady=8)
            fila += 1
        ttk.Label(
            marco, text="Todos los campos son obligatorios. Formato: AAAA-MM-DD HH:MM · Ejemplo: 2026-11-10 10:30",
            wraplength=760,
        ).grid(row=fila, column=0, columnspan=2, sticky="w", pady=8)
        return unidad, solicitante, inicio, fin, fila + 1, campos

    def _formulario_reservas(self, marco):
        self.unidad, self.solicitante, self.inicio, self.fin, fila, self._campos_reserva = self._campos_intervalo(marco, True)
        self.boton_crear = ttk.Button(marco, text="Crear reserva", command=self._crear, takefocus=True)
        self.boton_crear.grid(row=fila, column=1, sticky="e", pady=8)
        self.boton_crear.bind("<Return>", self._activar_boton)
        self._crear_mensaje(marco, "reserva", fila + 1)

    def _formulario_disponibilidad(self, marco):
        self.unidad_consulta, _, self.inicio_consulta, self.fin_consulta, fila, self._campos_consulta = self._campos_intervalo(marco)
        self.boton_consultar = ttk.Button(marco, text="Consultar disponibilidad", command=self._consultar, takefocus=True)
        self.boton_consultar.grid(
            row=fila, column=1, sticky="e", pady=8,
        )
        self.boton_consultar.bind("<Return>", self._activar_boton)
        self.resultado = self._crear_mensaje(marco, "consulta", fila + 1)
        self._mostrar_mensaje("consulta", Mensaje("Seleccioná una unidad e ingresá un intervalo para consultar."))
        for variable in (self.unidad_consulta, self.inicio_consulta, self.fin_consulta):
            variable.trace_add("write", lambda *_: self._invalidar_disponibilidad("La consulta cambió. Volvé a consultar disponibilidad."))

    def _crear_mensaje(self, marco, contexto, fila):
        variable = tk.StringVar()
        etiqueta = ttk.Label(marco, textvariable=variable, style="Info.TLabel", wraplength=760)
        etiqueta.grid(row=fila, column=0, columnspan=2, sticky="w", pady=8)
        self._mensajes[contexto] = (variable, etiqueta)
        return variable

    def _mostrar_mensaje(self, contexto, mensaje):
        variable, etiqueta = self._mensajes[contexto]
        estilos = {"exito": "Exito", "error": "Error", "aviso": "Aviso", "info": "Info"}
        variable.set(mensaje.texto)
        etiqueta.configure(style=f"{estilos[mensaje.tipo]}.TLabel")

    @staticmethod
    def _enfocar(control, seleccionar=False):
        control.focus_set()
        if seleccionar and hasattr(control, "selection_range"):
            control.selection_range(0, tk.END)

    def _mostrar_error(self, contexto, error, campos=None, alternativa=None):
        mensaje = mensaje_error(error)
        self._mostrar_mensaje(contexto, mensaje)
        control = (campos or {}).get(mensaje.campo, alternativa)
        if control is not None:
            self._enfocar(control, seleccionar=True)

    def _invalidar_disponibilidad(self, motivo="Las reservas cambiaron. Volvé a consultar disponibilidad."):
        self._mostrar_mensaje("consulta", Mensaje(motivo))

    @staticmethod
    def _activar_boton(evento):
        evento.widget.invoke()
        return "break"

    def _historial(self, marco):
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)
        self.estado_historial = tk.StringVar()
        ttk.Label(marco, textvariable=self.estado_historial).grid(sticky="w", pady=(0, 8))
        columnas = ("id", "unidad", "solicitante", "inicio", "fin", "estado")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse", height=8, takefocus=True)
        self.tabla.tag_configure("ACTIVA", foreground="#116329", background="#edf7ed")
        self.tabla.tag_configure("CANCELADA", foreground="#475467", background="#f2f4f7")
        for columna, titulo, ancho in zip(
            columnas, ("UUID", "Unidad", "Solicitante", "Inicio", "Fin", "Estado"),
            (280, 85, 160, 145, 145, 110),
        ):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, minwidth=ancho, stretch=False)
        self.tabla.grid(row=1, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview, takefocus=False)
        vertical.grid(row=1, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview, takefocus=False)
        horizontal.grid(row=2, column=0, sticky="ew")
        self.tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.boton_cancelar = ttk.Button(marco, text="Cancelar reserva seleccionada", command=self._cancelar, state="disabled", takefocus="ttk::takefocus")
        self.boton_cancelar.grid(row=3, column=0, sticky="e", pady=(12, 0))
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar)
        self.boton_cancelar.bind("<Return>", self._activar_boton)
        self._crear_mensaje(marco, "historial", 4)

    def _crear(self):
        try:
            reserva = self.servicio.crear(
                self._opciones.get(self.unidad.get(), ""), self.solicitante.get(),
                self.inicio.get(), self.fin.get(),
            )
        except Exception as exc:
            self._mostrar_error("reserva", exc, self._campos_reserva, self.boton_crear)
            return
        self._invalidar_disponibilidad()
        self._mostrar_mensaje("reserva", Mensaje(f"Éxito: reserva guardada. UUID: {reserva.id}", "exito"))
        self._refrescar_historial()
        self._enfocar(self._campos_reserva["inicio"], seleccionar=True)

    def _consultar(self):
        try:
            disponible = self.servicio.disponible(
                self._opciones.get(self.unidad_consulta.get(), ""),
                self.inicio_consulta.get(), self.fin_consulta.get(),
            )
        except Exception as exc:
            self._mostrar_error("consulta", exc, self._campos_consulta, self.boton_consultar)
            return
        self._mostrar_mensaje("consulta", mensaje_disponibilidad(disponible))
        self._enfocar(self.boton_consultar)

    def _refrescar_historial(self):
        try:
            reservas = self.servicio.historial()
        except Exception as exc:
            self._historial_actualizado = False
            self.estado_historial.set("No se pudo actualizar el historial. Se conserva la última lectura.")
            self.boton_cancelar.state(["disabled"])
            self._mostrar_error("historial", exc)
            return False
        seleccion = self.tabla.selection()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self._reservas = {reserva.id: reserva for reserva in reservas}
        for reserva in reservas:
            self.tabla.insert("", "end", iid=reserva.id, values=(
                reserva.id, reserva.unidad_id, reserva.solicitante,
                escribir_fecha(reserva.inicio), escribir_fecha(reserva.fin), reserva.estado,
            ), tags=(reserva.estado,))
        if seleccion and seleccion[0] in self._reservas:
            self.tabla.selection_set(seleccion[0])
            self.tabla.focus(seleccion[0])
            self.tabla.see(seleccion[0])
        activas = sum(reserva.estado == ACTIVA for reserva in reservas)
        self.estado_historial.set(
            f"{len(reservas)} reservas · {activas} ACTIVA · {len(reservas) - activas} CANCELADA"
            if reservas else "Todavía no hay reservas."
        )
        self._historial_actualizado = True
        self._mostrar_mensaje("historial", Mensaje(""))
        self._seleccionar()
        return True

    def _cambio_pestaña(self, _evento):
        seleccionada = self.pestañas.select()
        if seleccionada == self._pestaña_historial:
            self._refrescar_historial()
        control = self._focos_pestaña.get(seleccionada)
        if control is not None:
            self.raiz.after_idle(control.focus_set)

    def _seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        reserva = self._reservas.get(seleccion[0]) if seleccion else None
        habilitar = self._historial_actualizado and reserva and reserva.estado == ACTIVA
        self.boton_cancelar.state(["!disabled"] if habilitar else ["disabled"])

    def _cancelar(self):
        seleccion = self.tabla.selection()
        reserva = self._reservas.get(seleccion[0]) if seleccion else None
        if not self._historial_actualizado or reserva is None or reserva.estado != ACTIVA:
            return
        detalle = (
            f"¿Cancelar la reserva de {reserva.unidad_id}?\n"
            f"{escribir_fecha(reserva.inicio)} a {escribir_fecha(reserva.fin)}\n"
            f"UUID: {reserva.id}\n\nEl registro se conservará en el historial."
        )
        if not messagebox.askyesno("Confirmar cancelación", detalle, parent=self.raiz, default=messagebox.NO):
            self._enfocar(self.tabla)
            return
        try:
            self.servicio.cancelar(reserva.id)
        except ReservaYaCancelada as exc:
            mensaje = mensaje_error(exc)
        except Exception as exc:
            self._mostrar_error("historial", exc, alternativa=self.tabla)
            return
        else:
            mensaje = Mensaje("Éxito: reserva cancelada. Su intervalo se liberó y el registro se conserva.", "exito")
        self._invalidar_disponibilidad()
        if self._refrescar_historial():
            self._mostrar_mensaje("historial", mensaje)
        else:
            self._mostrar_mensaje("historial", Mensaje(
                "La reserva está cancelada, pero no se pudo actualizar el listado. Volvé a entrar a Historial.", "aviso",
            ))
        self._enfocar(self.tabla)
