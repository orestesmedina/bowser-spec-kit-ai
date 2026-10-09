# Roles

- [Introducción](#introducción)
- [Qué define un rol](#qué-define-un-rol)
- [Los once roles](#los-once-roles)
    - [analista-producto](#analista-producto)
    - [arquitecto](#arquitecto)
    - [disenador-ux](#disenador-ux)
    - [dev-backend](#dev-backend)
    - [dev-frontend](#dev-frontend)
    - [dev-dba](#dev-dba)
    - [qa-tester](#qa-tester)
    - [revisor-codigo](#revisor-codigo)
    - [seguridad](#seguridad)
    - [devops](#devops)
    - [documentador](#documentador)
- [Lo que cada rol recibe del proyecto](#lo-que-cada-rol-recibe-del-proyecto)
- [El formato de un rol](#el-formato-de-un-rol)
- [Cambiar un rol](#cambiar-un-rol)
- [Agregar un rol](#agregar-un-rol)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Un rol es la definición de un especialista del equipo: qué hace, qué puede tocar, qué entrega y con qué reglas. Cada rol es un archivo en `equipo/agentes/`, y a partir de él se genera el subagente de cada herramienta.

Esta página describe cada rol y explica cómo cambiarlos. La visión de conjunto está en [El equipo de agentes](equipo-de-agentes.md).

## Qué define un rol

Cuatro cosas distinguen a un rol de otro:

| | Qué es | Por qué importa |
|---|---|---|
| **Responsabilidad** | Una sola cosa que hacer, y la prohibición explícita de hacer lo de otros | Un agente con un encargo acotado lo hace mejor, y sus errores son más fáciles de ver |
| **Acceso** | Qué puede leer, escribir y ejecutar | No depende de que el agente "se porte bien": la herramienta se lo impide |
| **Nivel** | Cuánta capacidad de razonamiento necesita | Decide qué modelo usa, y por lo tanto cuánto cuesta |
| **Entrega** | El formato exacto de lo que devuelve | Permite que el orquestador y los demás roles trabajen con el resultado |

## Los once roles

### analista-producto

Convierte una necesidad de negocio en una especificación clara y verificable.

| | |
|---|---|
| **Cuándo entra** | Al inicio de cada funcionalidad, y para aclarar las dudas de una especificación |
| **Acceso** | Documentos |
| **Nivel** | Alto |
| **Entrega** | `spec.md` completo, y un resumen con las preguntas abiertas |

Describe **qué** se construye y **por qué**, con historias de usuario y criterios de aceptación en formato Dado / Cuando / Entonces. Incluye los casos límite, los errores esperados y lo que queda fuera de alcance.

Nunca habla de tecnología, ni inventa reglas de negocio: toda ambigüedad queda marcada como `[NECESITA ACLARACIÓN]` con una pregunta concreta.

### arquitecto

Decide **cómo** se construye lo que pide la especificación, respetando la constitución.

| | |
|---|---|
| **Cuándo entra** | Después de aprobar la especificación, para el plan y para las tareas |
| **Acceso** | Documentos, y puede buscar en internet |
| **Nivel** | Alto |
| **Entrega** | `plan.md`, `data-model.md`, los contratos en `contracts/` y `tasks.md` |

El plan incluye las decisiones técnicas con su justificación, las alternativas descartadas y los riesgos. Las tareas son pequeñas, están ordenadas por dependencia, y cada una indica la parte del proyecto que toca (`[api]`, con el nombre que tiene en el [perfil](perfil-del-proyecto.md)), sus archivos y la prueba esperada.

Diseña con las tecnologías que el proyecto ya usa. También es quien redacta el perfil del proyecto cuando se lo piden con `/bowser-profile`.

Usa lo que ya existe en el repositorio antes de proponer algo nuevo, y justifica cada dependencia que agrega. No escribe código de producción.

### disenador-ux

Define cómo se ve y cómo se usa la funcionalidad.

| | |
|---|---|
| **Cuándo entra** | Durante el plan, solo si la funcionalidad tiene interfaz |
| **Acceso** | Documentos |
| **Nivel** | Medio |
| **Entrega** | `ux.md` |

El documento cubre el flujo del usuario con sus caminos de error, cada pantalla, los estados de cada vista (vacío, cargando, error, éxito, sin permisos), los componentes a reutilizar o crear, la accesibilidad y los textos.

Diseña primero para móvil y reutiliza componentes existentes. No escribe código: su diseño lo implementa el desarrollador de la interfaz.

### dev-backend

Implementa el lado del servidor: reglas de negocio, API y procesos. No está atado a un lenguaje.

| | |
|---|---|
| **Cuándo entra** | En las tareas de las partes que el perfil le asigna |
| **Acceso** | Completo |
| **Nivel** | Medio |
| **Skills** | Las de sus partes, según el perfil (por ejemplo, `go-backend`) |
| **Entrega** | Código con sus pruebas, y un resumen de lo cambiado y de cualquier desviación del plan |

Escribe primero la prueba y después el código que la hace pasar. Marca la tarea como hecha solo si los comandos de su parte pasan.

No toca las partes que no son suyas. El esquema de la base de datos es de `dev-dba` cuando el proyecto lo tiene. Si una tarea exige cambiar el contrato de la API, se detiene y avisa al orquestador.

### dev-frontend

Implementa la interfaz de usuario: lo que la persona ve y usa. No está atado a un framework.

| | |
|---|---|
| **Cuándo entra** | En las tareas de las partes que el perfil le asigna |
| **Acceso** | Completo |
| **Nivel** | Medio |
| **Skills** | Las de sus partes, según el perfil (por ejemplo, `react-frontend`) |
| **Entrega** | Pantallas y componentes con sus pruebas, y el resultado de los comandos de su parte |

Implementa todos los estados definidos en `ux.md` y respeta el contrato de la API. Si el proyecto genera código a partir del contrato, lo regenera; nunca lo escribe a mano.

No toca las partes que no son suyas. Si el contrato no alcanza para la pantalla, se detiene y avisa.

### dev-dba

Trabaja la base de datos: tablas, migraciones, índices, consultas y procedimientos almacenados. No está atado a un motor.

| | |
|---|---|
| **Cuándo entra** | En las tareas de las partes que el perfil le asigna, o en las que lo nombran (`[api:dev-dba]`) |
| **Acceso** | Completo |
| **Nivel** | Medio |
| **Skills** | Las de sus partes, según el perfil (por ejemplo, `postgres-db`) |
| **Entrega** | Los archivos de cambio, cómo se revierten, cómo se probaron y qué debe saber quien use esas tablas |

Existe para que el desarrollador del servidor no sea a la vez quien decide el esquema: son dos oficios. Todo cambio va en un archivo nuevo y trae cómo revertirlo; los cambios riesgosos en tablas con datos se hacen por pasos, y las reglas de los datos se hacen cumplir en la base de datos.

No toca el código de la aplicación: deja escrito qué cambió para el desarrollador de esa parte. Nunca ejecuta nada contra una base de datos que no sea la local o la de pruebas.

> [!NOTE]
> Un proyecto sin [perfil](perfil-del-proyecto.md) no usa este rol: ahí la base de datos la sigue llevando `dev-backend`, como antes. Para incorporarlo, el perfil le asigna una parte. Ver [Lo que cada rol recibe del proyecto](#lo-que-cada-rol-recibe-del-proyecto).

### qa-tester

Comprueba el código contra los criterios de aceptación. Su lealtad es con la especificación, no con el código.

| | |
|---|---|
| **Cuándo entra** | Después de cada implementación, y para reproducir un bug |
| **Acceso** | Completo |
| **Nivel** | Medio |
| **Entrega** | Una matriz de criterios contra pruebas, la lista de defectos y un veredicto: APROBADO o RECHAZADO |

Para cada criterio de aceptación, verifica que exista al menos una prueba que lo cubra; si falta, la escribe. Prueba los casos límite y de error.

**Solo escribe archivos de pruebas.** Nunca modifica el código de producción, aunque vea el arreglo, y nunca debilita una prueba para que pase.

### revisor-codigo

Revisa la calidad del código como un ingeniero con experiencia, exigente pero justo.

| | |
|---|---|
| **Cuándo entra** | Después de generar las tareas (coherencia) y después de cada implementación |
| **Acceso** | Solo lectura |
| **Nivel** | Alto |
| **Entrega** | Hallazgos por severidad (Bloqueante, Importante, Sugerencia) y un veredicto |

Revisa el apego a la especificación y al plan, el cumplimiento de la constitución, la corrección, la legibilidad, la calidad de las pruebas y el rendimiento.

Cita siempre el archivo y la línea, y propone el cambio concreto. No reporta preferencias de estilo que el linter ya cubre.

### seguridad

Audita el código en busca de vulnerabilidades.

| | |
|---|---|
| **Cuándo entra** | Después de cada implementación y antes de cada despliegue |
| **Acceso** | Solo lectura |
| **Nivel** | Alto |
| **Entrega** | Hallazgos por severidad (Crítica, Alta, Media, Baja) y un veredicto |

Busca inyección, fallos de control de acceso, XSS, secretos en el código, problemas de autenticación, falta de validación de entradas, configuración insegura y dependencias con vulnerabilidades conocidas.

Cada hallazgo trae archivo, línea, impacto y corrección. **Cualquier hallazgo de severidad Crítica o Alta rechaza el cambio.**

### devops

Mantiene la infraestructura del proyecto.

| | |
|---|---|
| **Cuándo entra** | En las tareas marcadas `[infra]` y al entregar cada funcionalidad |
| **Acceso** | Completo |
| **Nivel** | Medio |
| **Entrega** | Los archivos cambiados, cómo probarlos y qué secretos o variables debe configurar una persona |

Se ocupa del entorno local, del empaquetado de cada parte, de la integración continua y el despliegue, de aplicar los cambios de la base de datos de forma automática y de mantener `.env.example` al día, con las herramientas que el proyecto ya usa.

Nunca pone secretos en archivos, fija las versiones de imágenes y herramientas, y **nunca despliega a producción** sin la aprobación explícita de una persona.

### documentador

Deja la documentación al día al cerrar cada funcionalidad.

| | |
|---|---|
| **Cuándo entra** | Al entregar cada funcionalidad y al cerrar un bug |
| **Acceso** | Documentos |
| **Nivel** | Bajo |
| **Entrega** | El registro de cambios, el README, la documentación de la API y las notas para el cliente |

Las notas para el cliente van en `docs/entregas/`, en lenguaje no técnico: qué se entregó, cómo usarlo y qué limitaciones tiene.

Documenta solo lo que existe en el código, y lo comprueba antes de escribir.

## Lo que cada rol recibe del proyecto

Ningún rol trae escrita una tecnología, una carpeta ni un comando. Un rol describe un oficio, y lo propio de cada proyecto sale de su [perfil](perfil-del-proyecto.md): al generar los subagentes, `make sincronizar` le agrega a cada rol una sección **"Este proyecto"**.

Así queda `dev-dba` en un proyecto cuyo perfil le asigna la parte `datos`:

```markdown
## Este proyecto
Sale del perfil del proyecto (`equipo/perfil.json`), que no editas tú. Tus partes:

- **datos**, en `bd`.
  - Skills que debes aplicar: `postgres-db` (en `.agents/skills/`).
  - Comandos: `make lint PARTE=datos`.
  - El proyecto todavía no tiene cómo: probar, cobertura, generar, auditar. No inventes un comando: dilo en tu entrega.
  - No se modifican una vez versionados (se crea un archivo nuevo): `bd/cambios/*.sql`.

Las demás partes no son tuyas: `api` (`servidor`, de `dev-backend`).
```

Qué recibe cada rol lo decide su campo `proyecto` (ver [El formato de un rol](#el-formato-de-un-rol)):

| `proyecto` | Qué ve | Roles |
|---|---|---|
| `partes` | Solo las partes que el perfil le asigna, con sus skills | `dev-backend`, `dev-frontend`, `dev-dba` |
| `mapa` | Todas las partes, con quién trabaja cada una y dónde están sus convenciones | `arquitecto`, `disenador-ux`, `qa-tester`, `revisor-codigo`, `seguridad`, `devops`, `documentador` |
| (sin el campo) | Nada | `analista-producto`, que no habla de tecnología |

Tres cosas a tener en cuenta:

- **Después de cambiar el perfil hay que regenerar.** `make instalar-kit` lo hace (y además trae las skills nuevas); si las skills no cambiaron, alcanza con `make sincronizar`. Si no, el commit se rechaza con `La configuración de agentes está desactualizada`.
- **Un rol de desarrollo sin ninguna parte lo sabe.** Sus instrucciones dicen "Hoy no te asigna ninguna parte", y si le llega una tarea avisa al orquestador en vez de suponer.
- **Sin perfil se supone la estructura original del kit:** `backend/` para `dev-backend` (con la base de datos) y `frontend/` para `dev-frontend`. Esa suposición se retira en la versión 2.0.

Para que `dev-dba` lleve la base de datos de un proyecto cuyo esquema vive dentro de la carpeta del servidor, la parte declara los dos roles y le da a cada uno su skill:

```json
{
  "nombre": "backend",
  "carpeta": "backend",
  "roles": [
    { "rol": "dev-backend", "skills": ["go-backend"] },
    { "rol": "dev-dba", "skills": ["postgres-db"] }
  ]
}
```

## El formato de un rol

```markdown
---
nombre: revisor-codigo
descripcion: Usar después de cada implementación para revisar calidad, apego al plan y a la constitución. Solo lee; nunca edita.
acceso: lectura
nivel: alto
temperatura: 0.1
web: no
proyecto: mapa
---
Eres el revisor de código del equipo…
```

| Campo | Valores | Qué define |
|---|---|---|
| `nombre` | Texto, sin espacios | El nombre con el que el orquestador lo invoca |
| `descripcion` | Una frase | **Cuándo** usar este agente. El orquestador decide a quién delegar leyendo esta frase |
| `acceso` | `lectura`, `documentos`, `completo` | Qué puede tocar |
| `nivel` | `alto`, `medio`, `bajo` | Qué modelo usa, según `equipo/config.json` |
| `temperatura` | De 0 a 2. Opcional | Cuánta variación tienen sus respuestas |
| `web` | `si`, `no` | Si puede buscar en internet |
| `proyecto` | `partes`, `mapa`. Opcional | Qué recibe del perfil: sus partes, o todas. Ver [Lo que cada rol recibe del proyecto](#lo-que-cada-rol-recibe-del-proyecto) |
| `skills` | Lista. Opcional | Skills fijas, que aplica en cualquier parte. Los roles del kit no la usan: sus skills las asigna el perfil. Sirve para un rol propio del proyecto |

Debajo del encabezado van las instrucciones, en lenguaje natural.

El rol no nombra ninguna herramienta ni ningún modelo, y tampoco una tecnología. Lo primero lo resuelve el generador; lo segundo, el perfil. Ver [Una fuente, varias herramientas](una-fuente-varias-herramientas.md).

## Cambiar un rol

Los roles vienen del kit, así que hay dos situaciones:

- **El cambio le sirve a todos los proyectos:** se hace en el repositorio del kit. Ver [Cómo contribuir](contribuir.md).
- **Es propio de un proyecto:** agrega el archivo a `"kit.excluir"`, edítalo y ejecuta `make sincronizar`. Ver [Personalizar un proyecto](personalizar.md).

Antes de cambiar un rol, considera si lo que necesitas es otra cosa:

| Quieres… | Lo que hay que cambiar |
|---|---|
| Que use otro modelo | `equipo/config.json`. No hace falta tocar el rol |
| Que escriba el código de otra manera | La [skill](skills.md) de esa tecnología |
| Que trabaje otra carpeta, con otra skill o con otros comandos | El [perfil del proyecto](perfil-del-proyecto.md) |
| Que cumpla una regla nueva en todo el proyecto | La [constitución](la-constitucion.md) |
| Que haga o deje de hacer algo propio de su trabajo | El rol |

## Agregar un rol

Crea un archivo nuevo en `equipo/agentes/`, con el formato de arriba, y regenera:

```bash
make sincronizar
make modelos       # comprueba que aparece, y con qué modelo
```

Un rol que no viene del kit nunca es tocado por una actualización: es del proyecto.

Dos consejos para que funcione:

- **La `descripcion` es lo más importante.** Si no dice con claridad cuándo usarlo, el orquestador no lo va a invocar.
- **Dile también al orquestador que existe.** Un rol nuevo no entra solo en el flujo: hay que indicar en qué fase participa, normalmente en una skill propia del proyecto.

## Siguientes pasos

- [Skills](skills.md): el conocimiento que usan los roles.
- [Modelos por agente](modelos.md): qué modelo conviene a cada nivel.
- [Personalizar un proyecto](personalizar.md): roles y skills propios.
