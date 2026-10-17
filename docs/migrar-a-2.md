# Migrar a la 2.0

- [Introducción](#introducción)
- [Qué cambia en la 2.0](#qué-cambia-en-la-20)
- [Antes de empezar](#antes-de-empezar)
    - [Probar primero en una copia aislada](#probar-primero-en-una-copia-aislada)
- [La migración paso a paso](#la-migración-paso-a-paso)
    - [1. Crear el perfil, si no lo tiene](#1-crear-el-perfil-si-no-lo-tiene)
    - [2. Actualizar el kit](#2-actualizar-el-kit)
    - [3. Ver lo que falta y aplicar los arreglos mecánicos](#3-ver-lo-que-falta-y-aplicar-los-arreglos-mecánicos)
    - [4. Completar el perfil](#4-completar-el-perfil)
    - [5. Escribir las convenciones](#5-escribir-las-convenciones)
    - [6. Rehacer la integración continua](#6-rehacer-la-integración-continua)
    - [7. Revisar las reglas y el .gitignore](#7-revisar-las-reglas-y-el-gitignore)
    - [8. Comprobar y abrir el Pull Request](#8-comprobar-y-abrir-el-pull-request)
- [Cuando algo falla](#cuando-algo-falla)
- [Límites](#límites)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Hasta la versión 1.x, el kit estaba pensado para un tipo de proyecto: Go y PostgreSQL en `backend/` y React en `frontend/`. En la 2.0 deja de suponer cualquier tecnología: lo que el proyecto es (sus partes, sus carpetas, cómo se prueba cada una) lo declara el propio proyecto en su [perfil](perfil-del-proyecto.md).

Esta página lleva un proyecto que usa una versión 1.x del kit hasta la 2.0, de punta a punta. Es la única actualización con pasos obligatorios: las demás son un comando (ver [Guía de actualización](actualizacion.md)).

Toma una tarde. La mayor parte del trabajo la hacen agentes con los comandos del chat; a ti te toca revisar y aprobar.

## Qué cambia en la 2.0

| Antes (1.x) | Desde la 2.0 | Qué te toca |
|---|---|---|
| Sin perfil, el kit suponía Go, React y PostgreSQL | Sin perfil, el kit no ejecuta ningún control de tecnología | Crear el perfil (pasos 1 y 4) |
| Las skills `go-backend`, `react-frontend` y `postgres-db` llegaban a todos los proyectos | Llegan solo las que el perfil nombra, y traen el estándar oficial de cada tecnología, sin elecciones de bibliotecas ni de estructura | Nombrarlas en el perfil y escribir las [convenciones](convenciones-del-proyecto.md) propias (pasos 4 y 5) |
| El kit gestionaba `.github/workflows/ci.yml` | El `ci.yml` es del proyecto; el kit trae solo `bowser.yml` | Rehacerlo con `/bowser-ci` (paso 6) |
| La constitución era del kit, con reglas de Go, React y PostgreSQL | Se genera con los principios del kit (sin tecnología) y las reglas del proyecto (`equipo/reglas.md`) | Revisar las reglas que heredó el proyecto (paso 7) |
| El `.gitignore` del kit traía reglas de Go y de Node | El bloque del kit solo cubre secretos, editores y archivos del kit | Revisar las reglas que quedaron debajo (paso 7) |
| Los comandos de `make` estaban en español (`make actualizar-kit`, `make cobertura PARTE=api`) | Están en inglés (`make update-kit`, `make coverage PART=api`); los anteriores siguen funcionando hasta después de la 2.0 | Nada obligatorio; `make upgrade` los cambia en tus workflows (paso 3) |
| `make test-backend`, `make test-frontend`, `make db-migrate`, `scripts/cobertura.py` | Se retiraron | `make upgrade` los reemplaza o te dice qué hacer (paso 3) |
| Claude Code formateaba el código al editarlo y podía ejecutar `go test` o `npm run` | Solo puede ejecutar `make`, `docker compose` y git sin preguntar; el formato lo revisa el commit | Reiniciar Claude Code después de actualizar |

El detalle de cada cambio está en las [novedades de cada versión](../CHANGELOG.md), de la 1.13.0 en adelante.

## Antes de empezar

- **Trabaja en una rama**, con la rama principal al día y sin cambios pendientes: `git switch -c chore/kit-2.0`.
- **Que no haya funcionalidades a medio hacer en esa rama.** Las que estén en otras ramas siguen como están; al traerles la rama principal después, recibirán el kit nuevo.
- **Avisa al equipo.** Después de la migración, cada persona debe reiniciar su herramienta y ejecutar `make doctor`, que le pedirá las herramientas que el perfil declare.
- **Quien apruebe necesita poder confirmar dos cosas en el commit:** el perfil (`APPROVED_PROFILE=1`) y las reglas del proyecto (`APPROVED_CONSTITUTION=1`). Son decisiones de una persona, no de un agente.

### Probar primero en una copia aislada

Si el proyecto es importante, haz la migración primero en una copia, y solo cuando salga bien repítela en el proyecto. La copia tiene que quedar **aislada** del proyecto real antes de que un agente trabaje en ella, porque los agentes ejecutan comandos de verdad: hacen push, levantan contenedores y corren pruebas que pueden vaciar una base de datos.

1. **Clona a una carpeta aparte**, nunca sobre tu carpeta de trabajo:

   ```bash
   git clone --recurse-submodules <tu-repositorio> ~/prueba-migracion && cd ~/prueba-migracion
   ```

2. **Quítale el remoto**, para que nada de lo que pase ahí llegue a GitHub:

   ```bash
   git remote remove origin
   ```

   El submódulo del kit sí necesita su remoto para traer la versión nueva. Si no quieres que la copia tenga ningún remoto, copia el kit a mano en `.bowser-spec-kit-ai/` antes del paso 2.

3. **Dale puertos propios.** Si el proyecto levanta servicios con `make up`, cambia en el `.env` de la copia los puertos y los nombres (por ejemplo `5433` en vez de `5432`), para que no choquen con los contenedores del proyecto real ni se conecten a ellos.

4. **Apaga los contenedores del proyecto real** mientras un agente trabaja en la copia. Las pruebas de integración suelen vaciar las tablas de la base de pruebas, y una variable mal copiada basta para que sea la del proyecto real.

> [!WARNING]
> Nunca pruebes la migración en la carpeta donde trabajas todos los días. Si algo sale mal en la copia, la borras y empiezas de nuevo; en tu carpeta de trabajo tendrías que deshacerlo a mano.

## La migración paso a paso

### 1. Crear el perfil, si no lo tiene

Si el proyecto ya tiene `equipo/perfil.json`, salta al paso 2.

Si no lo tiene, créalo **antes** de actualizar, con la versión que el proyecto tiene instalada. El comando existe desde la 1.12.0. En el chat:

```text
/bowser-profile
```

Un agente lee el proyecto y propone el perfil: sus partes, la carpeta de cada una y el comando de cada verbo (probar, revisar, formatear…). Revísalo con `make profile` y guárdalo:

```bash
make profile
git add equipo/perfil.json
APROBADO_PERFIL=1 git commit -m "chore: agrega el perfil del proyecto"
```

La confirmación se llama `APROBADO_PERFIL` porque la entiende el kit que el proyecto tiene en este momento; desde la 1.22.0 también acepta `APPROVED_PROFILE`.

> [!NOTE]
> Si el proyecto está en una versión anterior a la 1.12.0, no tiene `/bowser-profile`. Actualiza igual en el paso 2: la actualización se detendrá y te ofrecerá seguir con `FORZAR=1`; el perfil lo creas en el paso 4.

### 2. Actualizar el kit

Con el `Makefile` que el proyecto tiene ahora:

```bash
make actualizar-kit
```

Si el proyecto ya estaba en la 1.22.0 o posterior, el comando se llama `make update-kit` (el anterior también funciona).

Al terminar, la actualización muestra las novedades, reúne los pasos manuales de cada versión y avisa cuántos pendientes le quedan al proyecto:

```text
  ! Al proyecto le quedan 7 pendientes para aprovechar el kit: make upgrade
```

> [!NOTE]
> Si el proyecto viene de una versión muy anterior, la lista de pasos manuales es larga y junta los de todas las versiones intermedias. Algunos ya no aplican, porque una versión posterior los reemplazó (instalar herramientas que el kit dejó de usar, o "tu proyecto sigue funcionando sin perfil"). Para pasar a la 2.0, sigue esta página: los pasos 3 a 7 cubren lo que sigue vigente.

Guarda la actualización sola, antes de cambiar nada más, para que sea fácil de revisar:

```bash
git add . && git commit -m "chore: actualiza el kit a la 2.0"
```

Y **reinicia tu herramienta** (Claude Code, Codex u OpenCode), para que lea los roles, los comandos y los permisos nuevos.

> [!NOTE]
> Si la actualización se detiene con "Este proyecto no tiene perfil", es porque no hiciste el paso 1. Ver [Si el proyecto no tiene perfil](actualizacion.md#si-el-proyecto-no-tiene-perfil).

### 3. Ver lo que falta y aplicar los arreglos mecánicos

```bash
make upgrade
```

Muestra los pendientes agrupados según quién los resuelve: un agente, una persona o un arreglo mecánico. Los arreglos mecánicos son cambios de texto que no requieren ninguna decisión: cambiar `make cobertura PARTE=api` por `make coverage PART=api` en tus workflows, `make test-backend` por `make test PART=backend`, o mover `scripts/cobertura.py` a `tools/` y corregir quién lo nombra. Te muestra el cambio exacto y pregunta antes de aplicarlo.

Lo que dice cada pendiente y cómo se resuelve está en [Lo que queda pendiente](actualizacion.md#lo-que-queda-pendiente). Los pasos que siguen resuelven el resto, en orden.

> [!TIP]
> En el chat, `/bowser-upgrade` hace lo mismo que esta página desde el paso 3: aplica los arreglos mecánicos después de tu "sí" y te acompaña en los pasos 4 a 7.

### 4. Completar el perfil

El perfil que existía antes de la 2.0 suele estar incompleto: le faltan los `requisitos` de la máquina, las `skills` de cada parte y, si hay base de datos, el rol `dev-dba`. Vuelve a pedirlo, ahora con el kit nuevo:

```text
/bowser-profile
```

El agente revisa el perfil que existe y propone lo que falta. Comprueba con `make profile` que:

- **cada parte tenga sus `roles`**: una parte sin rol no tiene quién la trabaje;
- **las skills de tecnología estén nombradas** (`go-backend`, `react-frontend`, `postgres-db`, `php`…): la actualización retiró del proyecto las que el perfil no nombraba. Al agregarlas, `make install-kit` las vuelve a traer;
- **la base de datos declare sus `inmutables`** (por ejemplo `migrations/*.sql`): es lo que el hook del agente y el commit protegen;
- **estén los `requisitos`**: lo que `make doctor` revisará en cada máquina.

```bash
make install-kit       # trae las skills que el perfil nombra
git add . && APPROVED_PROFILE=1 git commit -m "chore: completa el perfil del proyecto"
```

### 5. Escribir las convenciones

Las skills de tecnología de la 2.0 traen solo el estándar oficial de cada tecnología. Lo que tu proyecto hace a su manera (cómo nombra los archivos, cómo organiza las carpetas, qué bibliotecas usa) lo escribe un agente leyendo el código, una vez por parte:

```text
/bowser-conventions api
```

Revisa lo que propone: es lo que los agentes van a copiar. Ver [Convenciones del proyecto](convenciones-del-proyecto.md).

### 6. Rehacer la integración continua

Si el proyecto tiene el `ci.yml` que instalaba el kit, ahora es suyo, pero sigue repitiendo lo que ya hace `bowser.yml` y copia los comandos en vez de ejecutar los verbos del perfil. Pide que lo rehaga:

```text
/bowser-ci
```

Comprueba que la integración continua ejecute todos los verbos:

```bash
make check-ci
```

> [!WARNING]
> Si la rama principal en GitHub exige comprobaciones por nombre, actualízalas: agrega las de `bowser.yml` ("Kit, agentes y perfil al día", "Archivos inmutables y constitución", "Búsqueda de secretos") y quita las que el `ci.yml` nuevo ya no tenga. Si no, ningún Pull Request se podrá aprobar.

### 7. Revisar las reglas y el .gitignore

Estos dos los decides tú: el kit no puede saber qué reglas le sirven a tu proyecto.

**`equipo/reglas.md`.** La actualización dejó ahí lo que la constitución anterior decía de tecnología (o la constitución completa, si el proyecto tenía una propia), con un párrafo que lo explica. Léelo y:

- conserva las reglas que le sirven al proyecto, corrigiéndolas si hace falta. Por ejemplo, "80 % de cobertura en `service/`" solo vale si el proyecto tiene esa carpeta;
- borra las que no son de tu tecnología. Un proyecto que no es de Go, React y PostgreSQL las borra todas;
- borra las que ya dicen los [principios del kit](la-constitucion.md) o las convenciones;
- quita el párrafo que explica de dónde vienen.

Si el proyecto no tiene pruebas, escribe aquí cuál es su alcance: los principios exigen pruebas "salvo que las reglas del proyecto digan otro alcance".

**`.gitignore`.** Debajo del bloque del kit quedaron las reglas de Go y de Node que el kit traía antes. Deja las que le sirven al proyecto y borra las demás.

```bash
make sync
git add . && APPROVED_CONSTITUTION=1 git commit -m "chore: reglas propias del proyecto"
```

### 8. Comprobar y abrir el Pull Request

```bash
make upgrade     # ✓ Nada pendiente: el proyecto aprovecha todo lo que el kit trae.
make doctor      # las herramientas que pide el perfil
make ci          # lo mismo que hará la integración continua
```

Si `make upgrade` todavía muestra algo, vuelve al paso que corresponda. Cuando todo pase, sube la rama y abre el Pull Request. En GitHub corren `bowser.yml` y el `ci.yml` nuevo: si alguno falla, el mensaje dice qué corregir.

Después de aprobarlo, cada persona del equipo trae la rama principal, reinicia su herramienta y ejecuta `make doctor`.

## Cuando algo falla

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| `Este proyecto no tiene perfil (equipo/perfil.json), y desde la versión 1.23.0 el kit lo necesita` | Actualizaste sin hacer el paso 1 | Ver [Si el proyecto no tiene perfil](actualizacion.md#si-el-proyecto-no-tiene-perfil) |
| `Estos archivos del kit fueron modificados en este proyecto` | Alguien editó un archivo del kit en el proyecto | Ver [Cuando la actualización se detiene](actualizacion.md#cuando-la-actualización-se-detiene) |
| `make test` responde que el proyecto no tiene perfil | Seguiste con `FORZAR=1` sin perfil | Haz el paso 4 |
| Cada edición en Claude Code muestra un error de un hook que no existe | Claude Code sigue con la configuración anterior | Reinícialo |
| Claude Code pide confirmación para `go test`, `npm run` u otra herramienta | Desde la 2.0 solo tiene permitido `make` | Es lo esperado: que use `make test`. Ver [Hooks del agente](hooks-del-agente.md#los-permisos) |
| Faltan los comandos de Spec Kit (`/speckit-plan` o `/speckit.plan`) | Los borró una versión entre la 1.11.0 y la 1.17.0 | `specify init --here --force --integration <herramienta>` |
| El commit se rechaza por formato | El código ya no se formatea solo al editarlo | Ejecuta el formateador de tu proyecto |
| `make upgrade` sigue diciendo que el `ci.yml` es el que instalaba el kit | Todavía tiene los grupos que ahora ejecuta `bowser.yml` | Haz el paso 6 |

Para los demás errores, ver [Problemas comunes](problemas-comunes.md).

## Límites

- `make upgrade` reconoce el `ci.yml` que instalaba el kit por los nombres de sus grupos. Si el proyecto lo modificó a fondo, puede no reconocerlo; `/bowser-ci` lo revisa igual.
- Los nombres anteriores solo se cambian dentro de las llamadas a `make` de los workflows y de `proyecto.mk`. La documentación del proyecto queda como está.
- La migración no toca tu código ni tus specs: solo los archivos del kit, el perfil, el workflow y las reglas.

## Siguientes pasos

- [El perfil del proyecto](perfil-del-proyecto.md): todo lo que puede declarar.
- [Integración continua](integracion-continua.md): qué hace `bowser.yml` y qué hace tu `ci.yml`.
- [La constitución](la-constitucion.md): los principios del kit y las reglas del proyecto.
- [Guía de actualización](actualizacion.md): las actualizaciones de siempre, después de la 2.0.
