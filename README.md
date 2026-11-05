# Sistema de Reservas de Laboratorio

Trabajo académico individual.

**Estado al 2026-11-05:** etapa 1 revisada y aceptada por la autora, versionada en
`b445b3d`. Segunda delegación: aplicación y pruebas implementadas; revisión
funcional humana y commit de esta implementación pendientes.

## 1. Especificación breve

El laboratorio registra solicitudes de equipos mediante mensajes y planillas, lo que puede generar superposiciones de reservas y horarios que permanecen bloqueados después de una cancelación.

Se propone desarrollar una aplicación local para administrar reservas de cinco unidades físicas fijas:

| Identificador | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

### Requisitos funcionales

- **RF01 — Inventario:** leer y mostrar las cinco unidades físicas disponibles.
- **RF02 — Disponibilidad:** consultar si una unidad está disponible en un intervalo determinado.
- **RF03 — Crear reserva:** registrar una reserva con UUID, solicitante ficticio, fecha y hora de inicio, fecha y hora de fin y estado.
- **RF04 — Cancelar reserva:** cancelar una reserva sin eliminar sus datos.
- **RF05 — Persistencia:** conservar las reservas activas y canceladas entre ejecuciones.
- **RF06 — Historial:** consultar todas las reservas registradas y sus estados.

### Reglas de negocio

Se rechazan las unidades inexistentes, los solicitantes vacíos, las fechas inválidas y los intervalos cuyo inicio sea igual o posterior al fin.

Sólo las reservas con estado `ACTIVA` de una misma unidad bloquean disponibilidad.

Se utilizan intervalos semiabiertos `[inicio, fin)`, considerando que existe superposición cuando:

`inicio_nuevo < fin_existente AND inicio_existente < fin_nuevo`

Las consultas de disponibilidad y la creación de reservas deben utilizar las mismas reglas.

Se permiten reservas consecutivas de una misma unidad y reservas simultáneas de unidades diferentes.

La cancelación libera el intervalo previamente ocupado, pero conserva el registro original en el historial.

### Supuestos y representación temporal

- Zona horaria de referencia: `America/Argentina/Cordoba`.
- Formato exacto de entrada: `AAAA-MM-DD HH:MM`.
- Ejemplo: `2026-11-10 10:30`.
- Fechas y horas civiles locales, sin conversiones entre zonas horarias.
- Precisión de minutos.
- Fechas pasadas permitidas.
- Sin restricciones adicionales de duración o anticipación.
- Rango técnico de años: 0001–9999.
- Identificación de reservas mediante UUID4.
- Estados posibles: `ACTIVA` y `CANCELADA`.

### Criterios de aceptación

La aplicación deberá:

- Mostrar correctamente las cinco unidades del inventario.
- Validar las entradas y evitar guardar operaciones rechazadas.
- Rechazar reservas superpuestas de una misma unidad.
- Permitir reservas consecutivas y simultáneas de unidades diferentes.
- Cancelar reservas sin eliminar sus campos originales.
- Liberar la disponibilidad después de una cancelación.
- Recuperar reservas activas y canceladas después de cerrar y reiniciar la aplicación.
- Mostrar el historial completo de reservas.

La [especificación completa](docs/especificacion.md) contiene los requisitos, las reglas de negocio RN01–RN09, los criterios CA01–CA06c y los casos de prueba previstos CP01–CP18.

La lógica y la persistencia cuentan con pruebas automáticas. Se comprobó la
interfaz con widgets ocultos; la revisión visual y la aceptación funcional humana
siguen pendientes. Resultados y límites en [verificaciones](docs/verificaciones.md).

### Fuera de alcance

No se incluyen autenticación, roles reales, notificaciones, pagos, integraciones externas, despliegue, aplicación web, interfaces complejas, concurrencia distribuida, escalabilidad de producción, MCP, sistemas multiagente ni administración dinámica del inventario.

## 2. Solución

### Estructura actual del proyecto

