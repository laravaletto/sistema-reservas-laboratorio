# Sistema de Reservas de Laboratorio

Trabajo académico individual.

**Estado al 2026-11-05:** Etapa 1 de preparación documental e inventario realizada por el agente. La autora completó la revisión documental de los archivos generados y registró su decisión de aceptación. La incorporación manual de los cambios a Git continúa pendiente.

**La aplicación y sus pruebas funcionales todavía no están implementadas.**

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

Estos criterios todavía no fueron verificados mediante una implementación funcional.

### Fuera de alcance

No se incluyen autenticación, roles reales, notificaciones, pagos, integraciones externas, despliegue, aplicación web, interfaces complejas, concurrencia distribuida, escalabilidad de producción, MCP, sistemas multiagente ni administración dinámica del inventario.

## 2. Solución

### Estructura actual del proyecto

```text
sistema-reservas-laboratorio/
├── .gitignore
├── AGENTS.md
├── README.md
├── data/
│   └── inventario.json
└── docs/
    ├── especificacion.md
    ├── decisiones.md
    ├── delegacion.md
    ├── progreso.md
    └── verificaciones.md
```

La estructura corresponde a la etapa de preparación documental. Los directorios `src/` y `tests/` todavía no existen.

### Arquitectura y tecnologías previstas

La implementación utilizará:

- **Python:** lenguaje principal de programación.
- **Tkinter/ttk:** interfaz gráfica de escritorio.
- **SQLite mediante `sqlite3`:** persistencia local de reservas.
- **pytest:** pruebas automáticas de lógica de negocio y persistencia.

Se mantendrá una separación entre interfaz gráfica, lógica de negocio y acceso a datos.

La lógica de validación y detección de conflictos deberá poder probarse sin abrir ventanas.

La justificación de las tecnologías, las alternativas consideradas y sus consecuencias están documentadas en [decisiones.md](docs/decisiones.md).

### Requisitos previos, instalación, ejecución y pruebas

Se necesitará una instalación de Python con soporte para Tkinter/ttk y SQLite. pytest se utilizará como dependencia de desarrollo.

En el entorno de trabajo se observaron:

- Python `3.13.7`.
- Git `2.47.0.windows.2`.

Estas versiones corresponden al entorno actual y no constituyen todavía una versión mínima validada para ejecutar la aplicación.

La disponibilidad de Tkinter y las versiones de SQLite y pytest aún no fueron verificadas durante esta etapa.

**Pendiente de implementación:** definir la versión mínima compatible, las dependencias de desarrollo, el punto de entrada y los comandos reproducibles de instalación, ejecución y pruebas.

Actualmente no existe un comando para iniciar la aplicación ni una suite de pruebas implementada.

Durante esta etapa, **el agente no instaló dependencias**.

La solución final deberá poder ejecutarse sin Codex, ChatGPT, una cuenta de IA ni servicios externos. Git y GitHub se utilizarán para registrar la evolución del proyecto, pero no serán necesarios para el funcionamiento de la aplicación.

### Interfaz gráfica prevista

Se propone una interfaz con tres pestañas:

- **Reservas:** visualización del inventario y creación de reservas.
- **Disponibilidad:** consulta de horarios disponibles por unidad e intervalo.
- **Historial:** visualización de reservas activas y canceladas, con posibilidad de cancelar reservas activas.

El inventario será de sólo lectura.

La interfaz deberá presentar mensajes claros ante entradas inválidas, conflictos de disponibilidad y operaciones exitosas.

Las cancelaciones requerirán confirmación para evitar operaciones accidentales.

### Persistencia y reinicio de datos

El archivo `data/inventario.json` contiene el inventario fijo de las cinco unidades y debe conservarse en Git.

La base de datos prevista será `data/reservas.db`, que todavía no existe.

SQLite almacenará las reservas activas y canceladas, conservando sus datos entre ejecuciones.

Las bases de datos locales estarán excluidas del control de versiones mediante `.gitignore`.

