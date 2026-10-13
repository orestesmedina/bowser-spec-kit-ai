# La constitución

- [Introducción](#introducción)
- [Para qué sirve](#para-qué-sirve)
- [Las dos partes](#las-dos-partes)
- [Los tres niveles](#los-tres-niveles)
- [Qué dicen los principios](#qué-dicen-los-principios)
- [Las reglas del proyecto](#las-reglas-del-proyecto)
- [Quién la aplica](#quién-la-aplica)
- [Cómo está protegida](#cómo-está-protegida)
- [Cambiarla](#cambiarla)
- [Si algo falla](#si-algo-falla)
- [Constitución, skills y plan](#constitución-skills-y-plan)
- [Límites](#límites)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

La constitución es un documento corto con las reglas que **todo el código del proyecto debe cumplir**, sin importar qué funcionalidad sea ni qué agente la escriba. Los agentes la leen en `.specify/memory/constitution.md`.

## Para qué sirve

Un agente toma cientos de decisiones pequeñas al programar. Sin reglas fijas, cada funcionalidad saldría con una arquitectura distinta, un manejo de errores distinto y un nivel de pruebas distinto.

La constitución fija esas decisiones una sola vez. Los agentes la leen antes de cada fase, el arquitecto no puede proponer un plan que la contradiga, y los revisores rechazan el código que no la cumple.

También le da a quien aprueba un criterio objetivo: no hace falta discutir en cada Pull Request si las pruebas son suficientes, porque el mínimo ya está escrito.

## Las dos partes

Hay reglas que valen para cualquier proyecto ("los secretos no van en el repositorio") y reglas que solo tienen sentido en uno ("el servidor se organiza en tres capas"). Por eso la constitución se escribe en dos archivos, y el que leen los agentes se genera juntándolos:

| Archivo | Qué contiene | De quién es | Cómo cambia |
|---|---|---|---|
| `equipo/principios.md` | Los principios: lo que vale con cualquier tecnología | Del kit | Solo al actualizar el kit |
| `equipo/reglas.md` | Las reglas del proyecto: su arquitectura, sus mínimos de prueba, sus bibliotecas obligatorias | Del proyecto | Con un commit aprobado por dirección técnica |
| `.specify/memory/constitution.md` | Los principios y, debajo, las reglas | Generado | Nunca a mano: lo escribe `make sync` |

Los principios no nombran ninguna tecnología. Todo lo que dependa de la tecnología va en las reglas del proyecto.

Un proyecto recién instalado tiene los principios y un archivo de reglas vacío.

## Los tres niveles

Cada regla usa una de tres palabras, y la palabra dice cuánto pesa:

| Nivel | Significa |
|---|---|
| **DEBE** | Obligatorio. Incumplirlo es motivo de rechazo |
| **DEBERÍA** | Recomendado. Se puede no cumplir con una justificación en el plan |
| **PUEDE** | Opcional |

## Qué dicen los principios

Tienen ocho secciones:

| Sección | En resumen |
|---|---|
| **I. La especificación manda** | El código implementa la especificación aprobada, no la interpreta. Todo cambio de comportamiento pasa primero por `spec.md` |
| **II. Arquitectura** | La arquitectura es del proyecto. Cuando dos partes se comunican, su contrato se escribe antes que el código. Toda dependencia nueva se justifica en el plan |
| **III. Pruebas** | Toda tarea incluye sus pruebas, salvo que las reglas del proyecto digan otro alcance. Nada se integra con pruebas fallando. El mínimo de cobertura lo fija el proyecto |
| **IV. Seguridad** | Consultas siempre parametrizadas, validación de toda entrada en el servidor, datos escapados al mostrarlos, contraseñas con bcrypt o argon2, secretos solo en variables de entorno, autenticación y autorización verificadas en el servidor, dependencias auditadas |
| **V. Calidad de código** | El código pasa el formato y la revisión del proyecto. Funciones cortas |
| **VI. Base de datos** | Todo cambio de esquema queda en un archivo versionado, con la forma de revertirlo. Uno ya aplicado nunca se modifica |
| **VII. Operación** | Configuración por variables de entorno. El proyecto se levanta en local con pasos documentados |
| **VIII. Gobierno** | La especificación, el plan y los despliegues a producción requieren aprobación de una persona. Dice también qué pueden hacer las reglas del proyecto |

El texto completo son unas cincuenta líneas, y vale la pena leerlo entero.

Dos puntos de la sección VIII importan en la práctica:

- **Las reglas del proyecto pueden agregar o endurecer los principios, y solo pueden reducirlos donde el principio lo permite expresamente.** Hoy lo permite uno solo, el de las pruebas: un proyecto puede escribir "sin pruebas en el panel" o "solo pruebas de la API". Los de seguridad no se pueden reducir.
- **En un proyecto existente, lo que hoy no cumple un principio se registra como deuda, y el código nuevo debe cumplirlo.** La deuda se anota en las [convenciones del proyecto](convenciones-del-proyecto.md), que tienen una sección para eso.

## Las reglas del proyecto

`equipo/reglas.md` es un archivo de texto con las reglas propias, escritas con los mismos tres niveles. Un ejemplo:

```markdown
# Constitución: reglas del proyecto

## Arquitectura
- El servidor DEBE seguir tres capas: entrada, reglas de negocio y datos.

## Pruebas
- La cobertura mínima de las reglas de negocio DEBE ser 80 %.
- El panel de administración no lleva pruebas automáticas.
```

Qué va ahí y qué no:

| Va en las reglas | No va en las reglas |
|---|---|
| Lo que debe cumplirse sin excepción en este proyecto | Cómo se escribe el código hoy (nombres, estructura, patrones): eso son las [convenciones](convenciones-del-proyecto.md) |
| La arquitectura y sus límites | Las decisiones de una sola funcionalidad: eso es el plan |
| Mínimos de prueba y qué partes no se prueban | Qué comando ejecuta cada comprobación: eso es el [perfil](perfil-del-proyecto.md) |
| Bibliotecas obligatorias o prohibidas | |

Las propone el `arquitecto` al planificar: si el plan fija algo que debe valer para todo el proyecto, lo deja en `plan.md`, en una sección "Reglas propuestas para el proyecto". Una persona las copia a `equipo/reglas.md` si las aprueba.

Después de cambiar las reglas, regenera la constitución y haz el commit con la aprobación:

```bash
make sync
```

```bash
APPROVED_CONSTITUTION=1 git commit -m "docs: agrega una regla del proyecto"
```

## Quién la aplica

Una regla escrita no sirve si nadie la comprueba. Cada parte de la constitución tiene al menos un control detrás:

| Regla | Quién la comprueba |
|---|---|
| Arquitectura y reglas del proyecto | El `revisor-codigo`, en cada validación |
| Seguridad | El agente `seguridad`, y el verbo `auditar` del perfil en la integración continua |
| Formato y revisión | Los [hooks de git](hooks-de-git.md) y la [integración continua](integracion-continua.md), con los verbos `formato` y `revisar` |
| Cobertura mínima | El verbo `cobertura` del perfil: el comando del proyecto es el que falla por debajo del mínimo |
| Cambios de esquema que no se modifican | Los `inmutables` del perfil: hooks de git, hooks del agente e integración continua |
| Secretos fuera del repositorio | Los hooks de git, y la búsqueda de secretos de la integración continua |
| Aprobaciones | El orquestador, que se detiene en cada puerta |

## Cómo está protegida

La constitución es lo más protegido del proyecto, porque cambiarla cambia las reglas para todos:

- **En Claude Code**, el agente no puede editar ninguno de los tres archivos: un [hook del agente](hooks-del-agente.md) lo bloquea.
- **En cualquier herramienta**, el hook de git rechaza un commit que modifique las reglas o los principios sin la aprobación, y uno donde el archivo generado no coincida con sus dos fuentes.
- **En GitHub**, la integración continua avisa si un Pull Request toca los principios o las reglas, y `CODEOWNERS` exige la aprobación de quien decide.

## Cambiarla

Depende de qué parte:

- **Una regla de este proyecto:** edita `equipo/reglas.md`, como en [Las reglas del proyecto](#las-reglas-del-proyecto).
- **Un principio, para todos los proyectos que usan el kit:** el cambio se hace en el repositorio del kit y llega con `make update-kit`. Cuando llega así, los controles lo dejan pasar, porque ya fue aprobado allá.
- **Un principio, solo en este proyecto:** casi nunca hace falta, porque las reglas del proyecto pueden endurecerlo. Si aun así el proyecto necesita otros principios, agrega `equipo/principios.md` a `"kit.excluir"` en `equipo/config.json`. Desde ese momento es del proyecto, deja de recibir las mejoras del kit y cada cambio pide la aprobación.

> [!WARNING]
> Un agente nunca cambia la constitución por su cuenta, aunque se lo pidas en el chat. Si una regla estorba, lo correcto es que el agente lo señale y una persona decida.

Antes de cambiar una regla, conviene preguntarse si el problema es la regla o un caso que no encaja. Para un caso puntual, lo normal es dejar la excepción justificada en el `plan.md` de esa funcionalidad.

## Si algo falla

| Mensaje | Por qué | Qué hacer |
|---|---|---|
| `La constitución cambió: las reglas del proyecto (equipo/reglas.md)` | El commit modifica o borra las reglas sin la aprobación | Si dirección técnica lo aprueba, repite el commit con `APPROVED_CONSTITUTION=1`. Si no, revierte el cambio |
| `La constitución cambió: los principios (equipo/principios.md)` | Alguien editó los principios en el proyecto | Revierte el cambio: los principios se cambian en el kit |
| `La configuración de agentes o la constitución generada están desactualizadas` | Cambiaron las reglas y no se regeneró, o alguien editó `.specify/memory/constitution.md` a mano | `make sync` y repite el commit |
| `Bloqueado: la constitución (principios y reglas del proyecto) solo se modifica con aprobación…` | Un agente intentó editarla en Claude Code | El agente propone el texto y una persona lo aplica |

## Constitución, skills y plan

Todos dicen cómo se construye, a distinto nivel:

| | Qué define | Alcance | Ejemplo |
|---|---|---|---|
| **Constitución: principios** | Lo no negociable en cualquier proyecto | Todos los proyectos | "Solo consultas parametrizadas" |
| **Constitución: reglas** | Lo no negociable en este proyecto | Todo el proyecto, siempre | "El servidor sigue tres capas" |
| **[Skills](skills.md) de tecnología y convenciones** | Cómo se escribe el código | Todo el código de una tecnología o de una parte | "Los errores se devuelven con contexto" |
| **Plan** | Decisiones de una funcionalidad | Una funcionalidad | "El registro usa una tabla `users` con estas columnas" |

Si chocan, manda la de arriba: un plan no puede contradecir la constitución.

## Límites

- **Ningún control comprueba que las reglas del proyecto no contradigan un principio.** Lo revisa la persona que aprueba el cambio.
- **"Deuda" no tiene fecha.** El principio pide registrarla y que el código nuevo cumpla, pero nada obliga a pagarla.
- **Un proyecto puede declarar que no lleva pruebas.** Los principios lo permiten si queda escrito en las reglas y aprobado; ahí los revisores tienen menos con qué validar.
- **En Claude Code el agente no puede escribir en `equipo/reglas.md`:** propone el texto y lo aplica una persona. En las demás herramientas puede editarlo, y el control es el del commit.

## Siguientes pasos

- [Capas de control](capas-de-control.md): todas las protecciones del kit, juntas.
- [Convenciones del proyecto](convenciones-del-proyecto.md): cómo escribe el código este proyecto, y dónde se anota la deuda.
- [Skills](skills.md): el estándar de cada tecnología.
- [Aprobaciones](aprobaciones.md): cómo comprobar que un plan respeta la constitución.