```text
sistema-reservas-laboratorio/
├── .gitignore
├── AGENTS.md
├── README.md
├── iniciar.py
├── pytest.ini
├── requirements-dev.txt
├── data/
│   └── inventario.json
├── docs/
│   ├── especificacion.md
│   ├── decisiones.md
│   ├── delegacion.md
│   ├── progreso.md
│   └── verificaciones.md
├── src/reservas_lab/
│   ├── __init__.py
│   ├── __main__.py
│   ├── dominio.py
│   ├── inventario.py
│   ├── persistencia.py
│   ├── servicio.py
│   └── interfaz.py
└── tests/
    ├── conftest.py
    ├── test_inventario.py
    ├── test_persistencia.py
    └── test_reglas.py
```

Se agregaron `iniciar.py`, `requirements-dev.txt`, `pytest.ini`, el paquete
`src/reservas_lab/` y `tests/`. La base local se crea en el primer inicio correcto;
no se distribuye una base con datos de prueba.

### Arquitectura y tecnologías

La implementación utiliza:

- **Python:** lenguaje principal de programación.
- **Tkinter/ttk:** interfaz gráfica de escritorio.
- **SQLite mediante `sqlite3`:** persistencia local de reservas.
- **pytest:** pruebas automáticas de lógica de negocio y persistencia.

`dominio.py` define datos, errores y fechas; `inventario.py` lee el JSON;
`servicio.py` valida y coordina los casos de uso; `persistencia.py` ejecuta SQL
parametrizado y transacciones; `interfaz.py` presenta los formularios y el historial.
`__main__.py` conecta los componentes y resuelve las rutas desde el archivo del
paquete. `iniciar.py` permite arrancar sin instalarlo como paquete.

Las pruebas de reglas y persistencia no importan la interfaz ni abren ventanas.

La justificación de las tecnologías, las alternativas consideradas y sus consecuencias están documentadas en [decisiones.md](docs/decisiones.md).

### Requisitos previos, instalación, ejecución y pruebas

Se requiere Python 3.10 o posterior, con Tkinter/ttk y sqlite3. La versión
comprobada en este entorno es Python 3.13.7; no se probaron otras versiones.
La aplicación usa sólo la biblioteca estándar. pytest es dependencia de desarrollo.

En el entorno de trabajo se observaron:

- Python `3.13.7`.
- Git `2.47.0.windows.2`.

También se observaron SQLite 3.50.4, Tcl/Tk 8.6.15 y pytest 8.4.2. La
comprobación de Tk necesitó autorización fuera del entorno restringido del agente;
esto no es un permiso ni una dependencia de la aplicación para su uso habitual.

Desde la raíz del repositorio, en PowerShell, preparar el entorno de desarrollo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

La instalación descarga únicamente herramientas de pruebas y sus dependencias
en `.venv`; requiere red si no están disponibles localmente. Para usar la
aplicación no hace falta instalar pytest ni activar el entorno virtual.

Iniciar la aplicación:

```powershell
.\.venv\Scripts\python.exe iniciar.py
```

También puede usarse `python iniciar.py` con un Python que incluya Tkinter.
Se puede ejecutar `iniciar.py` por ruta absoluta desde otro directorio: el inventario
y la base siempre se resuelven dentro del repositorio.

Ejecutar las pruebas sin abrir ventanas:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

El agente instaló pytest 8.4.2 en `.venv`. Los comandos realmente usados, incluido
el directorio temporal de pruebas dentro del repositorio, constan en
[verificaciones.md](docs/verificaciones.md). La aplicación funciona sin Codex,
ChatGPT, cuentas de IA ni servicios externos; Git/GitHub no son necesarios para ejecutarla.

### Interfaz gráfica

La interfaz tiene tres pestañas:

- **Reservas:** visualización del inventario y creación de reservas.
- **Disponibilidad:** consulta de horarios disponibles por unidad e intervalo.
- **Historial:** visualización de reservas activas y canceladas, con posibilidad de cancelar reservas activas.

El inventario completo es de sólo lectura y distingue cada unidad por ID y nombre.

La interfaz presenta mensajes ante entradas inválidas, conflictos y operaciones
exitosas. La confirmación de creación incluye el UUID después de persistir.

