# Registro de decisiones técnicas

**Fecha de elaboración:** 2026-11-04.  
**Fecha de revisión humana:** 2026-11-05.

Las decisiones técnicas fueron documentadas inicialmente por el agente a partir de la consigna y revisadas posteriormente por la autora.

La aceptación corresponde al diseño y las decisiones documentadas, no a una implementación funcional. Las tecnologías, reglas y mecanismos propuestos deberán comprobarse durante las etapas de implementación y pruebas.

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

La revisión humana confirmó su coherencia con los requisitos y el alcance previstos. Esto no implica que las funcionalidades, pruebas o mecanismos de persistencia ya se encuentren implementados.

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