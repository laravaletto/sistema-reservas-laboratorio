# Registro de verificaciones

Fecha de inicio: 2026-11-04. Última actualización documental: 2026-11-05.

Este registro distingue lo observado mediante herramientas del agente, lo informado por la autora y las verificaciones realizadas personalmente por ella.

Los resultados de la etapa 1 corresponden exclusivamente a la preparación documental:
en ese momento no había código ni pruebas. Los resultados reales de implementación
y pruebas de la segunda delegación se agregan al final, sin sustituir la evidencia histórica.

## Información del entorno y procedencia

| Dato | Valor | Procedencia y límite |
|---|---|---|
| Entorno | Visual Studio Code | Informado por la autora; el agente no inspeccionó directamente la interfaz. |
| Agente/harness | OpenAI Codex integrado en VS Code | Informado por la autora. |
| Extensión | `openai.chatgpt`, versión `26.1007.21434` | La autora informó una comprobación previa mediante `code --list-extensions --show-versions`. El agente obtuvo la misma versión, aunque su consulta presentó errores de permisos relacionados con logs. |
| Modelo seleccionado | `GPT-6.1 Sol High` | Selección de la interfaz observada por la autora; no comprobada directamente por el agente. |
| Modalidad | `Work locally` | Selección de la interfaz observada por la autora. |
| Permisos | `Ask for approval` | Selección de la interfaz observada por la autora. No implica que se haya comprobado una configuración interna equivalente. |
| Instrucciones del proyecto | `AGENTS.md` | Archivo leído por el agente antes de modificarlo y revisado posteriormente por la autora. |
| Python | `3.13.7` | Salida directa de `python --version`, ejecutado por el agente. |
| Git | `2.47.0.windows.2` | Salida directa de `git --version`, ejecutado por el agente. |
| pytest, Tcl/Tk y SQLite | Versiones pendientes de verificar | No consultadas ni probadas por el agente durante esta etapa. |
| Control humano | Revisión documental, aprobación de operaciones restringidas y commits manuales | Se realizó revisión documental de archivos específicos. Las pruebas funcionales y el commit del episodio permanecen pendientes. |

No se declara comprobada una configuración interna denominada `workspace-write`, `on-request` u otro identificador similar.

Los datos informados por la autora no se presentan como inspecciones directas del agente.

## Comandos ejecutados por el agente

Los siguientes comandos fueron ejecutados por Codex desde la raíz del repositorio durante el primer episodio de delegación.

| ID | Comando real | Resultado observado |
|---|---|---|
| V01 | `Get-Content -LiteralPath AGENTS.md` | Lectura exitosa; los acentos aparecieron incorrectamente por la codificación predeterminada. |
| V02 | `rg --files --hidden -g '!.git/**'` | Se encontraron inicialmente `AGENTS.md` y `.gitignore`. |
| V03 | `git status --short; git log -5 --oneline` | `AGENTS.md` estaba sin seguimiento; se observó el commit previo `3128779 chore: inicializar repositorio`. Ambos comandos fueron de sólo lectura. |
| V04 | `Get-Content -LiteralPath AGENTS.md -Encoding UTF8` | Lectura correcta de las instrucciones iniciales con acentos. No fue necesario reparar el archivo. |
| V05 | `Get-Content -LiteralPath .gitignore -Encoding UTF8` | Se comprobaron exclusiones para entorno virtual, cachés, bases locales, secretos y archivos del editor. |
| V06 | `git ls-files` | Inicialmente sólo `.gitignore` estaba versionado. |
| V07 | `python --version` | Python 3.13.7; ejecución exitosa. |
| V08 | `git --version` | Git 2.47.0.windows.2; ejecución exitosa. |
| V09 | `code --list-extensions --show-versions \| Select-String -Pattern '^openai\.chatgpt@'` | Se obtuvo `openai.chatgpt@26.1007.21434`, acompañado de errores de permisos relacionados con logs. |

