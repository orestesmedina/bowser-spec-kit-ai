# Windows y WSL

- [Introducción](#introducción)
- [Dos sistemas separados](#dos-sistemas-separados)
- [Preparar Windows paso a paso](#preparar-windows-paso-a-paso)
- [Cuando Ubuntu usa por error un programa de Windows](#cuando-ubuntu-usa-por-error-un-programa-de-windows)
    - [Cómo detectarlo](#cómo-detectarlo)
    - [Cómo corregirlo](#cómo-corregirlo)
- [Síntomas típicos](#síntomas-típicos)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

En Windows, el kit se usa dentro de **WSL2 con Ubuntu**: un Linux completo que corre dentro de Windows. Esta página explica cómo conviven los dos sistemas, porque mezclarlos es la causa de la mayoría de los errores que aparecen en Windows.

Si usas macOS o Linux, puedes saltarte esta página.

## Dos sistemas separados

En Windows con WSL conviven **dos sistemas, cada uno con sus propios programas**:

| | Windows | Ubuntu (WSL) |
|---|---|---|
| Qué va aquí | Navegador, DBeaver, Docker Desktop, VS Code (la ventana) | `make`, `python3`, `jq`, Go, Node, Spec Kit, git, **el agente de código** y **los proyectos** |
| Terminal | PowerShell | Terminal "Ubuntu" |

Un programa instalado en uno **no existe** en el otro. Por eso la regla es una sola: **todo lo del desarrollo se instala y se ejecuta dentro de Ubuntu**.

## Preparar Windows paso a paso

1. **Instala WSL con Ubuntu.** En PowerShell como administrador, y luego reinicia:
   ```powershell
   wsl --install -d Ubuntu
   ```
2. **Abre la terminal "Ubuntu".** Desde aquí, todos los comandos de esta documentación se ejecutan en esa terminal, salvo que se diga lo contrario.
3. **Guarda los proyectos dentro de Ubuntu**, por ejemplo en `~/proyectos/`. No trabajes en `/mnt/c/...` ni `/mnt/d/...` (los discos de Windows vistos desde Ubuntu): es mucho más lento y da problemas con los permisos de los scripts.
4. **Docker.** Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/) en Windows y actívalo para Ubuntu en **Settings → Resources → WSL Integration → Ubuntu → Apply & Restart**. Docker Desktop debe estar abierto cuando trabajes. Verifica en Ubuntu con `docker version`.
5. **VS Code.** Instala la extensión **WSL** de Microsoft y abre siempre los proyectos desde la terminal de Ubuntu:
   ```bash
   cd ~/proyectos/mi-proyecto
   code .
   ```
   Abajo a la izquierda debe decir **"WSL: Ubuntu"**.
6. **El agente de código** (Claude Code, Codex u OpenCode) se instala y se ejecuta en Ubuntu. El agente ejecuta comandos como `make test` o `git commit` en el sistema donde está instalado.
7. **PostgreSQL.** No instales PostgreSQL en Windows: el proyecto lo levanta con Docker. Si ya tienes uno instalado, ocupa el puerto 5432 y tu cliente se conectará a ese en lugar del de Docker.
8. **Cliente de base de datos.** Usa uno actualizado que soporte PostgreSQL 16, como [DBeaver Community](https://dbeaver.io/download/) o pgAdmin 4. Los clientes antiguos (por ejemplo Navicat 11) no pueden autenticarse con PostgreSQL moderno.

Con Windows preparado, continúa con la [Instalación](instalacion.md), ejecutando todo en la terminal de Ubuntu.

> [!WARNING]
> Si abres la carpeta del proyecto en VS Code desde Windows (y no con `code .` desde Ubuntu), VS Code usa el Git de Windows. Los commits fallan con mensajes confusos, porque del lado de Windows no existen `python3` ni `jq`, que necesitan los [hooks de git](hooks-de-git.md).

## Cuando Ubuntu usa por error un programa de Windows

WSL agrega por defecto las carpetas de programas de Windows al `PATH` de Ubuntu. Por eso, si tenías un programa instalado en Windows (por ejemplo OpenCode, Node o Git), **Ubuntu lo encuentra y lo usa aunque no esté instalado en Ubuntu**.

Parece que funciona, pero cuando ese programa ejecuta otros comandos lo hace del lado de Windows, donde no están `make`, `python3` ni el resto de las herramientas.

### Cómo detectarlo

`make doctor` lo detecta y lo marca con `✗`. Para revisarlo a mano:

```bash
which -a opencode      # o claude, codex, node, git...
```

- Las rutas que empiezan con `/home/...` o `/usr/...` son de **Ubuntu**: bien.
- Las rutas que empiezan con `/mnt/c/...` son de **Windows**: mal, si es la primera de la lista.

### Cómo corregirlo

Ejemplo con OpenCode:

1. Instálalo dentro de Ubuntu:
   ```bash
   curl -fsSL https://opencode.ai/install | bash
   ```
2. Cierra y vuelve a abrir la terminal, y verifica que la **primera** línea de `which -a opencode` empiece con `/home/`. Si sigue apareciendo primero la de Windows, pon la carpeta que indicó el instalador (normalmente `~/.opencode/bin`) al inicio del `PATH`:
   ```bash
   echo 'export PATH="$HOME/.opencode/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
3. **Vuelve a iniciar sesión o a configurar el proveedor.** La instalación de Ubuntu no comparte configuración con la de Windows: abre el agente en tu proyecto y conecta tu cuenta de nuevo.
4. Opcional: si no usas ese programa desde Windows, desinstálalo de Windows para evitar confusiones.

> [!NOTE]
> No desactives la integración de rutas de Windows en WSL. De ella depende, entre otras cosas, que `code .` abra VS Code desde Ubuntu.

## Síntomas típicos

| Lo que ves | Lo que pasa |
|---|---|
| El commit falla desde VS Code pero funciona desde la terminal, con varios `✗` a la vez | VS Code abrió el proyecto desde Windows. Ábrelo con `code .` desde Ubuntu |
| "No se encontró python3" al hacer commit | El commit se está haciendo con el Git de Windows |
| El agente no puede ejecutar `make`, `go` o `git` | El agente es el de Windows. Revisa `which -a <agente>` |
| `make doctor` dice "Se están usando versiones de Windows de: …" | Esas herramientas no están instaladas en Ubuntu |
| `make doctor` avisa que el proyecto está en el disco de Windows | El proyecto está en `/mnt/...`. Muévelo a `~/proyectos/` |
| Error de autenticación de la base de datos **en español** | Te estás conectando a un PostgreSQL instalado en Windows, no al de Docker |

La lista completa está en [Problemas comunes](problemas-comunes.md).

## Siguientes pasos

- [Instalación](instalacion.md): las herramientas que hay que instalar dentro de Ubuntu.
- [Problemas comunes](problemas-comunes.md): más errores y sus soluciones.
