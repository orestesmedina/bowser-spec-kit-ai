# Hooks de git

- [Introducción](#introducción)
- [Para qué sirven en este kit](#para-qué-sirven-en-este-kit)
- [Cómo se activan](#cómo-se-activan)
- [Qué revisa cada commit](#qué-revisa-cada-commit)
    - [Antes de guardar: pre-commit](#antes-de-guardar-pre-commit)
    - [El mensaje: commit-msg](#el-mensaje-commit-msg)
- [Cuando un commit es bloqueado](#cuando-un-commit-es-bloqueado)
- [Excepciones autorizadas](#excepciones-autorizadas)
- [Lo que los hooks no hacen](#lo-que-los-hooks-no-hacen)
- [Cambiar los hooks](#cambiar-los-hooks)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Un hook de git es un programa que git ejecuta por su cuenta en un momento determinado. El kit usa dos, y ambos se ejecutan **cada vez que alguien hace un commit**: uno revisa los archivos que se van a guardar y el otro revisa el mensaje. Si alguno encuentra un problema, el commit no se guarda y git muestra por qué.

Los hooks viven en la carpeta `.githooks/` del proyecto:

| Archivo | Cuándo se ejecuta | Qué revisa |
|---|---|---|
| `.githooks/pre-commit` | Antes de guardar el commit | Los archivos incluidos en el commit |
| `.githooks/commit-msg` | Después de escribir el mensaje | El formato del mensaje |

## Para qué sirven en este kit

En este proceso el código lo escribe un agente de IA. A un agente se le pueden dar instrucciones ("nunca subas contraseñas", "no modifiques una migración ya aplicada"), pero una instrucción es algo que el agente puede olvidar o interpretar mal. Un hook no depende de que el agente recuerde nada: es git el que revisa, y lo hace igual para una persona, para Claude Code, para Codex o para OpenCode.

Por eso las reglas más importantes del kit no están solo escritas en las instrucciones de los agentes: están también en los hooks. Las instrucciones evitan la mayoría de los errores; los hooks detienen los que se escapan.

## Cómo se activan

Git busca los hooks en la carpeta que indique su configuración `core.hooksPath`. El kit la apunta a `.githooks/`:

```bash
make instalar-hooks
```

Esa configuración se guarda en tu copia local del repositorio y **no viaja con el proyecto**. Por eso hay dos situaciones:

- **Quien instala el kit en un proyecto** no tiene que hacer nada: `make instalar-kit` ya los activa.
- **Quien clona un proyecto que ya tiene el kit** debe ejecutar `make instalar-hooks` una vez. Sin ese paso, sus commits no pasan por ningún control.

Para comprobar que están activos:

```bash
make doctor
```

Debe mostrar `✓ Hooks de git activos`.

> [!WARNING]
> Un hook sin permiso de ejecución no da error: git simplemente lo ignora y el commit pasa sin revisión. `make doctor` detecta ese caso, y tanto `make instalar-kit` como `make instalar-hooks` lo corrigen.

## Qué revisa cada commit

### Antes de guardar: pre-commit

Revisa únicamente los archivos incluidos en el commit. Hace estas comprobaciones, en este orden:

| Qué revisa | Por qué | Cómo corregirlo |
|---|---|---|
| Que no haya secretos: archivos `.env`, `*.pem`, `*.key` o dentro de `secrets/`. Si `gitleaks` está instalado, además busca claves y contraseñas dentro del contenido | Un secreto subido a git queda en el historial para siempre, aunque después se borre | Saca el archivo del commit. `.env.example` sí está permitido, porque no lleva valores reales |
| Que los archivos del kit coincidan con el submódulo | Los archivos que vienen del kit no se editan en el proyecto: la siguiente actualización los pisaría | `make verificar-kit` muestra cuál cambió. Revierte el cambio, o ejecuta `make instalar-kit` si actualizaste el submódulo sin instalar |
| Que la constitución no haya cambiado | Son las reglas no negociables del proyecto; cambiarlas requiere una decisión de dirección técnica | Revierte el cambio. Si el cambio llega por una actualización del kit, pasa sin problema |
| Que no se modifique ni se borre una migración existente | Una migración ya aplicada en otra base de datos no se puede "corregir": esa base quedaría distinta al código | Deja la migración como estaba y crea una nueva |
| Que el código Go esté formateado | Un formato único evita diferencias que no son cambios reales | `gofmt -w <archivo>` |
| Que el código del frontend esté formateado | Lo mismo, para TypeScript y CSS | `cd frontend && npx prettier --write .` |
| Que la configuración de los agentes esté al día | Si cambió un rol o una skill y no se regeneraron los archivos de cada herramienta, los agentes trabajarían con instrucciones viejas | `make sincronizar` y agrega el resultado al commit |
| Que no cambie un `costos.json` cerrado | El costo de una funcionalidad se congela al aprobar su Pull Request | Revierte el cambio |

En un proyecto con [perfil](perfil-del-proyecto.md), las comprobaciones de migraciones y de formato de esta tabla se reemplazan por lo que el perfil declara:

| Qué revisa | Por qué | Cómo corregirlo |
|---|---|---|
| Que el perfil no haya cambiado sin confirmación, y que esté bien escrito | Sus comandos se ejecutan en la máquina de cada persona y en la integración continua | Revísalo con `make profile` y confirma con `APROBADO_PERFIL=1` |
| Que no se modifique, renombre ni borre un archivo `inmutable` de ninguna parte | Es la misma regla de las migraciones, para la carpeta y el patrón que use el proyecto | Deja el archivo como estaba y crea uno nuevo |
| Que pase el verbo `formato` de cada parte que el commit toca | Un formato único, con la herramienta de cada tecnología | Formatea el código de esa parte |

Un commit que solo elimina archivos pasa por las mismas comprobaciones que cualquier otro.

Hay una comprobación más que **avisa pero no bloquea**: si cambian `spec.md`, `plan.md` o `tasks.md` de una funcionalidad y no cambia su `estado.md`, muestra una advertencia, porque el estado probablemente quedó desactualizado.

### El mensaje: commit-msg

Exige el formato [Conventional Commits](https://www.conventionalcommits.org/es/): un tipo, dos puntos y una descripción.

```
feat(users): registro con email
fix: la dirección de envío se borraba al editar un pedido
docs: actualiza la guía de instalación
```

Los tipos aceptados son `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci`, `perf`, `build`, `style` y `revert`. El texto entre paréntesis (el área afectada) es opcional. Los mensajes automáticos de git para merges y reverts se aceptan tal cual.

El formato no es un capricho: permite leer el historial de un vistazo y es lo que usa el documentador para armar el registro de cambios del producto.

## Cuando un commit es bloqueado

El hook muestra una línea por cada problema, empezando con `✗`, y termina con:

```
Commit bloqueado por los controles del proyecto.
```

Qué hacer:

1. **Lee el mensaje.** Cada uno indica qué archivo es y, casi siempre, el comando para corregirlo.
2. **Corrige la causa** y vuelve a hacer el commit.
3. Si el commit lo estaba haciendo un agente, es el agente quien debe corregir la causa. No le pidas ni le permitas que la esquive.

> [!WARNING]
> Nunca uses `git commit --no-verify`, ni permitas que un agente lo haga. Esa opción se salta los hooks, pero no arregla nada: la [integración continua](integracion-continua.md) repite las mismas comprobaciones en GitHub y el cambio se rechaza ahí, más tarde y a la vista de todo el equipo.

Si los hooks fallan todos a la vez con mensajes sobre `python3`, el problema no es tu cambio: estás haciendo el commit desde Windows y no desde Ubuntu. Revisa [Windows y WSL](windows-wsl.md).

## Excepciones autorizadas

Tres comprobaciones admiten una confirmación explícita, pensada para que la tome una persona con autoridad y no un agente:

| Situación | Cómo se autoriza |
|---|---|
| Cambiar la constitución | `APROBADO_CONSTITUCION=1 git commit ...` |
| Corregir un `costos.json` ya cerrado | `APROBADO_COSTOS=1 git commit ...` |
| Crear, cambiar o eliminar el perfil del proyecto | `APROBADO_PERFIL=1 git commit ...` |

Las tres dejan constancia en el propio comando de que alguien decidió saltarse la regla. Las demás comprobaciones no tienen excepción.

## Lo que los hooks no hacen

Los hooks están hechos para ser rápidos, así que no ejecutan las pruebas ni los linters completos. Tampoco ven lo que pasa fuera de tu máquina. Tres límites que conviene conocer:

- **No corren las pruebas.** Eso lo hace `make test` en tu máquina y la integración continua en GitHub.
- **Algunas comprobaciones dependen de herramientas opcionales.** Si no tienes `gitleaks`, `gofmt` o las dependencias del frontend instaladas, esa comprobación se salta sin avisar. La integración continua sí la hace siempre.
- **Solo actúan donde están activos.** Un clon sin `make instalar-hooks` no tiene ningún control local.

Por eso los hooks son una de varias capas, no la única:

| Capa | Cuándo actúa | Se puede saltar |
|---|---|---|
| Instrucciones a los agentes | Mientras el agente trabaja | Sí: el agente puede equivocarse |
| [Hooks del agente](hooks-del-agente.md) | Cuando el agente intenta editar un archivo (solo Claude Code) | Solo aplican en esa herramienta |
| **Hooks de git** | En cada commit, en tu máquina | Con `--no-verify`, o si no están activos |
| [Integración continua](integracion-continua.md) | En cada Pull Request, en GitHub | No |

## Cambiar los hooks

Los archivos de `.githooks/` vienen del kit, así que no se editan dentro del proyecto: el propio pre-commit lo detectaría. Hay dos caminos:

- **Si la regla nueva le sirve a todos los proyectos:** se agrega en el repositorio del kit y llega a cada proyecto con `make actualizar-kit`.
- **Si es propia de un proyecto:** agrega `.githooks/` a `"kit.excluir"` en `equipo/config.json`. Desde ese momento los hooks son del proyecto y el kit deja de actualizarlos, incluidas las mejoras futuras. Ver [Personalizar un proyecto](personalizar.md).

## Siguientes pasos

- [Cobertura y código generado](cobertura-y-codigo-generado.md): dos controles que no están en los hooks porque necesitan ejecutar las pruebas.
- [Capas de control](capas-de-control.md): el resumen de todas las protecciones del kit.
- [Problemas comunes](problemas-comunes.md#commits-rechazados): los mensajes de error más frecuentes y su solución.
