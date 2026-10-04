# Skills

- [Introducción](#introducción)
- [Skill, rol y constitución](#skill-rol-y-constitución)
- [Cómo se activa una skill](#cómo-se-activa-una-skill)
- [Las skills del stack](#las-skills-del-stack)
    - [go-backend](#go-backend)
    - [react-frontend](#react-frontend)
    - [postgres-db](#postgres-db)
- [Las skills de flujo](#las-skills-de-flujo)
- [El formato de una skill](#el-formato-de-una-skill)
- [Cuándo cambiar una skill](#cuándo-cambiar-una-skill)
- [Agregar una skill propia](#agregar-una-skill-propia)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Una skill es un conjunto de instrucciones reutilizables que un agente carga **cuando la tarea lo requiere**. El kit trae siete: tres con las convenciones de cada tecnología y cuatro con el paso a paso de cada flujo de trabajo.

Viven en `.agents/skills/`, una carpeta por skill, cada una con un archivo `SKILL.md`.

## Skill, rol y constitución

Los tres son instrucciones para los agentes, pero responden preguntas distintas:

| | Responde | Ejemplo |
|---|---|---|
| **[Rol](roles.md)** | ¿Quién soy y qué me toca hacer? | "Eres el desarrollador backend. No tocas `frontend/`" |
| **Skill** | ¿Cómo se hace esto aquí? | "Envuelve los errores con contexto. Las pruebas van en tabla de casos" |
| **[Constitución](la-constitucion.md)** | ¿Qué no se negocia? | "El backend sigue la arquitectura por capas" |

La ventaja de separar el "cómo" en skills es que varios roles comparten el mismo conocimiento: `dev-backend` escribe según `go-backend`, y `revisor-codigo` puede cargar la misma skill para revisar contra ella.

## Cómo se activa una skill

De tres maneras:

- **Por su descripción.** Cada skill dice cuándo usarse. Cuando la tarea coincide, el agente la carga solo. Es lo normal.
- **Porque el rol la declara.** `dev-backend` lleva `skills: go-backend, postgres-db` en su definición, así que siempre las aplica.
- **Nombrándola.** Puedes pedirla: "Usa la skill equipo-revision". En Claude Code también se invocan como `/equipo-feature`.

## Las skills del stack

Dicen cómo se escribe el código en cada tecnología. Son la razón por la que el código de distintas funcionalidades, escritas en distintos días, se parece.

### go-backend

Se usa siempre que se crea o modifica código en `backend/`.

| Tema | Lo que establece |
|---|---|
| Herramientas | Go 1.26 o superior, `pgx/v5` con `sqlc`, `golang-migrate`, `log/slog`, `golangci-lint`, `govulncheck` |
| Estructura | Una carpeta por dominio en `internal/`, con `handler.go`, `service.go`, `repository.go` y `model.go` |
| Capas | El handler depende de una interfaz del service, y el service de una interfaz del repository. Así cada capa se prueba aislada |
| Errores | Envueltos con contexto, errores de dominio propios, y traducidos a HTTP solo en el handler. Nunca se exponen errores internos al cliente |
| Pruebas | Tabla de casos. El service con un repositorio falso; el repository contra PostgreSQL real. Cobertura mínima de 80 % en la capa de servicio |

### react-frontend

Se usa siempre que se crea o modifica código en `frontend/`.

| Tema | Lo que establece |
|---|---|
| Herramientas | React 19, TypeScript estricto, Vite, React Router, TanStack Query, React Hook Form con Zod, Tailwind CSS |
| Estructura | `app/`, `api/`, `components/` y una carpeta por funcionalidad en `features/` |
| Datos | Nunca se llama a `fetch` desde un componente: se usa un hook. Los tipos de la API se generan desde el contrato |
| Interfaz | Cada vista con datos implementa los estados cargando, vacío, error y éxito. Elementos semánticos y navegación por teclado |
| Seguridad | Nada de `dangerouslySetInnerHTML`, nada de tokens en `localStorage` |
| Pruebas | Vitest y Testing Library, probando lo que ve el usuario. Playwright para flujos completos |

### postgres-db

Se usa al crear tablas, migraciones, índices o consultas.

| Tema | Lo que establece |
|---|---|
| Migraciones | Numeradas, cada `up` con su `down`. Una migración aplicada nunca se edita. Los cambios peligrosos en tablas grandes, en varios pasos |
| Tablas | Nombres en inglés, en plural y `snake_case`. Siempre `id`, `created_at` y `updated_at`. Fechas con zona horaria. Dinero nunca en `FLOAT` |
| Integridad | Claves foráneas explícitas, `NOT NULL` por defecto, restricciones `UNIQUE` y `CHECK` en la base de datos y no solo en el código |
| Consultas | Siempre parametrizadas, sin `SELECT *`, paginación por cursor para listas grandes |

## Las skills de flujo

Describen el paso a paso de cada tipo de trabajo. Las ejecuta el orquestador.

| Skill | Cuándo se usa | Qué hace | Página |
|---|---|---|---|
| `equipo-feature` | Se pide construir, agregar o cambiar una funcionalidad | El flujo completo en siete fases, desde la especificación hasta el Pull Request, con las puertas de aprobación | [Construir una funcionalidad](funcionalidad.md) |
| `equipo-bug` | Se reporta un error | Diagnóstico, prueba que lo reproduce, arreglo mínimo, validación y registro | [Corregir un bug](bugs.md) |
| `equipo-revision` | Antes de abrir o aprobar un Pull Request, o al pedir una revisión | Lanza QA, revisión y seguridad en paralelo y consolida un veredicto | [El equipo de agentes](equipo-de-agentes.md#quién-escribe-no-aprueba) |
| `equipo-retomar` | Al iniciar cada sesión, o al preguntar por dónde iban | Reconstruye el estado a partir de los archivos y de git. Solo lee | [Retomar el trabajo](retomar.md) |

Estas skills son las que hacen que el proceso sea el mismo cada vez. El orquestador no improvisa el orden de las fases: lo lee.

## El formato de una skill

Una skill sigue el estándar abierto `SKILL.md`, que entienden las tres herramientas:

```markdown
---
name: go-backend
description: Convenciones para escribir backend en Go (estructura, capas, errores, HTTP, pruebas). Usar siempre que se cree o modifique código en backend/.
---
# Backend en Go — convenciones

## Estructura
…
```

| Campo | Qué define |
|---|---|
| `name` | El nombre de la skill, igual al de su carpeta |
| `description` | Qué contiene y **cuándo usarla**. El agente decide si la carga leyendo esta frase |

El cuerpo es texto libre. Funciona mejor cuando es concreto: reglas cortas, la estructura de carpetas dibujada y un ejemplo de código.

Codex y OpenCode leen `.agents/skills/` directamente. Claude Code lee una copia en `.claude/skills/`, que produce `make sincronizar`.

## Cuándo cambiar una skill

La señal más clara: **un mismo error aparece en varias funcionalidades**. Si el revisor rechaza tres veces lo mismo, el problema no es el desarrollador sino que la convención no está escrita.

| Situación | Qué hacer |
|---|---|
| Los agentes repiten un error de código | Agrega la regla a la skill del stack |
| El proyecto adopta una librería nueva | Agrégala a la skill, con su forma de uso |
| Un flujo siempre se atasca en el mismo paso | Ajusta la skill de flujo correspondiente |
| La regla debe cumplirse sin excepción | Va en la constitución, no en una skill |

Las skills vienen del kit: el cambio se hace en el repositorio del kit, o el proyecto excluye la skill para tener su versión. Ver [Personalizar un proyecto](personalizar.md).

## Agregar una skill propia

Crea una carpeta nueva en `.agents/skills/` con su `SKILL.md`:

```bash
mkdir -p .agents/skills/pagos-stripe
# escribe .agents/skills/pagos-stripe/SKILL.md
make sincronizar
```

Una skill que no viene del kit es del proyecto: las actualizaciones nunca la tocan.

Buenos candidatos para una skill propia: las convenciones de una integración externa, las reglas de un dominio de negocio particular, o un procedimiento que el equipo repite.

> [!TIP]
> Escribe la descripción pensando en el agente que la va a leer para decidir si la carga. "Usar al crear o modificar cualquier código que cobre, reembolse o consulte pagos" funciona mucho mejor que "Skill de pagos".

## Siguientes pasos

- [Roles](roles.md): quién usa cada skill.
- [La constitución](la-constitucion.md): las reglas que están por encima de las skills.
- [Personalizar un proyecto](personalizar.md): skills y roles propios.
