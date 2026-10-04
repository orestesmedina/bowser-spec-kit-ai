# Desarrollo guiado por especificaciones

- [Introducción](#introducción)
- [Por qué empezar por escrito](#por-qué-empezar-por-escrito)
- [El papel de las personas](#el-papel-de-las-personas)
- [El proceso completo](#el-proceso-completo)
- [Las nueve fases](#las-nueve-fases)
- [Los documentos de una funcionalidad](#los-documentos-de-una-funcionalidad)
- [Spec Kit](#spec-kit)
- [Las reglas del proceso](#las-reglas-del-proceso)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit organiza el trabajo con un método llamado **Spec-Driven Development**, o desarrollo guiado por especificaciones: antes de escribir código se escribe **qué** se va a construir y **cómo**, y ambas cosas las aprueba una persona.

Esta página explica el método, sus fases y por qué funciona con agentes de IA.

## Por qué empezar por escrito

Un agente de IA escribe código rápido, pero construye exactamente lo que entendió, no lo que querías. Si la instrucción es "hazme el registro de usuarios", el agente decide por su cuenta decenas de cosas: qué pasa si el correo ya existe, qué tan larga debe ser la contraseña, si hay que confirmar el correo. Cada decisión que el agente inventa es un posible error que nadie revisó.

Escribir primero la especificación saca esas decisiones a la luz **antes** de que existan mil líneas de código que las den por sentadas. Corregir una frase en un documento cuesta un minuto; corregirla cuando ya está construida cuesta rehacer el trabajo.

Por eso, en este proceso:

- La **especificación** dice qué se construye y por qué, sin hablar de tecnología.
- El **plan** dice cómo se construye.
- El código implementa lo que dicen los dos documentos, no una interpretación.

Si la especificación y el plan están bien, la implementación casi siempre sale bien. La mayor parte de la atención de las personas va en esas dos aprobaciones.

## El papel de las personas

En este proceso la IA escribe casi todo el código, pero **una persona es responsable del resultado**. El trabajo de esa persona no es escribir código. Es:

- **Entender** lo que el cliente necesita y asegurarse de que la especificación lo refleje.
- **Aprobar o rechazar** la especificación y el plan antes de que se construya nada.
- **Revisar** el Pull Request final y decidir si se integra.
- **Intervenir** cuando los agentes se atascan o se desvían.

## El proceso completo

```
Idea del cliente
   │
   ▼
spec.md ─────── ✋ UNA PERSONA APRUEBA  (¿es lo que el cliente pidió?)
   │
   ▼
plan.md ─────── ✋ UNA PERSONA APRUEBA  (¿la solución técnica tiene sentido?)
   │
   ▼
tasks.md → implementación → QA + revisión + seguridad → corrección (bucle)
   │
   ▼
Pull Request ── ✋ UNA PERSONA APRUEBA  (¿está bien hecho? ¿se integra?)
   │
   ▼
Producción ──── ✋ UNA PERSONA APRUEBA
```

Las manos (✋) son las **puertas de aprobación**: puntos donde los agentes se detienen y no continúan sin un "apruebo" explícito. Qué revisar en cada una está en [Aprobaciones](aprobaciones.md).

## Las nueve fases

| Fase | Qué pasa | Quién lo hace | Resultado | ¿Aprueba una persona? |
|---|---|---|---|---|
| 1. Especificar | Se escribe qué se construye y por qué | `analista-producto` | `spec.md` | **Sí** |
| 2. Aclarar | Se resuelven las dudas que quedaron marcadas | `analista-producto` y una persona | Especificación sin dudas | — |
| 3. Planificar | Se decide cómo se construye | `arquitecto`, y `disenador-ux` si hay pantallas | `plan.md`, modelo de datos, contrato de la API, `ux.md` | **Sí** |
| 4. Tareas | El plan se divide en tareas pequeñas | `arquitecto` | `tasks.md` | — |
| 5. Coherencia | Se comprueba que especificación, plan y tareas no se contradigan | `revisor-codigo` | Reporte | — |
| 6. Implementar | Se escribe el código, tarea por tarea, con sus pruebas | `dev-backend`, `dev-frontend`, `devops` | Código y pruebas | — |
| 7. Validar | Tres revisiones independientes, en paralelo | `qa-tester`, `revisor-codigo`, `seguridad` | Reportes | — |
| 8. Converger | Se comprueba que no quedó nada de la especificación sin construir | Orquestador | Tareas pendientes, o "listo" | — |
| 9. Entregar | Documentación, integración continua y Pull Request | `devops`, `documentador` | Pull Request | **Sí** (integrar y desplegar) |

Si la validación de la fase 7 rechaza el trabajo, vuelve al desarrollador con los hallazgos. Ese ciclo se repite hasta tres veces; después, el orquestador se detiene y pide ayuda a una persona.

El recorrido de una funcionalidad real por estas fases está en [Construir una funcionalidad](funcionalidad.md).

## Los documentos de una funcionalidad

Cada funcionalidad tiene su carpeta en `specs/`, por ejemplo `specs/003-registro-usuarios/`, y normalmente una rama de git con el mismo nombre.

| Documento | Responde | Lo escribe |
|---|---|---|
| `spec.md` | ¿Qué se construye, para quién y cómo sabemos que está terminado? | Analista de producto |
| `plan.md` | ¿Cómo se construye? Decisiones técnicas, alternativas descartadas y riesgos | Arquitecto |
| `data-model.md` | ¿Qué tablas, columnas y relaciones? | Arquitecto |
| `contracts/openapi.yaml` | ¿Qué le ofrece el backend al frontend? | Arquitecto |
| `ux.md` | ¿Qué pantallas, flujos y estados? | Diseñador UX |
| `tasks.md` | ¿En qué pasos se divide el trabajo y en qué orden? | Arquitecto |
| `revision-<fecha>.md` | ¿Qué encontraron QA, revisión y seguridad? | Los tres revisores |
| `estado.md` | ¿En qué fase va, qué se aprobó y qué sigue? | Orquestador |
| `costos.json` | ¿Cuánto costó en IA? | El comando `make costos` |

Una buena especificación tiene tres propiedades: cada requisito trae **criterios de aceptación** verificables (en formato Dado / Cuando / Entonces), dice explícitamente qué queda **fuera de alcance** y no menciona tecnología.

## Spec Kit

[Spec Kit](https://github.com/github/spec-kit) es una herramienta de GitHub que aporta las plantillas de los documentos y un comando para cada fase. El kit se apoya en ella y le agrega el equipo de agentes, las reglas y los controles.

Los comandos se escriben dentro del agente de código:

| Fase | Claude Code y OpenCode | Codex |
|---|---|---|
| Especificar | `/speckit.specify` | `$speckit-specify` |
| Aclarar | `/speckit.clarify` | `$speckit-clarify` |
| Planificar | `/speckit.plan` | `$speckit-plan` |
| Tareas | `/speckit.tasks` | `$speckit-tasks` |
| Coherencia | `/speckit.analyze` | `$speckit-analyze` |
| Implementar | `/speckit.implement` | `$speckit-implement` |
| Converger | `/speckit.converge` | `$speckit-converge` |

Normalmente **no los escribes tú**. Le pides al orquestador lo que necesitas con tus palabras, y él ejecuta la fase que corresponde y la delega en el agente indicado. Los comandos sirven cuando quieres ejecutar una fase suelta.

## Las reglas del proceso

Cinco reglas sostienen todo lo demás:

1. **Nada de código sin especificación y plan aprobados.** La única excepción son los [cambios pequeños](cambios-pequenos.md), que no afectan comportamiento, datos ni la API.
2. **Las aprobaciones son explícitas.** Un "ok" ambiguo no cuenta. Tampoco se deducen: que exista `plan.md` no significa que alguien lo aprobó.
3. **Quien escribe el código nunca lo aprueba.** Todo lo que produce un desarrollador pasa por QA, revisión y seguridad.
4. **Si cambia el alcance, cambia primero el documento.** Cuando aparece algo que la especificación no cubre, no se resuelve en el código: se actualiza `spec.md`, se vuelve a aprobar y se sigue.
5. **El estado vive en archivos, no en la memoria de una sesión.** Cualquiera puede retomar el trabajo otro día. Ver [Retomar el trabajo](retomar.md).

## Siguientes pasos

- [El equipo de agentes](equipo-de-agentes.md): quién hace cada fase.
- [Construir una funcionalidad](funcionalidad.md): el proceso aplicado a un ejemplo, paso a paso.
- [Aprobaciones](aprobaciones.md): qué revisar antes de decir "apruebo".
