"""Mensajes y acciones de la interfaz con servicio real y controles sin Tk."""

from types import SimpleNamespace
from tkinter import TclError

import pytest

from reservas_lab.dominio import (
    ConflictoReserva, ErrorInventario, ErrorPersistencia, ErrorReservas,
    ErrorValidacion, ReservaInexistente, ReservaYaCancelada,
)
from reservas_lab.interfaz import Aplicacion
from reservas_lab.presentacion import mensaje_disponibilidad, mensaje_error


class Variable:
    def __init__(self, valor=""):
        self.valor = valor

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor


class Control:
    def __init__(self):
        self.opciones = {}
        self.foco = False
        self.seleccion_texto = None
        self.deshabilitado = False

    def configure(self, **opciones):
        self.opciones.update(opciones)

    def focus_set(self):
        self.foco = True

    def selection_range(self, inicio, fin):
        self.seleccion_texto = (inicio, fin)

    def state(self, estados):
        self.deshabilitado = "disabled" in estados


class Tabla(Control):
    def __init__(self):
        super().__init__()
        self.filas = {}
        self.seleccion = ()

    def selection(self):
        return self.seleccion

    def selection_set(self, item):
        self.seleccion = (item,)

    def get_children(self):
        return tuple(self.filas)

    def delete(self, item):
        del self.filas[item]
        if item in self.seleccion:
            self.seleccion = ()

    def insert(self, padre, posicion, iid, values, tags):
        self.filas[iid] = {"values": values, "tags": tags}

    def focus(self, item):
        self.item_foco = item

    def see(self, item):
        self.item_visible = item


@pytest.fixture
def app(servicio):
    # No se construye Tk ni se ejecuta __init__; se prueban las acciones reales.
    interfaz = Aplicacion.__new__(Aplicacion)
    interfaz.servicio = servicio
    interfaz.raiz = object()
    interfaz._opciones = {"MIC-01 — Microscopio digital": "MIC-01"}
    interfaz.unidad = Variable("MIC-01 — Microscopio digital")
    interfaz.solicitante = Variable("Persona ficticia")
    interfaz.inicio = Variable("2026-11-10 10:00")
    interfaz.fin = Variable("2026-11-10 11:00")
    interfaz.unidad_consulta = Variable(interfaz.unidad.get())
    interfaz.inicio_consulta = Variable(interfaz.inicio.get())
    interfaz.fin_consulta = Variable(interfaz.fin.get())
    interfaz._campos_reserva = {campo: Control() for campo in ("unidad", "solicitante", "inicio", "fin")}
    interfaz._campos_consulta = {campo: Control() for campo in ("unidad", "inicio", "fin")}
    interfaz.boton_crear = Control()
    interfaz.boton_consultar = Control()
    interfaz.boton_cancelar = Control()
    interfaz.tabla = Tabla()
    interfaz.estado_historial = Variable()
    interfaz._mensajes = {contexto: (Variable(), Control()) for contexto in ("reserva", "consulta", "historial")}
    interfaz.resultado = interfaz._mensajes["consulta"][0]
    interfaz._reservas = {}
    interfaz._historial_actualizado = False
    interfaz._refrescar_historial()
    return interfaz


def valores(app):
    return tuple(getattr(app, campo).get() for campo in ("unidad", "solicitante", "inicio", "fin"))


def estado(app, contexto):
    variable, etiqueta = app._mensajes[contexto]
    return variable.get(), etiqueta.opciones["style"]


@pytest.mark.parametrize("error, tipo", [
    (ErrorValidacion("Fin: fecha inválida.", campo="fin"), "error"),
    (ConflictoReserva("detalle no presentable"), "aviso"),
    (ReservaYaCancelada("detalle no presentable"), "info"),
    (ReservaInexistente("detalle no presentable"), "error"),
    (ErrorPersistencia("detalle no presentable"), "error"),
    (ErrorInventario("detalle no presentable"), "error"),
    (ErrorReservas("detalle no presentable"), "error"),
    (RuntimeError("detalle no presentable"), "error"),
])
def test_mensajes_seguros_y_clasificacion(error, tipo):
    mensaje = mensaje_error(error)
    assert mensaje.tipo == tipo
    assert "detalle no presentable" not in mensaje.texto
    if isinstance(error, ErrorValidacion):
        assert mensaje.campo == "fin"
        assert "Fin" in mensaje.texto


def test_disponibilidad_tiene_texto_y_tipo_distinto():
    libre, ocupada = mensaje_disponibilidad(True), mensaje_disponibilidad(False)
    assert libre.tipo == "exito" and libre.texto.startswith("Disponible:")
    assert ocupada.tipo == "aviso" and ocupada.texto.startswith("No disponible:")


