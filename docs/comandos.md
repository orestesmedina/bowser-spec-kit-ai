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
- [Nombres anteriores](#nombres-anteriores)
- [Quién ejecuta qué](#quién-ejecuta-qué)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Todo lo que el kit sabe hacer se ejecuta con `make`, desde la raíz del proyecto. Esta página lista cada comando: qué hace, cuándo usarlo y qué opciones tiene. Los más usados se pueden pedir también sin salir del chat: ver [Dentro de la herramienta](#dentro-de-la-herramienta).

Para ver la lista en la terminal:

```bash
make help
```

Las opciones se pasan después del comando, en mayúsculas: `make costs ALL=1`.

## Los que más vas a usar

| Comando | Para qué |
|---|---|
| `make doctor` | ¿Mi entorno está bien? |
| `make status` | ¿Por dónde vamos? |
| `make up` | Levantar los servicios locales del proyecto |
| `make ci` | ¿Esto va a pasar en GitHub? |
| `make update-kit` | Traer la última versión del kit |

## Dentro de la herramienta

Los comandos que más usa una persona tienen un equivalente que se escribe en el chat de Claude Code, Codex u OpenCode. El agente ejecuta el `make` correspondiente y explica el resultado en lenguaje simple, así que no hace falta abrir una terminal.

| Comando | Ejecuta | Qué responde |
|---|---|---|
| `/bowser-status` | `make status` | Por dónde vamos y cuál es el próximo paso |
| `/bowser-costs` | `make costs` | Cuánto ha costado la tarea actual, y qué agentes pesan más |
| `/bowser-doctor` | `make doctor` | Si el entorno está bien y, si no, cómo arreglar cada cosa |
| `/bowser-update-kit` | `make update-kit` | Qué trajo la versión nueva y qué pasos hay que hacer a mano |
| `/bowser-news` | `make news` | Qué cambió en el kit, versión por versión |
| `/bowser-models` | `make models` | Qué modelo usa cada agente |
| `/bowser-profile` | `make profile` | Crea o actualiza el [perfil del proyecto](perfil-del-proyecto.md) mirando el código, y lo propone para que lo apruebes |
| `/bowser-conventions` | — | Redacta las [convenciones propias del proyecto](convenciones-del-proyecto.md) leyendo su código, las compara con el estándar y las propone para que las apruebes |
| `/bowser-ci` | `make check-ci` | Redacta o actualiza la [integración continua del proyecto](integracion-continua.md#el-workflow-del-proyecto) desde el perfil, y la propone para que la apruebes |

Cómo se escriben en cada herramienta:

| Herramienta | Se escribe | Con opciones |
|---|---|---|
| Claude Code | `/bowser-status` | `/bowser-status todo` |
| OpenCode | `/bowser-status` | `/bowser-status todo` |
| Codex | `$bowser-status` | `$bowser-status` y la opción en la misma frase: "con todo" |

Opciones: `/bowser-status todo` incluye lo terminado; `/bowser-costs todo` resume el proyecto y `/bowser-costs hoy` cotiza a precios actuales; `/bowser-news 1.9.0` muestra desde esa versión; `/bowser-profile ver` solo muestra el perfil, sin proponer cambios; `/bowser-conventions api` redacta solo las de esa parte; `/bowser-ci ver` solo muestra qué verbos ejecuta hoy la integración continua.

Lo que estos comandos **no** hacen por su cuenta, porque son decisión de una persona: cerrar el costo (`make costs CLOSE=1`), forzar una instalación (`FORCE=1`), cambiar modelos, hacer el commit de una actualización del kit y confirmar un cambio del perfil (`APPROVED_PROFILE=1`). Los proponen y esperan.

> [!NOTE]
> Después de `make update-kit` o de `make sync`, abre una sesión nueva para que la herramienta vea los comandos nuevos o cambiados.

**Límites.** En Claude Code y en Codex el comando solo se carga cuando lo escribes: no ocupa espacio en la conversación mientras tanto. En OpenCode, además de aparecer como comando, el agente lo ve en su lista de skills (OpenCode lee `.claude/skills/` y `.agents/skills/`), así que cada comando le suma una línea de descripción. Codex no recibe lo que escribes después del nombre como un dato aparte: lo lee de la frase.

**Cómo cambiarlos o agregar uno.** Cada comando es un archivo en `equipo/comandos/`, y `make sync` genera el formato de cada herramienta. Ver [Una fuente, varias herramientas](una-fuente-varias-herramientas.md#cómo-se-traduce-un-comando) y [Personalizar un proyecto](personalizar.md#roles-skills-y-comandos-propios).

## Estado y costos

### `make status`

Muestra por dónde va el proyecto: el roadmap, la funcionalidad de la rama actual con su fase y sus aprobaciones, las tareas hechas, los hallazgos abiertos, el costo acumulado y el próximo paso. Desde la rama principal, también el trabajo en curso en otras ramas. No modifica nada.

- **Cuándo:** al empezar el día, al cambiar de rama, o cuando no recuerdas en qué quedó algo.
- **Opciones:** `ALL=1` incluye las funcionalidades ya terminadas.
- **Más:** [Retomar el trabajo](retomar.md).

### `make costs`

Registra el consumo de IA nuevo en la funcionalidad de la rama actual y muestra su costo por agente y modelo.

- **Cuándo:** normalmente lo ejecuta el orquestador al abrir y al cerrar cada sesión. A mano, si trabajaste sin pasar por él.
- **Opciones:**

| Opción | Efecto |
|---|---|
| `ALL=1` | Resumen de todo el proyecto. No registra |
| `PRICES=today` | Cuánto costaría a precios actuales. No guarda nada |
| `CLOSE=1` | Registra lo pendiente y cierra el costo. Solo después de aprobar el Pull Request |

- **Más:** [Costos de IA](costos.md).

## Entorno local

### `make doctor`

Revisa que tu máquina y el proyecto tengan todo: herramientas y sus versiones, hooks activos, `.env`, kit al día y Spec Kit inicializado. En Windows, además, que no se estén usando programas del lado de Windows.

Las herramientas van en dos grupos:

| Grupo | Qué revisa | De dónde sale |
|---|---|---|
| Herramientas base | Git, Python, `uv`, `jq`, `make`, Spec Kit y `gitleaks` | Fijo: es lo que el kit necesita en cualquier proyecto |
| Herramientas del proyecto | Las de su tecnología | De los [`requisitos`](perfil-del-proyecto.md#los-requisitos-de-la-máquina) del perfil. Sin perfil no revisa ninguna: avisa que falta |

Docker (instalado y corriendo) se revisa solo si el proyecto tiene un archivo de Docker Compose en la raíz o si su perfil lo pide.

- **Cuándo:** después de instalar, al clonar un proyecto, y siempre que algo falle de forma rara. Es el primer paso de cualquier diagnóstico.
- **Más:** [Instalación](instalacion.md#verificar-la-instalación).

### `make up` y `make down`

Levantan y detienen con Docker Compose los servicios locales del proyecto (su base de datos, por ejemplo). `make down` conserva los datos.

El kit no trae ningún servicio: lee el archivo que el proyecto tenga en la raíz (`compose.yaml`, `compose.yml`, `docker-compose.yaml` o `docker-compose.yml`), que crea el rol `devops`. Si no hay ninguno, los dos comandos terminan con error y este mensaje:

```
Este proyecto todavía no tiene entorno local: falta compose.yaml (o docker-compose.yml) en la raíz. Lo crea el rol devops con los servicios que el proyecto usa.
```

- **Cuándo:** `make up` al empezar a trabajar.

Aplicar las migraciones de la base de datos depende de la herramienta que use el proyecto: si lo necesita, es un [comando propio](#comandos-propios-del-proyecto) (por ejemplo, `make db-migrate` en su `proyecto.mk`).

### `make install-hooks`

Activa los hooks de git en tu copia del repositorio y les da permiso de ejecución.

- **Cuándo:** una vez, justo después de clonar un proyecto. Quien instala el kit no lo necesita.
- **Más:** [Hooks de git](hooks-de-git.md#cómo-se-activan).

## Calidad y pruebas

El kit no sabe cómo se prueba tu proyecto: lo dice su [perfil](perfil-del-proyecto.md). Cada comando ejecuta el verbo que el proyecto declaró para cada una de sus partes, dentro de la carpeta de la parte:

| Comando | Verbo del perfil | Cuándo |
|---|---|---|
| `make test` | `probar` | Antes de dar algo por terminado |
| `make lint` | `formato` y `revisar` | Antes de un commit grande |
| `make coverage` | `cobertura` | Después de agregar lógica de negocio |
| `make security` | `auditar` | Después de agregar o actualizar una dependencia |
| `make generate`, `make check-generated` | `generar` | Ver [Código generado](#código-generado) |
| `make ci` | Los seis, y al final un [resumen](perfil-del-proyecto.md#el-resumen-de-make-ci) de qué se comprobó y qué quedó sin comprobar | Antes de abrir un Pull Request |

`PART=nombre` limita el comando a una parte: `make test PART=api`. Una parte que no define un verbo se omite con un aviso.

Sin perfil, estos comandos no ejecutan nada y terminan con error:

```text
✗ Este proyecto no tiene perfil (equipo/perfil.json). Para crearlo, escribe en el chat: /bowser-profile
```

### `make profile`

Muestra el perfil del proyecto y comprueba que esté bien escrito. No modifica nada.

- **Cuándo:** antes de confirmar un cambio en el perfil, o para ver qué comando ejecuta cada verbo.
- **Opciones:** `DETECT=1` no muestra el perfil: mira el proyecto y lista, en JSON, las tecnologías y carpetas que encuentra. Es lo que usa `/bowser-profile` para redactarlo.
- **Más:** [El perfil del proyecto](perfil-del-proyecto.md).

### `make check-ci`

Dice qué verbos del perfil ejecuta la integración continua del proyecto, workflow por workflow, y avisa de los que no ejecuta ninguno. No modifica nada y siempre termina bien: es un aviso.

- **Cuándo:** después de cambiar el perfil o un workflow, y antes de dar por buena la integración continua de un proyecto.
- **Más:** [Integración continua](integracion-continua.md#comprobar-que-no-falta-nada).

### `make skills`

Muestra el catálogo de skills de tecnología del kit: la madurez de cada una (`probada` o `redactada`), cuáles tiene el proyecto y cuáles pide el perfil sin tenerlas todavía. No modifica nada.

- **Cuándo:** al escribir el perfil, para saber qué skills existen, o cuando un aviso dice que una skill falta.
- **Más:** [Skills](skills.md#el-catálogo-de-skills-de-tecnología).

Más: [Integración continua](integracion-continua.md) y [Cobertura y código generado](cobertura-y-codigo-generado.md).

## Código generado

| Comando | Qué hace | Cuándo |
|---|---|---|
| `make generate` | Ejecuta el verbo `generar` de cada parte: regenera el código que el proyecto genera a partir de otro archivo (consultas SQL, el contrato de la API…) | Después de cambiar lo que da origen a ese código |
| `make check-generated` | Regenera y falla si quedó algo sin subir a git | Antes de abrir un Pull Request |

Más: [Cobertura y código generado](cobertura-y-codigo-generado.md#código-generado).

## Agentes

| Comando | Qué hace | Cuándo |
|---|---|---|
| `make sync` | Genera la configuración de Claude Code, Codex y OpenCode a partir de los roles, las skills, `equipo/config.json` y el perfil del proyecto | Después de cambiar un rol, una skill, la configuración o el perfil |
| `make models` | Muestra qué modelo y qué temperatura usa cada agente en cada herramienta, y de dónde sale cada valor | Para comprobar un cambio de modelos, o diagnosticar por qué un agente usa el que usa |
| `make check-agents` | Comprueba que lo generado esté al día. No cambia nada | Lo usan el hook de git y la integración continua |
| `make update-models` | Aplica al proyecto los modelos que recomienda la versión instalada del kit. Muestra las diferencias y pide confirmación | Cuando `make update-kit` avisa que el kit recomienda otros modelos |

`make update-models YES=1` aplica sin preguntar.

Más: [Una fuente, varias herramientas](una-fuente-varias-herramientas.md) y [Modelos por agente](modelos.md).

## El kit

| Comando | Qué hace | Cuándo |
|---|---|---|
| `make update-kit` | Trae la última versión del kit, la instala y muestra las novedades y los pasos manuales | Para adoptar una versión nueva |
| `make install-kit` | Copia el kit desde el submódulo a la raíz, regenera los agentes y activa los hooks | La primera vez, y después de cambiar de versión del submódulo a mano |
| `make check-kit` | Comprueba que los archivos del kit en el proyecto coincidan con el submódulo | Cuando el hook dice que no coinciden: muestra cuál |
| `make news` | El historial de cambios del kit | Para volver a ver qué trajo una versión |

Opciones:

| Opción | En | Efecto |
|---|---|---|
| `FORCE=1` | `install-kit` | Pisa los archivos del kit modificados en el proyecto, guardando un respaldo en `.kit-respaldo/`. **Decisión de una persona** |
| `SINCE=1.6.0` | `news` | Muestra solo desde esa versión |
| `KIT=carpeta` | Todos | Indica otra carpeta para el submódulo, si no es `.bowser-spec-kit-ai/` |

La primera instalación, cuando el proyecto todavía no tiene `Makefile`, se ejecuta así:

```bash
make -f .bowser-spec-kit-ai/Makefile install-kit
```

Más: [Guía de actualización](actualizacion.md) y [El kit como submódulo](submodulo.md).

> [!NOTE]
> `make test-kit` ejecuta las pruebas automáticas del kit. Solo existe en el repositorio del kit, no en los proyectos: ver [Cómo contribuir](contribuir.md#probar-un-cambio).

## Comandos propios del proyecto

El proyecto puede agregar sus comandos en un archivo `proyecto.mk`. Aparecen en `make help` junto a los del kit. Ver [Personalizar un proyecto](personalizar.md#comandos-propios).

## Nombres anteriores

Hasta la versión 1.21.0, varios comandos de `make`, sus opciones y las confirmaciones del commit tenían nombre en español. Desde la 1.22.0 todos están en inglés, con el mismo nombre que su comando del chat: `/bowser-status` y `make status`.

**Los nombres anteriores siguen funcionando.** El comando hace lo mismo y al final avisa de cómo se llama ahora:

```bash
make estado
```

```text
Aviso: 'make estado' ahora se llama 'make status'. El nombre anterior se retirará en una versión futura.
```

| Antes | Ahora |
|---|---|
| `make estado` | `make status` |
| `make costos` | `make costs` |
| `make novedades` | `make news` |
| `make modelos` | `make models` |
| `make actualizar-modelos` | `make update-models` |
| `make sincronizar` | `make sync` |
| `make verificar-agentes` | `make check-agents` |
| `make instalar-kit` | `make install-kit` |
| `make actualizar-kit` | `make update-kit` |
| `make verificar-kit` | `make check-kit` |
| `make instalar-hooks` | `make install-hooks` |
| `make generar` | `make generate` |
| `make verificar-generados` | `make check-generated` |
| `make cobertura` | `make coverage` |

Las opciones y las confirmaciones se aceptan con los dos nombres, sin aviso:

| Antes | Ahora |
|---|---|
| `FORZAR=1` | `FORCE=1` |
| `DESDE=1.6.0` | `SINCE=1.6.0` |
| `TODO=1` | `ALL=1` |
| `CERRAR=1` | `CLOSE=1` |
| `PRECIOS=hoy` | `PRICES=today` |
| `SI=1` | `YES=1` |
| `DETECTAR=1` | `DETECT=1` |
| `PARTE=api` | `PART=api` |
| `APROBADO_PERFIL=1` | `APPROVED_PROFILE=1` |
| `APROBADO_CONSTITUCION=1` | `APPROVED_CONSTITUTION=1` |
| `APROBADO_COSTOS=1` | `APPROVED_COSTS=1` |

> [!NOTE]
> Los nombres anteriores se retiran en una versión posterior a la 2.0. Conviene cambiarlos ya en lo que el proyecto tenga escrito: su workflow de integración continua, `proyecto.mk` y su documentación. `make check-ci` entiende los dos nombres al leer los workflows.

No cambian los verbos del perfil (`formato`, `revisar`, `probar`, `cobertura`, `auditar`, `generar`): son contenido de `equipo/perfil.json`, no comandos. Tampoco las opciones de los scripts (`--verificar`, `--forzar`).

## Quién ejecuta qué

No hace falta memorizar la lista: la mayoría de los comandos los ejecuta alguien por ti.

| Quién | Comandos |
|---|---|
| **El orquestador,** en cada sesión | `make status`, `make costs` |
| **Los desarrolladores,** al terminar cada tarea | Las pruebas y los linters de su capa, `make generate` |
| **Los revisores** | `make test`, `make security` |
| **Los hooks y la integración continua** | `make check-kit`, `make check-agents` y sus equivalentes |
| **Tú** | `make doctor`, `make up`, `make status`, `make ci`, `make update-kit` |

Dos comandos son **decisión de una persona**, nunca de un agente por su cuenta: `make install-kit FORCE=1` y `make update-models`. Lo mismo vale para el commit de un cambio en el perfil, que se confirma con `APPROVED_PROFILE=1`. Y `make costs CLOSE=1` solo se ejecuta después de que apruebas el Pull Request.

## Siguientes pasos

- [Problemas comunes](problemas-comunes.md): qué hacer cuando un comando falla.
- [Estructura de carpetas](estructura.md): los archivos sobre los que actúan estos comandos.
