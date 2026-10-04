# El equipo de agentes

- [Introducción](#introducción)
- [Por qué un equipo y no un solo agente](#por-qué-un-equipo-y-no-un-solo-agente)
- [Quién es quién](#quién-es-quién)
- [Quién puede escribir qué](#quién-puede-escribir-qué)
- [Quién escribe no aprueba](#quién-escribe-no-aprueba)
- [Cómo se reparte el trabajo](#cómo-se-reparte-el-trabajo)
- [Si la herramienta no tiene subagentes](#si-la-herramienta-no-tiene-subagentes)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Cuando abres el agente de código en un proyecto con el kit, no hablas con "una IA que programa". Hablas con el **orquestador**, un agente que coordina a diez especialistas, cada uno con un trabajo, unos permisos y un modelo propios.

Esta página presenta al equipo. El detalle de cada especialista está en [Roles](roles.md), y el del coordinador en [El orquestador](el-orquestador.md).

## Por qué un equipo y no un solo agente

Un solo agente que especifica, programa y revisa su propio trabajo tiene tres problemas:

- **No ve sus propios errores.** Quien escribió el código lee lo que quiso escribir, no lo que escribió. Le pasa a las personas y le pasa a los modelos.
- **Mezcla responsabilidades.** Si puede cambiar el código y las pruebas, la forma más fácil de hacer pasar una prueba es debilitarla.
- **Pierde el hilo.** Una conversación larga que incluye todo, desde la idea hasta el despliegue, llena la memoria del agente y baja la calidad.

Separar el trabajo en roles resuelve los tres: cada especialista recibe solo lo que necesita, tiene permiso solo para lo que le toca, y lo que produce lo revisa otro.

## Quién es quién

| Rol | Qué hace | Cuándo entra |
|---|---|---|
| **Orquestador** | Habla contigo, decide qué flujo aplicar, delega y lleva el estado | Siempre |
| `analista-producto` | Convierte la necesidad en la especificación | Al inicio de cada funcionalidad |
| `arquitecto` | Diseña el plan, el modelo de datos y la API; divide el trabajo en tareas | Después de aprobar la especificación |
| `disenador-ux` | Define pantallas, flujos y estados | Durante el plan, si hay interfaz |
| `dev-backend` | Implementa en Go y PostgreSQL | En las tareas de backend y base de datos |
| `dev-frontend` | Implementa en React + TypeScript | En las tareas de frontend |
| `devops` | Docker, integración continua y despliegues | En las tareas de infraestructura y al entregar |
| `qa-tester` | Prueba el código contra los criterios de aceptación | Después de cada implementación |
| `revisor-codigo` | Revisa la calidad y el apego al plan y a la constitución | Después de las tareas y de cada implementación |
| `seguridad` | Audita vulnerabilidades, secretos y dependencias | Después de cada implementación y antes de desplegar |
| `documentador` | Registro de cambios, README y notas para el cliente | Al cerrar cada funcionalidad |

## Quién puede escribir qué

Cada rol tiene un nivel de acceso, y la herramienta lo hace cumplir: un rol de solo lectura no tiene manera de modificar un archivo aunque quiera.

| Acceso | Significa | Roles |
|---|---|---|
| **Solo lectura** | Lee y ejecuta comandos; no modifica nada | `revisor-codigo`, `seguridad` |
| **Documentos** | Escribe archivos, sin usar la terminal | `analista-producto`, `arquitecto`, `disenador-ux`, `documentador` |
| **Completo** | Escribe y ejecuta | `dev-backend`, `dev-frontend`, `devops`, `qa-tester` |

Además, cada rol tiene límites escritos en sus instrucciones: `qa-tester` solo escribe archivos de pruebas y nunca toca el código de producción; `dev-backend` no toca `frontend/` y `dev-frontend` no toca `backend/`.

## Quién escribe no aprueba

Es el principio central del equipo. Todo el código que produce un desarrollador pasa por tres revisiones independientes antes de llegar a una persona:

| Revisor | Su lealtad | Qué busca |
|---|---|---|
| `qa-tester` | La especificación | Que cada criterio de aceptación tenga una prueba y que pase |
| `revisor-codigo` | El plan y la constitución | Errores lógicos, apego al diseño, calidad |
| `seguridad` | La seguridad | Vulnerabilidades, secretos expuestos, dependencias con fallos conocidos |

El trabajo se da por bueno solo si **los tres** aprueban.

El principio se extiende a los modelos: el kit recomienda que quien revisa use un modelo de una familia distinta a la de quien escribió, para que no comparta sus puntos ciegos. Ver [Modelos por agente](modelos.md).

## Cómo se reparte el trabajo

El arquitecto marca cada tarea de `tasks.md` con su capa, y el orquestador la delega según esa marca:

| Marca en la tarea | La hace |
|---|---|
| `[backend]` o `[db]` | `dev-backend` |
| `[frontend]` | `dev-frontend` |
| `[infra]` | `devops` |
| `[P]` | Puede ir en paralelo con otras tareas `[P]` que no dependan entre sí |

Cada tarea terminada es un commit, y queda marcada con `[X]` en `tasks.md`.

## Si la herramienta no tiene subagentes

Claude Code, Codex y OpenCode pueden lanzar subagentes. Si se usa una herramienta o una configuración que no puede, el orquestador **asume cada rol en secuencia**, leyendo la definición del rol en `equipo/agentes/<rol>.md` antes de actuar.

En ese caso se pierde parte de la independencia, así que la regla es más estricta: nunca aprueba en el papel de revisor algo que escribió en el papel de desarrollador sin releerlo desde cero contra la especificación.

## Siguientes pasos

- [El orquestador](el-orquestador.md): cómo decide y cómo se comunica.
- [Roles](roles.md): cada especialista en detalle, y cómo cambiarlos o agregar uno.
- [Modelos por agente](modelos.md): qué modelo conviene para cada rol.
