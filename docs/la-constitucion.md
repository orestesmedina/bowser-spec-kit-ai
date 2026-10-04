# La constitución

- [Introducción](#introducción)
- [Para qué sirve](#para-qué-sirve)
- [Los tres niveles](#los-tres-niveles)
- [Qué establece](#qué-establece)
- [Quién la aplica](#quién-la-aplica)
- [Cómo está protegida](#cómo-está-protegida)
- [Cambiarla](#cambiarla)
- [Constitución, skills y plan](#constitución-skills-y-plan)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

La constitución es un documento corto con las reglas que **todo el código del proyecto debe cumplir**, sin importar qué funcionalidad sea ni qué agente la escriba. Vive en `.specify/memory/constitution.md`.

## Para qué sirve

Un agente toma cientos de decisiones pequeñas al programar. Sin reglas fijas, cada funcionalidad saldría con una arquitectura distinta, un manejo de errores distinto y un nivel de pruebas distinto.

La constitución fija esas decisiones una sola vez. Los agentes la leen antes de cada fase, el arquitecto no puede proponer un plan que la contradiga, y los revisores rechazan el código que no la cumple.

También le da a quien aprueba un criterio objetivo: no hace falta discutir en cada Pull Request si las pruebas son suficientes, porque el mínimo ya está escrito.

## Los tres niveles

Cada regla usa una de tres palabras, y la palabra dice cuánto pesa:

| Nivel | Significa |
|---|---|
| **DEBE** | Obligatorio. Incumplirlo es motivo de rechazo |
| **DEBERÍA** | Recomendado. Se puede no cumplir con una justificación en el plan |
| **PUEDE** | Opcional |

## Qué establece

La constitución que trae el kit tiene ocho secciones:

| Sección | En resumen |
|---|---|
| **I. La especificación manda** | El código implementa la especificación aprobada, no la interpreta. Todo cambio de comportamiento pasa primero por `spec.md` |
| **II. Arquitectura** | Un repositorio con `backend/` (Go) y `frontend/` (React + TypeScript). El backend en capas: `handler → service → repository`. La comunicación entre ambos, una API REST documentada en OpenAPI, y el contrato se escribe antes que el código |
| **III. Pruebas** | Toda tarea incluye sus pruebas. Cobertura mínima de 80 % en la capa de servicio. Nada se integra con pruebas fallando |
| **IV. Seguridad** | Consultas siempre parametrizadas, validación de toda entrada en el backend, contraseñas con bcrypt o argon2, secretos solo en variables de entorno, autenticación y autorización verificadas en el servidor |
| **V. Calidad de código** | Go sin errores de `gofmt`, `go vet` y `golangci-lint`. TypeScript en modo estricto. Funciones cortas |
| **VI. Base de datos** | Los cambios de esquema, solo con migraciones versionadas. Una migración aplicada nunca se modifica |
| **VII. Observabilidad y operación** | Logs estructurados, un endpoint `/healthz`, configuración por variables de entorno, y todo levanta con `docker compose up` |
| **VIII. Gobierno** | La especificación, el plan y los despliegues a producción requieren aprobación de una persona |

El texto completo son unas cincuenta líneas, y vale la pena leerlo entero.

## Quién la aplica

Una regla escrita no sirve si nadie la comprueba. Cada parte de la constitución tiene al menos un control detrás:

| Regla | Quién la comprueba |
|---|---|
| Arquitectura por capas, manejo de errores | El `revisor-codigo`, en cada validación |
| Seguridad | El agente `seguridad`, y `govulncheck` y `npm audit` en la integración continua |
| Formato y linters | Los [hooks de git](hooks-de-git.md) y la [integración continua](integracion-continua.md) |
| Cobertura mínima | `make cobertura` y la integración continua. Ver [Cobertura y código generado](cobertura-y-codigo-generado.md) |
| Migraciones que no se modifican | Los hooks de git, los hooks del agente y la integración continua |
| Secretos fuera del repositorio | Los hooks de git, y la búsqueda de secretos de la integración continua |
| Aprobaciones | El orquestador, que se detiene en cada puerta |

## Cómo está protegida

La constitución es el archivo más protegido del proyecto, porque cambiarla cambia las reglas para todos:

- **En Claude Code**, el agente no puede editarla: un [hook del agente](hooks-del-agente.md) lo bloquea.
- **En cualquier herramienta**, el hook de git rechaza un commit que la modifique.
- **En GitHub**, la integración continua avisa si un Pull Request la toca, y `CODEOWNERS` exige la aprobación de quien decide sobre las reglas.

## Cambiarla

La constitución viene del kit, así que hay dos caminos según a quién afecte el cambio:

- **Para todos los proyectos que usan el kit:** el cambio se hace en el repositorio del kit y llega con `make actualizar-kit`. Cuando llega así, los controles lo dejan pasar, porque ya fue aprobado allá.
- **Solo para un proyecto:** agrega `.specify/memory/constitution.md` a `"kit.excluir"` en `equipo/config.json`. Desde ese momento es del proyecto. El commit que la modifique requiere una autorización explícita de quien decide:
  ```bash
  APROBADO_CONSTITUCION=1 git commit -m "docs: ajusta la constitución"
  ```

> [!WARNING]
> Un agente nunca cambia la constitución por su cuenta, aunque se lo pidas en el chat. Si una regla estorba, lo correcto es que el agente lo señale y una persona decida.

Antes de cambiar una regla, conviene preguntarse si el problema es la regla o un caso que no encaja. Para un caso puntual, lo normal es dejar la excepción justificada en el `plan.md` de esa funcionalidad.

## Constitución, skills y plan

Los tres dicen cómo se construye, a distinto nivel:

| | Qué define | Alcance | Ejemplo |
|---|---|---|---|
| **Constitución** | Reglas no negociables | Todo el proyecto, siempre | "El backend sigue la arquitectura por capas" |
| **[Skills](skills.md) del stack** | Convenciones para escribir el código | Todo el código de una tecnología | "Envuelve los errores con `fmt.Errorf`" |
| **Plan** | Decisiones de una funcionalidad | Una funcionalidad | "El registro usa una tabla `users` con estas columnas" |

Si chocan, manda la de arriba: un plan no puede contradecir la constitución.

## Siguientes pasos

- [Capas de control](capas-de-control.md): todas las protecciones del kit, juntas.
- [Skills](skills.md): las convenciones del stack.
- [Aprobaciones](aprobaciones.md): cómo comprobar que un plan respeta la constitución.