La consulta V09 informó `CreateFile: Acceso denegado (0x5)` y `EPERM` al intentar crear logs de VS Code fuera del repositorio.

Aunque la shell devolvió código 0 y se obtuvo la versión de la extensión, no se considera una ejecución completamente limpia.

No se reintentó con permisos ampliados ni se autorizaron escrituras externas. Tampoco se inspeccionaron ni modificaron archivos externos.

Para crear y modificar los documentos, Codex utilizó la herramienta `apply_patch`. Esta operación no corresponde a un comando de shell.

## Comprobación documental del agente

Codex realizó comprobaciones adicionales para verificar la estructura y el contenido de los archivos generados.

| ID | Comando | Resultado observado |
|---|---|---|
| V10 | Script Python enviado mediante un here-string de PowerShell a `python -` | Código 0. Ocho archivos UTF-8 no vacíos y sin espacios finales; inventario exacto; bloque inicial de `AGENTS.md` conservado; 27 enlaces locales válidos; sin `src/`, `tests/` ni base de datos. |
| V11 | `git diff --check` | Código 0, sin salida. Esta comprobación no cubría los archivos nuevos sin seguimiento. |
| V12 | `git diff --exit-code -- .gitignore` | Código 0, sin salida. `.gitignore` permaneció sin modificaciones. |
| V13 | `git status --short --untracked-files=all` | Se observaron los ocho archivos solicitados sin seguimiento y un archivo adicional `debug.log` generado durante la consulta de extensiones. |
| V14 | `Get-Item -LiteralPath debug.log \| Select-Object Name,Length,CreationTime,LastWriteTime; Get-Content -LiteralPath debug.log -Encoding UTF8` | Se identificó un log de 131 bytes con el error de Crashpad asociado a V09. No figuraba en la enumeración inicial V02. |
| V15 | `Remove-Item -LiteralPath 'C:\Users\Windows\sistema-reservas-laboratorio\debug.log'` | Ejecutado mediante una solicitud de aprobación de la herramienta. Código 0, sin salida. Se retiró únicamente el log generado por V09. |

### Script utilizado en V10

Este script fue utilizado para comprobar la documentación. No corresponde a una prueba funcional de la aplicación.

```powershell
@'
import json
import re
from pathlib import Path

root = Path.cwd()
files = [Path(name) for name in (
    'AGENTS.md',
    'README.md',
    'docs/especificacion.md',
    'docs/decisiones.md',
    'docs/delegacion.md',
    'docs/progreso.md',
    'docs/verificaciones.md',
    'data/inventario.json'
)]

for path in files:
    content = path.read_text(encoding='utf-8')
    assert content.strip(), f'Archivo vacio: {path}'
    assert all(
        line == line.rstrip() for line in content.splitlines()
    ), f'Espacios finales: {path}'

expected = [
    {'id': 'MIC-01', 'nombre': 'Microscopio digital'},
    {'id': 'MIC-02', 'nombre': 'Microscopio digital'},
    {'id': 'OSC-01', 'nombre': 'Osciloscopio'},
    {'id': 'MUL-01', 'nombre': 'Multímetro'},
    {'id': 'FUE-01', 'nombre': 'Fuente de alimentación'}
]

actual = json.loads(
    Path('data/inventario.json').read_text(encoding='utf-8')
)

assert actual == expected, 'Inventario distinto de las cinco unidades solicitadas'
assert len({item['id'] for item in actual}) == 5

original = '''# Instrucciones para Codex

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
'''

assert Path('AGENTS.md').read_text(
    encoding='utf-8'
).lstrip('\n').startswith(original)

links = 0

for path in files:
    if path.suffix != '.md':
        continue

    content = path.read_text(encoding='utf-8')

    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', content):
        assert '://' not in target, f'Enlace externo inesperado: {target}'

        resolved = (path.parent / target.split('#')[0]).resolve()

        assert resolved.is_relative_to(root), (
            f'Enlace fuera del repositorio: {target}'
        )

        assert resolved.is_file(), (
            f'Enlace inexistente en {path}: {target}'
        )

        links += 1

assert not Path('src').exists() and not Path('tests').exists()
assert list(Path('data').iterdir()) == [Path('data/inventario.json')]

print(f'OK: {len(files)} archivos UTF-8 no vacios y sin espacios finales')
print('OK: inventario exacto de cinco unidades y bloque inicial de AGENTS.md conservado')
print(f'OK: {links} enlaces locales existentes dentro del repositorio')
print('OK: sin src/, tests/ ni base de datos; data/ contiene solo inventario.json')
'@ | python -
```

