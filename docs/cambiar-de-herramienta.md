# Cambiar de herramienta

- [Introducción](#introducción)
- [Qué cambia y qué no](#qué-cambia-y-qué-no)
- [Pasos](#pasos)
- [Usar varias herramientas a la vez](#usar-varias-herramientas-a-la-vez)
- [Diferencias que vas a notar](#diferencias-que-vas-a-notar)
- [Después de cambiar](#después-de-cambiar)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit funciona con Claude Code, Codex y OpenCode. Cambiar de una a otra, o agregar una segunda, es editar una línea y ejecutar un comando: los roles, las reglas y el trabajo hecho son los mismos.

## Qué cambia y qué no

| No cambia | Cambia |
|---|---|
| Las especificaciones, los planes y las tareas | Los archivos generados de cada herramienta |
| Los roles y las skills | Los modelos disponibles |
| La constitución | Cómo se escriben los comandos de Spec Kit |
| Los hooks de git y la integración continua | Algunas protecciones propias de cada herramienta |
| El estado del trabajo (`estado.md`, roadmap) | |

Por eso se puede cambiar de herramienta a mitad de una funcionalidad: la nueva lee el mismo `estado.md` y continúa desde la misma fase.

## Pasos

1. **Edita `equipo/config.json`** y deja en `"herramientas"` las que vayas a usar:
   ```json
   "herramientas": ["codex"]
   ```
2. **Completa los modelos de esa herramienta** en `"modelos"`. Un valor vacío significa "usa el modelo de la sesión". Ver [Modelos por agente](modelos.md).
3. **Regenera y guarda:**
   ```bash
   make sincronizar
   make modelos
   git add . && git commit -m "chore: cambia la herramienta a codex"
   ```
4. **Inicializa Spec Kit para la herramienta nueva,** si no lo habías hecho:
   ```bash
   specify init --here --force --integration codex
   ```
5. **Instala la herramienta** en cada máquina del equipo. Ver [Instalación](instalacion.md#el-agente-de-código).

## Usar varias herramientas a la vez

Un equipo puede tener a una persona con Claude Code y a otra con OpenCode sobre el mismo proyecto. Basta con dejar las dos en `"herramientas"`: `make sincronizar` genera la configuración de ambas.

Lo que comparten es todo lo importante: el proceso, las reglas, el estado y los controles de git.

> [!NOTE]
> Si activas Claude Code y OpenCode a la vez, OpenCode ve las skills dos veces, porque lee `.claude/skills/` y `.agents/skills/`. Son idénticas, así que no hay conflicto.

## Diferencias que vas a notar

| | Claude Code | Codex | OpenCode |
|---|---|---|---|
| Comandos de Spec Kit | `/speckit-plan` | `$speckit-plan` | `/speckit.plan` |
| El orquestador | La sesión principal | La sesión principal | Un agente llamado `orquestador`, abierto por defecto |
| Modelo del orquestador | Se configura | Se elige al iniciar la sesión | Se configura |
| [Hooks del agente](hooks-del-agente.md) | Sí | No | No |
| Temperatura por agente | No | No | Sí |
| [Costos de IA](costos.md) | No se registran | No se registran | Sí |

La diferencia que más importa es la de los hooks del agente. Solo Claude Code impide que el agente edite un archivo protegido en el momento. En Codex y OpenCode esa protección llega un paso después, en el commit, con los [hooks de git](hooks-de-git.md). El resultado final es el mismo: el cambio no entra.

## Después de cambiar

Cada modelo sigue las instrucciones de forma algo distinta. Lo que un modelo hace bien con una frase corta, otro puede necesitarlo más explícito.

Antes de usar la herramienta nueva para trabajo real:

1. **Construye una funcionalidad pequeña** de principio a fin.
2. **Fíjate** en si el orquestador delega o hace el trabajo él mismo, en si respeta las puertas de aprobación y en cuántos ciclos de corrección necesita.
3. **Si algo falla de forma consistente,** el ajuste suele ir en el rol o en la skill correspondiente.

## Siguientes pasos

- [Una fuente, varias herramientas](una-fuente-varias-herramientas.md): cómo funciona el generador.
- [Modelos por agente](modelos.md): elegir los modelos de la herramienta nueva.
- [Configuración](configuracion.md).
