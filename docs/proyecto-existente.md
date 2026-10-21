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
    - [6. Guardar la instalación](#6-guardar-la-instalación)
    - [7. Describir el proyecto](#7-describir-el-proyecto)
    - [8. Verificar](#8-verificar)
- [Lo que el kit aprende de tu proyecto](#lo-que-el-kit-aprende-de-tu-proyecto)
- [Adoptar el proceso con código ya escrito](#adoptar-el-proceso-con-código-ya-escrito)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit se puede instalar sobre un repositorio que ya tiene código. La instalación es la misma que en un proyecto nuevo, con una diferencia: tu proyecto ya tiene archivos con los mismos nombres que usa el kit, y hay que decidir qué pasa con ellos.

Esta página explica qué va a cambiar en tu repositorio, cómo recuperar lo que el kit reemplace y cómo hacer que el kit conozca tu proyecto.

> [!NOTE]
> Si tu proyecto ya usa una versión 1.x del kit, esta página no es para ti: sigue [Migrar a la 2.0](migrar-a-2.md).

## Antes de decidir

El kit no exige una tecnología ni una estructura de carpetas: el lenguaje, la base de datos, dónde está cada parte y cómo se prueba los declara el proyecto en su [perfil](perfil-del-proyecto.md), y un agente lo redacta leyendo tu código. Lo que sí pide:

| El kit necesita | Si tu proyecto es distinto |
|---|---|
| Que el proyecto esté en git | Inicializa el repositorio antes de empezar (`git init`) |
| `make` como punto de entrada de los comandos | El kit trae su propio `Makefile`. Tus comandos pasan a `proyecto.mk` |
| GitHub y GitHub Actions para la integración continua | La integración continua no aplica; el resto funciona |
| Herramientas que se puedan ejecutar desde la terminal para probar, revisar o formatear | Un verbo sin comando no falla: avisa que esa parte no tiene ese control. Un proyecto sin pruebas funciona, y lo dice en sus reglas |

El proceso, los roles, el estado del trabajo, los costos y los hooks de secretos y de mensajes de commit funcionan igual en cualquier proyecto.

## Qué reemplaza el kit y qué respeta

La instalación toca solo los archivos que el kit gestiona. Si alguno ya existía en tu proyecto, **lo reemplaza y guarda el tuyo** en `.kit-respaldo/<fecha>/`.

| Archivo de tu proyecto | Qué pasa |
|---|---|
| `Makefile` | **Se reemplaza** por el del kit. Respaldo en `.kit-respaldo/` |
| `AGENTS.md` | **Se reemplaza.** Respaldo en `.kit-respaldo/` |
| Tus workflows en `.github/workflows/` | Se respetan, también `ci.yml`. El kit agrega el suyo, `bowser.yml` |
| `.github/CODEOWNERS`, `.env.example` | Se respetan si ya existen. Si no existen, el kit copia los suyos (`.env.example`, vacío) |
| `docker-compose.yml` y el resto de tu entorno local | No se tocan: el kit no trae ninguno |
| `README.md`, `CHANGELOG.md` | Se respetan: son del producto |
| `.gitignore` | Se respeta, y se le agrega al final un bloque del kit, sin reglas de ninguna tecnología |
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
make -f .bowser-spec-kit-ai/Makefile install-kit
```

Se usa `make -f …` para ejecutar el `Makefile` del kit y no el de tu proyecto. Al terminar, la instalación muestra qué archivos eran nuevos, cuáles reemplazó y dónde quedó el respaldo:

```
Kit 1.7.1 instalado en mi-proyecto/
   38 nuevos
    2 reemplazados (existían antes)
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
| Tu integración continua | Se queda donde está: es del proyecto. Cuando tengas perfil, `/bowser-ci` la ajusta para que ejecute los verbos. Si repite lo que ya hace `bowser.yml` (buscar secretos), quítalo de la tuya |

Si prefieres conservar tu propia versión de alguno de esos archivos, agrégalo a `"kit.excluir"` en `equipo/config.json` y restáuralo desde el respaldo. El kit deja de tocarlo, y también deja de actualizarlo. Ver [Personalizar un proyecto](personalizar.md).

### 5. Ajustar la configuración

Igual que en un proyecto nuevo: revisa `equipo/config.json` y `.github/CODEOWNERS`, y crea tu `.env` a partir de `.env.example`. El detalle está en [Lo que debes ajustar](proyecto-nuevo.md#lo-que-debes-ajustar).

### 6. Guardar la instalación

```bash
git add . && git commit -m "chore: instala kit de desarrollo"
```

Este commit ya pasa por los [hooks de git](hooks-de-git.md). Todavía no revisan nada de tu tecnología: eso empieza cuando existe el perfil.

### 7. Describir el proyecto

Hasta que el perfil exista, el kit **no ejecuta ningún control de tecnología**: `make test`, `make lint` y `make ci` piden crearlo, el commit no revisa formato ni archivos inmutables, y los agentes no saben qué carpeta es de quién. Tres comandos del chat lo resuelven, en este orden:

| Comando | Qué hace | Ver |
|---|---|---|
| `/bowser-profile` | Un agente lee el proyecto y propone el perfil: sus partes, en qué carpeta está cada una, con qué tecnología, qué comando prueba, revisa o formatea cada parte y qué herramientas necesita una máquina | [El perfil del proyecto](perfil-del-proyecto.md) |
| `/bowser-conventions <parte>` | Un agente lee el código de una parte y escribe cómo hace las cosas este proyecto: nombres, carpetas, patrones y bibliotecas. Es lo que los agentes van a copiar | [Convenciones del proyecto](convenciones-del-proyecto.md) |
| `/bowser-ci` | Un agente redacta o ajusta la integración continua para que ejecute los verbos del perfil | [Integración continua](integracion-continua.md) |

Revisa cada propuesta antes de guardarla. El perfil lo confirmas tú en el commit, porque sus comandos se ejecutan en cada máquina y en GitHub:

```bash
make profile                     # muestra y valida el perfil
make install-kit                 # trae las skills de tecnología que el perfil nombra
git add . && APPROVED_PROFILE=1 git commit -m "chore: agrega el perfil del proyecto"
```

Si el proyecto ya tenía una constitución de Spec Kit escrita a mano, la instalación la pasó completa a `equipo/reglas.md` y generó la constitución con los principios del kit encima. Revisa ese archivo y borra lo que ya dicen los principios; ese commit pide `APPROVED_CONSTITUTION=1`. Ver [La constitución](la-constitucion.md).

### 8. Verificar

```bash
make doctor      # las herramientas que pide el perfil
make ci          # lo mismo que hará la integración continua
```

En un proyecto con historia es normal que el primer commit con perfil se bloquee por formato: los hooks solo revisan los archivos incluidos en el commit, así que basta con formatear esos.

Si `make ci` falla por reglas que tu código actual no cumple (por ejemplo, una cobertura mínima), decide con tu equipo si se corrige el código o si se cambia la regla en el perfil.

## Lo que el kit aprende de tu proyecto

El kit no busca el código en rutas fijas ni supone ninguna tecnología. No hace falta mover nada ni cambiar de lenguaje: lo que necesita saber lo aprende del proyecto.

- **Los roles no nombran ninguna tecnología.** Cada uno recibe del perfil sus carpetas, sus skills y sus comandos. Ver [Lo que cada rol recibe del proyecto](roles.md#lo-que-cada-rol-recibe-del-proyecto).
- **Los comandos (`make test`, `make lint`…) ejecutan lo que el perfil declara**, en la carpeta de cada parte.
- **Las skills de tecnología** llegan del [catálogo del kit](skills.md#el-catálogo-de-skills-de-tecnología), solo las que el perfil nombra, y traen el estándar de cada una según su documentación oficial. Para una tecnología que el catálogo no tiene, el proyecto escribe su propia skill en `.agents/skills/` y el perfil la nombra.
- **Lo propio de tu proyecto** (cómo nombra las cosas, cómo se organiza, qué patrones y bibliotecas usa) queda en sus convenciones. Si se contradicen con el estándar, manda el proyecto, salvo en seguridad.
- **Los archivos iniciales no traen tecnología:** el kit no instala base de datos ni servicios, `.env.example` llega vacío y su bloque de `.gitignore` solo cubre secretos, editores y archivos del kit. Lo que tu tecnología necesita ignorar lo propone `/bowser-profile`.

La página [Cómo contribuir](contribuir.md) explica cómo está organizado el kit por dentro.

## Adoptar el proceso con código ya escrito

Instalar el kit no obliga a documentar hacia atrás lo que ya existe. La forma práctica de empezar:

1. **Escribe el roadmap** con lo que viene, no con lo que ya está hecho. Ver [De la idea al roadmap](idea-al-roadmap.md).
2. **La siguiente funcionalidad nueva** ya sigue el flujo completo: especificación, plan, tareas y validación.
3. **Los agentes aprenden del código existente.** Copian sus patrones, así que conviene que la primera funcionalidad toque una parte del proyecto que esté bien resuelta.
4. **Si el código actual no cumple la constitución**, no lo corrijas todo de golpe. Los principios lo prevén: lo que hoy no cumple se registra como deuda (en las [convenciones del proyecto](convenciones-del-proyecto.md)) y el código nuevo sí debe cumplir. Decide qué deuda se corrige como funcionalidades propias.

## Siguientes pasos

- [Personalizar un proyecto](personalizar.md): versiones propias de archivos del kit, comandos y roles adicionales.
- [Estructura de carpetas](estructura.md): qué es cada archivo que apareció en el repositorio.
- [Construir una funcionalidad](funcionalidad.md): el flujo de trabajo, paso a paso.
