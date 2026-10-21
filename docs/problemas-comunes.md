# Problemas comunes

- [Introducción](#introducción)
- [Primero: make doctor](#primero-make-doctor)
- [Instalación y entorno](#instalación-y-entorno)
- [Windows y WSL](#windows-y-wsl)
- [Base de datos](#base-de-datos)
- [Commits rechazados](#commits-rechazados)
- [El kit y sus actualizaciones](#el-kit-y-sus-actualizaciones)
- [Integración continua](#integración-continua)
- [Los agentes](#los-agentes)
- [Estado y costos](#estado-y-costos)
- [Si nada de esto ayuda](#si-nada-de-esto-ayuda)

## Introducción

Los errores más frecuentes, con su causa y su solución. Están agrupados por el momento en que aparecen.

## Primero: make doctor

Antes de buscar en las tablas:

```bash
make doctor
```

Revisa el entorno completo y marca con `✗` lo que falta, indicando cómo corregirlo. La mayoría de los problemas de esta página los detecta por sí solo.

## Instalación y entorno

| Síntoma | Causa probable | Solución |
|---|---|---|
| `make: command not found` | Falta `make`. Es común en Ubuntu y WSL | `sudo apt install -y make build-essential` |
| `make: *** No rule to make target 'up'` | Estás en otra carpeta | `cd` a la carpeta del proyecto. `ls Makefile` debe encontrarlo |
| `make doctor` dice que falta `jq` | No está instalado | `sudo apt install -y jq` |
| `make doctor` dice "El proyecto no tiene perfil" | Sin perfil no sabe qué tecnología usa el proyecto: solo revisa las herramientas base | Crea el perfil con `/bowser-profile`: desde entonces revisa lo que el perfil declara en `requisitos` |
| `make test`, `make lint` o `make ci`: "Este proyecto no tiene perfil" | El kit no sabe cómo se prueba ni se revisa el proyecto | Crea el perfil con `/bowser-profile` |
| `make test-backend`, `make test-frontend` o `make db-migrate`: "No rule to make target" | Se retiraron en la 1.23.0: solo servían a la estructura que el kit suponía sin perfil | Usa `make test PART=<parte>`. Si el proyecto necesita esos comandos, defínelos en `proyecto.mk`. `make upgrade` los cambia en los workflows y en `proyecto.mk` cuando el reemplazo es claro |
| Al instalar o actualizar: "Al proyecto le quedan N pendientes para aprovechar el kit" | Es un aviso: hay cosas que la actualización no puede resolver sola (perfil, integración continua, reglas heredadas…) | `make upgrade` las lista, o `/bowser-upgrade` en el chat. Ver [Lo que queda pendiente](actualizacion.md#lo-que-queda-pendiente) |
| La actualización se detiene con "Este proyecto no tiene perfil" | El proyecto viene de una versión anterior a la 1.23.0, no tiene perfil y tiene `backend/` o `frontend/` | Ver [Si el proyecto no tiene perfil](actualizacion.md#si-el-proyecto-no-tiene-perfil) |
| `make doctor` dice "El perfil no declara requisitos" | Es un aviso: no sabe qué herramientas usa la tecnología del proyecto | `/bowser-profile`, o agrega `requisitos` al perfil. Ver [Los requisitos de la máquina](perfil-del-proyecto.md#los-requisitos-de-la-máquina) |
| `make doctor` dice "El perfil tiene errores" | `equipo/perfil.json` está mal escrito | `make profile` dice qué corregir |
| `make doctor` ya no revisa Docker | El proyecto no tiene archivo de Docker Compose ni lo pide su perfil | Nada, si el proyecto no usa Docker. Si lo usa, agrégalo a `requisitos` |
| Una herramienta del proyecto da "command not found" aunque está instalada | La carpeta donde la instaló su gestor de paquetes no está en el `PATH` (por ejemplo, `$(go env GOPATH)/bin` o `~/.local/bin`) | Agrega esa carpeta al `PATH` en tu `~/.bashrc` o `~/.zshrc` y abre una terminal nueva. La forma de instalarla está en los `requisitos` del perfil (`make profile`) |
| "Docker no está corriendo" | Docker Desktop está cerrado | Ábrelo y espera a que arranque |
| `make: docker: No such file or directory` | Docker no está instalado en Ubuntu, o falta la integración con WSL | Docker Desktop con **WSL Integration → Ubuntu** activado. Reabre la terminal |
| El agente no conoce los comandos `/speckit.*` | Spec Kit no está inicializado para esa herramienta | `specify init --here --force --integration <herramienta>` |
| Los comandos `/speckit.*` desaparecieron después de `make sync` o de actualizar el kit | Las versiones 1.11.0 a 1.17.0 del kit los borraban en OpenCode y Claude Code | Actualiza el kit y recupéralos: `git checkout -- .opencode/commands .claude/skills` si todavía no hiciste el commit, o `specify init --here --force --integration <herramienta>` |

## Windows y WSL

| Síntoma | Causa probable | Solución |
|---|---|---|
| El commit falla **desde VS Code** pero funciona desde la terminal, con varios `✗` a la vez | VS Code abrió el proyecto desde Windows y usa el Git de Windows, donde no hay `python3` | Instala la extensión **WSL** y abre el proyecto con `code .` desde Ubuntu. Abajo a la izquierda debe decir "WSL: Ubuntu" |
| "No se encontró python3" al hacer commit | Lo mismo: el commit se hace fuera de Ubuntu | Lo mismo |
| El agente no puede ejecutar `make`, `git` o las herramientas del proyecto, o `which opencode` muestra `/mnt/c/...` | Ubuntu está usando la versión de Windows del agente | Instálalo en Ubuntu y verifica con `which -a` |
| `make doctor` dice "Se están usando versiones de Windows de: …" | Esas herramientas no están instaladas en Ubuntu y se toman las de Windows | Instálalas en Ubuntu y verifica con `which -a <herramienta>` |
| `make doctor` avisa que el proyecto está en el disco de Windows | El proyecto está en `/mnt/...` | Muévelo a una carpeta de Ubuntu, por ejemplo `~/proyectos/` |

La explicación de fondo está en [Windows y WSL](windows-wsl.md).

## Base de datos

La base de datos y los demás servicios locales los define cada proyecto en su archivo de Docker Compose; el kit no trae ninguno. Los puertos y los nombres de las variables cambian según el motor y el proyecto: los de esta tabla son ejemplos.

| Síntoma | Causa probable | Solución |
|---|---|---|
| `make up` responde `Este proyecto todavía no tiene entorno local` | El proyecto no tiene archivo de Docker Compose en la raíz. El kit dejó de traer uno en la 1.17.0 | Pídele al equipo (rol `devops`) que lo cree con los servicios que el proyecto usa. Si el proyecto no necesita servicios locales, no hace falta `make up` |
| Después de actualizar el kit, `.gitignore` tiene reglas nuevas debajo del bloque del kit | El bloque ya no trae reglas de Go ni de Node; las que tenía se conservaron ahí para que git no empiece a ver lo que ignoraba | Son del proyecto: deja las que le sirven y borra las demás |
| Error de conexión a la base de datos | La base de datos no levantó, o `.env` es incorrecto | `make up`, `docker compose ps`, y revisa la dirección de la base de datos en `.env` |
| La contraseña de `.env` no funciona | El motor solo toma la contraseña al crear la base por primera vez; se cambió `.env` después | `docker compose down -v && make up`. **Borra los datos locales** |
| El puerto de la base de datos está ocupado (por ejemplo, 5432 o 3306) | Hay otra base de datos del mismo motor en la máquina, instalada a mano o de otro proyecto | Detén la otra, o cambia el puerto en `.env` (por ejemplo `5433`) y ajusta la dirección de la base de datos |
| El cliente de base de datos no puede autenticarse (por ejemplo, `authentication method 10 not supported`) | El cliente es demasiado viejo para la versión del motor | Actualiza tu cliente, o usa uno al día como DBeaver Community |
| La contraseña es correcta pero la conexión falla, o el error sale **en español** | Te estás conectando a una base de datos instalada en Windows (que puede responder en español), no a la de Docker, que ocupa el mismo puerto | Detén o desinstala la de Windows, o cambia el puerto de la de Docker |

## Commits rechazados

| Síntoma | Causa probable | Solución |
|---|---|---|
| "Mensaje de commit inválido" | No sigue el formato Conventional Commits | Usa `feat: …`, `fix: …`, `docs: …`, etc. |
| "No se permite commitear '.env'" | Se intentó subir un archivo con secretos | Sácalo del commit: `git restore --staged .env` |
| "La constitución cambió" | El commit modifica las reglas del proyecto (`equipo/reglas.md`) o los principios (`equipo/principios.md`) | Revierte el cambio. Si dirección técnica aprueba el de las reglas: `APPROVED_CONSTITUTION=1 git commit ...`. Ver [La constitución](la-constitucion.md#si-algo-falla) |
| "El perfil del proyecto (equipo/perfil.json) cambió" | El commit crea, cambia o elimina el perfil y nadie lo confirmó | Revísalo con `make profile` y repite el commit con `APPROVED_PROFILE=1 git commit ...` |
| "Estos archivos de la parte «…» no se modifican una vez versionados" | El commit cambia, renombra o borra un archivo que el perfil declara inmutable (por ejemplo, una migración) | Deja el archivo como estaba y crea uno nuevo |
| "La parte «…» no pasa la revisión de formato" | El verbo `formato` del perfil falló en una parte que el commit toca | Formatea el código de esa parte y repite el commit |
| `equipo/perfil.json:` seguido de un error | El perfil está mal escrito, y con un perfil inválido no entra ningún commit | `make profile` dice qué corregir. Ver [El perfil del proyecto](perfil-del-proyecto.md#cuando-algo-falla) |
| "La configuración de agentes o la constitución generada están desactualizadas" | Alguien cambió `equipo/` (los roles, la configuración, el perfil o las reglas del proyecto) o `.agents/` sin regenerar, o editó a mano `.specify/memory/constitution.md` | `make sync` y agrega el resultado al commit |
| "Los archivos del kit no coinciden con .bowser-spec-kit-ai/" | Se editó a mano un archivo del kit, o se actualizó el submódulo sin instalar | `make check-kit` para ver cuál. Revierte el cambio, o ejecuta `make install-kit` |
| "El costo de … ya está cerrado" | Se modificó el `costos.json` de una funcionalidad terminada | Revierte el cambio: `git checkout -- <archivo>` |
| ⚠ "sin actualizar estado.md" | Cambió la especificación, el plan o las tareas, y el estado no | Es un aviso, no bloquea. Actualiza `estado.md` y agrégalo al commit |
| `make doctor` dice "Hooks de git inactivos" | No se activaron en este clon | `make install-hooks` |
| `make doctor` dice "Hooks de git sin permiso de ejecución" | Los scripts perdieron el permiso, y git los ignora sin avisar | `make install-hooks` |

Qué revisa cada comprobación y por qué: [Hooks de git](hooks-de-git.md).

## El kit y sus actualizaciones

| Síntoma | Causa probable | Solución |
|---|---|---|
| "Submódulo .bowser-spec-kit-ai/ sin inicializar", o la carpeta está vacía | Se clonó sin `--recursive` | `git submodule update --init` |
| `make update-kit` se detiene por archivos modificados | Alguien cambió en el proyecto un archivo del kit | Decide entre llevarlo al kit, excluirlo o descartarlo. Ver [Guía de actualización](actualizacion.md#cuando-la-actualización-se-detiene) |
| Actualicé el kit, pero los modelos siguen iguales | Los modelos salen de `equipo/config.json`, que el kit no sobrescribe | `make update-models` y reinicia el agente |
| Después de actualizar, `git status` muestra archivos modificados sin cambios de contenido | Cambió el permiso de ejecución de los scripts | Inclúyelos en el commit |
| Después de cambiar de rama, el kit parece de otra versión | La otra rama usa otra versión del submódulo | `git submodule update` |

## Integración continua

| Síntoma | Causa probable | Solución |
|---|---|---|
| Falla al descargar el submódulo | El repositorio del kit es privado | Configura el secreto `KIT_TOKEN` en el repositorio del proyecto |
| Aviso "Ningún workflow del proyecto ejecuta estos verbos del perfil" | El proyecto no tiene su workflow, o no cubre una parte o un verbo nuevos | `/bowser-ci`. Para ver el detalle: `make check-ci` |
| "Estos archivos de la parte … no se modifican una vez versionados" | El Pull Request edita, renombra o borra un archivo que el perfil declara inmutable | Deshaz ese cambio y crea un archivo nuevo |
| Un verbo falla en GitHub con "command not found" | El workflow del proyecto no instala esa herramienta | `/bowser-ci`, o agrega el paso a tu `ci.yml` |
| Una herramienta fijada en el workflow ya no soporta la versión del lenguaje (por ejemplo, un linter anterior al lenguaje que usa el proyecto) | El proyecto subió de versión y el workflow no | Sube la versión de la herramienta en tu `ci.yml` |
| Después de actualizar el kit, algunas comprobaciones corren dos veces | Tu `ci.yml` venía del kit y repite lo que ahora hace `bowser.yml` | Borra de `ci.yml` los grupos `agentes`, `controles` y `secretos` |
| "El código generado de la parte … no estaba al día" | Se cambió la fuente del código generado (una consulta, el contrato de la API…) sin regenerar, o hay otros cambios sin commit en esa parte | `make generate` y agrega el resultado al commit |
| "cobertura falló en la parte …" | La cobertura quedó bajo el mínimo que fijan las reglas del proyecto | Pide las pruebas que faltan. La salida del verbo, justo encima, muestra dónde. Ver [Cobertura](cobertura-y-codigo-generado.md#cuando-no-alcanza-el-mínimo) |
| Pasa en mi máquina y falla en GitHub | Versiones distintas de las herramientas, o un archivo sin subir | Instala las versiones que fija el workflow del proyecto y revisa `git status` |

Más: [Integración continua](integracion-continua.md#cuando-falla).

## Los agentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| El agente no usa los subagentes | La configuración no está generada, o la herramienta no los soporta | `make sync` y reinicia el agente. Si no hay soporte, el orquestador asume los roles en secuencia |
| "Configuración de agentes desactualizada" | Cambió una fuente sin regenerar (un rol, una skill, la configuración o el perfil del proyecto) | `make sync` y commit |
| El agente da vueltas sin terminar una tarea | La instrucción es ambigua, o la tarea es muy grande | Detenlo. Divide la tarea o da una instrucción concreta |
| El agente quiere usar `--no-verify` o desactivar una prueba | Busca que el control pase, no resolver el problema | No lo permitas. Pídele que corrija la causa |
| El presupuesto de la suscripción se agota muy rápido | Un modelo caro en un rol de mucho volumen, o el orquestador hace el trabajo en vez de delegar | `make costs` para ver qué agente consume. Ver [Modelos por agente](modelos.md) |
| Escribo `/bowser-status` y la herramienta no lo reconoce | La configuración no está generada, la sesión es anterior al cambio, o estás en Codex | `make sync` y abre una sesión nueva. En Codex se escribe `$bowser-status`. Ver [Comandos](comandos.md#dentro-de-la-herramienta) |
| Desapareció una skill mía de `.agents/skills/` | Su carpeta empezaba con `bowser-`, el prefijo de los comandos generados | Recupérala con git y cámbiale el nombre |
| Desaparecieron `go-backend`, `react-frontend` o `postgres-db` al instalar | El proyecto tiene perfil y no las nombra: cada proyecto recibe solo las skills que su perfil pide | Si las usa, agrégalas a las `skills` del perfil y ejecuta `make install-kit`. Ver [Skills](skills.md#qué-skills-llegan-a-tu-proyecto) |
| "Las skills instaladas no son las que pide el perfil" | Cambiaron las `skills` del perfil y no se instaló | `make install-kit`. Ver [Skills](skills.md#cuando-algo-falla) |
| "El perfil pide la skill «x», que no está en el catálogo del kit" | Nombre mal escrito, o esa tecnología no tiene skill todavía | `make skills` lista las que hay. Los agentes trabajan sin ella mientras tanto |
| `make models` marca un modelo con ⚠ | Tu instalación no reconoce ese modelo | Compruébalo con `opencode models opencode-go` y corrige `equipo/config.json` |

## Estado y costos

| Síntoma | Causa probable | Solución |
|---|---|---|
| `make status` avisa "cambió después de estado.md" o "aprobación no registrada" | El estado no se actualizó en la última sesión | Pregúntale al orquestador "¿por dónde quedamos?": compara con los archivos, corrige `estado.md` y te pide confirmar lo que falte |
| `make costs` dice "No se encontró 'opencode'" | La terminal no es la de Ubuntu, o OpenCode no está instalado ahí | Abre la terminal de Ubuntu |
| `make costs` dice "Aún no hay consumo registrado" aunque ya trabajaste | Las sesiones se hicieron en otra carpeta o con otra herramienta, o el kit es anterior a la 1.6.3 | `make update-kit` y vuelve a ejecutarlo. Comprueba con `opencode session list` desde la carpeta del proyecto |
| `make costs` dice "Sin precio para: …" | El modelo no está en models.dev | Agrega su precio en `equipo/config.json`, en `costos.precios_manuales` |

Más: [Costos de IA](costos.md#avisos-y-qué-hacer).

## Si nada de esto ayuda

1. Ejecuta `make doctor` y lee todo lo que marca, no solo la primera línea.
2. Lee el mensaje de error completo. Los mensajes del kit casi siempre incluyen el comando que lo corrige.
3. Pásale al orquestador el error completo y el comando que lo produjo.
4. Si el problema es del kit (un control que rechaza algo válido, un comando que falla sin razón), repórtalo en el repositorio del kit: probablemente le pase a otros.
