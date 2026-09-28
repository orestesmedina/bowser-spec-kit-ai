# Kit de desarrollo con IA — React + Go + PostgreSQL

Plantilla base para que un equipo de subagentes desarrolle software siguiendo **Spec-Driven Development** con **Spec Kit**, con humanos aprobando en los puntos clave.

**Funciona con Claude Code, Codex y OpenCode.** El proceso, las reglas y los roles se definen una sola vez; un script genera el formato que necesita cada herramienta.

> **¿Eres nuevo en el equipo?** Empieza por la [Guía de inicio](docs/GUIA-INICIO.md): instalación paso a paso, el flujo completo de desarrollo con checklists de aprobación, y solución de problemas comunes. Ejecuta `make doctor` para verificar tu entorno.

## Cómo está organizado

La idea central: **núcleo portable** (lo que ustedes editan) + **adaptadores generados** (lo que cada herramienta lee).

```
NÚCLEO PORTABLE — se edita a mano
├── AGENTS.md                        # Instrucciones del orquestador (estándar abierto)
├── .specify/memory/constitution.md  # Reglas no negociables
├── equipo/
│   ├── agentes/*.md                 # Los 10 roles en formato neutral
│   ├── config.json                  # Herramientas activas y modelo de cada agente
│   ├── MODELOS.md                   # Cómo elegir modelos por rol
│   └── adaptadores/claude/          # Permisos y hooks propios de Claude Code
├── .agents/skills/                  # Skills (estándar SKILL.md)
│   ├── go-backend/  react-frontend/  postgres-db/        ← convenciones del stack
│   └── equipo-feature/  equipo-revision/  equipo-bug/    ← flujos del equipo
├── .githooks/                       # Controles en cada commit (cualquier agente o humano)
└── .github/                         # CI y CODEOWNERS

ADAPTADORES — generados con `make sincronizar`, no editar
├── CLAUDE.md, .claude/              # Claude Code
├── .codex/agents/*.toml             # Codex
└── .opencode/agents/*.md            # OpenCode
```

### Qué lee cada herramienta

| | Claude Code | Codex | OpenCode |
|---|---|---|---|
| Instrucciones | `CLAUDE.md` → importa `AGENTS.md` | `AGENTS.md` | `AGENTS.md` |
| Subagentes | `.claude/agents/*.md` | `.codex/agents/*.toml` | `.opencode/agents/*.md` |
| Skills | `.claude/skills/` (copia) | `.agents/skills/` | `.agents/skills/` |
| Comandos Spec Kit | `/speckit.plan` | `$speckit-plan` | `/speckit.plan` |
| Hooks del agente | Sí (formateo y protección) | — | — |
| Hooks de git y CI | Sí | Sí | Sí |

## Los roles

Cada archivo en `equipo/agentes/` tiene este formato neutral:

```markdown
---
nombre: revisor-codigo
descripcion: Cuándo usar este agente…
acceso: lectura        # lectura | documentos | completo
nivel: alto            # alto | medio | bajo  → modelo según equipo/config.json
temperatura: 0.1       # opcional; valor por defecto del agente (0 a 2)
web: no                # si = puede buscar en internet
skills: go-backend     # opcional
---
Instrucciones del rol…
```

| Acceso | Significado | Claude Code | Codex | OpenCode |
|---|---|---|---|---|
| `lectura` | Solo lee y ejecuta comandos | sin Write/Edit | `read-only` | `edit: deny` |
| `documentos` | Escribe archivos, sin terminal | sin Bash | `workspace-write` | `bash: deny` |
| `completo` | Escribe y ejecuta | todo | `workspace-write` | todo |

Roles incluidos: `analista-producto`, `arquitecto`, `disenador-ux`, `dev-backend`, `dev-frontend`, `qa-tester`, `revisor-codigo`, `seguridad`, `devops`, `documentador`.

## Instalación (por cada proyecto nuevo)

