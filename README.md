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

> **Antes de empezar, prepara tu máquina con la sección 3 de la [Guía de inicio](docs/GUIA-INICIO.md#3-instalación-del-entorno).** Ahí está cómo instalar cada herramienta y cómo verificarlo con `make doctor`.
>
> **¿Usas Windows?** Lee primero la sección [3.1.1 — Windows: cómo funciona WSL](docs/GUIA-INICIO.md#311-windows-cómo-funciona-wsl-importante). Todo el desarrollo (herramientas, proyectos, agente de código y git) va **dentro de Ubuntu (WSL)**. Mezclarlo con Windows es la causa de la mayoría de los errores.

Requisitos: Git, `make`, `jq`, Docker, Go 1.26+, Node 24+, Python 3.11+ y [uv](https://docs.astral.sh/uv/), y al menos uno de: Claude Code, Codex u OpenCode.

El kit vive en su propio repositorio de GitHub y cada proyecto lo incluye como **submódulo de git** en `.bowser-spec-kit-ai/`. Así, cuando el kit mejora, cada proyecto se actualiza con un comando.

```bash
# 1. Instalar Spec Kit (una vez por máquina)
uv tool install specify-cli

# 2. Crear el proyecto e inicializar Spec Kit para cada herramienta que vayan a usar
mkdir mi-proyecto && cd mi-proyecto && git init
specify init --here --integration claude
specify init --here --force --integration codex      # opcional
specify init --here --force --integration opencode   # opcional
git add . && git commit -m "chore: inicializa spec kit"

# 3. Agregar el kit como submódulo e instalarlo
git submodule add git@github.com:<tu-org>/bowser-spec-kit-ai.git .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit

# 4. Entorno local
cp .env.example .env      # completar valores
make up
make doctor

# 5. Commit
git add . && git commit -m "chore: instala kit de desarrollo"
```

> Ejecuta `specify init` **antes** de instalar el kit: nuestra constitución reemplaza la plantilla de Spec Kit (queda un respaldo en `.kit-respaldo/`). Verifica los nombres de integración con `specify integration list`.

### Qué hace `make instalar-kit`

Las herramientas leen sus archivos en la raíz del proyecto, no dentro de `.bowser-spec-kit-ai/`. Por eso el comando:

1. **Copia a la raíz los archivos del kit** (`AGENTS.md`, roles, skills, hooks, CI, constitución, scripts, `Makefile`) y los registra con su hash en `.kit-manifest.json`.
2. **Copia las semillas** solo si no existen: `equipo/config.json`, `.github/CODEOWNERS`, `.env.example`, `docker-compose.yml`. Desde ese momento son del proyecto.
3. Agrega un bloque del kit a `.gitignore` sin tocar el resto.
4. Regenera la configuración de agentes (`make sincronizar`) y activa los hooks de git.

### Actualizar el kit en un proyecto

```bash
make actualizar-kit       # trae la última versión de .bowser-spec-kit-ai/, instala y muestra las novedades
make actualizar-modelos   # (si lo avisa) aplica los modelos recomendados por el kit
git add . && git commit -m "chore: actualiza kit de desarrollo"
```

`equipo/config.json` es del proyecto, así que `make actualizar-kit` no cambia los modelos: solo avisa si el kit recomienda otros. `make actualizar-modelos` muestra las diferencias y, si confirmas, copia únicamente la asignación de modelos (`orquestador`, `ligero`, `niveles`, `agentes`) y regenera `.opencode/`, `.claude/` y `.codex/`. El resto de tu configuración se conserva. Con `SI=1` aplica sin preguntar.

- Reemplaza los archivos que cambiaron, agrega los nuevos y **borra los que el kit eliminó**.
- **Si alguien modificó localmente un archivo del kit, se detiene** y lo muestra, sin pisar nada. Opciones: llevar ese cambio al repositorio del kit, marcar el archivo como propio del proyecto, o descartarlo con `make instalar-kit FORZAR=1` (guarda respaldo).
- `make verificar-kit` comprueba que la raíz coincida con `.bowser-spec-kit-ai/`. El hook de git y el CI hacen la misma comprobación, así que un archivo del kit editado a mano no llega a `main`.

### Archivos propios de un proyecto

- **Una versión propia de un archivo del kit:** agrégalo a `"kit.excluir"` en `equipo/config.json` (una carpeta termina en `/`). El kit deja de tocarlo.
- **Skills o roles adicionales:** crea carpetas nuevas en `.agents/skills/` o archivos nuevos en `equipo/agentes/`. Lo que no viene del kit nunca se toca.
- **Comandos de `make` propios:** créalos en `proyecto.mk`, que el `Makefile` incluye automáticamente.

### Empezar un proyecto desde una idea

Usa la plantilla `docs/plantillas/idea.md` y sigue la sección "De la idea a la primera funcionalidad" de la [Guía de inicio](docs/GUIA-INICIO.md).

### Clonar un proyecto existente

```bash
git clone --recursive git@github.com:<tu-org>/<proyecto>.git
# si ya clonaste sin --recursive:
git submodule update --init
```

Si el repositorio del kit es privado, el CI necesita un secreto `KIT_TOKEN` con permiso de lectura sobre el kit.

### Alternativa sin submódulo

Si un proyecto no puede usar submódulos, se puede copiar el kit a mano (`cp -r bowser-spec-kit-ai/. .`, luego `make sincronizar` y `make instalar-hooks`). En ese caso no hay actualizaciones automáticas.

## Uso diario

Abre la herramienta en la carpeta del proyecto y pide lo que necesitas. Las skills se activan por su descripción, o puedes nombrarlas:

| Quiero… | Pide |
|---|---|
| Construir una funcionalidad | "Usa la skill equipo-feature: los clientes pueden registrarse con email…" |
| Revisar cambios | "Usa la skill equipo-revision" |
| Corregir un bug | "Usa la skill equipo-bug: al editar un pedido se pierde la dirección" |
| Regenerar código generado (sqlc, tipos de la API) | `make generar`; `make verificar-generados` comprueba que esté al día |
| Ver la cobertura de la capa de servicio | `make cobertura` (el CI exige 80 %) |
| Saber cuánto costó en IA | `make costos` (tarea actual) o `make costos TODO=1` (proyecto) |
| Saber por dónde íbamos | `make estado` en la terminal, o "¿por dónde quedamos?" al orquestador (skill equipo-retomar) |
| Una fase suelta de Spec Kit | `/speckit.specify`, `/speckit.plan`… (o `$speckit-…` en Codex) |

En Claude Code las skills también se pueden invocar como `/equipo-feature`.

### Estado del trabajo

Nada depende de la memoria de una sesión. El orquestador mantiene dos archivos versionados en git:

- `docs/producto/roadmap.md` — cada funcionalidad con su estado: pendiente, en curso, en revisión, terminada o pausada (plantilla `docs/plantillas/roadmap.md`).
- `specs/<rama>/estado.md` — fase, aprobaciones (quién y cuándo), ciclo de corrección, hallazgos abiertos, decisiones del chat y próximo paso (plantilla `docs/plantillas/estado.md`).

Al abrir una sesión, el orquestador revisa ambos y te dice dónde quedaron.

### Costo de IA por funcionalidad

`make costos` registra cuántos tokens gastó cada agente con cada modelo y su costo **equivalente** en dólares, en `specs/<rama>/costos.json` (versionado: suma el trabajo de todo el equipo). Lo ejecuta el orquestador al iniciar y al cerrar cada sesión.

- **Precios:** salen de [models.dev](https://models.dev), el catálogo que usa OpenCode. Cada tarea guarda su propio historial de precios: si un precio cambia, se **agrega** una versión nueva con su fecha, y cada respuesta se valoriza con el precio vigente cuando ocurrió (incluida la tarifa de hora pico de DeepSeek).
- **Cierre:** cuando apruebas el PR, `make costos CERRAR=1` congela el costo. El pre-commit bloquea cualquier cambio posterior a un `costos.json` cerrado.
- **Reportes:** `make costos` (tarea actual), `make costos TODO=1` (proyecto completo, por funcionalidad, agente y modelo), `make costos PRECIOS=hoy` (cuánto costaría hoy, para cotizar; no guarda nada).

Con una suscripción (OpenCode Go) no pagas por token: el dólar es lo que costaría ese consumo a precio de API, y tu gasto real es el % de la consola. Hoy registra sesiones de OpenCode. `make estado` muestra lo mismo en la terminal y avisa si el estado no cuadra con los archivos o con git. El pre-commit avisa (sin bloquear) cuando cambian spec, plan o tareas sin actualizar `estado.md`.

## Un modelo distinto para cada agente

En `equipo/config.json` se elige el modelo por herramienta con tres niveles de detalle: el modelo del **orquestador**, un modelo por **nivel** (alto, medio, bajo) y **excepciones por agente**.

```json
"opencode": {
  "orquestador": "opencode-go/deepseek-v4.1-flash",
  "niveles": { "alto": "opencode-go/mimo-v2.6-pro", "medio": "opencode-go/glm-5.3-flash", "bajo": "opencode-go/mimo-v2.6-flash" },
  "agentes": { "dev-backend": "opencode-go/deepseek-v4.1-flash", "revisor-codigo": "opencode-go/mimo-v2.6-pro" }
}
```

```bash
make sincronizar   # aplica los cambios
make modelos       # tabla de qué modelo usa cada agente
make actualizar-modelos   # adopta los modelos que recomienda la versión actual del kit
```

Criterios, cómo funciona el presupuesto de OpenCode Go, rendimiento de cada modelo, horario pico de DeepSeek y privacidad: [`equipo/MODELOS.md`](equipo/MODELOS.md).

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

Para trabajar el kit con Claude Code, ábrelo en la carpeta del kit (dentro de Ubuntu/WSL): `CLAUDE.md` le carga [`MANTENER-KIT.md`](MANTENER-KIT.md), con el contexto, las decisiones de diseño y las reglas para cambiarlo.

**Todo cambio al kit se registra en [`CHANGELOG.md`](CHANGELOG.md)** y sube la versión en `VERSION`:

1. Agrega la entrada en `CHANGELOG.md` (Agregado / Cambiado / Corregido y, si un proyecto debe hacer algo a mano, **Al actualizar**).
2. Sube `VERSION`: parche (1.6.1) para correcciones, menor (1.7.0) para funciones nuevas, mayor (2.0.0) si los proyectos deben hacer algo a mano para seguir funcionando.
3. Commit y etiqueta: `git commit -m "feat: …" && git tag v1.7.0 && git push --follow-tags`.

En los proyectos, `make actualizar-kit` muestra al terminar las novedades entre la versión que tenían y la nueva (con los pasos manuales al final), y `make novedades` muestra el historial cuando quieras.

- ¿Un error se repite? Agrégalo a la skill correspondiente o a la constitución.
- ¿Un rol nuevo? Crea `equipo/agentes/<rol>.md` y ejecuta `make sincronizar`.
- ¿Una nueva herramienta? Agrega una función `generar_<herramienta>` en `scripts/sincronizar.py`.
- ¿Algo nunca debe pasar? Agrégalo a `.githooks/pre-commit` y al CI.
