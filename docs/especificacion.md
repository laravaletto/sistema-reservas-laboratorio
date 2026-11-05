# Especificación del sistema de reservas

Versión inicial: etapa 1, 2026-11-04. Documento preparado por el agente;
revisión humana pendiente. No hay aplicación ni pruebas implementadas.

## Problema, objetivo y alcance

La coordinación del laboratorio recibe solicitudes mediante mensajes y planillas.
Esto produce reservas superpuestas y horarios bloqueados después de cancelaciones.
La aplicación local permitirá leer el inventario fijo, consultar disponibilidad,
crear y cancelar reservas y consultar el historial conservado entre ejecuciones.
Se utilizarán exclusivamente solicitantes ficticios.

No incluye administración de inventario, autenticación, roles reales,
notificaciones, pagos, integraciones, despliegue, frontend web, interfaces
complejas, concurrencia distribuida, escalabilidad de producción, MCP ni
sistemas multiagente. No requiere una cuenta de IA para instalarse o ejecutarse.

## Inventario y datos

La fuente precargada es [data/inventario.json](../data/inventario.json), un arreglo
de objetos con claves `id` y `nombre`. Cada identificador es una unidad física:

| ID | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

Una reserva contiene `id` (UUID generado al crear), `unidad_id`, `solicitante`,
`inicio`, `fin` y `estado`. Estados únicos: `ACTIVA` y `CANCELADA`.
Se quitan espacios de los extremos del solicitante antes de validarlo y guardarlo;
no se permite un resultado vacío. No se exige unicidad del solicitante.
Los IDs de unidad se validan contra el inventario, respetando su escritura exacta.

## Requisitos y criterios de aceptación

Los criterios siguientes son obligaciones futuras, no verificaciones ya aprobadas.

| Requisito | Comportamiento requerido | Criterios de aceptación verificables |
|---|---|---|
| RF01 | Leer y mostrar inventario precargado. | CA01: al iniciar se muestran exactamente las cinco unidades del JSON con su ID y nombre, incluidas las dos unidades de microscopio como opciones distintas; no existen controles para modificarlo. |
| RF02 | Consultar disponibilidad de una unidad para un intervalo. | CA02a: unidad o intervalo inválidos generan un error explicativo, no una respuesta de disponibilidad. CA02b: con datos válidos se informa disponible si y sólo si no hay una reserva activa superpuesta de esa unidad. CA02c: la consulta no crea ni modifica reservas. |
| RF03 | Crear una reserva identificable. | CA03a: una entrada válida y libre genera un UUID único, guarda los campos y estado ACTIVA, y muestra confirmación con el ID. CA03b: unidad inexistente, solicitante vacío, fecha inválida, inicio >= fin o conflicto rechazan la operación sin insertar datos. CA03c: se permiten consecutivas y simultáneas de unidades distintas. |
| RF04 | Cancelar conservando identidad y datos originales. | CA04a: cancelar una ACTIVA por UUID cambia sólo el estado y libera su intervalo. CA04b: ID, unidad, solicitante, inicio y fin permanecen iguales. CA04c: un UUID inexistente informa error sin cambios; repetir cancelación informa que ya estaba cancelada y no modifica datos. |
| RF05 | Recuperar activas y canceladas al reiniciar. | CA05a: tras crear dos reservas y cancelar una, cerrar y reabrir la misma base conserva ambos UUID, todos sus datos y sus estados. CA05b: la activa sigue bloqueando y la cancelada no bloquea. CA05c: una operación fallida no deja escrituras parciales ni anuncia éxito. |
| RF06 | Consultar historial con estados. | CA06a: el listado incluye todas las reservas, activas y canceladas, con todos los campos definidos. CA06b: tras crear o cancelar se actualiza el listado; sólo las activas ofrecen cancelación. CA06c: sin registros muestra un estado vacío comprensible. |

## Reglas de negocio

