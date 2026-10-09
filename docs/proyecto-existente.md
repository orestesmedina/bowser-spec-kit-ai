# Integrar el kit en un proyecto existente

- [Introducción](#introducción)
- [Antes de decidir](#antes-de-decidir)
- [Qué reemplaza el kit y qué respeta](#qué-reemplaza-el-kit-y-qué-respeta)
- [Integración paso a paso](#integración-paso-a-paso)
    - [1. Trabajar en una rama](#1-trabajar-en-una-rama)
    - [2. Inicializar Spec Kit](#2-inicializar-spec-kit)
    - [3. Instalar el kit](#3-instalar-el-kit)
    - [4. Recuperar lo que fue reemplazado](#4-recuperar-lo-que-fue-reemplazado)
    - [5. Ajustar la configuración](#5-ajustar-la-configuración)
    - [6. Verificar y guardar](#6-verificar-y-guardar)
- [Si la estructura del proyecto es distinta](#si-la-estructura-del-proyecto-es-distinta)
- [Si el stack es distinto](#si-el-stack-es-distinto)
- [Adoptar el proceso con código ya escrito](#adoptar-el-proceso-con-código-ya-escrito)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit se puede instalar sobre un repositorio que ya tiene código. La instalación es la misma que en un proyecto nuevo, con una diferencia: tu proyecto ya tiene archivos con los mismos nombres que usa el kit, y hay que decidir qué pasa con ellos.

Esta página explica qué va a cambiar en tu repositorio, cómo recuperar lo que el kit reemplace y qué hacer si tu proyecto no se parece al que el kit espera.

## Antes de decidir

El kit está hecho para un tipo de proyecto concreto. Cuanto más se parezca el tuyo, menos trabajo de integración:

| El kit asume | Si tu proyecto es distinto |
|---|---|
| Backend en Go en `backend/`, frontend en React + TypeScript en `frontend/` | Los controles de esa capa se omiten solos, pero las skills y los roles hablan de ese stack. Ver [Si el stack es distinto](#si-el-stack-es-distinto) |
| PostgreSQL, con migraciones en `backend/migrations/` | Lo mismo |
| El proyecto está en GitHub y usa GitHub Actions | La integración continua no aplica; el resto funciona |
| `make` como punto de entrada de los comandos | El kit trae su propio `Makefile`. Tus comandos pasan a `proyecto.mk` |

Lo que no depende del stack (el proceso, los roles de analista, arquitecto y revisores, el estado del trabajo, los hooks de secretos y de mensajes de commit) funciona en cualquier proyecto.

## Qué reemplaza el kit y qué respeta

La instalación toca solo los archivos que el kit gestiona. Si alguno ya existía en tu proyecto, **lo reemplaza y guarda el tuyo** en `.kit-respaldo/<fecha>/`.

| Archivo de tu proyecto | Qué pasa |
|---|---|
| `Makefile` | **Se reemplaza** por el del kit. Respaldo en `.kit-respaldo/` |
| `AGENTS.md` | **Se reemplaza.** Respaldo en `.kit-respaldo/` |
| `.github/workflows/ci.yml` | **Se reemplaza.** Respaldo en `.kit-respaldo/` |
| Otros workflows en `.github/workflows/` | Se respetan |
| `.github/CODEOWNERS`, `docker-compose.yml`, `.env.example` | Se respetan si ya existen. Si no existen, el kit copia los suyos |
| `README.md`, `CHANGELOG.md` | Se respetan: son del producto |
| `.gitignore` | Se respeta, y se le agrega al final un bloque del kit |
| Tu código, tus documentos y el resto de las carpetas | No se tocan |

En resumen: en un proyecto típico se reemplazan tres archivos, y los tres quedan respaldados.

> [!NOTE]
> Lo mismo aplica a cualquier archivo tuyo que coincida exactamente con una ruta del kit, por ejemplo un `scripts/doctor.sh` propio. La instalación lista todos los archivos reemplazados al terminar.

## Integración paso a paso

### 1. Trabajar en una rama

```bash
git checkout -b chore/instalar-kit
```

Así la integración se revisa en un Pull Request como cualquier otro cambio, y se puede descartar entera si algo no convence.

### 2. Inicializar Spec Kit

```bash
specify init --here --integration claude     # una vez por cada herramienta que use el equipo
git add . && git commit -m "chore: inicializa spec kit"
```

### 3. Instalar el kit

```bash
git submodule add https://github.com/orestesmedina/bowser-spec-kit-ai.git .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit
```

Se usa `make -f …` para ejecutar el `Makefile` del kit y no el de tu proyecto. Al terminar, la instalación muestra qué archivos eran nuevos, cuáles reemplazó y dónde quedó el respaldo:

```
Kit 1.7.1 instalado en mi-proyecto/
   38 nuevos
    3 reemplazados (existían antes)
        .github/workflows/ci.yml
        AGENTS.md
        Makefile
    2 semillas (ahora son del proyecto)
  Respaldo de lo reemplazado: .kit-respaldo/20261004-152715/
```

### 4. Recuperar lo que fue reemplazado

Revisa cada archivo de `.kit-respaldo/` y lleva lo que necesites a su nuevo lugar:

| Lo que tenías | Dónde va ahora |
|---|---|
| Comandos propios en el `Makefile` | En `proyecto.mk`, que el `Makefile` del kit incluye automáticamente. Si un comando tuyo se llama igual que uno del kit, cámbiale el nombre |
| Instrucciones para los agentes en `AGENTS.md` | Si son reglas de código, en una [skill](skills.md) propia. Si son reglas del proyecto, en la [constitución](la-constitucion.md) o en la documentación del proyecto |
| Pasos propios en `ci.yml` | En un workflow aparte, por ejemplo `.github/workflows/proyecto.yml`. El kit solo gestiona `ci.yml` |

Si prefieres conservar tu propia versión de alguno de esos archivos, agrégalo a `"kit.excluir"` en `equipo/config.json` y restáuralo desde el respaldo. El kit deja de tocarlo, y también deja de actualizarlo. Ver [Personalizar un proyecto](personalizar.md).

### 5. Ajustar la configuración

Igual que en un proyecto nuevo: revisa `equipo/config.json` y `.github/CODEOWNERS`, y crea tu `.env` a partir de `.env.example`. El detalle está en [Lo que debes ajustar](proyecto-nuevo.md#lo-que-debes-ajustar).

### 6. Verificar y guardar

```bash
make doctor
git add . && git commit -m "chore: instala kit de desarrollo"
```

Este commit ya pasa por los hooks. En un proyecto con historia es normal que el primero se bloquee por formato: los hooks solo revisan los archivos incluidos en el commit, así que basta con formatear esos.

Antes de integrar la rama, ejecuta lo mismo que hará la integración continua:

```bash
make ci
```

Si falla por reglas que tu código actual no cumple (por ejemplo, la cobertura mínima), decide con tu equipo si se corrige el código o si esa parte del `ci.yml` se excluye del kit.

## Si la estructura del proyecto es distinta

Los controles del kit buscan el código en rutas fijas. Cuando una ruta no existe, el control correspondiente **se omite**, no falla:

| Si no existe | Se omite |
|---|---|
| `backend/go.mod` | Todo el trabajo de backend en la integración continua |
| `frontend/package.json` | Todo el trabajo de frontend en la integración continua |
| `backend/sqlc.yaml` o el script `api:gen` | La verificación de [código generado](cobertura-y-codigo-generado.md) |
| Archivos `service*.go` en `backend/internal/` | La medición de cobertura |

Eso significa que un proyecto con otra organización de carpetas instala sin errores, pero queda **sin esos controles**. Para tenerlos hay dos caminos: mover el código a la estructura que el kit espera, o mantener una versión propia de `ci.yml` y del `Makefile` mediante `kit.excluir`.

## Si el stack es distinto

El kit nació para React, Go y PostgreSQL y está dejando de depender de ellas. Hoy:

- **Los roles ya no nombran ninguna tecnología.** Cada uno recibe del [perfil del proyecto](perfil-del-proyecto.md) sus carpetas, sus skills y sus comandos. Ver [Lo que cada rol recibe del proyecto](roles.md#lo-que-cada-rol-recibe-del-proyecto).
- **Los comandos (`make test`, `make lint`…) ejecutan lo que el perfil declara.**
- **Las skills de tecnología** llegan del [catálogo del kit](skills.md#el-catálogo-de-skills-de-tecnología). Hoy tiene las de Go, React y PostgreSQL; para otra tecnología, el proyecto escribe su propia skill en `.agents/skills/` y el perfil la nombra.
- **La constitución, la integración continua y los archivos iniciales** (`docker-compose.yml`, `.env.example`) todavía suponen React, Go y PostgreSQL. Mientras eso cambia, un proyecto con otras tecnologías mantiene su versión de esos archivos mediante `kit.excluir`.

Así que el primer paso con otro stack es crear el perfil: `/bowser-profile`. El proceso, el estado, los costos y la instalación no dependen del stack. La página [Cómo contribuir](contribuir.md) explica cómo está organizado el kit por dentro.

## Adoptar el proceso con código ya escrito

Instalar el kit no obliga a documentar hacia atrás lo que ya existe. La forma práctica de empezar:

1. **Escribe el roadmap** con lo que viene, no con lo que ya está hecho. Ver [De la idea al roadmap](idea-al-roadmap.md).
2. **La siguiente funcionalidad nueva** ya sigue el flujo completo: especificación, plan, tareas y validación.
3. **Los agentes aprenden del código existente.** Copian sus patrones, así que conviene que la primera funcionalidad toque una parte del proyecto que esté bien resuelta.
4. **Si el código actual no cumple la constitución**, no lo corrijas todo de golpe. Anota las diferencias y decide cuáles se corrigen como funcionalidades propias.

## Siguientes pasos

- [Personalizar un proyecto](personalizar.md): versiones propias de archivos del kit, comandos y roles adicionales.
- [Estructura de carpetas](estructura.md): qué es cada archivo que apareció en el repositorio.
- [Construir una funcionalidad](funcionalidad.md): el flujo de trabajo, paso a paso.