@pytest.mark.parametrize("campo, valor, foco, fragmento", [
    ("unidad", "", "unidad", "Seleccioná"),
    ("inicio", "2026-11-10 24:00", "inicio", "Inicio"),
    ("fin", "2026-11-10 25:00", "fin", "Fin"),
    ("fin", "2026-11-10", "fin", "AAAA-MM-DD HH:MM"),
    ("fin", "2026-11-10 09:00", "fin", "posterior"),
    ("solicitante", "  ", "solicitante", "solicitante ficticio"),
])
def test_error_de_creacion_conserva_campos_y_dirige_foco(app, campo, valor, foco, fragmento):
    getattr(app, campo).set(valor)
    antes = valores(app)
    app._crear()
    texto, estilo = estado(app, "reserva")
    assert fragmento in texto and estilo == "Error.TLabel"
    assert valores(app) == antes
    assert app._campos_reserva[foco].foco
    assert app.servicio.historial() == ()


@pytest.mark.parametrize("campo, valor", [
    ("unidad", ""), ("inicio", "texto inválido"),
    ("fin", "2026-02-30 11:00"), ("fin", "2026-11-10 09:00"),
])
def test_consulta_invalida_reemplaza_resultado_previo_sin_perder_datos(app, campo, valor):
    app._consultar()
    assert estado(app, "consulta")[1] == "Exito.TLabel"
    getattr(app, campo + "_consulta").set(valor)
    app._consultar()
    assert estado(app, "consulta")[1] == "Error.TLabel"
    assert getattr(app, campo + "_consulta").get() == valor
    assert app._campos_consulta[campo].foco
    assert app.servicio.historial() == ()


def test_conflicto_se_distingue_de_error_de_entrada(app):
    app._crear()
    antes = valores(app)
    app._crear()
    assert estado(app, "reserva")[1] == "Aviso.TLabel"
    assert estado(app, "reserva")[0].startswith("No disponible:")
    assert valores(app) == antes
    assert len(app.servicio.historial()) == 1


def test_crear_actualiza_historial_invalida_consulta_y_mantiene_formulario(app):
    app._consultar()
    antes = valores(app)
    app._crear()
    reserva = app.servicio.historial()[0]
    assert reserva.id in estado(app, "reserva")[0]
    assert estado(app, "reserva")[1] == "Exito.TLabel"
    assert "Volvé a consultar" in app.resultado.get()
    assert estado(app, "consulta")[1] == "Info.TLabel"
    assert app.tabla.filas[reserva.id]["tags"] == ("ACTIVA",)
    assert valores(app) == antes
    assert app._campos_reserva["inicio"].seleccion_texto is not None


def preparar_seleccion(app):
    app._crear()
    reserva = app.servicio.historial()[0]
    app.tabla.selection_set(reserva.id)
    app._seleccionar()
    assert not app.boton_cancelar.deshabilitado
    return reserva


def test_rechazar_confirmacion_no_cambia_reserva_ni_consulta(app, monkeypatch):
    reserva = preparar_seleccion(app)
    app._consultar()
    resultado = app.resultado.get()
    confirmaciones = []

    def rechazar(*args, **kwargs):
        confirmaciones.append((args, kwargs))
        return False

    monkeypatch.setattr("reservas_lab.interfaz.messagebox.askyesno", rechazar)
    app._cancelar()
    assert app.servicio.historial() == (reserva,)
    assert app.resultado.get() == resultado
    assert app.tabla.foco
    assert confirmaciones[0][1]["default"] == "no"
    assert reserva.id in confirmaciones[0][0][1]
    assert "MIC-01" in confirmaciones[0][0][1]


def test_cancelar_actualiza_estado_seleccion_y_boton(app, monkeypatch):
    reserva = preparar_seleccion(app)
    monkeypatch.setattr("reservas_lab.interfaz.messagebox.askyesno", lambda *a, **kw: True)
    app._cancelar()
    assert app.servicio.historial()[0].estado == "CANCELADA"
    assert app.tabla.filas[reserva.id]["tags"] == ("CANCELADA",)
    assert app.tabla.selection() == (reserva.id,)
    assert app.boton_cancelar.deshabilitado
    assert estado(app, "historial")[1] == "Exito.TLabel"
    assert estado(app, "consulta")[1] == "Info.TLabel"
    assert "0 ACTIVA" in app.estado_historial.get()
    assert "1 CANCELADA" in app.estado_historial.get()
    assert app.tabla.foco


