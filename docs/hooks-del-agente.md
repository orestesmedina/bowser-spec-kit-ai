# Hooks del agente

- [Introducción](#introducción)
- [En qué se diferencian de los hooks de git](#en-qué-se-diferencian-de-los-hooks-de-git)
- [Qué archivos protege](#qué-archivos-protege)
- [El formateo automático](#el-formateo-automático)
- [Los permisos](#los-permisos)
- [Qué ve el agente cuando se le bloquea](#qué-ve-el-agente-cuando-se-le-bloquea)
- [En Codex y OpenCode](#en-codex-y-opencode)
- [Cuando no funcionan](#cuando-no-funcionan)
- [Cambiarlos](#cambiarlos)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Los hooks del agente son programas que **Claude Code** ejecuta justo antes y justo después de que el agente edite un archivo. El kit usa dos: uno impide que el agente toque archivos protegidos, y el otro formatea lo que el agente acaba de escribir.

Junto con ellos, el kit configura qué comandos puede ejecutar el agente sin preguntar, cuáles requieren tu confirmación y cuáles tiene prohibidos.

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
| La constitución | Solo la cambia una persona con autoridad. Ver [La constitución](la-constitucion.md) |
| Todo dentro del submódulo del kit | Los cambios al kit se hacen en su repositorio |
| Los archivos listados en `.kit-manifest.json` | Vienen del kit y se reemplazan al actualizarlo |
| Una migración que ya está en git | Una migración aplicada no se edita: se crea una nueva |
| `specs/**/costos.json` | Lo escribe solo `make costos` |

Una migración **nueva**, que todavía no está en git, sí se puede escribir y corregir libremente.

## El formateo automático

Después de cada edición, el segundo hook formatea el archivo que el agente acaba de tocar:

| Archivos | Con qué |
|---|---|
| `.go` | `gofmt` |
| `.ts`, `.tsx`, `.js`, `.jsx`, `.css`, `.json`, `.md` | Prettier, si el frontend tiene sus dependencias instaladas |

Este hook nunca bloquea nada. Su único efecto es que el código llega ya formateado al commit, y el hook de git no tiene que rechazarlo por eso.

## Los permisos

El kit también define qué puede ejecutar el agente en la terminal:

| Nivel | Comandos | Qué pasa |
|---|---|---|
| **Permitido** | `go test`, `go vet`, `go build`, `gofmt`, `golangci-lint`, `govulncheck`, `npm run`, `npm test`, Playwright, `make`, `docker compose`, y de git: `status`, `diff`, `log`, `add`, `commit` | Lo ejecuta sin preguntar |
| **Pregunta** | `git push`, `npm install`, `go get` | Te pide confirmación cada vez |
| **Prohibido** | Leer `.env` y `secrets/`, `git push --force`, `rm -rf`, `docker compose down -v` | No puede hacerlo |

La lógica de cada grupo:

- **Lo permitido** es lo que el agente hace decenas de veces por tarea. Pedir confirmación cada vez solo entrenaría a aprobar sin mirar.
- **Lo que pregunta** tiene efectos fuera de tu máquina (subir código) o cambia las dependencias del proyecto, que deben estar justificadas en el plan.
- **Lo prohibido** es difícil o imposible de deshacer: borrar archivos, reescribir el historial compartido, borrar los datos de la base local, o exponer secretos.

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
| Formato | Se formatea solo al editar | El desarrollador ejecuta el formateador; el hook de git lo comprueba |
| Acceso por rol | Las herramientas de cada subagente | El modo de sandbox o los permisos de cada subagente |

El resultado final es el mismo: el cambio prohibido no entra al repositorio. La diferencia es cuándo se entera el agente.

## Cuando no funcionan

| Síntoma | Causa | Solución |
|---|---|---|
| El agente edita un archivo protegido sin que nada lo detenga | Los scripts no tienen permiso de ejecución, o falta `jq` | `make instalar-kit` repara el permiso. `jq` se instala según la página de [Instalación](instalacion.md) |
| El código no se formatea al editar | Falta `gofmt`, o no están instaladas las dependencias del frontend | Instala Go; ejecuta `cd frontend && npm ci` |
| El agente pide confirmación para todo | La configuración generada está desactualizada | `make sincronizar` y reinicia Claude Code |

Los hooks necesitan `jq` para leer qué archivo se va a editar. Sin `jq` no bloquean nada, y tampoco avisan. Por eso `make doctor` lo marca como requerido.

## Cambiarlos

Los hooks y los permisos están en `equipo/adaptadores/claude/`, y a partir de ahí se genera `.claude/settings.json`. Vienen del kit:

- **Un cambio para todos los proyectos** se hace en el repositorio del kit. Ver [Cómo contribuir](contribuir.md).
- **Un cambio propio del proyecto** requiere excluir `equipo/adaptadores/` del kit. Ver [Personalizar un proyecto](personalizar.md).

Después de cualquier cambio: `make sincronizar` y reiniciar Claude Code.

## Siguientes pasos

- [Hooks de git](hooks-de-git.md): la capa que aplica a todas las herramientas.
- [Capas de control](capas-de-control.md): cómo encaja esta capa con las demás.
- [Una fuente, varias herramientas](una-fuente-varias-herramientas.md): por qué cada herramienta tiene protecciones distintas.
