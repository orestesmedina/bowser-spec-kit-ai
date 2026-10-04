# Construir una funcionalidad

- [Introducción](#introducción)
- [Antes de empezar](#antes-de-empezar)
- [Paso 1: pedir la funcionalidad](#paso-1-pedir-la-funcionalidad)
- [Paso 2: responder las aclaraciones](#paso-2-responder-las-aclaraciones)
- [Paso 3: aprobar la especificación](#paso-3-aprobar-la-especificación)
- [Paso 4: aprobar el plan técnico](#paso-4-aprobar-el-plan-técnico)
- [Paso 5: tareas y coherencia](#paso-5-tareas-y-coherencia)
- [Paso 6: implementación](#paso-6-implementación)
- [Paso 7: validación](#paso-7-validación)
- [Paso 8: revisar y aprobar el Pull Request](#paso-8-revisar-y-aprobar-el-pull-request)
- [Paso 9: despliegue](#paso-9-despliegue)
- [Resumen del flujo](#resumen-del-flujo)
- [Cambiar algo ya aprobado](#cambiar-algo-ya-aprobado)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página recorre una funcionalidad de principio a fin, desde que la pides hasta que está en producción. Es el flujo que más vas a usar.

El ejemplo: **"Los clientes pueden registrarse con correo y contraseña."**

De los nueve pasos, tú actúas en seis. Los otros tres los hacen los agentes, y tu papel es supervisar. Los pasos marcados con ✋ son puertas de aprobación: el trabajo no avanza sin tu "apruebo".

## Antes de empezar

```bash
git checkout main && git pull
make up
make doctor
make estado      # qué está en curso y qué sigue en el roadmap
```

Abre tu agente de código en la carpeta del proyecto (`claude`, `codex` u `opencode`). Lo primero que hace el orquestador es decirte dónde quedó el trabajo.

## Paso 1: pedir la funcionalidad

Escríbele al orquestador:

> Construyamos esta funcionalidad: los clientes pueden registrarse con correo y contraseña. Deben confirmar su correo antes de poder iniciar sesión. Si el correo ya existe, deben ver un mensaje claro.

Consejos para una buena solicitud:

- **Describe qué y para quién, no cómo.** Nada de "usa tal librería".
- **Incluye las reglas de negocio que conozcas:** límites, casos especiales, qué pasa si algo falla.
- **Adjunta lo que tengas del cliente:** correos, notas de reunión, capturas.
- **Si no sabes algo, dilo.** El analista te hará preguntas.

Spec Kit crea una carpeta para la funcionalidad, por ejemplo `specs/001-registro-usuarios/`, y una rama de git con el mismo nombre. El orquestador crea ahí el `estado.md` y marca la funcionalidad como `en curso` en el roadmap.

## Paso 2: responder las aclaraciones

El `analista-producto` marca lo que no está claro como `[NECESITA ACLARACIÓN]` y te pregunta. Respóndelo tú, o consúltalo con el cliente.

> [!WARNING]
> No dejes que el agente adivine reglas de negocio. Una duda sin responder se convierte en una decisión que tomó el agente y que nadie revisó.

## Paso 3: aprobar la especificación

✋ **Puerta de aprobación.** Abre `specs/001-registro-usuarios/spec.md` y léelo completo. La lista de qué revisar está en [Aprobaciones](aprobaciones.md#la-especificación).

Si algo falla, pide cambios concretos:

> Agrega un criterio: la contraseña debe tener mínimo 12 caracteres.

Cuando esté bien, escribe: **"Apruebo la spec."**

## Paso 4: aprobar el plan técnico

El `arquitecto` genera `plan.md`, `data-model.md` y `contracts/`. Si hay pantallas, el `disenador-ux` genera `ux.md`.

✋ **Puerta de aprobación.** Revisa el plan con la lista de [Aprobaciones](aprobaciones.md#el-plan-técnico).

Si no tienes la experiencia técnica para juzgar el plan, **pide revisión a alguien que la tenga antes de aprobar**. No hay vergüenza en eso; aprobar un mal plan sí es caro.

Cuando esté bien: **"Apruebo el plan."**

## Paso 5: tareas y coherencia

Automático. El `arquitecto` genera `tasks.md`, y el `revisor-codigo` comprueba que especificación, plan y tareas no se contradigan.

Dale un vistazo a `tasks.md`: las tareas deben ser pequeñas, y cada una debe incluir sus pruebas.

## Paso 6: implementación

Automático, con supervisión. Los desarrolladores implementan tarea por tarea, con un commit por tarea. Tu papel:

- **Deja trabajar,** pero revisa el progreso cada cierto tiempo.
- **Intervén si ves** que el agente repite el mismo error, modifica cosas fuera del alcance o dice "voy a desactivar esta prueba".
- **Si un commit es rechazado** por los [hooks de git](hooks-de-git.md), el agente debe corregir la causa. Nunca le permitas usar `--no-verify`.

Si la sesión se corta o lo dejas para otro día, no se pierde nada: ver [Retomar el trabajo](retomar.md).

## Paso 7: validación

Automático. `qa-tester`, `revisor-codigo` y `seguridad` revisan en paralelo, y el orquestador consolida los tres reportes en `specs/<funcionalidad>/revision-<fecha>.md`.

Si alguno rechaza, el trabajo vuelve al desarrollador con los hallazgos. Después de **tres ciclos** sin éxito, el orquestador se detiene y te pide ayuda. En ese caso:

1. Lee los reportes `revision-*.md`.
2. Decide de qué es el problema:

| El problema es de… | Qué hacer |
|---|---|
| Código | Da instrucciones más precisas |
| Plan | Vuelve al paso 4 |
| Especificación | Vuelve al paso 3 |

Cuando la validación aprueba, el orquestador comprueba que no quedó nada de la especificación sin construir. Si falta algo, agrega las tareas y repite los pasos 6 y 7 solo para ellas.

## Paso 8: revisar y aprobar el Pull Request

El `devops` verifica la integración continua, el `documentador` actualiza el registro de cambios y las notas para el cliente, y el orquestador abre el Pull Request.

✋ **Puerta de aprobación.** Revisa con la lista de [Aprobaciones](aprobaciones.md#el-pull-request). Lo más importante: **prueba la funcionalidad tú mismo** en tu máquina.

Cuando apruebas, el orquestador cierra el costo de IA de la funcionalidad (`make costos CERRAR=1`) antes de integrar. Después de integrar, la funcionalidad queda `terminada` en el roadmap.

## Paso 9: despliegue

✋ **Puerta de aprobación.** El despliegue a producción siempre lo aprueba una persona. Sigue el procedimiento del proyecto y, después de desplegar, comprueba que la funcionalidad responda y revisa los logs durante unos minutos.

## Resumen del flujo

| Paso | Quién | Tu acción | Tiempo típico |
|---|---|---|---|
| 1. Pedir | Tú | Describir la necesidad | 10 min |
| 2. Aclarar | Analista y tú | Responder preguntas | 10 a 30 min |
| 3. Especificación | Analista | **Aprobar** | 15 a 30 min |
| 4. Plan | Arquitecto y UX | **Aprobar** | 20 a 45 min |
| 5. Tareas | Arquitecto y revisor | Vistazo rápido | 5 min |
| 6. Implementar | Desarrolladores | Supervisar | Variable |
| 7. Validar | QA, revisor y seguridad | Intervenir si se atasca | Variable |
| 8. Pull Request | Orquestador | **Revisar y aprobar** | 20 a 40 min |
| 9. Desplegar | DevOps | **Aprobar** | 10 min |

## Cambiar algo ya aprobado

A mitad de la implementación aparece algo que la especificación no cubría, o el cliente cambia de opinión. No se resuelve en el código.

El orden es siempre el mismo: primero se actualiza `spec.md` y se vuelve a aprobar; después el plan y las tareas; después el código. **Nunca al revés.**

Lo mismo vale para cambiar una funcionalidad que ya está terminada: es una funcionalidad nueva, que empieza por su especificación.

## Siguientes pasos

- [Aprobaciones](aprobaciones.md): las listas de revisión de cada puerta.
- [Retomar el trabajo](retomar.md): continuar otro día, o que continúe otra persona.
- [Corregir un bug](bugs.md) y [Cambios pequeños](cambios-pequenos.md): los flujos más cortos.
