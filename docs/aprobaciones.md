# Aprobaciones

- [Introducción](#introducción)
- [Cómo se aprueba](#cómo-se-aprueba)
- [La especificación](#la-especificación)
- [El plan técnico](#el-plan-técnico)
- [El Pull Request](#el-pull-request)
- [El despliegue](#el-despliegue)
- [Cómo queda registrada](#cómo-queda-registrada)
- [Cuando no estás seguro](#cuando-no-estás-seguro)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Una aprobación es el momento en que una persona se hace responsable de lo que sigue. El proceso tiene cuatro: la especificación, el plan técnico, el Pull Request y el despliegue. En cada una, los agentes se detienen y esperan.

Esta página tiene la lista de qué revisar en cada puerta. Es la misma lista que el orquestador te presenta cuando llega a una.

## Cómo se aprueba

Con una frase explícita en el chat:

| Puerta | Frase |
|---|---|
| Especificación | "Apruebo la spec" |
| Plan | "Apruebo el plan" |
| Pull Request | "Apruebo el PR" |

Un "ok", un "dale" o un "se ve bien" **no cuentan**: el orquestador te va a pedir que confirmes. Tampoco se deduce una aprobación de que exista un archivo o de que el trabajo haya seguido adelante.

La regla es estricta a propósito. Tu aprobación es tu firma, y una firma no se da por accidente.

> [!WARNING]
> Nunca apruebes lo que no leíste. Si no tienes tiempo de leerlo ahora, no lo apruebes ahora: el trabajo puede esperar, y queda guardado. Ver [Retomar el trabajo](retomar.md).

## La especificación

Pregunta que responde: **¿es lo que el cliente pidió?**

Abre `specs/<funcionalidad>/spec.md` y revisa:

- [ ] Describe lo que el cliente pidió, ni más ni menos.
- [ ] Cada historia de usuario tiene criterios de aceptación en formato Dado / Cuando / Entonces.
- [ ] Los criterios son verificables. "Rápido" no sirve; "responde en menos de 2 segundos" sí.
- [ ] Incluye casos de error y casos límite (correo duplicado, contraseña débil, enlace vencido…).
- [ ] La sección "fuera de alcance" es correcta.
- [ ] No quedan marcas `[NECESITA ACLARACIÓN]`.
- [ ] No menciona tecnología. Eso va en el plan.

Si algo falla, pide el cambio concreto en lugar de rechazar en general: *"Agrega un criterio: la contraseña debe tener mínimo 12 caracteres."*

## El plan técnico

Pregunta que responde: **¿la solución técnica tiene sentido?**

Revisa `plan.md`, `data-model.md`, `contracts/` y, si hay pantallas, `ux.md`:

- [ ] Respeta el stack del proyecto y la [constitución](la-constitucion.md).
- [ ] Cada requisito de la especificación tiene una parte del plan que lo resuelve.
- [ ] El modelo de datos tiene sentido: tablas, relaciones, restricciones e índices.
- [ ] Los endpoints de la API cubren todo lo que el frontend necesita.
- [ ] Las dependencias nuevas están justificadas.
- [ ] Los riesgos están identificados.
- [ ] Si hay interfaz, `ux.md` cubre los estados de carga, vacío, error y éxito.

Esta es la aprobación que más conocimiento técnico pide. Si no lo tienes, pide revisión a alguien que sí antes de aprobar.

## El Pull Request

Pregunta que responde: **¿está bien hecho, y se integra?**

- [ ] La integración continua de GitHub está en verde.
- [ ] Los reportes de QA, revisión y seguridad dicen APROBADO.
- [ ] Probaste la funcionalidad tú mismo en tu máquina: `make up`, levantar backend y frontend, recorrer el flujo.
- [ ] Los cambios tienen sentido al leerlos; no hay archivos inesperados.
- [ ] El registro de cambios y la documentación están actualizados.
- [ ] No hay secretos, datos reales de clientes ni código comentado.

Si el Pull Request toca archivos críticos (las reglas, los agentes, los workflows), GitHub pide además la aprobación de quien figura en `CODEOWNERS`.

> [!NOTE]
> Los tres primeros puntos no se reemplazan entre sí. La integración continua comprueba lo que se puede automatizar, los agentes revisores comprueban el código contra los documentos, y solo tú compruebas que la funcionalidad hace lo que el cliente necesitaba.

## El despliegue

Pregunta que responde: **¿es el momento de que llegue a los usuarios?**

- [ ] El Pull Request está integrado y la integración continua de la rama principal está en verde.
- [ ] Se siguió el procedimiento de despliegue del proyecto.
- [ ] Hay una forma conocida de volver atrás si algo sale mal.
- [ ] Después de desplegar: la funcionalidad responde, y los logs no muestran errores nuevos durante unos minutos.

Ningún agente despliega a producción ni modifica infraestructura productiva sin esta aprobación.

## Cómo queda registrada

El orquestador anota cada aprobación en `specs/<funcionalidad>/estado.md`, con quién la dio, cuándo y la frase exacta:

| Puerta | Estado | Quién | Fecha | Frase |
|---|---|---|---|---|
| Spec | aprobado | Ana | 2026-10-04 | "Apruebo la spec" |
| Plan | pendiente | | | |

Como el archivo va en git, cualquiera puede ver después qué se aprobó y quién lo hizo. `make estado` muestra las aprobaciones de la funcionalidad actual, y avisa si el trabajo avanzó a una fase que requería una aprobación que no consta.

## Cuando no estás seguro

| Duda | Qué hacer |
|---|---|
| Es de negocio: ¿esto es lo que quiere el cliente? | Pregúntale al cliente. No apruebes una suposición |
| Es técnica: ¿este diseño es bueno? | Pide revisión a alguien con más experiencia |
| El documento es demasiado largo para revisarlo bien | La funcionalidad es demasiado grande. Pide dividirla |
| Algo no cuadra, pero no sabes decir qué | Pídele al orquestador que te explique esa parte. Si la explicación no convence, no apruebes |

## Siguientes pasos

- [Construir una funcionalidad](funcionalidad.md): dónde cae cada puerta dentro del flujo.
- [Reglas de oro](reglas-de-oro.md): lo que nunca se hace.
- [Retomar el trabajo](retomar.md): qué pasa con las aprobaciones entre sesiones.
