# Crear un proyecto nuevo

- [Introducción](#introducción)
- [Antes de empezar](#antes-de-empezar)
- [Crear el proyecto](#crear-el-proyecto)
    - [1. Inicializar Spec Kit](#1-inicializar-spec-kit)
    - [2. Agregar el kit](#2-agregar-el-kit)
    - [3. Preparar el entorno local](#3-preparar-el-entorno-local)
    - [4. Guardar](#4-guardar)
- [Qué hizo la instalación](#qué-hizo-la-instalación)
- [Lo que debes ajustar](#lo-que-debes-ajustar)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página crea un proyecto desde cero con el kit instalado. Al terminar tendrás un repositorio con las instrucciones de los agentes, los controles activos y PostgreSQL corriendo, listo para escribir la idea del producto.

Si el proyecto ya existe y tiene código, usa [Integrar el kit en un proyecto existente](proyecto-existente.md).

## Antes de empezar

Tu máquina debe tener todo lo de la página de [Instalación](instalacion.md). En Windows, todo se ejecuta en la terminal de Ubuntu ([Windows y WSL](windows-wsl.md)).

## Crear el proyecto

### 1. Inicializar Spec Kit

```bash
mkdir mi-proyecto && cd mi-proyecto && git init
specify init --here --integration claude
specify init --here --force --integration codex      # opcional
specify init --here --force --integration opencode   # opcional
git add . && git commit -m "chore: inicializa spec kit"
```

Ejecuta `specify init` una vez por cada herramienta que vaya a usar el equipo. Los nombres disponibles se ven con `specify integration list`.

> [!NOTE]
> Spec Kit se inicializa **antes** de instalar el kit. El kit reemplaza la plantilla de constitución que trae Spec Kit por la suya, y deja un respaldo en `.kit-respaldo/`.

### 2. Agregar el kit

El kit se agrega como submódulo de git en la carpeta `.bowser-spec-kit-ai/` y se instala con un comando:

```bash
git submodule add https://github.com/orestesmedina/bowser-spec-kit-ai.git .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit
```

Si tu equipo mantiene su propia copia del kit, usa la dirección de ese repositorio. La primera vez se usa `make -f …` porque el proyecto todavía no tiene `Makefile`; después de instalar, basta con `make`.

### 3. Preparar el entorno local

```bash
cp .env.example .env      # completa los valores
make up                   # levanta PostgreSQL con Docker
make doctor               # verifica que todo esté listo
```

> [!WARNING]
> Ajusta la contraseña en `.env` **antes** del primer `make up`. PostgreSQL solo la toma al crear la base de datos; si la cambias después, hay que recrearla con `docker compose down -v && make up`, que borra los datos locales.

### 4. Guardar

```bash
git add . && git commit -m "chore: instala kit de desarrollo"
```

Este commit ya pasa por los [hooks de git](hooks-de-git.md). Si alguno lo bloquea, el mensaje indica qué corregir.

## Qué hizo la instalación

Las herramientas leen sus archivos en la raíz del proyecto, no dentro del submódulo. Por eso `make instalar-kit`:

1. **Copió a la raíz los archivos del kit:** las instrucciones de los agentes, los roles, las skills, los hooks, la integración continua, la constitución, los scripts y el `Makefile`. Quedan registrados en `.kit-manifest.json`.
2. **Copió las semillas:** `equipo/config.json`, `.github/CODEOWNERS`, `.env.example` y `docker-compose.yml`. Son un punto de partida; desde ahora son del proyecto.
3. **Agregó un bloque del kit a `.gitignore`.**
4. **Generó la configuración de cada herramienta** (`CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`).
5. **Activó los hooks de git.**

El detalle de cada grupo está en [El kit como submódulo](submodulo.md) y en [Estructura de carpetas](estructura.md).

## Lo que debes ajustar

La instalación deja valores genéricos en tres lugares:

| Archivo | Qué cambiar |
|---|---|
| `equipo/config.json` | Deja en `"herramientas"` solo las que use tu equipo y revisa los modelos de cada agente. Ver [Configuración](configuracion.md) |
| `.github/CODEOWNERS` | Reemplaza `@tu-org/direccion-tecnica` por el usuario o equipo de GitHub que debe aprobar los cambios a las reglas |
| `.specify/memory/constitution.md` | Son las reglas del kit. Si tu equipo necesita otras, lee [La constitución](la-constitucion.md) antes de cambiarlas |

Después de cambiar `equipo/config.json`, ejecuta `make sincronizar`.

## Siguientes pasos

- [De la idea al roadmap](idea-al-roadmap.md): el primer trabajo real en un proyecto nuevo.
- [Estructura de carpetas](estructura.md): qué es cada archivo que apareció.
- [Desarrollo guiado por especificaciones](sdd.md): el proceso que va a seguir el equipo.