El resultado informado por Codex para V10 fue exitoso, con ocho archivos comprobados y 27 enlaces locales existentes.

El script se conserva como evidencia del procedimiento utilizado. Su inclusión no significa que la autora lo haya ejecutado independientemente.

### Incidente de `debug.log` y aprobación humana

Durante la consulta de extensiones V09 se generó un archivo `debug.log` no solicitado en la raíz del repositorio.

Codex identificó el archivo y solicitó aprobación para eliminarlo, respetando la restricción establecida en `AGENTS.md`.

El comando V15 se ejecutó mediante el mecanismo de aprobación de la herramienta y terminó con código 0.

La opción exacta seleccionada por la autora (`Allow once` o `Deny`) queda pendiente de confirmar y registrar. No se atribuye una elección específica sin confirmación.

Este incidente constituye evidencia de la aplicación de las instrucciones de control humano, pero no representa una aceptación de la documentación generada.

Después de retirar el log y actualizar los documentos, Codex repitió V10, V11, V12 y V13.

Los resultados informados fueron:

- V10: código 0, ocho archivos y 27 enlaces locales válidos.
- V11 y V12: código 0, sin salida.
- V13: únicamente los ocho archivos solicitados sin seguimiento; `debug.log` ya no estaba presente.

No se modificó `.gitignore` para ocultar el archivo.

No se ejecutó `git add`, no se realizaron commits ni se publicaron cambios.

## Pruebas de aplicación ejecutadas por el agente — etapa 1

**Ninguna.**

Durante la etapa 1 no se implementó la aplicación ni se crearon archivos de pruebas.

No se ejecutó pytest, no se instalaron dependencias ni se abrió la interfaz gráfica.

Los casos CP01–CP18 definidos en [especificacion.md](especificacion.md) son casos previstos para etapas posteriores, no resultados de pruebas ejecutadas.

## Verificaciones personales de la autora

La autora realizó una revisión documental de archivos generados durante el primer episodio de delegación.

Estas verificaciones permiten evaluar la correspondencia entre la documentación y los requisitos solicitados, pero no constituyen pruebas funcionales de la aplicación.

| Fecha | Persona | Archivo o versión revisada | Procedimiento personal | Resultado observado | Decisión / evidencia |
|---|---|---|---|---|---|
| 2026-11-05 | Autora | `data/inventario.json` | Inspección manual del inventario. | Se confirmó que contiene las cinco unidades solicitadas, con sus identificadores y nombres correctos. | Aceptado. |
| 2026-11-05 | Autora | `docs/especificacion.md` | Lectura y revisión de requisitos, reglas, criterios de aceptación y casos previstos. | Se comprobaron RF01–RF06, RN01–RN09, criterios de aceptación, reglas de superposición, adyacencia y cancelación. | Aceptado a nivel documental. |
| 2026-11-05 | Autora | `AGENTS.md` | Revisión de las instrucciones iniciales y ampliaciones realizadas por Codex. | Se comprobó que conserva las restricciones de control humano e incorpora reglas específicas para el sistema de reservas. | Aceptado. |
| 2026-11-05 | Autora | `docs/delegacion.md` | Lectura y revisión del primer episodio de delegación. | Se comprobó que registra el objetivo, contexto, instrucciones, acciones informadas y evidencia, manteniendo pendientes los episodios 2 y 3. | Aceptado a nivel documental. |
| Pendiente | Autora | Implementación futura | Ejecutar pruebas automáticas de forma independiente. | No ejecutado. | Pendiente. |
| Pendiente | Autora | Implementación futura | Recorrer inventario, creación, disponibilidad, historial y cancelación en la interfaz gráfica. | No ejecutado. | Pendiente. |

