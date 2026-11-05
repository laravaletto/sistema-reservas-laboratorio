# Registro de decisiones técnicas

**Fecha de elaboración:** 2026-11-04.  
**Fecha de revisión humana:** 2026-11-05.

Las decisiones técnicas fueron documentadas inicialmente por el agente a partir de la consigna y revisadas posteriormente por la autora.

La primera revisión humana correspondió al diseño y las decisiones documentadas. Posteriormente, durante la segunda delegación, se implementaron las funcionalidades previstas y se verificaron mediante pruebas automatizadas y comprobaciones manuales realizadas por la autora, quien aceptó la implementación el 2026-11-05.

## Decisiones técnicas

| ID | Decisión adoptada | Motivo | Alternativas consideradas | Consecuencias |
|---|---|---|---|---|
| DT01 | Python; biblioteca estándar para lógica y persistencia. | Tecnología solicitada y adecuada para una aplicación académica local. | Otros lenguajes quedan fuera de la consigna. | Código ejecutable sin IA; validar versión mínima al implementar. Se observó Python 3.13.7 en el entorno actual. |
| DT02 | Tkinter y ttk con tres pestañas. | Interfaz de escritorio sencilla con formularios y tabla sin servidor. | Consola: menos accesible para la operación solicitada. Web: agrega frontend/servidor y está fuera de alcance. | Requiere una instalación de Python con Tk; disponibilidad gráfica aún sin verificar. Mantener reglas fuera de callbacks gráficos. |
| DT03 | SQLite mediante `sqlite3` y archivo `data/reservas.db`. | Persistencia local transaccional sin servicio externo. | JSON para reservas dificulta transacciones; servidor de bases agrega complejidad. | Conservar archivo entre ejecuciones, usar parámetros y transacciones; base ignorada por Git. Sin garantías de concurrencia distribuida. |
| DT04 | Separar interfaz, lógica de negocio y persistencia. | Permite verificar reglas sin ventanas y aislar acceso a SQLite. | Código monolítico de callbacks mezcla responsabilidades; capas adicionales no justificadas. | Se prevén módulos simples en `src/`, aún sin crearlos. Una sola regla de conflictos para consultar y crear. |
| DT05 | pytest para pruebas futuras de lógica y persistencia. | Herramienta pedida, admite casos parametrizados y bases temporales. | `unittest` sería viable, pero no es la herramienta elegida por la consigna. | Dependencia sólo de desarrollo; no instalada ni ejecutada por el agente en esta etapa. Pruebas futuras sin GUI ni datos reales. |
| DT06 | Intervalos semiabiertos `[inicio, fin)`. | Expresan exactamente la regla de negocio y permiten reservas consecutivas. | Extremos cerrados bloquearían indebidamente la hora de fin. | Conflicto si `inicio_nuevo < fin_existente AND inicio_existente < fin_nuevo`, sólo misma unidad y `ACTIVA`; verificar adyacencia por ambos lados. |
| DT07 | Horas civiles locales de `America/Argentina/Cordoba`; `datetime` sin `tzinfo` y texto `YYYY-MM-DD HH:MM`. | Toda la agenda opera en una sola zona y con minutos; evita mezclar representaciones y depender de datos IANA adicionales en Windows. | Instantes UTC con `zoneinfo`: apropiados para conversiones y cambios de offset, pero requieren resolver ambigüedad histórica y disponibilidad de datos de zonas. Timestamps: menos legibles para este modelo civil. | No se convierten zonas ni se representan cambios de offset; calendario gregoriano, años 0001–9999, texto de ancho fijo. Comparar y persistir el mismo valor civil. Ver límites explícitos en la especificación. |
| DT08 | Permitir pasado, sin límite adicional de duración o anticipación. | Supuesto definido para el proyecto; facilita reproducir ejemplos sin depender del reloj. | Rechazar pasado o limitar horizonte introduciría reglas no pedidas. | No comparar contra la fecha actual; exigir sólo fecha válida, inicio anterior al fin y disponibilidad dentro del rango técnico. |
| DT09 | Cancelar mediante estado y conservar el registro completo. | Libera disponibilidad y preserva trazabilidad e historial tras reiniciar. | Borrado pierde historial; mover registros a otra tabla agrega complejidad. | Sólo `ACTIVA` participa en conflictos. `CANCELADA` conserva UUID y campos; no hay reactivación ni eliminación. |
| DT10 | UUID4 como texto; estados `ACTIVA` y `CANCELADA`. | Identidad estable sin secuencia manual; estados explícitos solicitados. | Entero incremental sería simple, pero no cumple el supuesto de UUID. | Usar `uuid` de la biblioteca estándar como clave primaria; cancelar por UUID sin reasignar identidad. |
| DT11 | Inventario fijo en JSON y confirmación al cancelar. | JSON hace visible cada unidad física; confirmar evita una cancelación accidental. | CRUD de equipos y motivos de cancelación ampliarían el alcance. | Selectores muestran ID y nombre, inventario de sólo lectura; confirmar cancelación no borra datos. |
| DT12 | Documentar primero y diferir código, pruebas y versionado manual. | Conservar evidencia real de evolución por etapas, como solicita la autora. | Generar todo en la primera etapa impediría esa secuencia verificable. | Durante la primera delegación no crear `src/` ni `tests/`, no instalar dependencias ni realizar commits. La incorporación manual a Git se efectúa después de la revisión humana. |

