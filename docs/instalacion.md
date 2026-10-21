# Instalación

- [Introducción](#introducción)
- [Requisitos](#requisitos)
    - [Las herramientas base](#las-herramientas-base)
    - [Las herramientas de tu proyecto](#las-herramientas-de-tu-proyecto)
- [Sistema operativo](#sistema-operativo)
- [Instalar las herramientas base](#instalar-las-herramientas-base)
    - [macOS](#macos)
    - [Ubuntu y WSL](#ubuntu-y-wsl)
- [Spec Kit](#spec-kit)
- [El agente de código](#el-agente-de-código)
- [GitHub](#github)
- [Verificar la instalación](#verificar-la-instalación)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página prepara **tu máquina** para trabajar con el kit. Se hace una sola vez por computadora. No instala nada dentro de un proyecto: eso viene después, en [Siguientes pasos](#siguientes-pasos).

El kit no es un programa que se instala. Es un conjunto de archivos (instrucciones para los agentes, scripts y controles) que vive dentro de cada proyecto. Lo que instalas aquí son las herramientas que esos archivos necesitan para funcionar.

Son de dos clases. Las **herramientas base** las usa el kit en cualquier proyecto, sea del lenguaje que sea. Las **herramientas de tu proyecto** (su lenguaje, su base de datos, su formateador) dependen de con qué esté hecho, y cada proyecto las declara en su perfil.

## Requisitos

### Las herramientas base

| Herramienta | Versión | Para qué la usa el kit |
|---|---|---|
| Git | 2.30 o superior | Control de versiones; los [hooks de git](hooks-de-git.md) revisan cada commit |
| `make` | cualquiera | Ejecuta todos los comandos del kit (`make doctor`, `make test`, `make status`…) |
| Python | 3.11 o superior | Los scripts del kit. No necesitan ninguna librería adicional |
| `jq` | cualquiera | Lo usan los hooks que impiden al agente editar archivos protegidos |
| [uv](https://docs.astral.sh/uv/) | cualquiera | Instala Spec Kit |
| Spec Kit (`specify`) | 1.0 o superior | El motor del proceso: genera specs, planes y tareas |
| Un agente de código | — | Claude Code, Codex u OpenCode. Al menos uno |
| GitHub CLI (`gh`) | cualquiera | Recomendada: los agentes abren los Pull Requests con ella |
| gitleaks | cualquiera | Recomendada: busca secretos en el código antes de que lleguen a GitHub. Sin ella, ese control recién corre en la [integración continua](integracion-continua.md) |

### Las herramientas de tu proyecto

El lenguaje, la base de datos y las demás herramientas de un proyecto no las fija el kit: las declara el propio proyecto en los [`requisitos`](perfil-del-proyecto.md#los-requisitos-de-la-máquina) de su perfil, con la versión mínima y cómo instalar cada una. `make doctor` las revisa y te dice cuál falta.

- **Te unes a un proyecto que ya usa el kit:** instala las herramientas base, clona el proyecto y ejecuta `make doctor`. La lista de lo que falta sale de ahí. Ver [Unirse a un proyecto](unirse-a-un-proyecto.md).
- **Empiezas un proyecto o le instalas el kit a uno existente:** con las herramientas base alcanza para empezar. Los requisitos los escribe un agente al crear el perfil (`/bowser-profile`), y desde ese momento `make doctor` los revisa.

**Docker** es un caso intermedio: el kit no lo necesita, pero lo pide si el proyecto tiene un entorno local (un archivo `compose.yaml` o `docker-compose.yml` en la raíz, que es lo que levanta `make up`).

## Sistema operativo

**macOS y Linux** funcionan directamente.

**Windows** requiere WSL2 con Ubuntu: todo el desarrollo (las herramientas, los proyectos, el agente de código y git) va dentro de Ubuntu, no en Windows.

> [!WARNING]
> En Windows, mezclar programas instalados en Windows con programas instalados en Ubuntu es la causa de la mayoría de los errores. Antes de instalar nada, lee [Windows y WSL](windows-wsl.md).

## Instalar las herramientas base

### macOS

Con [Homebrew](https://brew.sh):

```bash
brew install git python@3.12 jq make gh gitleaks
```

### Ubuntu y WSL

En la terminal de Ubuntu:

```bash
sudo apt update && sudo apt install -y git jq make unzip curl python3
```

La CLI de GitHub y gitleaks se instalan desde sus sitios oficiales, porque las versiones de `apt` suelen ser antiguas:

| Herramienta | Cómo instalarla |
|---|---|
| GitHub CLI (`gh`) | [Instrucciones para Linux](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) |
| gitleaks | [Instrucciones de instalación](https://github.com/gitleaks/gitleaks#installing) |

> [!NOTE]
> Si tu proyecto usa Docker: en Windows, instala Docker Desktop con la integración de WSL activada; en Linux, sigue [docs.docker.com/engine/install/ubuntu](https://docs.docker.com/engine/install/ubuntu/); en macOS, `brew install --cask docker` y abre Docker Desktop una vez para que arranque.

## Spec Kit

Spec Kit es la herramienta de GitHub sobre la que está construido el kit. Aporta los comandos que usan los agentes para escribir la especificación, el plan y las tareas. Se instala con `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install specify-cli
specify --version
```

## El agente de código

Instala el que use tu equipo. Si te unes a un proyecto, está indicado en `"herramientas"` dentro de `equipo/config.json`.

| Herramienta | Instalación | Primer inicio |
|---|---|---|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | `claude` y luego iniciar sesión |
| Codex | `npm install -g @openai/codex` (necesita Node.js) | `codex` y luego iniciar sesión |
| OpenCode | `curl -fsSL https://opencode.ai/install \| bash` | `opencode` y luego configurar el proveedor |

> [!WARNING]
> En Windows, instala el agente **en la terminal de Ubuntu**. El agente ejecuta comandos como `make` o `git commit` en el sistema donde está instalado; si está en Windows, no encuentra ninguna de las herramientas de esta página.

Estos comandos de instalación los mantiene cada proveedor y pueden cambiar. Si alguno falla, consulta la documentación oficial de la herramienta.

## GitHub

Los agentes abren los Pull Requests con la CLI de GitHub, así que necesita estar autenticada. Git necesita saber quién eres para firmar los commits:

```bash
gh auth login
git config --global user.name  "Tu Nombre"
git config --global user.email "tu@correo.com"
```

## Verificar la instalación

El kit trae un diagnóstico que revisa todo lo anterior de una vez. Se ejecuta desde la carpeta de un proyecto que ya tenga el kit instalado:

```bash
make doctor
```

Cada línea empieza con un símbolo:

| Símbolo | Significado | Qué hacer |
|---|---|---|
| `✓` | Correcto | Nada |
| `!` | Recomendado, pero no obligatorio | Conviene resolverlo; no te bloquea |
| `✗` | Falta algo necesario | Corrígelo antes de trabajar. El mensaje dice cómo |

Primero revisa las herramientas base y después las del proyecto. En un proyecto que todavía no tiene perfil verás este aviso, que es lo esperado: el siguiente paso es crearlo.

```text
  ! El proyecto no tiene perfil: no se sabe qué tecnología usa ni qué herramientas necesita (en el chat: /bowser-profile)
```

Además de las herramientas, `make doctor` revisa cosas que solo aparecen al trabajar: que Docker esté corriendo (si el proyecto lo usa), que los hooks de git estén activos, que exista el archivo `.env` (si el proyecto declara alguna variable en `.env.example`), que el kit del proyecto esté al día y, en Windows, que no se estén usando por error programas instalados del lado de Windows.

La instalación está completa cuando termina con:

```
Todo listo para trabajar.
```

> [!TIP]
> Si todavía no tienes `make`, el mismo diagnóstico se puede ejecutar con `bash scripts/doctor.sh`.

## Siguientes pasos

Con la máquina lista, el siguiente paso depende de tu situación:

- **Vas a empezar un proyecto desde cero:** [Crear un proyecto nuevo](proyecto-nuevo.md).
- **Ya tienes un proyecto con código:** [Integrar el kit en un proyecto existente](proyecto-existente.md).
- **Tu proyecto ya usa una versión 1.x del kit:** [Migrar a la 2.0](migrar-a-2.md).
- **Te unes a un proyecto que ya usa el kit:** [Unirse a un proyecto](unirse-a-un-proyecto.md).
- **Quieres entender cómo funciona antes de usarlo:** [Desarrollo guiado por especificaciones](sdd.md).

Si algo no funcionó, revisa [Problemas comunes](problemas-comunes.md).
