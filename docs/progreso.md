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

La segunda delegación quedó completada, revisada y aceptada por la autora. Sus resultados fueron versionados y publicados en GitHub mediante el commit `5c70ae0`. Los resultados completos de las verificaciones se encuentran en [verificaciones.md](verificaciones.md).

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

Estos supuestos fueron documentados y revisados durante la primera etapa. Su implementación se realizó en la segunda delegación y su comportamiento se evaluó mediante las pruebas automatizadas y las verificaciones manuales registradas.

No se agregaron restricciones de horarios hábiles, duración máxima, anticipación ni prohibiciones sobre fechas pasadas.

## Etapas y tareas pendientes

| Etapa o tarea | Estado |
|---|---|
| 1. Generar especificación, preparación y documentación | Completada y aceptada. |
| Revisar documentos de etapa 1 | Completado por la autora. |
| Incorporar evidencia de etapa 1 a Git | Versionada en `b445b3d`. |
| 2. Implementar lógica, persistencia, GUI y pruebas | Completada y aceptada. |
| Ejecutar pytest y pruebas de persistencia | 81 pruebas aprobadas por Codex y por la autora. |
| Verificación humana de interfaz y reinicio completo | Completada satisfactoriamente el 2026-11-05. |
| Commit del episodio 2 | `5c70ae0`, creado y publicado por la autora. |
| 3. Mejoras puntuales de usabilidad | Implementadas por Codex y aceptadas por la autora. |
| Pruebas automatizadas del episodio 3 | 115 aprobadas por Codex y posteriormente por la autora. |
| Verificación humana de la interfaz actualizada | Completada satisfactoriamente el 2026-11-05. |
| Decisión humana del episodio 3 | Aceptar la implementación. |
| Commit del episodio 3 | Pendiente de creación manual. |



## Próximos pasos

La autora completará la revisión de la documentación de la tercera delegación y realizará manualmente el commit correspondiente.

No se prevén nuevas delegaciones dentro del alcance actual del trabajo.

## Estado general

- **Preparación documental:** finalizada y aceptada.
- **Revisión humana de la etapa 1:** completada.
- **Implementación del sistema:** realizada y aceptada en la segunda delegación.
- **Pruebas automatizadas:** 115 casos aprobados por Codex y por la autora.
- **Verificación funcional humana:** completada satisfactoriamente.
- **Persistencia entre ejecuciones:** comprobada manualmente durante la segunda delegación.
- **Commit de la primera delegación:** `b445b3d`.
- **Commit de la segunda delegación:** `5c70ae0`.
- **Episodio 3:** mejoras implementadas, revisadas y aceptadas; commit pendiente.

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

## Actualización — tercera delegación, 2026-11-05

Los apartados anteriores se conservan como registro de las etapas previas.
AGENTS.md autoriza la tercera delegación y declara aceptada la etapa 2; se observó
el commit `5c70ae0`. Este episodio se limita a usabilidad de la GUI existente.

Trabajo realizado: mensajes específicos y seguros con texto/color; foco por campo
sin duplicar reglas; etiquetas y espaciado; selección explícita de unidad;
navegación por teclado; conservación de entradas y selección del historial;
estados visibles; invalidación de disponibilidad al editar o cambiar reservas;
confirmación de cancelación y control del listado cuando falla su actualización.

Se modificaron interfaz.py, dominio.py, servicio.py y __main__.py; se agregaron
presentacion.py y tests/test_usabilidad.py. Sólo se añaden secciones necesarias a
decisiones, delegación, progreso y verificaciones. README, especificación,
inventario, persistencia, esquema y dependencias quedan fuera de estos cambios;
AGENTS.md ya estaba modificado por la autora y no se editó.

| Tarea de este episodio | Estado |
|---|---|
| Comprobar pruebas existentes antes de intervenir | 81 aprobadas en 4.18 s. |
| Implementar mejoras solicitadas | Realizado por el agente, sin ampliar funciones de negocio. |
| Agregar verificaciones sin GUI real | 34 casos nuevos; suite final: 115 aprobados en 6.22 s con advertencias como errores. |
| Compilar Python | Código 0. |
| Comprobar widgets reales con ventana invisible | Aprobado: foco, Tab, estilos, confirmación, actualización y límites a 900x620; base en memoria. |
| Revisar visualmente y usar personalmente la GUI actualizada | Completado satisfactoriamente por la autora el 2026-11-05. |
| Registrar decisión humana del episodio 3 | Aceptar las mejoras implementadas. |
| Commit manual de este episodio | Pendiente de creación manual. El agente no realizó commits ni push. |


Decisiones DT16–DT18: metadatos del campo afectado, mensajes seguros y manejo del
listado desactualizado. No hay cambios de requisitos ni nuevas dependencias.

La autora realizó la revisión funcional de la interfaz actualizada y ejecutó independientemente las 115 pruebas automatizadas, aprobadas en 4,83 segundos. Los resultados y el alcance de las comprobaciones se encuentran registrados en [verificaciones.md](verificaciones.md).

La tercera delegación fue aceptada por la autora. El agente se detuvo al finalizar su trabajo y no realizó commits ni push.