# De la idea al roadmap

- [Introducción](#introducción)
- [Por qué no pedir "hazme la aplicación"](#por-qué-no-pedir-hazme-la-aplicación)
- [1. Escribir la idea](#1-escribir-la-idea)
- [2. Pedir el roadmap](#2-pedir-el-roadmap)
- [3. La primera funcionalidad: la estructura base](#3-la-primera-funcionalidad-la-estructura-base)
- [4. Seguir con el roadmap](#4-seguir-con-el-roadmap)
- [Los estados de una funcionalidad](#los-estados-de-una-funcionalidad)
- [Cambiar el roadmap](#cambiar-el-roadmap)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Antes de construir la primera funcionalidad hay dos documentos que escribir: la **idea** del producto y el **roadmap**, la lista ordenada de funcionalidades. Esta página explica cómo se hacen y por qué se hacen en ese orden.

Este paso es **nivel producto**: no usa Spec Kit ni el flujo de funcionalidad. Se trabaja directamente con el orquestador.

## Por qué no pedir "hazme la aplicación"

Un agente puede generar una aplicación entera de una sola instrucción. El resultado suele compilar y casi nunca es lo que se necesitaba: miles de líneas construidas sobre suposiciones que nadie revisó, imposibles de aprobar con criterio.

El proceso funciona al revés: se divide el producto en **funcionalidades pequeñas e independientes**, y se construyen una por una, cada una con su especificación, su plan y su revisión. Así, cada aprobación es sobre algo que una persona puede leer y entender.

## 1. Escribir la idea

```bash
mkdir -p docs/producto
cp docs/plantillas/idea.md docs/producto/idea.md
```

Complétala **tú, sin IA**. La plantilla pide el problema, los usuarios, cómo se resuelve hoy, qué sería un éxito, lo mínimo que debe hacer el producto, qué queda fuera y las restricciones.

Tres reglas para escribirla:

- **Una página.** Frases cortas.
- **Describe el problema, no la solución.** Nada de lenguajes, frameworks ni bases de datos: eso lo decide el arquitecto después.
- **Si no puedes llenar una sección, es una pregunta para el cliente**, no para el agente.

> [!NOTE]
> La idea se escribe sin IA porque es la materia prima de todo lo demás. Un agente puede redactar una idea que suena muy bien y que no es la tuya. El orquestador puede señalarte huecos, pero no inventa reglas de negocio.

## 2. Pedir el roadmap

Con la idea escrita, pídele al orquestador:

> Lee docs/producto/idea.md. Propón el MVP más pequeño y divídelo en funcionalidades independientes, en orden de dependencia. La primera debe ser la estructura base del proyecto. Guárdalo en docs/producto/roadmap.md con el formato de docs/plantillas/roadmap.md. No escribas specs todavía.

El resultado es una tabla:

| # | Funcionalidad | Qué incluye | Depende de | Estado | Rama / PR |
|---|---|---|---|---|---|
| 1 | Estructura base | Backend con `/healthz`, frontend, PostgreSQL, Docker Compose e integración continua | — | pendiente | |
| 2 | Registro de usuarios | Alta con correo y contraseña, confirmación por correo | 1 | pendiente | |
| 3 | Inicio de sesión | Entrada, cierre de sesión y recuperación de contraseña | 2 | pendiente | |

**Revísala y ajústala.** El orquestador propone; el orden y el alcance los decides tú. Buenas preguntas al revisar:

- ¿Cada funcionalidad se puede entregar y probar por separado?
- ¿Alguna es demasiado grande? Si no cabe en una línea, probablemente son dos.
- ¿El orden respeta las dependencias?
- ¿Falta algo de lo mínimo, o sobra algo que puede esperar?

## 3. La primera funcionalidad: la estructura base

La primera funcionalidad de cualquier proyecto es el esqueleto:

> Usa la skill equipo-feature: estructura base del proyecto. Backend en Go con endpoint /healthz conectado a PostgreSQL, frontend React que muestre el estado del backend, Docker Compose levantando todo, y CI en verde.

Parece poco, pero es la más importante: **los agentes copian los patrones del código que ya existe**. Un esqueleto limpio y aprobado hace que todo lo siguiente salga consistente. Uno descuidado se multiplica en cada funcionalidad.

Vale la pena revisar con cuidado su plan y su Pull Request, aunque "no haga nada" visible.

## 4. Seguir con el roadmap

Una funcionalidad a la vez, con el flujo de [Construir una funcionalidad](funcionalidad.md), **integrando cada una antes de empezar la siguiente**.

```bash
make estado
```

muestra en todo momento qué está terminado, qué está en curso y qué sigue.

## Los estados de una funcionalidad

El orquestador actualiza la columna **Estado** del roadmap a medida que avanza el trabajo:

| Estado | Cuándo |
|---|---|
| `pendiente` | Todavía no se empezó |
| `en curso` | Se creó su especificación |
| `en revisión` | Tiene un Pull Request abierto |
| `terminada` | Una persona confirmó que se integró |
| `pausada` | Se empezó y se dejó a propósito. El motivo queda en su `estado.md` |

El cambio de estado se hace en la rama de la funcionalidad y llega a la rama principal cuando se integra. Mientras tanto, `make estado` muestra desde la rama principal el trabajo en curso de las otras ramas.

## Cambiar el roadmap

El roadmap no es un contrato. Cambia cuando el cliente cambia de prioridades, cuando una funcionalidad resulta más grande de lo previsto o cuando aparece algo que no estaba.

Edítalo directamente o pídeselo al orquestador, y deja una línea en la sección **Cambios al roadmap** con la fecha, qué cambió y quién lo decidió. Lo que no hay que hacer es cambiar el alcance de una funcionalidad ya empezada sin pasar por su especificación. Ver [Construir una funcionalidad](funcionalidad.md#cambiar-algo-ya-aprobado).

## Siguientes pasos

- [Construir una funcionalidad](funcionalidad.md): el flujo completo, paso a paso.
- [Desarrollo guiado por especificaciones](sdd.md): por qué el proceso es así.
- [Retomar el trabajo](retomar.md): cómo se lleva el estado entre sesiones.
