# Guía de actualización

- [Introducción](#introducción)
- [Cómo se numeran las versiones](#cómo-se-numeran-las-versiones)
- [Actualizar un proyecto](#actualizar-un-proyecto)
- [Leer las novedades](#leer-las-novedades)
- [Pasos manuales](#pasos-manuales)
- [Cuando el kit recomienda otros modelos](#cuando-el-kit-recomienda-otros-modelos)
- [Cuando la actualización se detiene](#cuando-la-actualización-se-detiene)
    - [Si el proyecto no tiene perfil](#si-el-proyecto-no-tiene-perfil)
- [Después de actualizar](#después-de-actualizar)
- [Lo que queda pendiente](#lo-que-queda-pendiente)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit mejora con el tiempo, y cada proyecto decide cuándo adoptar una versión nueva. Actualizar es un comando, pero conviene saber qué hace, qué no hace y qué revisar después.

> [!NOTE]
> **¿Tu proyecto usa una versión 1.x?** Pasar a la 2.0 tiene pasos obligatorios: sigue [Migrar a la 2.0](migrar-a-2.md), que usa los comandos de esta página en orden.

## Cómo se numeran las versiones

El kit usa tres números, por ejemplo `1.7.1`:

| Cambia | Significa | Qué esperar |
|---|---|---|
| El tercero (`1.7.0` → `1.7.1`) | Correcciones y documentación | Nada que hacer |
| El segundo (`1.6.4` → `1.7.0`) | Funciones nuevas, compatibles | Puede traer pasos opcionales |
| El primero (`1.x` → `2.0.0`) | El proyecto debe hacer algo a mano para seguir funcionando | Lee los pasos antes de actualizar. Para la 2.0: [Migrar a la 2.0](migrar-a-2.md) |

La versión instalada en un proyecto está en `.kit-manifest.json`. Cada cambio queda registrado en las [novedades de cada versión](../CHANGELOG.md).

## Actualizar un proyecto

Desde la raíz del proyecto, con la rama al día y sin cambios pendientes:

```bash
make update-kit
```

El comando hace tres cosas:

1. Trae la última versión del kit al submódulo.
2. Instala: reemplaza los archivos del kit que cambiaron, agrega los nuevos y borra los que el kit eliminó.
3. Regenera la configuración de los agentes y muestra las novedades.

Lo que **no** hace: tocar las semillas (`equipo/config.json`, `equipo/reglas.md`, `.github/CODEOWNERS`, `.env.example`) ni ningún archivo propio del proyecto, como su `docker-compose.yml`. En `.gitignore` solo cambia el bloque del kit; si una versión nueva saca reglas de ese bloque, las deja escritas debajo, como del proyecto.

Al terminar, revisa los cambios y guárdalos:

```bash
git status
git add . && git commit -m "chore: actualiza kit de desarrollo"
```

## Leer las novedades

`make update-kit` muestra al final lo que cambió entre la versión que tenías y la nueva. Para volver a verlo en cualquier momento:

```bash
make news                # historial completo
make news SINCE=1.6.0    # solo desde una versión
```

## Pasos manuales

Algunas versiones traen una sección **Al actualizar**: cosas que el kit no puede hacer por ti. `make update-kit` las reúne al final, de la versión más antigua a la más nueva:

```
⚠ PASOS MANUALES AL ACTUALIZAR:
  - docker-compose.yml es una semilla y no se actualiza solo. Si tu proyecto todavía tiene…  (1.6.2)
  - En local, instala Node 24 (nvm install 24)…  (1.6.2)
```

Hazlos **antes** del commit de la actualización. Suelen ser de tres tipos: un cambio a una semilla que el kit no puede tocar, una herramienta que hay que instalar en cada máquina, o un comando que hay que ejecutar una vez.

## Cuando el kit recomienda otros modelos

Los modelos de cada agente están en `equipo/config.json`, que es del proyecto. Si la versión nueva del kit recomienda una distribución distinta, `make update-kit` lo avisa pero no cambia nada. Para adoptarla:

```bash
make update-models
```

Muestra qué cambiaría, pide confirmación y copia **solo** la asignación de modelos. El resto de tu configuración (herramientas activas, temperaturas, exclusiones) se conserva. Después, reinicia el agente de código.

## Cuando la actualización se detiene

```
✗ Estos archivos del kit fueron modificados en este proyecto:
    .githooks/pre-commit
```

Alguien editó en el proyecto un archivo que viene del kit. La actualización no lo pisa: se detiene y te deja decidir.

| Si el cambio… | Haz esto |
|---|---|
| Le sirve a todos los proyectos | Llévalo al repositorio del kit y vuelve a actualizar. Ver [Cómo contribuir](contribuir.md) |
| Es propio de este proyecto | Agrega el archivo a `"kit.excluir"` en `equipo/config.json`. Ver [Personalizar un proyecto](personalizar.md) |
| Fue un error | Descártalo con `make install-kit FORCE=1`. Guarda una copia en `.kit-respaldo/` |

> [!WARNING]
> `FORCE=1` es una decisión de una persona, no de un agente. Antes de usarlo, mira qué cambió: ese cambio local puede ser importante.

### Si el proyecto no tiene perfil

Hasta la versión 1.22.0, un proyecto sin [perfil](perfil-del-proyecto.md) funcionaba igual: el kit suponía Go y PostgreSQL en `backend/` y React en `frontend/`. Desde la 1.23.0 el kit no supone nada. Si un proyecto así se actualiza sin crear el perfil, dejan de funcionar `make test`, `make lint`, `make ci` y los demás verbos, los controles del commit dejan de revisar el formato y las migraciones, y los agentes pierden las skills `go-backend`, `postgres-db` y `react-frontend`.

Por eso, si el proyecto viene de una versión anterior, no tiene perfil y tiene `backend/` o `frontend/`, la actualización se detiene antes de cambiar nada:

```text
✗ Este proyecto no tiene perfil (equipo/perfil.json), y desde la versión 1.23.0 el kit lo necesita.
  …
  No se cambió nada en el proyecto.
  Opciones:
  • Recomendado: crea el perfil antes de seguir. En el chat, escribe /bowser-profile y revísalo. Sin hacer commit todavía, repite: make instalar-kit
    Al terminar, haz un solo commit con todo (el control te pide confirmar el perfil).
  • Si prefieres crearlo después, actualiza igual con: make instalar-kit FORZAR=1 (también descarta los cambios locales a archivos del kit, con respaldo).
  Guía completa: .bowser-spec-kit-ai/docs/migrar-a-2.md
```

Los comandos que nombra son los que entiende el `Makefile` que el proyecto tiene en ese momento, que todavía es el de la versión anterior. Si la versión instalada es anterior a la 1.12.0, no tiene `/bowser-profile`: el mensaje lo dice y solo ofrece la segunda salida, forzar y crear el perfil después.

El commit va al final porque el submódulo ya quedó en la versión nueva y los archivos del kit en la raíz todavía no: hasta que termine la instalación, el control del commit lo rechaza con `Los archivos del kit no coinciden`. Es lo esperado.

Si eliges forzar, la actualización termina y avisa de lo que no va a funcionar hasta que crees el perfil.

> [!NOTE]
> Un proyecto que ya tenía perfil, o que no tiene ni `backend/` ni `frontend/`, se actualiza sin detenerse. Un proyecto instalado desde la 1.23.0 tampoco se detiene: nunca dependió de esa suposición.

## Después de actualizar

Cuatro comprobaciones rápidas:

```bash
make doctor          # el entorno y el kit, al día
make check-kit       # los archivos del proyecto coinciden con el kit
make upgrade         # lo que el proyecto todavía tiene que hacer
make ci              # lo mismo que hará la integración continua
```

Si la versión nueva trae controles nuevos, el primer commit o el primer Pull Request puede ser rechazado por algo que antes no se revisaba. Es lo esperado: corrige lo que indique el mensaje.

## Lo que queda pendiente

Una actualización cambia los archivos del kit, pero hay cosas que no puede decidir sola: crear el perfil, redactar la integración continua del proyecto, revisar las reglas que heredó de la constitución anterior. Sobre todo al pasar de la 1.x a la 2.0, un proyecto queda con varios de esos pendientes repartidos.

Cuando hay alguno, `make install-kit` (y por eso también `make update-kit`) lo avisa al terminar:

```text
  ! Al proyecto le quedan 9 pendientes para aprovechar el kit: make upgrade
```

`make upgrade` los muestra agrupados según quién los resuelve:

```text
Lo que le falta al proyecto para aprovechar el kit

Lo resuelve un agente (escribe el comando en el chat)
  • El perfil no declara `requisitos`: make doctor no sabe qué herramientas necesita una máquina para este proyecto. En el chat: /bowser-profile
  • .github/workflows/ci.yml es el que instalaba el kit: repite lo que ya hace bowser.yml (kit, agentes y secretos) y copia los comandos en vez de ejecutar los verbos. En el chat: /bowser-ci

Lo resuelve una persona
  • equipo/reglas.md todavía tiene las reglas que traía la constitución anterior (de Go, React y PostgreSQL, o la constitución completa del proyecto). Conserva las que le sirven a este proyecto, borra las demás y quita el párrafo que lo explica. El commit pide APPROVED_CONSTITUTION=1.

Avisos
  • .github/workflows/ci.yml usa `make db-migrate`, que se retiró en la 1.23.0: defínelo en proyecto.mk.
  • Recomendado: la parte backend no tiene convenciones propias (cómo nombra y organiza las cosas este proyecto). En el chat: /bowser-conventions

Arreglos mecánicos (nombres anteriores, comandos retirados y scripts que pasan a tools/)
  scripts/cobertura.py → tools/cobertura.py
  equipo/perfil.json
    -        "cobertura": "python3 ../scripts/cobertura.py"
    +        "cobertura": "python3 ../tools/cobertura.py"
  .github/workflows/ci.yml
    -      - run: make cobertura PARTE=backend
    -      - run: make test-backend
    +      - run: make coverage PART=backend
    +      - run: make test PART=backend

¿Aplicar estos arreglos? [s/N]
```

Lo que revisa:

| Pendiente | Quién lo resuelve |
|---|---|
| El proyecto no tiene [perfil](perfil-del-proyecto.md), o el perfil no declara sus `requisitos` | Un agente: `/bowser-profile` |
| La integración continua no ejecuta algún verbo del perfil, o el `ci.yml` es el que instalaba el kit | Un agente: `/bowser-ci` |
| Una parte no tiene [convenciones propias](convenciones-del-proyecto.md) | Un agente: `/bowser-conventions`. Es una recomendación |
| `equipo/reglas.md` todavía tiene las reglas que traía la constitución anterior | Una persona (el commit pide `APPROVED_CONSTITUTION=1`) |
| `.gitignore` tiene, debajo del bloque del kit, reglas de tecnología que el kit traía antes | Una persona |
| `kit.excluir` nombra un archivo que ya no es del kit | Una persona: quitar la línea |
| Los workflows o `proyecto.mk` usan los [nombres anteriores](comandos.md#nombres-anteriores) de los comandos, opciones o confirmaciones | **Arreglo mecánico** |
| Usan `make test-backend` o `make test-frontend`, y el perfil tiene esa parte | **Arreglo mecánico**: `make test PART=backend`. Si no hay reemplazo (`make db-migrate`), es un aviso |
| `scripts/` tiene archivos que no son del kit (los que el kit retiró y el proyecto conservó, como `scripts/cobertura.py`) | **Arreglo mecánico**: pasan a `tools/`, y se corrige quién los nombra (el perfil, `proyecto.mk`, los workflows). Los que el proyecto puso en `kit.excluir` no se tocan |

Los arreglos mecánicos solo se aplican con tu confirmación: `make upgrade` pregunta en la terminal, y `make upgrade YES=1` los aplica sin preguntar. Si cambia el perfil, regenera los agentes y te recuerda que su commit pide `APPROVED_PROFILE=1`. Nunca hace commit.

> [!TIP]
> En el chat, `/bowser-upgrade` hace lo mismo y además te acompaña en lo que necesita un agente o una persona, en orden: primero los arreglos mecánicos, después el perfil, la integración continua y las convenciones, y al final lo que te toca revisar a ti. `/bowser-upgrade ver` solo muestra la lista.

Cuando no queda nada:

```text
✓ Nada pendiente: el proyecto aprovecha todo lo que el kit trae.
```

## Siguientes pasos

- [Migrar a la 2.0](migrar-a-2.md): el paso de la 1.x a la 2.0, de punta a punta.
- [Novedades de cada versión](../CHANGELOG.md): el historial completo.
- [El kit como submódulo](submodulo.md): cómo funciona la instalación por dentro.
- [Problemas comunes](problemas-comunes.md): errores frecuentes al actualizar.