La aceptación documental del episodio 1 se registra en [delegacion.md](delegacion.md).

La revisión humana no implica que se haya verificado el funcionamiento de la aplicación, la persistencia real o el resultado de pruebas automáticas.

Los documentos `README.md`, `docs/decisiones.md` y `docs/progreso.md` quedan sujetos a revisión antes del commit de esta etapa.

## Persistencia tras reinicio — pendiente

El siguiente procedimiento se realizará en una etapa posterior. **Todavía no fue ejecutado.**

1. Utilizar datos ficticios y una base de verificación separada, sin borrar datos existentes.
2. Crear dos reservas en intervalos distintos y anotar sus UUID y campos.
3. Cancelar una reserva y comprobar que permanece en el historial y libera su intervalo.
4. Cerrar completamente la aplicación y volver a abrirla utilizando la misma base.
5. Comparar los registros originales y sus estados, comprobando que únicamente las reservas activas bloquean disponibilidad.
6. Registrar el resultado, la fecha, la versión utilizada y cualquier fallo observado.

| Ejecutor | Fecha / versión | Base utilizada | Resultado antes/después | Evidencia |
|---|---|---|---|---|
| Agente | Pendiente | Base temporal, pendiente | No ejecutado | Pendiente |
| Autora | Pendiente | Base separada, pendiente | No ejecutado | Pendiente |

La prueba automática de persistencia mediante reapertura de SQLite no reemplaza la comprobación humana del cierre y reinicio completo de la aplicación gráfica.

## Fallos, límites y tareas sin ejecutar

- La primera lectura de `AGENTS.md` presentó acentos incorrectos. Se resolvió mediante una nueva lectura con codificación UTF-8.
- La consulta de extensiones de VS Code presentó errores de permisos relacionados con la creación de logs. Se documentó la limitación sin afirmar que la consulta fue completamente limpia.
- La consulta de extensiones generó un archivo temporal `debug.log`, retirado mediante una solicitud de aprobación de la herramienta.
- No se verificaron durante esta etapa las versiones de pytest, Tcl/Tk y SQLite utilizadas por la futura aplicación.
- No se implementaron funcionalidades ni pruebas automáticas.
- No se ejecutaron pruebas de disponibilidad, superposición, creación, cancelación o persistencia.
- No se realizó todavía la comprobación de reinicio completo de la aplicación.
- No se eliminaron reservas ni bases de datos existentes.
- No se realizaron commits, push ni operaciones remotas de Git durante la delegación.
- La revisión documental de la autora no sustituye las pruebas funcionales posteriores.
- Permanecen pendientes la revisión de los demás documentos y el commit manual del primer episodio.

## Estado de la etapa 1 al preparar el registro documental

**Trabajo del agente:** finalizado.

**Revisión humana:** realizada sobre inventario, especificación, instrucciones del agente y registro de delegación. Pendiente de completar sobre los documentos restantes.

**Implementación:** pendiente.

**Pruebas funcionales:** pendientes.

**Commit del episodio:** pendiente de creación manual.

La siguiente etapa sólo comenzará después de completar la revisión humana y registrar el avance mediante Git.

## Segunda delegación — 2026-11-05

### Punto de partida y alcance real

La autora informó que revisó, aceptó y versionó la etapa 1. El agente observó
`b445b3d docs: agregar especificacion y preparacion del agente` y
`3128779 chore: inicializar repositorio`. El estado inicial sólo mostraba una
modificación de AGENTS.md hecha previamente; el agente la conservó sin editarlo.
Las referencias anteriores a tareas pendientes de etapa 1 son históricas.