@pytest.mark.parametrize("operacion", ["crear", "disponible", "cancelar"])
def test_excepcion_interna_no_se_muestra_y_no_se_anuncia_exito(app, monkeypatch, operacion):
    if operacion == "cancelar":
        preparar_seleccion(app)
        monkeypatch.setattr("reservas_lab.interfaz.messagebox.askyesno", lambda *a, **kw: True)
    antes = valores(app)

    def fallar(*args):
        raise RuntimeError("sqlite: ruta-interna-secreta")

    monkeypatch.setattr(app.servicio, operacion, fallar)
    contexto, accion = {
        "crear": ("reserva", app._crear),
        "disponible": ("consulta", app._consultar),
        "cancelar": ("historial", app._cancelar),
    }[operacion]
    accion()
    texto, estilo = estado(app, contexto)
    assert "ruta-interna-secreta" not in texto
    assert "sqlite" not in texto
    assert estilo == "Error.TLabel"
    assert valores(app) == antes


def test_historial_no_actualizado_no_habilita_cancelaciones(app, monkeypatch):
    reserva = preparar_seleccion(app)

    def fallar():
        raise ErrorPersistencia("detalle interno")

    monkeypatch.setattr(app.servicio, "historial", fallar)
    assert app._refrescar_historial() is False
    app._seleccionar()
    assert app.boton_cancelar.deshabilitado
    assert reserva.id in app.tabla.filas
    assert "detalle interno" not in estado(app, "historial")[0]
    assert "última lectura" in app.estado_historial.get()
    monkeypatch.setattr("reservas_lab.interfaz.messagebox.askyesno", lambda *a, **kw: pytest.fail("No debe cancelar un listado desactualizado"))
    app._cancelar()


def test_creacion_guardada_se_distingue_del_fallo_de_actualizacion(app, monkeypatch):
    historial_original = app.servicio.historial

    def fallar():
        raise ErrorPersistencia("detalle interno")

    monkeypatch.setattr(app.servicio, "historial", fallar)
    app._crear()
    assert len(historial_original()) == 1
    assert estado(app, "reserva")[1] == "Exito.TLabel"
    assert estado(app, "historial")[1] == "Error.TLabel"
    assert app.boton_cancelar.deshabilitado


def test_cancelacion_previa_externa_se_informa_y_refresca(app, monkeypatch):
    reserva = preparar_seleccion(app)
    app.servicio.cancelar(reserva.id)
    monkeypatch.setattr("reservas_lab.interfaz.messagebox.askyesno", lambda *a, **kw: True)
    app._cancelar()
    assert "ya estaba cancelada" in estado(app, "historial")[0]
    assert estado(app, "historial")[1] == "Info.TLabel"
    assert app.boton_cancelar.deshabilitado


def test_cancelacion_guardada_se_informa_si_falla_la_lectura_posterior(app, monkeypatch):
    preparar_seleccion(app)
    historial_original = app.servicio.historial

    def fallar():
        raise ErrorPersistencia("detalle interno")

    monkeypatch.setattr(app.servicio, "historial", fallar)
    monkeypatch.setattr("reservas_lab.interfaz.messagebox.askyesno", lambda *a, **kw: True)
    app._cancelar()
    assert historial_original()[0].estado == "CANCELADA"
    texto, estilo = estado(app, "historial")
    assert "está cancelada" in texto and "no se pudo actualizar" in texto
    assert "detalle interno" not in texto
    assert estilo == "Aviso.TLabel"
    assert app.boton_cancelar.deshabilitado


@pytest.mark.parametrize("error", [
    ErrorInventario("ruta-interna"), ErrorPersistencia("ruta-interna"),
    RuntimeError("ruta-interna"), TclError("ruta-interna"),
])
def test_inicio_no_presenta_detalles_tecnicos(monkeypatch, capsys, error):
    import reservas_lab.__main__ as entrada

    raiz = SimpleNamespace(withdraw=lambda: None, protocol=lambda *a: None, destroy=lambda: None)
    monkeypatch.setattr("tkinter.Tk", lambda: raiz)

    def fallar(*args):
        raise error

    monkeypatch.setattr(entrada, "cargar_inventario", fallar)
    mensajes = []
    monkeypatch.setattr("tkinter.messagebox.showerror", lambda titulo, texto, **kw: mensajes.append(texto))
    assert entrada.main() == 1
    assert "ruta-interna" not in capsys.readouterr().err
    assert "ruta-interna" not in mensajes[0]
