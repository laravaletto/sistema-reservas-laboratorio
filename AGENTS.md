
# Instrucciones para Codex

## Contexto del proyecto
Sistema local de reservas de equipos de laboratorio.
Tecnologías: Python, Tkinter, SQLite y pytest.

## Control y aprobaciones humanas
- No realizar commits, push ni operaciones remotas de Git
  sin autorización explícita.
- No eliminar archivos, reservas o bases de datos existentes
  sin aprobación humana.
- No modificar archivos fuera del repositorio.
- Informar qué archivos se modificaron y qué comandos se ejecutaron.
- Detenerse al finalizar cada etapa para permitir la revisión humana.

## Calidad y verificaciones
- Respetar la especificación y las reglas de negocio.
- No inventar resultados de pruebas ni verificaciones humanas.
- Mantener separadas la interfaz, la lógica y la persistencia.
- No agregar funcionalidades fuera del alcance solicitado.

## Objetivo y documentos de referencia
- Construir una aplicación local para consultar disponibilidad, crear reservas,
  cancelarlas sin perder datos y consultar su historial.
- Consultar `docs/especificacion.md` antes de implementar o modificar reglas.
- Registrar decisiones en `docs/decisiones.md`, trabajo real en
  `docs/delegacion.md` y `docs/progreso.md`, y verificaciones en
  `docs/verificaciones.md`. No presentar propuestas como resultados ejecutados.
- La etapa 1 (documentación e inventario) fue revisada y aceptada por la autora, y sus resultados quedaron versionados en Git. En la etapa 2 se autoriza la implementación de la aplicación conforme a docs/especificacion.md, dentro del alcance indicado en cada delegación. No avanzar a etapas posteriores sin revisión y autorización humana.

## Tecnologías y arquitectura permitidas
- Python, Tkinter y ttk, SQLite mediante `sqlite3` y pytest.
- Git y GitHub para versionado, sujetos a la autorización humana ya establecida.
- Separar interfaz, lógica de negocio y persistencia; las reglas deben poder
  probarse sin abrir ventanas ni iniciar el bucle gráfico.
- Mantener una arquitectura simple y dependencias mínimas. La aplicación debe
  funcionar sin servicios externos, IA ni cuentas de ChatGPT/Codex.

## Reglas específicas del laboratorio
- El inventario es fijo: MIC-01 y MIC-02 (Microscopio digital), OSC-01
  (Osciloscopio), MUL-01 (Multímetro), FUE-01 (Fuente de alimentación).
  Cada ID representa una unidad física distinta. No ofrecer altas, bajas ni cambios.
- Las reservas tienen UUID, unidad, solicitante ficticio no vacío, inicio, fin
  y estado `ACTIVA` o `CANCELADA`. Rechazar unidades desconocidas y solicitantes
  vacíos o compuestos sólo por espacios.
- Validar fechas reales y formato exacto `AAAA-MM-DD HH:MM`; exigir inicio < fin.
  Permitir fechas pasadas, cualquier duración positiva y cualquier anticipación
  dentro del rango temporal documentado.
- Usar horas civiles locales de `America/Argentina/Cordoba`, sin conversiones
  de zona, según la representación uniforme definida en la especificación.
- Usar intervalos semiabiertos `[inicio, fin)` y detectar superposición mediante
  `inicio_nuevo < fin_existente AND inicio_existente < fin_nuevo`.
- Considerar exclusivamente reservas `ACTIVA` de la misma unidad. Compartir
  validación temporal, validación de unidad y detección de conflictos entre
  consulta de disponibilidad y creación; la creación también valida solicitante.
- Permitir intervalos consecutivos: MIC-01 10:00–11:00 y 11:00–12:00.
  Permitir simultaneidad entre unidades: MIC-01 y MIC-02 10:00–11:00.
- Cancelar sólo cambia el estado a `CANCELADA`: conservar UUID, unidad,
  solicitante e intervalo originales. La reserva cancelada libera el intervalo
  y continúa visible después de reiniciar. Repetir la cancelación no altera datos.
- Persistir tanto reservas activas como canceladas en SQLite; registrar éxito
  sólo después de confirmar la transacción. Revalidar conflictos al crear.

## Adaptación comprobable y evidencia
- En las etapas de implementación, incluir y ejecutar pruebas de superposición,
  adyacencia en ambos extremos, unidades distintas, cancelación que libera el
  intervalo, conservación del historial y recuperación tras reabrir SQLite.
- Verificar que consultar y crear coincidan para la misma unidad e intervalo
  bajo el mismo estado de datos; documentar los resultados reales.
- Ejecutar las pruebas pertinentes cuando haya código y reportar comandos,
  resultados y fallos. Si un chequeo no se ejecuta, declarar el motivo.
- Diferenciar resultados del agente de verificaciones personales de la autora.
  No inventar aprobaciones, errores, correcciones, pruebas ni commits.
- Mantener los episodios futuros pendientes hasta que ocurran; no adjuntar
  conversaciones privadas completas, secretos ni datos personales reales.
- Solicitar aprobación humana antes de operaciones destructivas, incluidas
  eliminación o reinicio de datos y sobrescrituras que pierdan información.

## Fuera de alcance
- Sin autenticación, roles reales, notificaciones, pagos ni integraciones externas.
- Sin despliegue, frontend web, interfaces complejas, concurrencia distribuida,
  escalabilidad de producción, MCP ni sistemas multiagente.
- No incorporar gestión de inventario ni funciones no solicitadas.
