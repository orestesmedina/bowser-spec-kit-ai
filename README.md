# bowser-spec-kit-ai

Un kit para que un equipo de agentes de IA construya software con **React + TypeScript, Go y PostgreSQL**, siguiendo **Spec-Driven Development** con [Spec Kit](https://github.com/github/spec-kit): todo empieza por escrito, y las personas aprueban en los puntos clave.

**Funciona con Claude Code, Codex y OpenCode.** El proceso, las reglas y los roles se definen una sola vez; un script genera el formato que necesita cada herramienta.

> **[Documentación completa →](docs/README.md)**

## La idea en un minuto

La IA escribe casi todo el código, pero una persona es responsable del resultado. Para que eso sea seguro, el kit aporta tres cosas:

- **Un proceso.** Antes del código se escribe qué se construye (la especificación) y cómo (el plan). Una persona aprueba cada uno.
- **Un equipo.** Un orquestador coordina a diez especialistas: analista, arquitecto, diseñador, dos desarrolladores, QA, revisor, seguridad, DevOps y documentador. Quien escribe el código nunca lo aprueba.
- **Controles automáticos.** Hooks de git e integración continua que revisan cada cambio, sin depender de que alguien se acuerde ni de que el agente obedezca.

```
Idea
  └─► especificación ── ✋ aprueba una persona
        └─► plan técnico ── ✋ aprueba una persona
              └─► tareas ► implementación ► QA + revisión + seguridad
                    └─► Pull Request ── ✋ aprueba una persona
```

## Empezar

Requisitos: Git, `make`, `jq`, Docker, Go 1.26+, Node 24, Python 3.11+, [uv](https://docs.astral.sh/uv/) y al menos un agente de código. El detalle está en [Instalación](docs/instalacion.md); en Windows, lee antes [Windows y WSL](docs/windows-wsl.md).

```bash
# 1. Spec Kit, una vez por máquina
uv tool install specify-cli

# 2. El proyecto
mkdir mi-proyecto && cd mi-proyecto && git init
specify init --here --integration claude        # o codex, u opencode
git add . && git commit -m "chore: inicializa spec kit"

# 3. El kit, como submódulo
git submodule add https://github.com/orestesmedina/bowser-spec-kit-ai.git .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit

# 4. El entorno local
cp .env.example .env      # completa los valores
make up && make doctor
```

Después abre tu agente en la carpeta del proyecto y pídele lo que necesitas.

| Tu situación | Empieza por |
|---|---|
| Proyecto desde cero | [Crear un proyecto nuevo](docs/proyecto-nuevo.md) |
| Ya tienes un proyecto con código | [Integrar el kit en un proyecto existente](docs/proyecto-existente.md) |
| Te unes a un proyecto que ya usa el kit | [Unirse a un proyecto](docs/unirse-a-un-proyecto.md) |
| Quieres entender la idea primero | [Desarrollo guiado por especificaciones](docs/sdd.md) |

## Uso diario

| Quiero… | Hago |
|---|---|
| Construir una funcionalidad | Le pido al agente: "Construyamos esta funcionalidad: los clientes pueden registrarse con correo…" |
| Corregir un error | "Al editar un pedido se pierde la dirección" |
| Saber por dónde íbamos | `make estado`, o "¿por dónde quedamos?" |
| Comprobar mi entorno | `make doctor` |
| Saber si un cambio va a pasar en GitHub | `make ci` |
| Saber cuánto costó en IA | `make costos` |
| Actualizar el kit | `make actualizar-kit` |

Todos los comandos están en [Comandos](docs/comandos.md), y los errores frecuentes en [Problemas comunes](docs/problemas-comunes.md).

## Documentación

| Sección | Qué encuentras |
|---|---|
| [Primeros pasos](docs/README.md#primeros-pasos) | Instalación, proyectos nuevos y existentes, estructura y configuración |
| [Conceptos](docs/README.md#conceptos) | El proceso, el equipo de agentes, la constitución y cómo funciona el kit por dentro |
| [El flujo de trabajo](docs/README.md#el-flujo-de-trabajo) | De la idea al roadmap, funcionalidades, aprobaciones, bugs y cómo retomar |
| [Profundizando](docs/README.md#profundizando) | Roles, skills, modelos, costos y personalización |
| [Controles](docs/README.md#controles) | Hooks de git, hooks del agente, integración continua, cobertura |
| [Referencia](docs/README.md#referencia) | Comandos, problemas comunes, reglas de oro y glosario |

## Contribuir

Los cambios al kit se hacen en este repositorio y llegan a los proyectos con `make actualizar-kit`. Cada cambio se registra en [`CHANGELOG.md`](CHANGELOG.md). Cómo está organizado, cómo probar un cambio y cómo mantener tu propia copia: [Cómo contribuir](docs/contribuir.md).

Hacia dónde va el kit (cualquier tecnología, proyectos existentes, catálogo de skills abierto a contribuciones): [Hoja de ruta](HOJA-DE-RUTA.md).

## Licencia

[MIT](LICENSE) © Infinity Solutions AI. Puedes usar, modificar y distribuir el kit conservando el aviso de autoría. La licencia cubre el kit, no el código de los proyectos que lo usan.