Se implementaron siete módulos en src/reservas_lab, iniciar.py, pytest.ini,
requirements-dev.txt y cuatro archivos en tests/. Se actualizan únicamente
README.md, decisiones.md, delegacion.md, progreso.md y este registro.
No se modifican especificación, inventario ni .gitignore. No se crea una base de
producción; las pruebas usan bases temporales o en memoria, con datos ficticios.

### Comandos de inspección y preparación ejecutados

Las lecturas fueron individuales con `Get-Content -LiteralPath <archivo> -Encoding UTF8`
para AGENTS.md, docs/especificacion.md, README.md, docs/decisiones.md,
docs/delegacion.md, docs/progreso.md, docs/verificaciones.md y data/inventario.json.
Se repitieron las lecturas de decisiones, delegación y progreso porque la salida
conjunta anterior había sido truncada. Todas esas lecturas devolvieron código 0.
`apply_patch` se utilizó para las ediciones; no es un comando de shell.

| Comando real | Resultado observado |
|---|---|
| `rg --files --hidden -g '!.git/**'` | Se encontraron instrucciones, README, cinco documentos, JSON e ignore, sin aplicación ni tests. |
| `git status --short` | Sólo AGENTS.md ya modificado antes de intervenir. |
| `git log -5 --oneline` | b445b3d y 3128779; no operaciones remotas. |
| `python -m pytest --version` | Código 1: No module named pytest en Python global. |
| `python -m venv .venv` | Código 0; entorno local preparado. |
| `.\.venv\Scripts\python.exe -m pip install --no-cache-dir pytest==8.4.2` | Primer intento con código 1: conexión bloqueada, WinError 10013; no se pudo consultar el índice. Se repitió mediante solicitud de autorización de red y terminó con código 0, pytest 8.4.2 instalado dentro de .venv. |
| `Get-Item -LiteralPath 'C:\Users\Windows\AppData\Local\Programs\Python\Python313\tcl\tcl8.6\init.tcl'` | Código 0; archivo de Tcl existente. Sólo lectura para diagnosticar el entorno. |

Comando de versiones inicial:

```powershell
python -c "import sys, sqlite3, tkinter; print(sys.version); print('SQLite:', sqlite3.sqlite_version); print('Tcl:', tkinter.Tcl().eval('info patchlevel')); print('Tk declarado por tkinter:', tkinter.TkVersion)"
```

Devolvió Python 3.13.7 y SQLite 3.50.4, y código 1 al intentar inicializar Tcl
(`Can't find a usable init.tcl`). Se repitió en el entorno virtual:

```powershell
.\.venv\Scripts\python.exe -c "import sqlite3, tkinter; print('SQLite:', sqlite3.sqlite_version); print('Tcl:', tkinter.Tcl().eval('info patchlevel')); print('Tk declarado:', tkinter.TkVersion)"
```

También devolvió código 1 por Tcl. El archivo existente no bastó para inicializar
Tcl dentro del entorno restringido; la comprobación autorizada fuera de él sí
pasó, como se detalla abajo. No se reparó ni modificó la instalación global.

### Pruebas y comprobaciones ejecutadas por el agente

