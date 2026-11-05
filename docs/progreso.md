# Progreso del proyecto

## Estado al 2026-11-05

**Etapa 1:** preparación documental realizada por el agente el 2026-11-04.

La autora revisó y aceptó documentalmente el inventario, la especificación, `AGENTS.md`, el registro de delegación, las verificaciones y las decisiones técnicas.

La autora informó al autorizar la segunda delegación que completó la revisión,
aceptación y versionado de la etapa 1. El agente comprobó el commit `b445b3d`.

**Etapa 2:** lógica de negocio, persistencia SQLite, interfaz Tkinter/ttk y pruebas automatizadas implementadas.

Codex ejecutó satisfactoriamente 81 pruebas en 3,76 segundos, con advertencias tratadas como errores, y realizó una comprobación de la interfaz con widgets ocultos.

Posteriormente, la autora ejecutó independientemente las 81 pruebas automatizadas y verificó manualmente la interfaz, la creación de reservas, la detección de superposiciones, los horarios consecutivos, la cancelación y la persistencia después de cerrar y reabrir la aplicación.

**Decisión humana:** aceptar la implementación de la segunda delegación.

El commit de esta etapa permanece pendiente. Los resultados completos se encuentran en [verificaciones.md](verificaciones.md).

## Trabajo realizado

Durante el primer episodio de delegación, Codex realizó las siguientes actividades:

- Lectura de las instrucciones iniciales del proyecto, los archivos existentes y el estado e historial local de Git.
- Ampliación de `AGENTS.md`, conservando las restricciones iniciales de control y aprobación humana.
- Elaboración de la especificación de los requisitos RF01–RF06, las reglas de negocio RN01–RN09, los criterios de aceptación y los casos de prueba previstos CP01–CP18.
- Documentación de decisiones técnicas, alcance, arquitectura y representación temporal.
- Registro del episodio 1 de delegación, dejando preparados los apartados correspondientes a los episodios 2 y 3.
- Preparación del `README.md`, el registro de verificaciones y el inventario fijo de cinco unidades en formato JSON.
- Consulta de herramientas y ejecución de comprobaciones documentales, cuyos comandos y resultados se encuentran registrados en [verificaciones.md](verificaciones.md).
- Identificación de un archivo `debug.log` generado durante la consulta de extensiones, ajeno al alcance documental. Su eliminación se realizó mediante una solicitud de aprobación de la herramienta y quedó registrada en el documento de verificaciones.

Posteriormente, la autora comenzó la revisión de los archivos generados y registró su decisión de aceptación documental del primer episodio en [delegacion.md](delegacion.md).

Las verificaciones personales realizadas se documentan por separado en [verificaciones.md](verificaciones.md).

## Decisiones significativas

Se documentaron las siguientes decisiones para orientar la futura implementación:

- **Lenguaje y tecnologías:** Python, Tkinter/ttk, SQLite y pytest, conforme a la consigna.
- **Arquitectura:** separación entre interfaz gráfica, lógica de negocio y persistencia.
- **Disponibilidad:** intervalos semiabiertos `[inicio, fin)` y una misma regla de detección de conflictos para consultar disponibilidad y crear reservas.
- **Identificación:** UUID4 para cada reserva.
- **Cancelación:** modificación del estado de la reserva sin eliminar sus datos, conservando el historial.
- **Representación temporal:** fechas y horas civiles locales de Córdoba, con precisión de minutos y sin conversión entre zonas horarias.
- **Restricciones temporales:** se permiten reservas en fechas pasadas y no se establecen límites adicionales de duración o anticipación.

Los motivos, las alternativas consideradas y las consecuencias de estas decisiones se encuentran en [decisiones.md](decisiones.md).

Estas decisiones fueron revisadas documentalmente durante la primera etapa. En la segunda delegación se implementaron y se verificaron mediante pruebas automatizadas y comprobaciones funcionales realizadas por la autora, según el alcance registrado en verificaciones.md.

