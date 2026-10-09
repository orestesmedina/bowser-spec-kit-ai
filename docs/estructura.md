# Estructura de carpetas

- [Introducción](#introducción)
- [Vista general](#vista-general)
- [Las cuatro clases de archivos](#las-cuatro-clases-de-archivos)
- [Carpeta por carpeta](#carpeta-por-carpeta)
    - [Instrucciones y reglas](#instrucciones-y-reglas)
    - [El equipo](#el-equipo)
    - [Controles](#controles)
    - [El trabajo del producto](#el-trabajo-del-producto)
    - [El código](#el-código)
    - [El kit](#el-kit)
    - [Archivos generados](#archivos-generados)
- [Qué puedes editar](#qué-puedes-editar)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Un proyecto con el kit instalado tiene bastantes archivos que no son código del producto. Esta página explica qué es cada uno, quién lo escribe y si se puede editar.

## Vista general

```
mi-proyecto/
├── AGENTS.md                        # Instrucciones del orquestador
├── .specify/memory/constitution.md  # Reglas no negociables del código
├── equipo/
│   ├── orquestador.md               # Manual de trabajo del orquestador
│   ├── agentes/*.md                 # Los 11 roles, sin tecnología
│   ├── comandos/*.md                # Comandos del chat (/bowser-status…)
│   ├── config.json                  # Herramientas activas y modelo de cada agente
│   ├── perfil.json                  # Partes del proyecto y comando de cada verbo (opcional)
│   └── adaptadores/claude/          # Permisos y hooks propios de Claude Code
├── .agents/skills/                  # Skills: flujos del equipo y las de tecnología que pide el perfil
├── .githooks/                       # Controles en cada commit
├── .github/
│   ├── workflows/ci.yml             # Integración continua
│   └── CODEOWNERS                   # Quién aprueba los cambios a las reglas
├── scripts/                         # Los programas detrás de los comandos make
├── Makefile                         # Comandos del kit
├── proyecto.mk                      # Comandos propios del proyecto (opcional)
├── tools/                           # Scripts propios del proyecto para los verbos del perfil (opcional)
│
├── docs/
│   ├── producto/idea.md             # La idea del producto
│   ├── producto/roadmap.md          # Funcionalidades y su estado
│   └── plantillas/                  # Plantillas de idea, roadmap y estado
├── specs/<NNN-funcionalidad>/       # Una carpeta por funcionalidad
│
├── backend/                         # Go
├── frontend/                        # React + TypeScript
├── docker-compose.yml               # PostgreSQL local
├── .env.example                     # Variables de entorno, sin valores reales
│
├── .bowser-spec-kit-ai/             # El kit (submódulo de git)
├── .kit-manifest.json               # Qué archivos vienen del kit
│
└── CLAUDE.md, .claude/, .codex/, .opencode/, opencode.json   # Generados
```

## Las cuatro clases de archivos

Todo archivo que no es código del producto pertenece a una de estas clases. Saber a cuál pertenece responde la pregunta "¿puedo editarlo?".

| Clase | Qué son | Quién los cambia |
|---|---|---|
| **Del kit** | Vienen del submódulo y están listados en `.kit-manifest.json` | Nadie en el proyecto. Se actualizan con `make actualizar-kit` |
| **Semillas** | El kit los copia una sola vez; después son del proyecto | El equipo del proyecto |
| **Generados** | Los produce `make sincronizar` a partir de otros archivos | Nadie a mano. Se cambia la fuente y se regeneran |
| **Del proyecto** | Todo lo demás: especificaciones, documentos, código | El equipo y los agentes |

## Carpeta por carpeta

### Instrucciones y reglas

| Archivo | Qué es | Clase |
|---|---|---|
| `AGENTS.md` | Lo primero que lee el agente al abrir el proyecto: su papel, el stack, el proceso y las reglas de coordinación. Ver [El orquestador](el-orquestador.md) | Del kit |
| `equipo/orquestador.md` | El manual de trabajo completo del orquestador | Del kit |
| `.specify/memory/constitution.md` | Las reglas que todo el código debe cumplir. Ver [La constitución](la-constitucion.md) | Del kit |

### El equipo

| Archivo | Qué es | Clase |
|---|---|---|
| `equipo/agentes/*.md` | Un archivo por rol: qué hace, qué puede tocar y qué entrega. Ver [Roles](roles.md) | Del kit |
| `.agents/skills/` | Conocimiento reutilizable: cómo ejecutar cada flujo y cómo escribir código en las tecnologías del proyecto. Las de tecnología llegan del catálogo del kit según el perfil. Ver [Skills](skills.md). Las carpetas `bowser-*` son generadas (comandos para Codex) | Del kit |
| `equipo/comandos/*.md` | Un archivo por comando del chat. Ver [Comandos](comandos.md#dentro-de-la-herramienta) | Del kit |
| `equipo/config.json` | Qué herramientas usa el equipo y qué modelo usa cada agente. Ver [Configuración](configuracion.md) | Semilla |
| `equipo/adaptadores/claude/` | Permisos y [hooks del agente](hooks-del-agente.md) para Claude Code | Del kit |

### Controles

| Archivo | Qué es | Clase |
|---|---|---|
| `.githooks/` | Revisan cada commit. Ver [Hooks de git](hooks-de-git.md) | Del kit |
| `.github/workflows/ci.yml` | Lo que GitHub revisa en cada Pull Request. Ver [Integración continua](integracion-continua.md) | Del kit |
| `.github/CODEOWNERS` | Quién debe aprobar los cambios a las reglas y a los agentes | Semilla |
| `scripts/` | Los programas que ejecutan los comandos `make` | Del kit |
| `Makefile` | La lista de [comandos](comandos.md) del kit | Del kit |
| `proyecto.mk` | Comandos `make` propios del proyecto. El `Makefile` lo incluye si existe | Del proyecto |

### El trabajo del producto

| Archivo | Qué es | Quién lo escribe |
|---|---|---|
| `docs/producto/idea.md` | El problema, los usuarios y lo mínimo que debe hacer el producto | Una persona, sin IA |
| `docs/producto/roadmap.md` | Las funcionalidades en orden, con el estado de cada una | Lo propone el orquestador; una persona decide el orden y el alcance |
| `specs/<NNN-nombre>/spec.md` | Qué se construye y por qué | El analista de producto |
| `specs/<NNN-nombre>/plan.md`, `data-model.md`, `contracts/` | Cómo se construye | El arquitecto |
| `specs/<NNN-nombre>/ux.md` | Pantallas, flujos y estados | El diseñador UX |
| `specs/<NNN-nombre>/tasks.md` | La lista de tareas | El arquitecto |
| `specs/<NNN-nombre>/revision-<fecha>.md` | Los reportes de validación | QA, revisor y seguridad |
| `specs/<NNN-nombre>/estado.md` | Fase, aprobaciones, hallazgos y próximo paso | El orquestador |
| `specs/<NNN-nombre>/costos.json` | Tokens y costo de IA por agente y modelo | Solo `make costos`. Nunca a mano |
| `docs/plantillas/` | Plantillas de idea, roadmap y estado | Del kit |

### El código

| Carpeta | Qué contiene |
|---|---|
| `backend/` | Go. Su organización interna está en la skill `go-backend` |
| `backend/migrations/` | Los cambios de esquema de la base de datos, numerados |
| `backend/api/openapi.yaml` | El contrato de la API |
| `frontend/` | React + TypeScript. Su organización interna está en la skill `react-frontend` |
| `docker-compose.yml` | PostgreSQL para desarrollo local (semilla) |
| `.env.example` | Las variables de entorno que necesita el proyecto, sin valores reales (semilla) |
| `.env` | Los valores reales. Nunca se sube a git |

### El kit

| Archivo | Qué es |
|---|---|
| `.bowser-spec-kit-ai/` | El kit completo, como submódulo de git. Incluye esta documentación |
| `.kit-manifest.json` | La lista de archivos que vienen del kit, con la versión instalada |
| `.kit-respaldo/` | Copias de archivos que una instalación reemplazó. No se sube a git |

Cómo funciona esto por dentro está en [El kit como submódulo](submodulo.md).

### Archivos generados

`CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/` y `opencode.json` son la traducción de los roles y las skills al formato que lee cada herramienta. Los produce `make sincronizar`. Ver [Una fuente, varias herramientas](una-fuente-varias-herramientas.md).

## Qué puedes editar

| Archivo | ¿Lo editas? |
|---|---|
| `specs/`, `docs/producto/`, `backend/`, `frontend/`, `proyecto.mk` | Sí. Es el trabajo de todos los días |
| `equipo/config.json`, `.github/CODEOWNERS`, `docker-compose.yml`, `.env.example` | Sí, con el acuerdo de quien lidera el proyecto |
| Archivos del kit | No. El cambio se propone en el repositorio del kit, o el archivo se marca como propio. Ver [Personalizar un proyecto](personalizar.md) |
| Archivos generados | Nunca. Cambia la fuente y ejecuta `make sincronizar` |
| `specs/**/costos.json` | Nunca. Lo escribe `make costos` |
| `.env` | Solo en tu máquina. Nunca se sube |

Estas reglas no dependen de la memoria de nadie: las hacen cumplir los [hooks de git](hooks-de-git.md) y la [integración continua](integracion-continua.md).

## Siguientes pasos

- [Configuración](configuracion.md): los archivos que sí se ajustan en cada proyecto.
- [El kit como submódulo](submodulo.md): cómo llegan los archivos del kit al proyecto.
- [Una fuente, varias herramientas](una-fuente-varias-herramientas.md): por qué existen los archivos generados.