La cancelación exige seleccionar una activa y confirmar; conserva el registro.
El historial incluye ambos estados, ordenados por inicio y UUID, con barras de
desplazamiento. Crear o cancelar actualiza el listado e invalida el resultado
previo de disponibilidad para que se vuelva a consultar.

### Persistencia y reinicio de datos

El archivo `data/inventario.json` contiene el inventario fijo de las cinco unidades y debe conservarse en Git.

La base es `data/reservas.db`; el esquema se crea si falta, sin reemplazar
registros. La aplicación guarda activas y canceladas, y reutiliza el mismo archivo
entre ejecuciones. El agente no creó una base de producción: las verificaciones
usaron bases temporales y una base en memoria.

Las bases de datos locales estarán excluidas del control de versiones mediante `.gitignore`.

No se implementará un reinicio automático de datos. Cualquier eliminación manual de información existente requerirá autorización y resguardo previo.

Durante la preparación documental se retiró un archivo temporal `debug.log`, generado por una consulta de extensiones, mediante una solicitud de aprobación de la herramienta. El incidente se encuentra documentado en [verificaciones.md](docs/verificaciones.md).

La prueba automática de cerrar/reabrir SQLite pasó. La comprobación personal de
cerrar y reiniciar la aplicación completa sigue pendiente en ese documento.

### Ejemplos de comportamiento esperado

Supongamos que existe una reserva activa de `MIC-01` para el día `2026-11-10`, de `10:00` a `11:00`.

| Nueva solicitud | Resultado esperado | Motivo |
|---|---|---|
| MIC-01, 10:30–11:30 | Rechazar | Se superpone con una reserva activa de la misma unidad. |
| MIC-01, 11:00–12:00 | Aceptar | Es consecutiva; no existe superposición. |
| MIC-02, 10:00–11:00 | Aceptar | Corresponde a otra unidad física. |

Si se cancela la reserva original, deberá permanecer en el historial con estado `CANCELADA` y su intervalo quedará disponible.

Estos comportamientos tienen cobertura automática en `tests/test_reglas.py`;
la autora aún debe recorrerlos en la interfaz.

### Limitaciones

Se asume una aplicación local con una única zona horaria de referencia.

No se modelan conversiones UTC ni cambios históricos de offset. Los intervalos se comparan utilizando horas civiles locales.

La aplicación está implementada para una instancia local. La comprobación oculta
de widgets no sustituye revisar tamaño, legibilidad y uso manual en pantalla.
Si aparece un error de Tcl/Tk al iniciar, comprobar la instalación de Python con
soporte Tk; no cambiar reglas ni borrar datos para corregir ese problema del entorno.

## 3. Preparación del agente

### Entorno y agente utilizado

La autora preparó el trabajo utilizando:

| Elemento | Configuración |
|---|---|
| Entorno de desarrollo | Visual Studio Code |
| Agente de programación | OpenAI Codex integrado en VS Code |
| Extensión | `openai.chatgpt` |
| Versión de la extensión | `26.1007.21434` |
| Modelo seleccionado | `GPT-6.1 Sol High` |
| Modalidad | `Work locally` |
| Permisos de la interfaz | `Ask for approval` |

La selección del modelo, la modalidad y los permisos fue observada e informada por la autora; el agente no verificó directamente estas opciones en la interfaz.

Codex consultó la versión de la extensión y obtuvo el valor indicado, aunque la consulta presentó errores de permisos relacionados con logs.

Los comandos ejecutados, los resultados observados y sus limitaciones están registrados en [verificaciones.md](docs/verificaciones.md).

### Instrucciones específicas del agente

Se utilizó el archivo [AGENTS.md](AGENTS.md), preparado inicialmente por la autora y ampliado posteriormente por Codex.

Las instrucciones establecen:

- Respetar los requisitos y las reglas de negocio documentadas.
- Compartir la lógica de conflictos entre consulta de disponibilidad y creación de reservas.
- Permitir reservas consecutivas.
- Ignorar reservas canceladas al comprobar conflictos.
- Conservar los datos originales de las reservas canceladas.
- Mantener separadas la interfaz, la lógica y la persistencia.
- No realizar commits, push ni operaciones remotas de Git sin autorización explícita.
- No eliminar archivos, reservas ni bases de datos existentes sin aprobación humana.
- No modificar archivos fuera del repositorio.
- Informar los archivos modificados y los comandos ejecutados.
- No inventar resultados de pruebas ni verificaciones humanas.
- Detenerse al finalizar cada etapa para permitir la revisión de la autora.

La autora revisó el archivo y comprobó que conserva las restricciones iniciales de control humano.

La segunda delegación agregó pruebas de adyacencia, cancelación que libera el
intervalo, conservación del historial y coherencia entre consulta y creación.

### Contexto suministrado y excluido

Para el primer episodio de delegación se proporcionaron al agente:

- La consigna del trabajo académico.
- Los requisitos y las reglas del sistema de reservas.
- El inventario de cinco unidades físicas.
- Los supuestos temporales y las restricciones de alcance.
- Los criterios de evaluación.
- Las instrucciones iniciales de `AGENTS.md`.
- La información del entorno de desarrollo.
- La indicación de preparar únicamente documentación e inventario, sin implementar la aplicación ni sus pruebas.

Se excluyeron credenciales, tokens, secretos, datos personales reales, conversaciones privadas completas, proyectos ajenos y archivos externos innecesarios.

### Control y revisión humana

La autora conserva el control sobre la aceptación de los cambios, las autorizaciones de operaciones restringidas, la ejecución independiente de pruebas y los commits.

Durante el primer episodio, Codex preparó la documentación y se detuvo antes de implementar el sistema.

Posteriormente, la autora revisó los archivos generados y registró la aceptación documental del episodio.

Esta aceptación no constituye una verificación funcional de la aplicación.

La etapa 1 quedó versionada en `b445b3d`, observado por el agente. La revisión
humana y la incorporación manual de la segunda delegación siguen pendientes.

## 4. Registro de decisiones y delegación

La evolución del proyecto se documenta mediante los siguientes archivos:

- [Decisiones técnicas](docs/decisiones.md): tecnologías, arquitectura, reglas de disponibilidad, representación temporal, UUID y conservación del historial.
- [Registro de delegación](docs/delegacion.md): episodio 1 aceptado y versionado; episodio 2 implementado, pendiente de revisión; episodio 3 no iniciado.
- [Progreso del proyecto](docs/progreso.md): trabajo realizado, revisión humana y etapas pendientes.
- [Registro de verificaciones](docs/verificaciones.md): comandos y resultados reales del agente, revisiones documentales de la autora y verificaciones funcionales humanas pendientes.

### Estado del control de versiones

Antes de la primera delegación se registró el commit inicial:

`3128779 chore: inicializar repositorio`

Ese commit es anterior al trabajo documental de Codex y no incluye los archivos generados durante el primer episodio.

Durante la delegación, el agente no realizó commits, push ni operaciones remotas de Git.

La autora realizó la revisión documental del primer episodio y registró su decisión de aceptación.

El commit `b445b3d docs: agregar especificacion y preparacion del agente` contiene
la etapa 1. La segunda delegación fue autorizada por la autora el 2026-11-05.
El agente no realizó commits ni operaciones remotas; el commit de implementación
y su aceptación humana permanecen pendientes.

### Episodios de delegación

| Episodio | Objetivo | Estado |
|---|---|---|
| 1 | Preparar especificación, instrucciones del agente, inventario y documentación de trazabilidad. | Aceptado; versionado en b445b3d. |
| 2 | Implementar lógica, SQLite, GUI y pruebas de esta delegación. | Implementado y verificado por el agente; revisión humana pendiente. |
| 3 | Implementación o verificación complementaria según el alcance que autorice la autora. | No iniciado. |

Los episodios posteriores se documentarán con sus instrucciones, resultados reales, verificaciones, decisiones humanas y evidencia de Git.

La aplicación deberá desarrollarse y verificarse de forma progresiva, manteniendo la correspondencia entre requisitos, decisiones técnicas, código y pruebas.
