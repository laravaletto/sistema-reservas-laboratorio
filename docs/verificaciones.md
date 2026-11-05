# Registro de verificaciones

Fecha de inicio: 2026-11-04. Última actualización documental: 2026-11-05.

Este registro distingue lo observado mediante herramientas del agente, lo informado por la autora y las verificaciones realizadas personalmente por ella.

Los resultados de la etapa 1 corresponden exclusivamente a la preparación documental. No contienen resultados de pruebas funcionales de la aplicación, ya que todavía no existen código ni pruebas implementadas.

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

## Pruebas de aplicación ejecutadas por el agente

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

## Estado de la etapa 1

**Trabajo del agente:** finalizado.

**Revisión humana:** realizada sobre inventario, especificación, instrucciones del agente y registro de delegación. Pendiente de completar sobre los documentos restantes.

**Implementación:** pendiente.

**Pruebas funcionales:** pendientes.

**Commit del episodio:** pendiente de creación manual.

La siguiente etapa sólo comenzará después de completar la revisión humana y registrar el avance mediante Git.