## Cambios de alcance o especificación

No se amplió el alcance funcional solicitado.

Durante la preparación documental se explicitaron algunos supuestos para resolver aspectos que no estaban completamente definidos:

- Uso de UUID4 para identificar reservas.
- Eliminación de espacios exteriores del nombre del solicitante.
- Validación del formato exacto de fecha y hora.
- Orden de presentación del historial.
- Comportamiento ante cancelaciones repetidas.
- Confirmación visual antes de cancelar una reserva.
- Ruta prevista del archivo SQLite.
- Representación de horas civiles locales sin conversiones de zona horaria ni tratamiento de cambios históricos de offset.

Estos supuestos fueron documentados por el agente y revisados por la autora a nivel documental. Su aplicación efectiva se comprobará durante la implementación y las pruebas.

No se agregaron restricciones de horarios hábiles, duración máxima, anticipación ni prohibiciones sobre fechas pasadas.

## Etapas y tareas pendientes


| Etapa o tarea | Estado |
|---|---|
| 1. Generar especificación, preparación y documentación | Completada y aceptada. |
| Revisar documentos de etapa 1 | Completado por la autora. |
| Incorporar evidencia de etapa 1 a Git | Versionada en `b445b3d`. |
| 2. Implementar lógica, persistencia, GUI y pruebas | Completada por Codex y aceptada por la autora. |
| Ejecutar pytest y pruebas de persistencia | 81 pruebas aprobadas por Codex y posteriormente por la autora. |
| Verificación humana de interfaz y reinicio completo | Completada satisfactoriamente el 2026-11-05. |
| Decisión humana del episodio 2 | Aceptar la implementación. |
| Commit del episodio 2 | Pendiente de creación manual. |
| 3. Nueva delegación | No iniciada; pendiente de definición y autorización. |

La segunda delegación autorizó también la GUI, por lo que se implementó aquí.
El episodio 3 continúa pendiente de definición y autorización; no se avanzó a él.

La autora definirá los objetivos, el alcance y las instrucciones de cada nueva delegación antes de continuar.

## Próximos pasos

La autora completará la revisión de la documentación actualizada y realizará manualmente el commit de la segunda delegación.

Posteriormente, definirá el objetivo y el alcance del tercer episodio de delegación, que no podrá comenzar sin autorización humana.

## Estado general

- **Preparación documental:** finalizada y aceptada.
- **Revisión humana de la etapa 1:** completada.
- **Implementación del sistema:** realizada en la segunda delegación.
- **Pruebas automatizadas:** 81 casos aprobados por Codex y por la autora.
- **Verificación funcional humana:** completada satisfactoriamente.
- **Persistencia entre ejecuciones:** comprobada manualmente.
- **Commit de la primera delegación:** `b445b3d`.
- **Episodio 2:** implementado, revisado y aceptado; commit pendiente.
- **Episodio 3:** no iniciado.

## Archivos y alcance de la segunda delegación

Se agregaron iniciar.py, requirements-dev.txt, pytest.ini, src/reservas_lab/
(__init__, __main__, dominio, inventario, persistencia, servicio e interfaz) y
tests/ (conftest y pruebas de reglas, persistencia e inventario).
Se actualizaron README y decisiones, delegación, progreso y verificaciones.
La modificación previa de AGENTS.md se conservó sin editarla. No se modificaron
la especificación, el JSON ni .gitignore. .venv es local y no versionable.

Sin cambios a los requisitos: se concretaron DT13–DT15 sobre organización,
transacciones y entorno de pruebas. Se implementó el esquema SQLite al iniciar,
sin migraciones destructivas, servicios externos ni dependencias de ejecución.

La documentación de esta etapa constituye la base para desarrollar el sistema de reservas y permite conservar la trazabilidad entre requisitos, decisiones, implementación y verificaciones posteriores.