No se implementará un reinicio automático de datos. Cualquier eliminación manual de información existente requerirá autorización y resguardo previo.

Durante la preparación documental se retiró un archivo temporal `debug.log`, generado por una consulta de extensiones, mediante una solicitud de aprobación de la herramienta. El incidente se encuentra documentado en [verificaciones.md](docs/verificaciones.md).

El procedimiento de comprobación de persistencia después de cerrar y volver a abrir la aplicación está previsto en ese mismo documento y todavía no fue ejecutado.

### Ejemplos de comportamiento esperado

Supongamos que existe una reserva activa de `MIC-01` para el día `2026-11-10`, de `10:00` a `11:00`.

| Nueva solicitud | Resultado esperado | Motivo |
|---|---|---|
| MIC-01, 10:30–11:30 | Rechazar | Se superpone con una reserva activa de la misma unidad. |
| MIC-01, 11:00–12:00 | Aceptar | Es consecutiva; no existe superposición. |
| MIC-02, 10:00–11:00 | Aceptar | Corresponde a otra unidad física. |

Si se cancela la reserva original, deberá permanecer en el historial con estado `CANCELADA` y su intervalo quedará disponible.

Estos ejemplos describen criterios de aceptación y **no corresponden a pruebas ejecutadas**.

### Limitaciones

Se asume una aplicación local con una única zona horaria de referencia.

No se modelan conversiones UTC ni cambios históricos de offset. Los intervalos se comparan utilizando horas civiles locales.

La interfaz gráfica, la persistencia y el comportamiento funcional todavía no pueden evaluarse porque la aplicación no está implementada.

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

Las reglas de implementación todavía deberán verificarse mediante código y pruebas.

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

La incorporación de los cambios a Git se realizará manualmente, después de completar la revisión.

## 4. Registro de decisiones y delegación

La evolución del proyecto se documenta mediante los siguientes archivos:

- [Decisiones técnicas](docs/decisiones.md): tecnologías, arquitectura, reglas de disponibilidad, representación temporal, UUID y conservación del historial.
- [Registro de delegación](docs/delegacion.md): primer episodio documental registrado y revisado por la autora, con decisión de aceptación. Commit pendiente; episodios 2 y 3 todavía no iniciados.
- [Progreso del proyecto](docs/progreso.md): trabajo realizado, revisión humana y etapas pendientes.
- [Registro de verificaciones](docs/verificaciones.md): comandos y resultados informados por el agente, procedencia de la información del entorno, revisiones documentales realizadas por la autora y pruebas funcionales y de persistencia pendientes.

### Estado del control de versiones

Antes de la primera delegación se registró el commit inicial:

`3128779 chore: inicializar repositorio`

Ese commit es anterior al trabajo documental de Codex y no incluye los archivos generados durante el primer episodio.

Durante la delegación, el agente no realizó commits, push ni operaciones remotas de Git.

La autora realizó la revisión documental del primer episodio y registró su decisión de aceptación.

**La incorporación manual de los archivos a Git continúa pendiente.**

Antes de autorizar la implementación, se completará el versionado de esta etapa y se conservará la evidencia correspondiente.

Los identificadores y enlaces a commits se incorporarán a la documentación cuando existan.

### Episodios de delegación

| Episodio | Objetivo | Estado |
|---|---|---|
| 1 | Preparar especificación, instrucciones del agente, inventario y documentación de trazabilidad. | Trabajo del agente finalizado y aceptado documentalmente; commit pendiente. |
| 2 | Implementación de funcionalidades según el alcance que autorice la autora. | No iniciado. |
| 3 | Implementación o verificación complementaria según el alcance que autorice la autora. | No iniciado. |

Los episodios posteriores se documentarán con sus instrucciones, resultados reales, verificaciones, decisiones humanas y evidencia de Git.

La aplicación deberá desarrollarse y verificarse de forma progresiva, manteniendo la correspondencia entre requisitos, decisiones técnicas, código y pruebas.