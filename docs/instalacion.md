# Instalación

- [Introducción](#introducción)
- [Requisitos](#requisitos)
- [Sistema operativo](#sistema-operativo)
- [Herramientas base](#herramientas-base)
    - [macOS](#macos)
    - [Ubuntu y WSL](#ubuntu-y-wsl)
- [Spec Kit](#spec-kit)
- [Herramientas de Go](#herramientas-de-go)
- [El agente de código](#el-agente-de-código)
- [GitHub](#github)
- [Verificar la instalación](#verificar-la-instalación)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página prepara **tu máquina** para trabajar con el kit. Se hace una sola vez por computadora y toma entre una y dos horas. No instala nada dentro de un proyecto: eso viene después, en [Siguientes pasos](#siguientes-pasos).

El kit no es un programa que se instala. Es un conjunto de archivos (instrucciones para los agentes, scripts y controles) que vive dentro de cada proyecto. Lo que instalas aquí son las herramientas que esos archivos necesitan para funcionar: el lenguaje del backend, el del frontend, la base de datos, Spec Kit y el agente de código.

## Requisitos

| Herramienta | Versión | Para qué la usa el kit |
|---|---|---|
| Git | 2.30 o superior | Control de versiones; los [hooks de git](hooks-de-git.md) revisan cada commit |
| `make` | cualquiera | Ejecuta todos los comandos del kit (`make doctor`, `make up`, `make estado`…) |
| Python | 3.11 o superior | Los scripts del kit. No necesitan ninguna librería adicional |
| `jq` | cualquiera | Lo usan los hooks que impiden al agente editar archivos protegidos |
| Docker | 24 o superior | Levanta PostgreSQL en tu máquina; no se instala PostgreSQL a mano |
| Go | 1.26 o superior | Backend |
| Node.js | 24 | Frontend |
| [uv](https://docs.astral.sh/uv/) | cualquiera | Instala Spec Kit |
| Spec Kit (`specify`) | 1.0 o superior | El motor del proceso: genera specs, planes y tareas |
| Un agente de código | — | Claude Code, Codex u OpenCode. Al menos uno |

Además, hay cinco herramientas recomendadas: `golangci-lint`, `govulncheck`, `migrate`, `sqlc` y `gitleaks`. Sin ellas el kit funciona, pero algunos controles se saltan en tu máquina y recién fallan en la [integración continua](integracion-continua.md).

## Sistema operativo

**macOS y Linux** funcionan directamente.

**Windows** requiere WSL2 con Ubuntu: todo el desarrollo (las herramientas, los proyectos, el agente de código y git) va dentro de Ubuntu, no en Windows.

> [!WARNING]
> En Windows, mezclar programas instalados en Windows con programas instalados en Ubuntu es la causa de la mayoría de los errores. Antes de instalar nada, lee [Windows y WSL](windows-wsl.md).

## Herramientas base

### macOS

Con [Homebrew](https://brew.sh):

```bash
brew install git go node@24 python@3.12 jq make gh gitleaks golang-migrate
brew install --cask docker
```

Abre Docker Desktop una vez para que arranque.

### Ubuntu y WSL

En la terminal de Ubuntu:

```bash
sudo apt update && sudo apt install -y git jq make unzip curl build-essential python3 python3-pip
```

Go, Node, Docker y la CLI de GitHub se instalan desde sus sitios oficiales, porque las versiones de `apt` suelen ser antiguas:

| Herramienta | Cómo instalarla |
|---|---|
| Go 1.26+ | [go.dev/doc/install](https://go.dev/doc/install) |
| Node 24 | [nvm](https://github.com/nvm-sh/nvm), y luego `nvm install 24` |
| Docker | En Windows, Docker Desktop con la integración de WSL activada. En Linux nativo, [docs.docker.com/engine/install/ubuntu](https://docs.docker.com/engine/install/ubuntu/) |
| GitHub CLI (`gh`) | [Instrucciones para Linux](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) |
| gitleaks | [Instrucciones de instalación](https://github.com/gitleaks/gitleaks#installing) |

## Spec Kit

Spec Kit es la herramienta de GitHub sobre la que está construido el kit. Aporta los comandos que usan los agentes para escribir la especificación, el plan y las tareas. Se instala con `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install specify-cli
specify --version
```

## Herramientas de Go

```bash
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.14.0
go install golang.org/x/vuln/cmd/govulncheck@v1.8.0
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@v4.20.1
go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.31.1
```

| Herramienta | Qué hace | Comando del kit que la usa |
|---|---|---|
| `golangci-lint` | Revisa la calidad del código Go | `make lint` |
| `govulncheck` | Busca vulnerabilidades conocidas en las dependencias de Go | `make security` |
| `migrate` | Aplica las migraciones de la base de datos | `make db-migrate` |
| `sqlc` | Genera código Go a partir de las consultas SQL | `make generar` |

Las versiones son las mismas que fija la integración continua. Usar otras puede hacer que algo pase en tu máquina y falle en GitHub, o al revés.

> [!NOTE]
> `go install` deja los programas en `$(go env GOPATH)/bin`. Si después de instalarlos la terminal dice `command not found`, agrega esa carpeta a tu `PATH`:
> ```bash
> echo 'export PATH="$PATH:$(go env GOPATH)/bin"' >> ~/.bashrc && source ~/.bashrc
> ```

## El agente de código

Instala el que use tu equipo. Si te unes a un proyecto, está indicado en `"herramientas"` dentro de `equipo/config.json`.

| Herramienta | Instalación | Primer inicio |
|---|---|---|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | `claude` y luego iniciar sesión |
| Codex | `npm install -g @openai/codex` | `codex` y luego iniciar sesión |
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

Además de las herramientas, `make doctor` revisa cosas que solo aparecen al trabajar: que Docker esté corriendo, que los hooks de git estén activos, que exista el archivo `.env`, que el kit del proyecto esté al día y, en Windows, que no se estén usando por error programas instalados del lado de Windows.

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
- **Te unes a un proyecto que ya usa el kit:** [Unirse a un proyecto](unirse-a-un-proyecto.md).
- **Quieres entender cómo funciona antes de usarlo:** [Desarrollo guiado por especificaciones](sdd.md).

Si algo no funcionó, revisa [Problemas comunes](problemas-comunes.md).
