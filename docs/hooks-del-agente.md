# Hooks del agente

- [Introducción](#introducción)
- [En qué se diferencian de los hooks de git](#en-qué-se-diferencian-de-los-hooks-de-git)
- [Qué archivos protege](#qué-archivos-protege)
- [Los archivos inmutables del proyecto](#los-archivos-inmutables-del-proyecto)
- [El formato del código](#el-formato-del-código)
- [Los permisos](#los-permisos)
- [Qué ve el agente cuando se le bloquea](#qué-ve-el-agente-cuando-se-le-bloquea)
- [En Codex y OpenCode](#en-codex-y-opencode)
- [Cuando no funcionan](#cuando-no-funcionan)
- [Cambiarlos](#cambiarlos)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Un hook del agente es un programa que **Claude Code** ejecuta justo antes de que el agente edite un archivo. El kit usa uno: impide que el agente toque archivos protegidos.

Junto con él, el kit configura qué comandos puede ejecutar el agente sin preguntar, cuáles requieren tu confirmación y cuáles tiene prohibidos.

Todo vive en `equipo/adaptadores/claude/`.

## En qué se diferencian de los hooks de git

| | Hooks del agente | [Hooks de git](hooks-de-git.md) |
|---|---|---|
| Cuándo actúan | Cuando el agente intenta editar un archivo | Cuando alguien hace un commit |
| A quién aplican | Solo al agente, y solo en Claude Code | A cualquier persona y a cualquier herramienta |
| Qué logran | El error no llega a ocurrir | El error no llega al repositorio |

Los hooks del agente son más tempranos: el agente recibe el motivo del bloqueo en el momento y puede corregir el rumbo, en lugar de descubrirlo veinte archivos después al hacer commit.

## Qué archivos protege

Antes de cada edición, el hook revisa la ruta del archivo. Si coincide con alguno de estos casos, la edición no ocurre:

| Archivo | Por qué está protegido |
|---|---|
| `.env`, `.env.*`, `secrets/`, `*.pem`, `*.key` | Pueden contener secretos. `.env.example` sí se puede editar, porque no lleva valores reales |
| La constitución: los principios (`equipo/principios.md`), las reglas del proyecto (`equipo/reglas.md`) y el archivo que se genera con los dos | Solo la cambia una persona con autoridad. El agente propone el texto. Ver [La constitución](la-constitucion.md) |
| Todo dentro del submódulo del kit | Los cambios al kit se hacen en su repositorio |
| Los archivos listados en `.kit-manifest.json` | Vienen del kit y se reemplazan al actualizarlo |
| Los archivos inmutables del proyecto que ya están en git | No se editan una vez versionados: se crea uno nuevo. Ver [abajo](#los-archivos-inmutables-del-proyecto) |
| `specs/**/costos.json` | Lo escribe solo `make costos` |

## Los archivos inmutables del proyecto

Hay archivos que no se corrigen: se reemplazan con uno nuevo. El caso típico es un cambio de esquema de la base de datos (una migración): si ya se aplicó en alguna máquina, editarlo deja esa base distinta de las demás.

Cuáles son lo dice el proyecto, en el campo `inmutables` de cada parte de su [perfil](perfil-del-proyecto.md):

```json
{ "nombre": "datos", "carpeta": "base", "roles": ["dev-dba"], "inmutables": ["cambios/*.sql"] }
```

Con ese perfil, el hook bloquea la edición de `base/cambios/001_inicio.sql` si el archivo ya está en git:

```
Bloqueado: Estos archivos de la parte «datos» no se modifican una vez versionados; crea uno nuevo: base/cambios/001_inicio.sql
```

Un archivo **nuevo**, que todavía no está en git, sí se puede escribir y corregir libremente.

| Situación | Qué protege el hook |
|---|---|
| El proyecto tiene perfil | Lo que el perfil declara en `inmutables`, y nada más |
| El proyecto no tiene perfil | `backend/migrations/*.sql`, como antes de existir el perfil |
| El perfil tiene errores | Ningún archivo inmutable, hasta que se corrija. El [hook de git](hooks-de-git.md) rechaza el commit mientras tanto |

Es la misma lista que revisan el hook de git en cada commit y la [integración continua](integracion-continua.md) en cada Pull Request. El hook del agente solo se adelanta: el agente se entera al intentar la edición.

## El formato del código

El hook **no formatea** lo que el agente escribe. Hasta la versión 1.19.0 lo hacía, con `gofmt` y Prettier; se quitó porque ataba el kit a dos tecnologías y porque el control ya existe en otro lugar: el [hook de git](hooks-de-git.md) ejecuta el verbo `formato` de cada parte tocada y rechaza el commit si el código no está formateado.

El agente formatea con el comando que el proyecto tenga para eso. El control, para las tres herramientas, es el del commit.

## Los permisos

El kit también define qué puede ejecutar el agente en la terminal:

| Nivel | Comandos | Qué pasa |
|---|---|---|
| **Permitido** | `make`, `docker compose`, y de git: `status`, `diff`, `log`, `add`, `commit` | Lo ejecuta sin preguntar |
| **Pregunta** | `git push`, y cualquier comando que no esté en las otras dos filas | Te pide confirmación |
| **Prohibido** | Leer `.env` y `secrets/`, `git push --force`, `rm -rf`, `docker compose down -v` | No puede hacerlo |

La lógica de cada grupo:

- **Lo permitido** es lo que el agente hace decenas de veces por tarea. Pedir confirmación cada vez solo entrenaría a aprobar sin mirar. Probar, revisar y formatear se hacen con `make` (`make test PARTE=api`, `make ci`), que ejecuta los [verbos del perfil](perfil-del-proyecto.md): por eso el kit no necesita nombrar las herramientas de ninguna tecnología.
- **Lo que pregunta** tiene efectos fuera de tu máquina (subir código), o es un comando que el kit no conoce: instalar una dependencia, o llamar directo a una herramienta del proyecto.
- **Lo prohibido** es difícil o imposible de deshacer: borrar archivos, reescribir el historial compartido, borrar los datos de la base local, o exponer secretos.

> [!TIP]
> Si el agente te pregunta una y otra vez por un comando de tu proyecto (por ejemplo, ejecutar una sola prueba con `go test` o `php artisan test`), puedes permitirlo en tu máquina: Claude Code ofrece "no volver a preguntar" y lo guarda en `.claude/settings.local.json`, que es personal y no se sube a git.

> [!NOTE]
> El agente no puede **leer** `.env`. Va más allá de no poder editarlo: un secreto que el agente lee puede terminar en la conversación, en un registro o en un mensaje de commit.

## Qué ve el agente cuando se le bloquea

El hook le devuelve el motivo y qué hacer en su lugar:

```
Bloqueado: 'equipo/agentes/dev-backend.md' viene del kit compartido y se reemplaza al
actualizarlo. Propón el cambio en el repositorio del kit, o si es propio de este proyecto,
un humano puede agregarlo a "kit.excluir" en equipo/config.json.
```

Un agente que funciona bien se detiene ahí y te lo cuenta. Si en cambio busca otra forma de lograr lo mismo (por ejemplo, escribir el archivo con un comando de terminal en vez de editarlo), detenlo: está esquivando un control.

## En Codex y OpenCode

Estas herramientas no tienen hooks del agente. Las mismas reglas se aplican por otros medios:

| Protección | En Claude Code | En Codex y OpenCode |
|---|---|---|
| Archivos protegidos | El hook bloquea la edición | Las instrucciones lo prohíben; el [hook de git](hooks-de-git.md) rechaza el commit |
| Acceso por rol | Las herramientas de cada subagente | El modo de sandbox o los permisos de cada subagente |

El resultado final es el mismo: el cambio prohibido no entra al repositorio. La diferencia es cuándo se entera el agente.

## Cuando no funcionan

| Síntoma | Causa | Solución |
|---|---|---|
| El agente edita un archivo protegido sin que nada lo detenga | Los scripts no tienen permiso de ejecución, o falta `jq` | `make instalar-kit` repara el permiso. `jq` se instala según la página de [Instalación](instalacion.md) |
| El agente edita un archivo inmutable ya versionado | El perfil no lo declara en `inmutables`, el perfil tiene errores, o falta `python3` | `make profile` muestra los inmutables de cada parte y dice si el perfil tiene errores |
| Después de actualizar el kit, cada edición muestra un error que nombra `formatear.sh` | Claude Code sigue con la configuración de antes, que llamaba al hook de formateo | Reinicia Claude Code |
| El agente pide confirmación para `go test`, `npm run` u otra herramienta del proyecto | Desde la 1.20.0 el kit solo permite `make` | Ver [Los permisos](#los-permisos) |
| El agente pide confirmación para todo | La configuración generada está desactualizada | `make sincronizar` y reinicia Claude Code |

El hook necesita `jq` para leer qué archivo se va a editar. Sin `jq` no bloquea nada, y tampoco avisa. Por eso `make doctor` lo marca como requerido. Para los archivos inmutables necesita además `python3`, que el kit ya usa en todo lo demás.

## Cambiarlos

El hook y los permisos están en `equipo/adaptadores/claude/`, y a partir de ahí se genera `.claude/settings.json`. Vienen del kit:

- **Qué archivos son inmutables** se cambia en el perfil del proyecto, no en el hook.
- **Un cambio para todos los proyectos** se hace en el repositorio del kit. Ver [Cómo contribuir](contribuir.md).
- **Un cambio propio del proyecto** requiere excluir `equipo/adaptadores/` del kit. Ver [Personalizar un proyecto](personalizar.md).

Después de cualquier cambio: `make sincronizar` y reiniciar Claude Code.

## Siguientes pasos

- [Hooks de git](hooks-de-git.md): la capa que aplica a todas las herramientas.
- [Capas de control](capas-de-control.md): cómo encaja esta capa con las demás.
- [Una fuente, varias herramientas](una-fuente-varias-herramientas.md): por qué cada herramienta tiene protecciones distintas.