| ID | Regla |
|---|---|
| RN01 | Aceptar sólo IDs de unidades existentes. |
| RN02 | Aceptar sólo solicitantes ficticios no vacíos luego de quitar espacios exteriores. |
| RN03 | Validar formato, fecha y hora reales; exigir inicio estrictamente anterior a fin. |
| RN04 | Una ACTIVA ocupa `[inicio, fin)`; una CANCELADA no ocupa disponibilidad. |
| RN05 | Hay conflicto únicamente en la misma unidad y con una ACTIVA cuando `inicio_nuevo < fin_existente AND inicio_existente < fin_nuevo`. |
| RN06 | Permitir adyacencia en cualquiera de los extremos y simultaneidad de unidades distintas. |
| RN07 | Consulta y creación comparten validación de unidad e intervalo y la misma regla de conflictos. Crear revalida al guardar y además valida el solicitante. Una consulta previa no bloquea horarios. |
| RN08 | Cancelación conserva el registro y todos sus datos originales; sólo cambia su estado. No hay eliminación de reservas en el producto. |
| RN09 | Guardar activas y canceladas y recuperar el historial completo después del reinicio. |

Para MIC-01 ACTIVA el `2026-11-10` de `10:00` a `11:00`: MIC-01
`10:30–11:30` se rechaza, MIC-01 `11:00–12:00` se acepta y MIC-02
`10:00–11:00` se acepta. Si se cancela la primera, su intervalo queda libre,
salvo que otra reserva activa lo ocupe.

## Supuestos y decisiones temporales

- Zona de referencia única: `America/Argentina/Cordoba`. La aplicación no usa
  la zona del sistema operativo ni convierte a otras zonas.
- Entrada exacta: `AAAA-MM-DD HH:MM` (`%Y-%m-%d %H:%M`), por ejemplo
  `2026-11-10 10:30`, con campos de ancho fijo, hora de 24 horas y sin segundos,
  offsets ni espacios exteriores. Validar también el calendario: `2026-02-30`
  no es válido. No depender sólo de la tolerancia de `strptime` a anchos variables.
- Representación: horas **civiles locales**, como `datetime` sin `tzinfo` en la
  lógica y texto canónico `YYYY-MM-DD HH:MM` en SQLite. Todos los valores tienen
  el mismo formato y precisión de minutos; su orden textual coincide con el civil.
- Estas horas representan turnos del calendario local, no instantes UTC ni
  duraciones físicas. No se modelan cambios históricos o futuros de huso ni horas
  repetidas/inexistentes por cambios de offset: los valores válidos del calendario
  se comparan como horas civiles. No asumir UTC−03 para todas las fechas.
  Esta simplificación explícita evita depender de bases de zonas horarias en
  Windows; si se requieren instantes reales, habrá que revisar esta decisión.
- Rango técnico: años `0001` a `9999`, calendario gregoriano de `datetime`, con
  representación de año de cuatro cifras. Pasado permitido, sin restricciones
  respecto del reloj actual. No se imponen límites adicionales a duración positiva
  ni anticipación dentro del rango representable. Se permiten intervalos entre días.
- UUID como texto canónico y clave primaria, estable tras cancelaciones y reinicios;
  se propone UUID4 de la biblioteca estándar para generación local sin contador.
- Sólo `ACTIVA` y `CANCELADA`; crear siempre como ACTIVA. No hay edición,
  reactivación, borrado, aprobación de reservas ni registro de motivos de cancelación.
- La aplicación está pensada para una instancia local. No hay agenda de apertura,
  feriados ni restricciones por solicitante. Estos supuestos evitan reglas no pedidas.

## Interfaz esperada

Tkinter y ttk con tres pestañas y mensajes claros en español:

1. **Reservas:** seleccionar unidad mostrando ID y nombre; ingresar solicitante,
   inicio y fin, con formato y ejemplo visibles. Crear muestra UUID y confirmación
   después de persistir; errores indican qué corregir sin cerrar la aplicación.
2. **Disponibilidad:** seleccionar unidad e intervalo; consultar muestra el resultado
   o la validación fallida. La selección permite distinguir MIC-01 de MIC-02.
3. **Historial:** tabla con UUID, unidad, solicitante, inicio, fin y estado. Orden
   ascendente por inicio y UUID como desempate, incluyendo canceladas. Cancelar
   exige seleccionar una ACTIVA y confirmar la acción; actualizar al completarla.

El inventario completo se visualiza en un listado de sólo lectura en la ventana,
además de los selectores. No se requieren filtros, exportaciones ni calendario gráfico.
La confirmación de cancelación es un supuesto de interfaz para evitar errores.

## Persistencia y fallos