| Comando real | Resultado observado |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.venv/pruebas-etapa2-01` | Código 0: **81 passed in 3.47s**. Bases nuevas dentro de .venv; sin ventanas. |
| `.\.venv\Scripts\python.exe -m compileall -q src tests iniciar.py` | Código 0, sin salida; ejecutado antes y después del ajuste de cierre de conexiones de pruebas. |
| `.\.venv\Scripts\python.exe -W error -m pytest -q --basetemp=.venv/pruebas-etapa2-02` | Código 0: **81 passed in 3.76s**, advertencias tratadas como errores. Corrida final tras cerrar explícitamente conexiones auxiliares en tests. |
| `.\.venv\Scripts\python.exe -m pip check` | Código 0: No broken requirements found. |
| `.\.venv\Scripts\python.exe -m pip list --format=freeze` | Código 0: colorama 0.4.6, iniconfig 2.3.1, packaging 26.3, pip 25.2, pluggy 1.7.0, Pygments 2.21.0 y pytest 8.4.2. |
| `git diff --check` | Código 0; avisos de conversión futura LF a CRLF en documentos editados, sin errores de espacios. No se cambió la configuración Git. |
| `git status --short --untracked-files=all` | Código 0; archivos nuevos y documentos editados, más la modificación previa de AGENTS.md. No hay commit de implementación. |
| `git diff --exit-code -- docs/especificacion.md data/inventario.json .gitignore` | Código 0, sin salida; los tres archivos permanecen intactos. |

La primera instalación falló por red; no fue un fallo de una prueba del sistema.
No hubo fallos en las dos corridas de pytest. Las excepciones de escritura y
commit inducidas en tests son escenarios esperados con rollback comprobado,
no errores encontrados en datos de uso real. No se usó data/reservas.db.

### Correspondencia con los casos previstos

| Casos | Evidencia automática |
|---|---|
| CP01, CP18 (inventario) | tests/test_inventario.py: unidades exactas, lectura sin cambios, contenido inválido/ausente y rutas independientes del directorio actual. |
| CP02–CP12, CP14, CP15 | tests/test_reglas.py: validaciones, matriz de superposiciones, ambos extremos consecutivos, unidades distintas, UUID, cancelación, repetición, pasado, cruces de día y rango 0001–9999. |
| CP13, CP16, CP18 (base) | tests/test_persistencia.py: reapertura con ambos estados, conflicto posterior a consulta, rollback ante fallos de inserción/cancelación/commit, base inaccesible o inválida sin reemplazar contenido y parámetros SQL. |
| CP17 | Orden y estados del historial en test_reglas.py; selección/cancelación y actualización en la comprobación gráfica oculta. Revisión visual humana realizada el 2026-11-05; resultado satisfactorio. |

La reapertura automática de SQLite conservó UUID, unidad, solicitante, inicio,
fin y estado de dos reservas, una cancelada y otra activa. Después de reabrir,
la cancelada no bloqueó y la activa sí. Es evidencia de RF05 a nivel de persistencia;
no se presenta como reinicio manual completo de la GUI.

### Comprobación gráfica del agente con ventana oculta

Se envió un script inline mediante here-string de PowerShell a
`.\.venv\Scripts\python.exe -`, con solicitud de autorización porque Tcl no
inicializaba dentro del entorno restringido. Devolvió código 0.

Procedimiento ejecutado: crear Tk y ocultarlo, abrir SQLite en memoria, cargar el
JSON y construir Aplicacion. Se reemplazaron sólo en ese proceso los diálogos por
funciones que registraban mensajes y aceptaban la confirmación de cancelación.
El script comprobó el historial vacío, creó una reserva ficticia, consultó su
superposición, intentó duplicarla (error sin inserción), seleccionó la activa,
comprobó el botón habilitado, la canceló, comprobó el estado y botón deshabilitado,
y volvió a consultar el intervalo libre. Finalmente ejecutó el punto de entrada
con base en memoria, mantuvo la ventana oculta y cerró el bucle con un evento programado.

Salida observada:

```text
OK: widgets ocultos, creacion, conflicto, consulta, cancelacion e historial
Tcl: 8.6.15
Tk: 8.6.15
OK: punto de entrada, bucle grafico y cierre sin errores; sin base de produccion
```

Esto comprueba construcción y acciones de widgets reales. No comprueba
legibilidad, composición visual, interacción personal con los diálogos ni el
reinicio completo contra una base en disco de la aplicación real. No se atribuye
ninguna de esas verificaciones a la autora ni se agregan pruebas GUI a la suite
que debe correr sin ventanas.

### Verificación humana de la segunda delegación

La autora realizó pruebas funcionales de la aplicación y ejecutó independientemente la suite automatizada el 2026-11-05, después de finalizar el trabajo de Codex.

| Fecha | Persona | Procedimiento | Resultado / decisión |
|---|---|---|---|
| 2026-11-05 | Autora | Ejecutar `./.venv/Scripts/python.exe -m pytest` desde Git Bash. | 81 pruebas aprobadas en 3,33 segundos. Se presentó una advertencia `PytestCacheWarning` por permisos de escritura en `.pytest_cache`. |
| 2026-11-05 | Autora | Ejecutar `./.venv/Scripts/python.exe -m pytest -p no:cacheprovider`. | 81 pruebas aprobadas en 3,31 segundos, sin advertencias. |
| 2026-11-05 | Autora | Iniciar la aplicación mediante `./.venv/Scripts/python.exe iniciar.py` e inspeccionar sus pestañas. | La interfaz abrió correctamente y mostró las cinco unidades del inventario, Reservas, Disponibilidad e Historial. |
| 2026-11-05 | Autora | Crear una reserva para MIC-01 de 10:00 a 11:00 e intentar otra de 10:30 a 11:30 del mismo día. | Se creó la primera reserva y se rechazó la segunda por superposición. |
| 2026-11-05 | Autora | Crear una segunda reserva para MIC-01 de 11:00 a 12:00. | Se permitió la reserva consecutiva y ambas aparecieron activas en el historial. |
| 2026-11-05 | Autora | Consultar disponibilidad de MIC-01 de 10:30 a 11:30. | Se informó correctamente que el intervalo no estaba disponible. |
| 2026-11-05 | Autora | Cancelar la reserva de 10:00 a 11:00 y consultar nuevamente ese intervalo. | La reserva permaneció en el historial como CANCELADA y el intervalo quedó disponible. La reserva de 11:00 a 12:00 continuó activa. |
| 2026-11-05 | Autora | Cerrar y volver a abrir la aplicación. | Las dos reservas permanecieron registradas con sus estados correspondientes, confirmando persistencia entre ejecuciones. |
| 2026-11-05 | Autora | Revisar `dominio.py`, `servicio.py` y `persistencia.py`. | Se comprobó la coherencia de las validaciones, reglas de negocio, consultas SQL y transacciones. No se identificaron correcciones necesarias. |

Las reservas utilizadas contenían datos ficticios y correspondían al 2026-11-10.

La advertencia de caché de pytest no fue un fallo de las pruebas. La segunda ejecución confirmó que la suite podía completarse sin advertencias al desactivar el proveedor de caché.

La autora aceptó la implementación de la segunda delegación. La decisión y sus motivos se registran en [delegacion.md](delegacion.md).

El commit de la etapa 2 permanece pendiente de creación manual. El episodio 3 todavía no se inició.

### Inspección final de archivos y documentación

Un segundo script inline enviado mediante here-string a
`.\.venv\Scripts\python.exe -` enumeró iniciar.py, pytest.ini,
requirements-dev.txt y los .py de src/ y tests/, validó UTF-8 y ausencia de espacios
finales, resolvió los enlaces Markdown del README y docs/ y comprobó data/.
Código 0: **14 archivos nuevos comprobados, 40 enlaces locales existentes y sólo
inventario.json en data/**. No se abrió una base de producción.

Se ejecutaron también `git diff --stat` y `git diff -- AGENTS.md`, ambos con
código 0: el primero mostró cinco documentos editados por el agente y AGENTS.md;
el segundo mostró únicamente la autorización de etapa 2 ya presente al comenzar.
Los 14 archivos nuevos aparecen en `git status --short --untracked-files=all`,
que se repitió junto con `git diff --check` y la comprobación de especificación,
inventario e ignore sin cambios. Todos devolvieron código 0. Git avisó de futuras
conversiones LF a CRLF; no informó errores de espacios. No se añadieron archivos
al índice ni se alteró la configuración del repositorio.
