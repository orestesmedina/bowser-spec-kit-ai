# El orquestador

- [Introducción](#introducción)
- [Qué hace y qué no hace](#qué-hace-y-qué-no-hace)
- [Cómo hablarle](#cómo-hablarle)
- [Al abrir y al cerrar una sesión](#al-abrir-y-al-cerrar-una-sesión)
- [Sus prioridades](#sus-prioridades)
- [Lo que nunca hace](#lo-que-nunca-hace)
- [Cuando le pides saltarse el proceso](#cuando-le-pides-saltarse-el-proceso)
- [Cómo se comunica](#cómo-se-comunica)
- [De dónde salen sus instrucciones](#de-dónde-salen-sus-instrucciones)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El orquestador es el agente con el que hablas. Funciona como un jefe de proyecto: entiende lo que pides, decide qué flujo corresponde, reparte el trabajo entre los [especialistas](equipo-de-agentes.md) y lleva la cuenta de en qué va cada cosa.

## Qué hace y qué no hace

| Hace | No hace |
|---|---|
| Decide qué flujo aplicar según lo que pides | Escribir código de producción |
| Ejecuta las fases de Spec Kit y delega cada una | Aprobar en nombre de una persona |
| Se detiene en cada puerta de aprobación | Inventar reglas de negocio |
| Mantiene `estado.md` y el roadmap al día | Saltarse un control porque "es más rápido" |
| Registra el costo de IA de cada funcionalidad | Editar los archivos del kit o la constitución |

## Cómo hablarle

Con naturalidad. No hace falta conocer los comandos ni los nombres de los flujos: el orquestador decide cuál aplicar.

| Si le dices… | Hace esto |
|---|---|
| "Construyamos la funcionalidad 2 del roadmap", "agrega exportar a Excel" | El flujo completo de [funcionalidad](funcionalidad.md) |
| "Al editar un pedido se pierde la dirección" | El flujo de [bug](bugs.md): diagnóstico, prueba que falla, arreglo mínimo, revisión |
| "Revisa estos cambios", "revisa este PR" | La validación con QA, revisión y seguridad |
| "Cambia el texto del botón Enviar por Crear cuenta" | Un [cambio pequeño](cambios-pequenos.md): lo delega directo y luego lo valida |
| "¿Por dónde quedamos?", "retomemos" | [Retoma el trabajo](retomar.md) a partir de los archivos y de git |
| "Lo dejamos por hoy" | Cierra la sesión: actualiza el estado y lo guarda |
| "¿Cómo funciona X?" | Responde, y cita el archivo donde está |
| Algo ambiguo | Pregunta antes de actuar |

La línea entre "cambio pequeño" y "funcionalidad" la tiene clara: **no es pequeño** si cambia comportamiento, datos, la API, permisos o seguridad.

## Al abrir y al cerrar una sesión

Las sesiones se pierden; el estado del trabajo no. Por eso el orquestador hace lo mismo cada vez:

**Al abrir**, antes de responder cualquier cosa, ejecuta `make estado` y `make costos`, y empieza con dos a cuatro líneas:

```
Quedamos en: 003-registro-usuarios · Fase 6/9 (implementar) · 7/12 tareas
Aprobados: spec y plan · Hallazgos abiertos: 0
Próximo paso: T008 [frontend] formulario de registro → dev-frontend. ¿Sigo?
```

**Al cerrar**, ejecuta `make costos`, anota en `estado.md` el próximo paso concreto y guarda todo en un commit. Si quedan cambios de código sin guardar, te lo dice en lugar de hacer commit de trabajo a medias.

## Sus prioridades

En este orden:

1. Respetar el proceso y los controles.
2. Entregar lo que pediste.
3. Hacerlo rápido.

El orden importa. Cuando la velocidad choca con el proceso, gana el proceso, y el orquestador te explica por qué.

## Lo que nunca hace

1. Saltarse una puerta de aprobación, o darla por hecha.
2. Escribir código de producción sin especificación y plan aprobados (salvo cambios pequeños).
3. Usar por su cuenta `git commit --no-verify`, `git push --force`, `APROBADO_CONSTITUCION=1`, `APROBADO_COSTOS=1` o `make instalar-kit FORZAR=1`. Son decisiones de una persona.
4. Editar archivos generados, archivos del kit, la constitución, `.env` o secretos.
5. Debilitar o desactivar una prueba para que pase.
6. Inventar reglas de negocio. Si la especificación es ambigua, pregunta.
7. Desplegar a producción o integrar un Pull Request sin aprobación.
8. Registrar en `estado.md` una aprobación que nadie dio explícitamente.
9. Editar `costos.json` a mano, o cerrar el costo de una funcionalidad antes de que se apruebe su Pull Request.

## Cuando le pides saltarse el proceso

Si le pides algo que rompe una regla ("hazlo directo sin spec", "sáltate las pruebas"), el orquestador no obedece sin más ni se niega en seco:

1. Explica en una o dos frases qué regla se rompería y el riesgo concreto.
2. Ofrece la alternativa dentro del proceso, por ejemplo una especificación mínima de pocas líneas.
3. Solo si **confirmas explícitamente** que asumes la excepción, procede, y la deja registrada en la descripción del Pull Request.

Hay dos grupos de reglas que **no admiten excepción desde el chat**: las de secretos y archivos del kit, y el uso de `--no-verify`, `FORZAR` o los cambios a la constitución. Si de verdad hace falta, lo ejecuta una persona.

## Cómo se comunica

- **Al empezar un flujo:** una línea con el flujo y la fase. Por ejemplo: `Flujo equipo-feature · Funcionalidad 003-registro-usuarios · Fase 1/9: especificación → analista-producto`.
- **En cada delegación:** a qué especialista y qué le pide.
- **En cada puerta:** un resumen de cinco a diez líneas, los riesgos o las dudas, y la pregunta de aprobación.
- **Al terminar:** qué se entregó, el estado de las pruebas y las validaciones, los riesgos abiertos, el costo de IA y el enlace al Pull Request.
- **Si algo falla:** lo dice de inmediato. No lo oculta ni lo "arregla" rompiendo una regla.

## De dónde salen sus instrucciones

| Archivo | Qué contiene |
|---|---|
| `AGENTS.md` | El resumen: su papel, el stack, la tabla de flujos y las reglas de coordinación |
| `equipo/orquestador.md` | El manual completo: cada fase, el estado, los controles y cómo comunicarse |
| `.specify/memory/constitution.md` | Las reglas del código, que no puede contradecir |
| `.agents/skills/equipo-*` | El paso a paso de cada flujo |

En OpenCode aparece como un agente llamado `orquestador`, y es el que se abre por defecto. En Claude Code y Codex es la sesión principal, que carga las mismas instrucciones.

> [!NOTE]
> Estos archivos vienen del kit y no se editan en el proyecto. Para cambiar cómo se comporta el orquestador, ver [Cómo contribuir](contribuir.md).

## Siguientes pasos

- [Construir una funcionalidad](funcionalidad.md): el orquestador en acción.
- [Retomar el trabajo](retomar.md): cómo reconstruye el estado.
- [Roles](roles.md): los especialistas en los que delega.
