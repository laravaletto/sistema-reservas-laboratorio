# Sistema de Reservas de Laboratorio

Trabajo académico individual. Proyecto local desarrollado con apoyo de OpenAI Codex en Visual Studio Code, mediante tres episodios de delegación y verificación humana.

**Estado al 2026-11-05:** las tres delegaciones fueron revisadas y aceptadas por la autora. La versión final está publicada en la rama `main`, commit [`91fb0e0`](https://github.com/laravaletto/sistema-reservas-laboratorio/commit/91fb0e0). La última ejecución independiente de la suite finalizó con **115 pruebas aprobadas en 4,83 segundos**. Los procedimientos y resultados están registrados en [verificaciones](docs/verificaciones.md).

## 1. Especificación breve

El laboratorio registra solicitudes de equipos mediante mensajes y planillas, lo que puede generar superposiciones de reservas y horarios que permanecen bloqueados después de una cancelación. Se desarrolla una aplicación local para administrar reservas de cinco unidades físicas fijas:

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
- **RF03 — Crear reserva:** registrar una reserva con UUID, solicitante ficticio, inicio, fin y estado.
- **RF04 — Cancelar reserva:** cancelar una reserva sin eliminar sus datos.
- **RF05 — Persistencia:** conservar las reservas activas y canceladas entre ejecuciones.
- **RF06 — Historial:** consultar todas las reservas registradas y sus estados.

### Reglas de negocio

Se rechazan las unidades inexistentes, los solicitantes vacíos o compuestos solo por espacios, las fechas inválidas y los intervalos cuyo inicio sea igual o posterior al fin.

Solo las reservas con estado `ACTIVA` de una misma unidad bloquean disponibilidad. Se utilizan intervalos semiabiertos `[inicio, fin)`: existe superposición cuando `inicio_nuevo < fin_existente AND inicio_existente < fin_nuevo`.

Las consultas de disponibilidad y la creación de reservas usan las mismas reglas. Se permiten reservas consecutivas de una misma unidad y reservas simultáneas de unidades diferentes. La cancelación libera el intervalo, pero conserva la reserva y su identificador en el historial.

### Supuestos y representación temporal

- Zona horaria de referencia: `America/Argentina/Cordoba`.
- Formato exacto de entrada: `AAAA-MM-DD HH:MM` (por ejemplo, `2026-11-10 10:30`).
- Fechas y horas civiles locales, sin conversiones entre zonas horarias; precisión de minutos.
- Fechas pasadas permitidas; sin restricciones adicionales de duración o anticipación.
- Rango técnico de años: 0001–9999.
- Identificación mediante UUID4; estados `ACTIVA` y `CANCELADA`.

### Criterios de aceptación

La aplicación debe mostrar las cinco unidades, validar entradas, evitar guardar operaciones rechazadas, impedir superposiciones, permitir intervalos consecutivos y reservas de distintas unidades en paralelo, cancelar sin eliminar registros, liberar horarios cancelados, recuperar reservas tras reiniciar y mostrar el historial completo.

La [especificación completa](docs/especificacion.md) contiene los requisitos, reglas RN01–RN09, criterios CA01–CA06c y casos previstos CP01–CP18. La evidencia de ejecución y sus límites se encuentran en [verificaciones](docs/verificaciones.md).

### Fuera de alcance

No se incluyen autenticación, roles reales, notificaciones, pagos, integraciones externas, despliegue, aplicación web, interfaces complejas, concurrencia distribuida, escalabilidad de producción, MCP, sistemas multiagente ni administración dinámica del inventario.

## 2. Solución

### Estructura del proyecto

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
│   ├── presentacion.py
│   ├── servicio.py
│   └── interfaz.py
└── tests/
    ├── conftest.py
    ├── test_inventario.py
    ├── test_persistencia.py
    ├── test_reglas.py
    └── test_usabilidad.py
```

La base local se crea al iniciar correctamente la aplicación; no se distribuye una base con reservas de prueba.

### Arquitectura y tecnologías

- **Python:** lenguaje principal.
- **Tkinter/ttk:** interfaz gráfica de escritorio.
- **SQLite (`sqlite3`):** persistencia local.
- **pytest:** pruebas automatizadas.

`dominio.py` define entidades, errores y fechas; `inventario.py` carga el JSON; `servicio.py` valida y coordina los casos de uso; `persistencia.py` administra SQLite mediante SQL parametrizado y transacciones; `presentacion.py` contiene funciones auxiliares de presentación; `interfaz.py` implementa la GUI. `__main__.py` conecta los componentes y `iniciar.py` permite arrancar desde la raíz sin instalar un paquete.

Las pruebas de reglas y persistencia no requieren abrir ventanas. La justificación de tecnologías, alternativas y consecuencias se documenta en [decisiones](docs/decisiones.md).

### Requisitos previos, instalación, ejecución y pruebas

Se requiere **Python 3.10 o posterior**, con Tkinter/ttk y `sqlite3`. Se verificó el funcionamiento con Python **3.13.7**; no se probaron otras versiones. En el entorno se observaron Git `2.47.0.windows.2`, SQLite `3.50.4`, Tcl/Tk `8.6.15` y pytest `8.4.2`.

La aplicación usa la biblioteca estándar; `pytest` es una dependencia de desarrollo. Desde la raíz del repositorio, en **PowerShell**:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

La instalación de dependencias de pruebas puede requerir conexión a Internet. Para utilizar la aplicación no hace falta instalar pytest ni activar el entorno virtual.

**Iniciar la aplicación:**

```powershell
.\.venv\Scripts\python.exe iniciar.py
```

También se puede ejecutar `python iniciar.py` con una instalación de Python que incluya Tkinter. El inventario y la base se resuelven dentro del repositorio, incluso al ejecutar el iniciador desde otro directorio.

**Ejecutar las pruebas:**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Este último comando fue ejecutado independientemente por la autora en la tercera delegación: **115 pruebas aprobadas en 4,83 segundos**. Los comandos del agente, sus resultados y las verificaciones humanas están separados en [verificaciones](docs/verificaciones.md). El sistema funciona sin Codex, ChatGPT, cuentas de IA ni servicios externos.

### Interfaz gráfica

La aplicación cuenta con tres pestañas: **Disponibilidad** (consultar horarios por unidad e intervalo), **Reservas** (consultar el inventario y crear reservas) e **Historial** (ver reservas activas y canceladas y cancelar las activas).

La interfaz informa errores, conflictos y operaciones exitosas, identifica campos inválidos, mantiene los datos del formulario ante errores y muestra el UUID al crear una reserva. La cancelación requiere confirmación. Tras crear o cancelar, se actualiza el historial y se invalida el resultado anterior de disponibilidad para evitar mostrar información desactualizada.

### Persistencia y reinicio de datos

`data/inventario.json` contiene el inventario fijo y debe conservarse. Las reservas se guardan en **`data/reservas.db`**; el esquema se crea automáticamente si falta, sin reemplazar registros existentes. Se conservan tanto reservas activas como canceladas. La base local está excluida de Git mediante `.gitignore`.

**No hay un botón ni un comando de reinicio de datos.** Si se necesita empezar desde cero, se debe cerrar la aplicación y eliminar manualmente `data/reservas.db`, **solo después de hacer una copia de seguridad si se desea conservar la información**. Esto borra todas las reservas y su historial; al volver a iniciar, se crea una base vacía. No se debe eliminar `data/inventario.json`.

Se verificó la persistencia automáticamente y también mediante cierre y reapertura de la aplicación, sin borrar la base, conservando reservas activas y canceladas. El procedimiento y resultado observado constan en [verificaciones](docs/verificaciones.md).

### Ejemplo de entrada y resultado

Supongamos una reserva activa de `MIC-01` desde `2026-11-10 10:00` hasta `2026-11-10 11:00`.

| Nueva solicitud | Resultado | Motivo |
|---|---|---|
| MIC-01, 10:30–11:30 | Rechazada | Superposición con reserva activa |
| MIC-01, 11:00–12:00 | Aceptada | Intervalo consecutivo |
| MIC-02, 10:00–11:00 | Aceptada | Otra unidad física |

Al cancelar la reserva original de MIC-01, sigue visible como `CANCELADA` y su intervalo vuelve a estar disponible. Estos casos fueron cubiertos por pruebas automatizadas y verificados manualmente durante la segunda delegación.

### Limitaciones y pendientes

La aplicación es local y utiliza una única zona horaria de referencia. No realiza conversiones UTC ni modela cambios históricos de offset; compara fechas y horas civiles locales. No está diseñada para concurrencia distribuida ni escalabilidad de producción. Para ejecutarla es necesario disponer de Python con soporte Tcl/Tk. **No quedan tareas funcionales pendientes dentro del alcance de la consigna.**

## 3. Preparación del agente

### Entorno y agente utilizado

| Elemento | Configuración observada |
|---|---|
| Entorno de desarrollo | Visual Studio Code |
| Agente de programación | OpenAI Codex integrado en VS Code |
| Extensión | `openai.chatgpt` |
| Versión de la extensión | `26.1007.21434` |
| Modelo seleccionado | `GPT-6.1 Sol High` |
| Modalidad | `Work locally` |
| Permisos de la interfaz | `Ask for approval` |

La selección del modelo, modalidad y permisos fue observada e informada por la autora; el agente no verificó directamente estas opciones en la interfaz. Codex consultó la versión de la extensión, aunque la consulta mostró errores de permisos relacionados con logs. Se distingue esta evidencia de las comprobaciones ejecutadas en [verificaciones](docs/verificaciones.md).

### Instrucciones, configuración y adaptación específica

Se utilizó [AGENTS.md](AGENTS.md), preparado inicialmente por la autora y ampliado para las delegaciones. Las instrucciones establecen respetar las reglas documentadas; compartir la lógica de conflictos entre consulta y creación; permitir intervalos consecutivos; excluir canceladas de los conflictos; preservar los datos al cancelar; separar interfaz, servicio y persistencia; no hacer commits ni push sin autorización; no borrar datos sin aprobación; no modificar archivos ajenos al repositorio; informar archivos y comandos; no inventar verificaciones humanas; y detenerse para revisión al terminar cada episodio.

**Adaptación comprobable:** la instrucción específica sobre intervalos consecutivos `[inicio, fin)` y reservas canceladas se aplicó en la lógica y fue verificada con pruebas automáticas y recorridos manuales. Las instrucciones y evidencias concretas se vinculan en [delegación](docs/delegacion.md) y [verificaciones](docs/verificaciones.md).

### Contexto suministrado y excluido

Se proporcionaron la consigna, los requisitos y reglas, el inventario fijo, los supuestos temporales, los criterios de evaluación, `AGENTS.md` y los documentos del proyecto pertinentes a cada etapa. En el primer episodio se restringió la tarea a documentación e inventario; en el segundo se autorizó implementar la aplicación y las pruebas; en el tercero se autorizaron mejoras de usabilidad sin alterar las reglas ni el esquema de datos.

Se excluyeron secretos, credenciales, tokens, datos personales reales, conversaciones privadas completas, proyectos ajenos y archivos externos innecesarios. Los solicitantes utilizados son ficticios.

### Herramientas, permisos y revisión humana

Codex trabajó sobre archivos locales del repositorio y ejecutó comandos y pruebas con las herramientas disponibles en el entorno. Las operaciones restringidas requirieron aprobación cuando correspondió; los commits y push fueron realizados por la autora. La autora revisó los cambios antes de aceptarlos, ejecutó pruebas de forma independiente y verificó manualmente la GUI, las reglas principales y la persistencia. Los comandos, resultados, autorizaciones y límites observados se detallan en [verificaciones](docs/verificaciones.md).

## 4. Registro de decisiones y delegación

Los documentos versionados permiten reconstruir la evolución del proyecto:

- [Decisiones técnicas](docs/decisiones.md): elecciones, motivos, alternativas y consecuencias.
- [Registro de delegación](docs/delegacion.md): objetivos, contexto, extractos de instrucciones, resultados, decisiones humanas y evidencias de los tres episodios.
- [Progreso del proyecto](docs/progreso.md): avance, aceptación y estado final.
- [Registro de verificaciones](docs/verificaciones.md): comandos y procedimientos, versiones, resultados del agente y comprobaciones independientes de la autora.

### Episodios reales de delegación

| Episodio | Objetivo y resultado | Decisión humana | Evidencia versionada |
|---|---|---|---|
| 1 | Preparar especificación, instrucciones, inventario y trazabilidad | Revisado y aceptado | [`b445b3d`](https://github.com/laravaletto/sistema-reservas-laboratorio/commit/b445b3d) |
| 2 | Implementar lógica, SQLite, interfaz y pruebas; 81 pruebas aprobadas | Pruebas independientes, recorrido manual y aceptación | [`5c70ae0`](https://github.com/laravaletto/sistema-reservas-laboratorio/commit/5c70ae0) |
| 3 | Mejorar mensajes, validaciones visuales y usabilidad; 115 pruebas aprobadas | Revisión de cambios, ejecución independiente y aceptación | [`91fb0e0`](https://github.com/laravaletto/sistema-reservas-laboratorio/commit/91fb0e0) |

Para cada episodio, [delegacion.md](docs/delegacion.md) relaciona el requisito, el contexto suministrado, las instrucciones utilizadas, las acciones del agente, la decisión humana y las pruebas o archivos verificables. Las correcciones y limitaciones se registraron cuando ocurrieron; no se inventaron fallas.

### Control de versiones y entrega

El commit inicial fue [`3128779`](https://github.com/laravaletto/sistema-reservas-laboratorio/commit/3128779). Los tres episodios se versionaron después de la revisión humana. El agente no realizó commits ni push; la autora los efectuó manualmente.

**Versión funcional aceptada:** rama `main`, commit `91fb0e0`. Si se realiza un commit posterior para actualizar este README, ese commit solo modifica documentación y no sustituye la evidencia funcional de `91fb0e0`.
