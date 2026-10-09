# Una fuente, varias herramientas

- [Introducción](#introducción)
- [El problema que resuelve](#el-problema-que-resuelve)
- [Fuentes y archivos generados](#fuentes-y-archivos-generados)
- [Qué lee cada herramienta](#qué-lee-cada-herramienta)
- [Cómo se traduce un rol](#cómo-se-traduce-un-rol)
- [Cómo se traduce un comando](#cómo-se-traduce-un-comando)
- [Regenerar](#regenerar)
- [Cómo se mantiene al día](#cómo-se-mantiene-al-día)
- [Lo que no es igual en todas las herramientas](#lo-que-no-es-igual-en-todas-las-herramientas)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit funciona con tres agentes de código: Claude Code, Codex y OpenCode. Cada uno espera su configuración en un lugar y en un formato distintos. En vez de mantener tres copias de todo, el kit define los roles y las reglas **una sola vez** y genera a partir de ahí lo que necesita cada herramienta.

## El problema que resuelve

Sin un generador, cambiar una línea en las instrucciones de un rol obliga a cambiarla en tres archivos con tres formatos. Tarde o temprano alguien olvida uno, y el mismo rol se comporta distinto según la herramienta que use cada persona.

Con una sola fuente:

- **Cambiar de herramienta no obliga a reescribir nada.** Las especificaciones, los planes, las skills y las reglas son los mismos.
- **Un equipo puede usar varias herramientas a la vez** con el mismo comportamiento.
- **Hay un solo lugar donde mirar** cuando un agente hace algo inesperado.

## Fuentes y archivos generados

| Fuentes: se editan | Generados: nunca se editan |
|---|---|
| `AGENTS.md` | `CLAUDE.md` |
| `equipo/orquestador.md` | `.claude/agents/`, `.claude/skills/`, `.claude/settings.json` |
| `equipo/agentes/*.md` | `.codex/agents/*.toml`, `.agents/skills/bowser-*/` |
| `equipo/comandos/*.md` | `.opencode/agents/*.md`, `.opencode/commands/*.md` |
| `equipo/config.json` | `opencode.json` |
| `.agents/skills/` (menos las carpetas `bowser-*`) | |
| `equipo/adaptadores/` | |

Cada archivo generado empieza con un aviso que dice de qué fuente salió y que no se edita.

> [!NOTE]
> Spec Kit guarda sus comandos dentro de dos de esas carpetas: `.claude/skills/speckit-*/` y `.opencode/commands/speckit.*.md`. No son del kit: `make sincronizar` no los borra ni los cambia, y `make verificar-agentes` no los cuenta. Todo lo demás que haya en las carpetas generadas sí se borra.

## Qué lee cada herramienta

| | Claude Code | Codex | OpenCode |
|---|---|---|---|
| Instrucciones | `CLAUDE.md`, que importa `AGENTS.md` | `AGENTS.md` | `AGENTS.md` |
| Subagentes | `.claude/agents/*.md` | `.codex/agents/*.toml` | `.opencode/agents/*.md` |
| Skills | `.claude/skills/` (una copia) | `.agents/skills/` | `.agents/skills/` |
| Comandos del kit | `.claude/skills/bowser-*/` | `.agents/skills/bowser-*/` | `.opencode/commands/bowser-*.md` |
| Comandos de Spec Kit | `/speckit-plan` | `$speckit-plan` | `/speckit.plan` |
| Hooks del agente | Sí | No | No |
| Hooks de git e integración continua | Sí | Sí | Sí |

`AGENTS.md` es un estándar abierto que Codex y OpenCode leen directamente; por eso no necesita traducción para ellos.

## Cómo se traduce un rol

Un rol se escribe en un formato neutral, sin nombrar ninguna herramienta ni ningún modelo:

```markdown
---
nombre: revisor-codigo
descripcion: Usar después de cada implementación para revisar calidad…
acceso: lectura
nivel: alto
temperatura: 0.1
web: no
---
Eres el revisor de código del equipo…
```

El generador convierte cada campo en lo que entiende cada herramienta:

| Campo neutral | Claude Code | Codex | OpenCode |
|---|---|---|---|
| `acceso: lectura` | Sin las herramientas de escritura | `sandbox_mode = "read-only"` | `edit: deny` |
| `acceso: documentos` | Sin la terminal | `workspace-write` | `bash: deny` |
| `acceso: completo` | Todas las herramientas | `workspace-write` | Todo permitido |
| `nivel: alto` | El modelo configurado para ese nivel | El esfuerzo de razonamiento | El modelo configurado para ese nivel |
| `web: si` | Agrega las herramientas de búsqueda | — | `webfetch: allow` |
| `temperatura` | No aplica | No aplica | Se envía al modelo |

Qué modelo corresponde a cada nivel no está en el rol, sino en `equipo/config.json`. Así, cambiar de modelo no obliga a tocar ningún rol. Ver [Modelos por agente](modelos.md).

## Cómo se traduce un comando

Un comando es lo que una persona escribe en el chat para pedir algo concreto, como `/bowser-status`. Se escribe una vez en `equipo/comandos/`, en un archivo con el nombre del comando sin el prefijo:

```markdown
---
nombre: status
descripcion: Muestra por dónde va el proyecto y cuál es el próximo paso (make estado).
argumentos: [todo]
---
Ejecuta `make estado` en la raíz del proyecto…
```

`argumentos` es opcional: es la pista de qué se puede escribir después del nombre. El generador agrega el prefijo `bowser-` y produce:

| Herramienta | Archivo generado | Cómo se invoca | Se carga |
|---|---|---|---|
| Claude Code | `.claude/skills/bowser-status/SKILL.md` | `/bowser-status` | Solo cuando la persona lo escribe |
| Codex | `.agents/skills/bowser-status/` | `$bowser-status` | Solo cuando la persona lo escribe |
| OpenCode | `.opencode/commands/bowser-status.md` | `/bowser-status` | Al escribirlo |

En Claude Code y Codex un comando propio es una skill con la invocación automática desactivada (`disable-model-invocation` y `allow_implicit_invocation: false`): así no ocupa contexto hasta que se usa.

> [!WARNING]
> Codex solo lee skills de `.agents/skills/`, que es una carpeta de fuentes. Por eso sus comandos se generan ahí mismo, en carpetas que empiezan con `bowser-`. Esas carpetas son generadas: `make sincronizar` las borra y las vuelve a crear. No pongas una skill propia en una carpeta con ese prefijo.

Lista de comandos y cómo usarlos: [Comandos](comandos.md#dentro-de-la-herramienta).

## Regenerar

Después de cambiar cualquier fuente:

```bash
make sincronizar
```

Para ver el resultado sin leer los archivos generados:

```bash
make modelos
```

Muestra, para cada herramienta activa, qué modelo y qué temperatura usa cada agente y de dónde sale cada valor.

Después de regenerar, reinicia el agente de código: la mayoría lee su configuración solo al arrancar.

## Cómo se mantiene al día

Olvidar `make sincronizar` dejaría a los agentes trabajando con instrucciones viejas. Tres controles lo impiden:

| Control | Cuándo |
|---|---|
| El [hook de git](hooks-de-git.md) | Bloquea el commit si cambió una fuente y los generados no están al día |
| La [integración continua](integracion-continua.md) | Repite la comprobación en cada Pull Request |
| `make doctor` | Lo muestra entre los problemas del proyecto |

La comprobación se puede ejecutar a mano:

```bash
make verificar-agentes
```

> [!WARNING]
> Nunca edites un archivo generado para "arreglar algo rápido". El próximo `make sincronizar` borra el cambio, y mientras tanto el hook de git rechaza los commits. Cambia la fuente.

## Lo que no es igual en todas las herramientas

El kit iguala todo lo que puede, pero las herramientas no ofrecen lo mismo:

| Diferencia | Detalle |
|---|---|
| Hooks del agente | Solo existen en Claude Code. En Codex y OpenCode, esa protección la dan los hooks de git y la integración continua. Ver [Hooks del agente](hooks-del-agente.md) |
| Temperatura por subagente | Solo OpenCode permite fijarla |
| Agente principal | En OpenCode, el orquestador es un agente con nombre que se abre por defecto. En Claude Code y Codex es la sesión principal |
| Modelo del orquestador | En Codex se elige al iniciar la sesión; en las otras dos se configura |
| Costos de IA | Hoy `make costos` registra solo las sesiones de OpenCode |

Además, cada modelo sigue las instrucciones de forma algo distinta. Al cambiar de herramienta o de modelo conviene probar con una funcionalidad pequeña.

## Siguientes pasos

- [Cambiar de herramienta](cambiar-de-herramienta.md): los pasos para pasar de un agente de código a otro.
- [Roles](roles.md): el formato neutral, campo por campo.
- [Modelos por agente](modelos.md): cómo se decide el modelo de cada rol.