Requisitos: Git, Docker, Go 1.23+, Node 22+, Python 3.11+ y [uv](https://docs.astral.sh/uv/), `jq`, y al menos uno de: Claude Code, Codex u OpenCode.

```bash
# 1. Instalar Spec Kit (una vez por máquina)
uv tool install specify-cli

# 2. Crear el proyecto e inicializar Spec Kit para cada herramienta que vayan a usar
mkdir mi-proyecto && cd mi-proyecto && git init
specify init --here --integration claude
specify init --here --force --integration codex      # opcional
specify init --here --force --integration opencode   # opcional

# 3. Copiar el kit ENCIMA (nuestra constitución reemplaza la plantilla de Spec Kit)
cp -r /ruta/a/kit-ia-dev/. .

# 4. Generar adaptadores y activar hooks de git
make sincronizar
make instalar-hooks

# 5. Entorno local
cp .env.example .env      # completar valores
make up

# 6. Primer commit
git add . && git commit -m "chore: estructura inicial del proyecto"
```

> Ejecuta `specify init` **antes** de copiar el kit. Verifica los nombres exactos de integración con `specify integration list`.

## Uso diario

Abre la herramienta en la carpeta del proyecto y pide lo que necesitas. Las skills se activan por su descripción, o puedes nombrarlas:

| Quiero… | Pide |
|---|---|
| Construir una funcionalidad | "Usa la skill equipo-feature: los clientes pueden registrarse con email…" |
| Revisar cambios | "Usa la skill equipo-revision" |
| Corregir un bug | "Usa la skill equipo-bug: al editar un pedido se pierde la dirección" |
| Una fase suelta de Spec Kit | `/speckit.specify`, `/speckit.plan`… (o `$speckit-…` en Codex) |

En Claude Code las skills también se pueden invocar como `/equipo-feature`.

## Un modelo distinto para cada agente

En `equipo/config.json` se elige el modelo por herramienta con tres niveles de detalle: el modelo del **orquestador**, un modelo por **nivel** (alto, medio, bajo) y **excepciones por agente**.

```json
"opencode": {
  "orquestador": "opencode-go/glm-5.3",
  "niveles": { "alto": "opencode-go/kimi-k3", "medio": "opencode-go/glm-5.3", "bajo": "opencode-go/glm-5.3-flash" },
  "agentes": { "dev-backend": "opencode-go/kimi-k2.7-code", "revisor-codigo": "opencode-go/deepseek-v4-pro" }
}
```

```bash
make sincronizar   # aplica los cambios
make modelos       # tabla de qué modelo usa cada agente
```

Criterios, límites de uso de OpenCode Go y advertencias de privacidad: [`equipo/MODELOS.md`](equipo/MODELOS.md).

## Cambiar de herramienta

1. Edita `equipo/config.json` → `"herramientas"` (por ejemplo `["codex"]`).
2. Completa los modelos de esa herramienta en `"modelos"` (vacío = usa el modelo de la sesión).
3. `make sincronizar` y commit.
4. Si no lo hiciste al inicio: `specify init --here --force --integration <herramienta>`.

Las specs, planes, tareas, skills y reglas no cambian. Al migrar, prueben una funcionalidad pequeña: cada modelo sigue instrucciones de forma algo distinta y puede requerir ajustes en los roles.

> Si activan Claude Code y OpenCode a la vez, OpenCode verá las skills dos veces (lee `.claude/skills/` y `.agents/skills/`). Son idénticas, así que no hay conflicto de contenido.

## Dónde intervienen los humanos

1. **Aprobar la spec** (`spec.md`): ¿es lo que el cliente pidió?
2. **Aprobar el plan** (`plan.md`): ¿la arquitectura tiene sentido?
3. **Aprobar el Pull Request y el despliegue a producción.**

## Capas de control

| Capa | Dónde | Protege contra | Portable |
|---|---|---|---|
| Instrucciones | `AGENTS.md`, roles, constitución | errores de criterio | Sí |
| Hooks del agente | `equipo/adaptadores/claude/hooks/` | errores en el momento de editar | Solo Claude Code |
| Hooks de git | `.githooks/` | secretos, migraciones editadas, formato, commits mal nombrados | Sí |
| CI | `.github/workflows/ci.yml` | todo lo anterior, aunque alguien use `--no-verify` | Sí |
| CODEOWNERS | `.github/CODEOWNERS` | cambios sin aprobación en reglas y agentes | Sí |

La protección real está en git y en CI. Los hooks del agente son una ayuda adicional.

## Cómo evolucionar el kit

- ¿Un error se repite? Agrégalo a la skill correspondiente o a la constitución.
- ¿Un rol nuevo? Crea `equipo/agentes/<rol>.md` y ejecuta `make sincronizar`.
- ¿Una nueva herramienta? Agrega una función `generar_<herramienta>` en `scripts/sincronizar.py`.
- ¿Algo nunca debe pasar? Agrégalo a `.githooks/pre-commit` y al CI.