Ubicación prevista: `data/reservas.db`, relativa a la raíz del proyecto y resuelta
independientemente del directorio desde el que se ejecute. Aún no existe.
El inventario se lee del JSON sin escribir en él; las reservas se guardan en SQLite.
Al primer uso se crea el esquema si no existe; reiniciar no reemplaza registros.
Campos obligatorios, UUID único, unidad válida y estados limitados a los definidos.
El esquema y las consultas concretas se implementarán en la siguiente etapa.

Validar antes de insertar y revalidar conflictos dentro de la operación de creación;
usar transacciones y parámetros SQL. Al cancelar, persistir el cambio de estado.
Un error debe revertir la operación y generar un mensaje; no anunciar éxito antes
de confirmar la transacción. Un inventario ausente/inválido o una base inaccesible
se informa sin reemplazar archivos ni destruir datos. Las bases locales están
ignoradas por `.gitignore`; el inventario y el esquema futuro serán reproducibles.
No habrá función de reinicio de datos. Cualquier reinicio manual requiere aprobación
y resguardo previo; no se ejecuta ni prescribe un borrado en esta etapa.

## Casos previstos de prueba

Todos están **pendientes de implementar y ejecutar**. Usar datos ficticios,
bases temporales y lógica sin ventanas; no tocar una base de uso real.

| Caso | Requisitos / reglas | Entrada o situación | Resultado esperado |
|---|---|---|---|
| CP01 | RF01 | Leer JSON inicial | Cinco IDs únicos, nombres correctos, dos microscopios distintos. |
| CP02 | RF02, RF03 / RN01 | Unidad XXX-99 | Error en consulta y creación; sin cambios. |
| CP03 | RF03 / RN02 | Solicitante vacío o sólo espacios | Error; no se crea registro. |
| CP04 | RF02, RF03 / RN03 | Fecha imposible, hora 24:00, texto incompleto o formato sin ceros | Error en ambos flujos. |
| CP05 | RF02, RF03 / RN03 | Inicio igual o posterior a fin | Error en ambos flujos. |
| CP06 | RF02, RF03 / RN05 | MIC-01 10:00–11:00 activa; pedir 10:30–11:30 | No disponible; creación rechazada. |
| CP07 | RF02, RF03 / RN05 | Mismo intervalo, contenido dentro de otro o envolviendo otro | Conflicto en cada caso de la misma unidad. |
| CP08 | RF02, RF03 / RN06 | MIC-01 10:00–11:00 activa; pedir 11:00–12:00 o 09:00–10:00 | Disponible; creación permitida en ambos extremos. |
| CP09 | RF02, RF03 / RN06 | MIC-01 ocupada; pedir MIC-02 en el mismo intervalo | Disponible; creación permitida. |
| CP10 | RF03 | Entrada válida, con espacios exteriores en solicitante | UUID válido y único; solicitante normalizado y estado ACTIVA. |
| CP11 | RF02, RF04, RF06 / RN04, RN08 | Cancelar una reserva y volver a consultar/crear su intervalo | Se libera; original conserva sus campos y figura CANCELADA en historial. |
| CP12 | RF04 | UUID inexistente o reserva ya cancelada | Error por inexistente o aviso de cancelación previa; sin cambios. |
| CP13 | RF05, RF06 / RN09 | Crear dos, cancelar una, cerrar conexión y reabrir la misma base | Datos y estados idénticos; sólo la activa bloquea. |
| CP14 | RF02, RF03 / RN07 | Mismo estado de datos, unidad e intervalo en consulta y creación | Coinciden en validez y conflicto, usando solicitante válido. |
| CP15 | RF02, RF03 | Fechas pasadas, cruce de día, intervalo largo, inicio muy futuro | Aceptados si son válidos y libres; sin límites adicionales. |
| CP16 | RF03, RF05 | Conflicto surgido después de una consulta; fallo de escritura | Revalidar y rechazar conflicto; ante fallo revertir sin confirmar éxito. |
| CP17 | RF06 | Historial vacío y luego con activas/canceladas | Listado completo, orden definido y cancelación sólo para activas. |
| CP18 | RF01, RF05 | JSON inválido/ausente o base inaccesible | Mensaje de error; no reemplazar ni perder archivos existentes. |

La autora verificará además la interfaz, errores visibles, inventario, creación,
cancelación y cierre/reapertura de la aplicación real. Las pruebas automáticas de
reapertura de SQLite no sustituyen esa comprobación humana del reinicio completo.