## Seguimiento de decisiones

Las decisiones DT01–DT12 constituyen la base documental de la primera etapa.

La revisión humana de la primera etapa confirmó la coherencia de las decisiones con los requisitos y el alcance previstos. En la segunda delegación se implementaron las decisiones técnicas correspondientes y se verificó su funcionamiento mediante 81 pruebas automatizadas y comprobaciones manuales de la interfaz, las reservas, la disponibilidad, la cancelación y la persistencia.

Si durante el desarrollo surge la necesidad de modificar una decisión, deberá registrarse:

- Fecha del cambio.
- Decisión original y nueva decisión.
- Motivo del cambio.
- Alternativas consideradas, cuando corresponda.
- Requisitos afectados.
- Consecuencias técnicas.
- Revisión y decisión humana correspondiente.

Los cambios significativos deberán reflejarse también en `docs/especificacion.md` y `docs/progreso.md`, conservando su evolución mediante Git.

No se atribuirán aprobaciones, verificaciones ni resultados a la autora sin que hayan ocurrido efectivamente.

## Segunda delegación — 2026-11-05

Se implementaron DT01–DT11 sin cambiar los requisitos ni la representación civil del tiempo. La autora informó que aceptó y versionó la etapa 1; el agente observó el commit b445b3d.

Las decisiones adicionales DT13–DT15 fueron incorporadas durante la segunda delegación. Codex ejecutó satisfactoriamente 81 pruebas automatizadas y comprobaciones de la interfaz con widgets ocultos.

Posteriormente, la autora ejecutó independientemente las 81 pruebas, verificó manualmente el funcionamiento de la interfaz y comprobó la persistencia de las reservas después de cerrar y volver a abrir la aplicación.

Decisión humana: aceptar la implementación y las decisiones técnicas de la segunda delegación. El commit correspondiente permanece pendiente de creación manual.
| ID | Decisión adoptada | Motivo | Alternativas consideradas | Consecuencias |
|---|---|---|---|---|
| DT13 | Paquete simple en src/reservas_lab y lanzador iniciar.py; Python 3.10+ por la sintaxis utilizada. | Separar responsabilidades y arrancar sin instalar un paquete ni usar IA. | Instalar un paquete editable agregaría herramientas de construcción innecesarias para esta entrega local. | Rutas calculadas desde __file__, independientes del directorio actual. Se probó Python 3.13.7; otras versiones no se verificaron. |
| DT14 | Una consulta SQL de conflictos compartida, con BEGIN IMMEDIATE al crear o cancelar. | Revalidar el conflicto al guardar y confirmar éxito sólo después del commit; garantizar rollback ante errores. | Consultar sólo antes de abrir la transacción dejaría una separación entre comprobar e insertar. | El servicio valida unidad/intervalo en ambos flujos y solicitante al crear. SQLite aplica restricciones de campos, unidades y estados. No se agregan servicios ni concurrencia distribuida. |
| DT15 | pytest 8.4.2 en requirements-dev.txt, bases temporales y fallos controlados en pruebas. | Ejecución reproducible y comprobación real de reapertura y rollback sin ventanas ni datos de uso. | Pruebas contra data/reservas.db arriesgarían mezclar datos ficticios con registros de la autora. | Pruebas independientes de Tk; tests de inserción, cancelación y commit fallidos. El entorno .venv y sus bases de prueba no se versionan. La aplicación no depende de pytest. |

En la interfaz se confirma la creación con UUID y se invalida el resultado anterior
de disponibilidad después de crear/cancelar. El historial se actualiza y sólo
habilita cancelar cuando se selecciona una ACTIVA. Se conserva el diseño de tres
pestañas y el inventario visible de sólo lectura.

El error de Tcl en el entorno restringido se investigó sin modificar la instalación
global ni agregar dependencias: la comprobación autorizada fuera de esa restricción
inicializó Tcl/Tk 8.6.15. No se incorporaron ajustes de entorno específicos en el
código de la aplicación. Detalle en [verificaciones.md](verificaciones.md).
