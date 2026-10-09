# Comandos

- [Introducción](#introducción)
- [Los que más vas a usar](#los-que-más-vas-a-usar)
- [Dentro de la herramienta](#dentro-de-la-herramienta)
- [Estado y costos](#estado-y-costos)
- [Entorno local](#entorno-local)
- [Calidad y pruebas](#calidad-y-pruebas)
- [Código generado](#código-generado)
- [Agentes](#agentes)
- [El kit](#el-kit)
- [Comandos propios del proyecto](#comandos-propios-del-proyecto)
- [Quién ejecuta qué](#quién-ejecuta-qué)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Todo lo que el kit sabe hacer se ejecuta con `make`, desde la raíz del proyecto. Esta página lista cada comando: qué hace, cuándo usarlo y qué opciones tiene. Los más usados se pueden pedir también sin salir del chat: ver [Dentro de la herramienta](#dentro-de-la-herramienta).

Para ver la lista en la terminal:

```bash
make help
```

Las opciones se pasan después del comando, en mayúsculas: `make costos TODO=1`.

## Los que más vas a usar

| Comando | Para qué |
|---|---|
| `make doctor` | ¿Mi entorno está bien? |
| `make estado` | ¿Por dónde vamos? |
| `make up` | Levantar la base de datos |
| `make ci` | ¿Esto va a pasar en GitHub? |
| `make actualizar-kit` | Traer la última versión del kit |

## Dentro de la herramienta

Los comandos que más usa una persona tienen un equivalente que se escribe en el chat de Claude Code, Codex u OpenCode. El agente ejecuta el `make` correspondiente y explica el resultado en lenguaje simple, así que no hace falta abrir una terminal.

| Comando | Ejecuta | Qué responde |
|---|---|---|
| `/bowser-status` | `make estado` | Por dónde vamos y cuál es el próximo paso |
| `/bowser-costs` | `make costos` | Cuánto ha costado la tarea actual, y qué agentes pesan más |
| `/bowser-doctor` | `make doctor` | Si el entorno está bien y, si no, cómo arreglar cada cosa |
| `/bowser-update-kit` | `make actualizar-kit` | Qué trajo la versión nueva y qué pasos hay que hacer a mano |
| `/bowser-news` | `make novedades` | Qué cambió en el kit, versión por versión |
| `/bowser-models` | `make modelos` | Qué modelo usa cada agente |
| `/bowser-profile` | `make profile` | Crea o actualiza el [perfil del proyecto](perfil-del-proyecto.md) mirando el código, y lo propone para que lo apruebes |

Cómo se escriben en cada herramienta:

| Herramienta | Se escribe | Con opciones |
|---|---|---|
| Claude Code | `/bowser-status` | `/bowser-status todo` |
| OpenCode | `/bowser-status` | `/bowser-status todo` |
| Codex | `$bowser-status` | `$bowser-status` y la opción en la misma frase: "con todo" |

Opciones: `/bowser-status todo` incluye lo terminado; `/bowser-costs todo` resume el proyecto y `/bowser-costs hoy` cotiza a precios actuales; `/bowser-news 1.9.0` muestra desde esa versión; `/bowser-profile ver` solo muestra el perfil, sin proponer cambios.

Lo que estos comandos **no** hacen por su cuenta, porque son decisión de una persona: cerrar el costo (`make costos CERRAR=1`), forzar una instalación (`FORZAR=1`), cambiar modelos, hacer el commit de una actualización del kit y confirmar un cambio del perfil (`APROBADO_PERFIL=1`). Los proponen y esperan.

> [!NOTE]
> Después de `make actualizar-kit` o de `make sincronizar`, abre una sesión nueva para que la herramienta vea los comandos nuevos o cambiados.

**Límites.** En Claude Code y en Codex el comando solo se carga cuando lo escribes: no ocupa espacio en la conversación mientras tanto. En OpenCode, además de aparecer como comando, el agente lo ve en su lista de skills (OpenCode lee `.claude/skills/` y `.agents/skills/`), así que cada comando le suma una línea de descripción. Codex no recibe lo que escribes después del nombre como un dato aparte: lo lee de la frase.

**Cómo cambiarlos o agregar uno.** Cada comando es un archivo en `equipo/comandos/`, y `make sincronizar` genera el formato de cada herramienta. Ver [Una fuente, varias herramientas](una-fuente-varias-herramientas.md#cómo-se-traduce-un-comando) y [Personalizar un proyecto](personalizar.md#roles-skills-y-comandos-propios).

## Estado y costos

### `make estado`

Muestra por dónde va el proyecto: el roadmap, la funcionalidad de la rama actual con su fase y sus aprobaciones, las tareas hechas, los hallazgos abiertos, el costo acumulado y el próximo paso. Desde la rama principal, también el trabajo en curso en otras ramas. No modifica nada.

- **Cuándo:** al empezar el día, al cambiar de rama, o cuando no recuerdas en qué quedó algo.
- **Opciones:** `TODO=1` incluye las funcionalidades ya terminadas.
- **Más:** [Retomar el trabajo](retomar.md).

### `make costos`

Registra el consumo de IA nuevo en la funcionalidad de la rama actual y muestra su costo por agente y modelo.

- **Cuándo:** normalmente lo ejecuta el orquestador al abrir y al cerrar cada sesión. A mano, si trabajaste sin pasar por él.
- **Opciones:**

| Opción | Efecto |
|---|---|
| `TODO=1` | Resumen de todo el proyecto. No registra |
| `PRECIOS=hoy` | Cuánto costaría a precios actuales. No guarda nada |
| `CERRAR=1` | Registra lo pendiente y cierra el costo. Solo después de aprobar el Pull Request |

- **Más:** [Costos de IA](costos.md).

## Entorno local

### `make doctor`

Revisa que tu máquina y el proyecto tengan todo: herramientas y sus versiones, Docker corriendo, hooks activos, `.env`, kit al día y Spec Kit inicializado. En Windows, además, que no se estén usando programas del lado de Windows.

- **Cuándo:** después de instalar, al clonar un proyecto, y siempre que algo falle de forma rara. Es el primer paso de cualquier diagnóstico.
- **Más:** [Instalación](instalacion.md#verificar-la-instalación).

### `make up` y `make down`

Levantan y detienen los servicios locales (PostgreSQL) con Docker Compose. `make down` conserva los datos.

- **Cuándo:** `make up` al empezar a trabajar.

### `make db-migrate`

Aplica las migraciones pendientes a la base de datos indicada en `DATABASE_URL`.

- **Cuándo:** después de traer cambios que incluyen migraciones nuevas, o al crear una.

### `make instalar-hooks`

Activa los hooks de git en tu copia del repositorio y les da permiso de ejecución.

- **Cuándo:** una vez, justo después de clonar un proyecto. Quien instala el kit no lo necesita.
- **Más:** [Hooks de git](hooks-de-git.md#cómo-se-activan).

## Calidad y pruebas

| Comando | Qué ejecuta | Cuándo |
|---|---|---|
| `make test` | Todas las pruebas, de backend y de frontend | Antes de dar algo por terminado |
| `make test-backend` | Pruebas unitarias y de integración de Go | Al trabajar solo en el backend |
| `make test-frontend` | Pruebas del frontend | Al trabajar solo en el frontend |
| `make lint` | Formato, `go vet`, `golangci-lint`, y lint y tipos del frontend | Antes de un commit grande |
| `make cobertura` | La cobertura de la capa de servicio. Falla bajo 80 % | Después de agregar lógica de negocio |
| `make security` | Vulnerabilidades en las dependencias de Go y de Node | Después de agregar o actualizar una dependencia |
| `make ci` | Todo lo anterior, más la verificación del código generado | Antes de abrir un Pull Request |

Esto es lo que ejecutan en un proyecto **sin perfil**: asumen `backend/` en Go y `frontend/` en React. Las pruebas de integración necesitan la base de datos levantada: `make up`.

En un proyecto **con [perfil](perfil-del-proyecto.md)**, cada comando ejecuta el verbo que el proyecto declaró para cada una de sus partes:

| Comando | Verbo del perfil |
|---|---|
| `make test` | `probar` |
| `make lint` | `formato` y `revisar` |
| `make cobertura` | `cobertura` |
| `make security` | `auditar` |
| `make generar`, `make verificar-generados` | `generar` |
| `make ci` | Los seis, y al final un [resumen](perfil-del-proyecto.md#el-resumen-de-make-ci) de qué se comprobó y qué quedó sin comprobar |

`PARTE=nombre` limita el comando a una parte: `make test PARTE=api`. Una parte que no define un verbo se omite con un aviso. `make test-backend` y `make test-frontend` no leen el perfil.

### `make profile`

Muestra el perfil del proyecto y comprueba que esté bien escrito. No modifica nada.

- **Cuándo:** antes de confirmar un cambio en el perfil, o para ver qué comando ejecuta cada verbo.
- **Opciones:** `DETECTAR=1` no muestra el perfil: mira el proyecto y lista, en JSON, las tecnologías y carpetas que encuentra. Es lo que usa `/bowser-profile` para redactarlo.
- **Más:** [El perfil del proyecto](perfil-del-proyecto.md).

### `make skills`

Muestra el catálogo de skills de tecnología del kit: la madurez de cada una (`probada` o `redactada`), cuáles tiene el proyecto y cuáles pide el perfil sin tenerlas todavía. No modifica nada.

- **Cuándo:** al escribir el perfil, para saber qué skills existen, o cuando un aviso dice que una skill falta.
- **Más:** [Skills](skills.md#el-catálogo-de-skills-de-tecnología).

Más: [Integración continua](integracion-continua.md) y [Cobertura y código generado](cobertura-y-codigo-generado.md).

## Código generado

| Comando | Qué hace | Cuándo |
|---|---|---|
| `make generar` | Regenera el código de sqlc y los tipos de la API | Después de cambiar una consulta SQL, una migración o el contrato de la API |
| `make verificar-generados` | Regenera y falla si quedó algo sin subir a git | Antes de abrir un Pull Request |

Más: [Cobertura y código generado](cobertura-y-codigo-generado.md#código-generado).

## Agentes

| Comando | Qué hace | Cuándo |
|---|---|---|
| `make sincronizar` | Genera la configuración de Claude Code, Codex y OpenCode a partir de los roles, las skills y `equipo/config.json` | Después de cambiar un rol, una skill o la configuración |
| `make modelos` | Muestra qué modelo y qué temperatura usa cada agente en cada herramienta, y de dónde sale cada valor | Para comprobar un cambio de modelos, o diagnosticar por qué un agente usa el que usa |
| `make verificar-agentes` | Comprueba que lo generado esté al día. No cambia nada | Lo usan el hook de git y la integración continua |
| `make actualizar-modelos` | Aplica al proyecto los modelos que recomienda la versión instalada del kit. Muestra las diferencias y pide confirmación | Cuando `make actualizar-kit` avisa que el kit recomienda otros modelos |

`make actualizar-modelos SI=1` aplica sin preguntar.

Más: [Una fuente, varias herramientas](una-fuente-varias-herramientas.md) y [Modelos por agente](modelos.md).

## El kit

| Comando | Qué hace | Cuándo |
|---|---|---|
| `make actualizar-kit` | Trae la última versión del kit, la instala y muestra las novedades y los pasos manuales | Para adoptar una versión nueva |
| `make instalar-kit` | Copia el kit desde el submódulo a la raíz, regenera los agentes y activa los hooks | La primera vez, y después de cambiar de versión del submódulo a mano |
| `make verificar-kit` | Comprueba que los archivos del kit en el proyecto coincidan con el submódulo | Cuando el hook dice que no coinciden: muestra cuál |
| `make novedades` | El historial de cambios del kit | Para volver a ver qué trajo una versión |

Opciones:

| Opción | En | Efecto |
|---|---|---|
| `FORZAR=1` | `instalar-kit` | Pisa los archivos del kit modificados en el proyecto, guardando un respaldo en `.kit-respaldo/`. **Decisión de una persona** |
| `DESDE=1.6.0` | `novedades` | Muestra solo desde esa versión |
| `KIT=carpeta` | Todos | Indica otra carpeta para el submódulo, si no es `.bowser-spec-kit-ai/` |

La primera instalación, cuando el proyecto todavía no tiene `Makefile`, se ejecuta así:

```bash
make -f .bowser-spec-kit-ai/Makefile instalar-kit
```

Más: [Guía de actualización](actualizacion.md) y [El kit como submódulo](submodulo.md).

> [!NOTE]
> `make test-kit` ejecuta las pruebas automáticas del kit. Solo existe en el repositorio del kit, no en los proyectos: ver [Cómo contribuir](contribuir.md#probar-un-cambio).

## Comandos propios del proyecto

El proyecto puede agregar sus comandos en un archivo `proyecto.mk`. Aparecen en `make help` junto a los del kit. Ver [Personalizar un proyecto](personalizar.md#comandos-propios).

## Quién ejecuta qué

No hace falta memorizar la lista: la mayoría de los comandos los ejecuta alguien por ti.

| Quién | Comandos |
|---|---|
| **El orquestador,** en cada sesión | `make estado`, `make costos` |
| **Los desarrolladores,** al terminar cada tarea | Las pruebas y los linters de su capa, `make generar` |
| **Los revisores** | `make test`, `make security` |
| **Los hooks y la integración continua** | `make verificar-kit`, `make verificar-agentes` y sus equivalentes |
| **Tú** | `make doctor`, `make up`, `make estado`, `make ci`, `make actualizar-kit` |

Dos comandos son **decisión de una persona**, nunca de un agente por su cuenta: `make instalar-kit FORZAR=1` y `make actualizar-modelos`. Lo mismo vale para el commit de un cambio en el perfil, que se confirma con `APROBADO_PERFIL=1`. Y `make costos CERRAR=1` solo se ejecuta después de que apruebas el Pull Request.

## Siguientes pasos

- [Problemas comunes](problemas-comunes.md): qué hacer cuando un comando falla.
- [Estructura de carpetas](estructura.md): los archivos sobre los que actúan estos comandos.
