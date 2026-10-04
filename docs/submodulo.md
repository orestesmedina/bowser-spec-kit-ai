# El kit como submódulo

- [Introducción](#introducción)
- [Por qué un submódulo](#por-qué-un-submódulo)
- [Por qué se copian los archivos](#por-qué-se-copian-los-archivos)
- [Archivos gestionados y semillas](#archivos-gestionados-y-semillas)
- [El manifiesto](#el-manifiesto)
- [Qué pasa en una actualización](#qué-pasa-en-una-actualización)
- [Cómo se evita que alguien edite el kit](#cómo-se-evita-que-alguien-edite-el-kit)
- [Trabajar con el submódulo](#trabajar-con-el-submódulo)
- [Sin submódulo](#sin-submódulo)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit no se copia una vez y se olvida. Vive en su propio repositorio, y cada proyecto lo incluye como **submódulo de git** en la carpeta `.bowser-spec-kit-ai/`. Esta página explica cómo llegan sus archivos al proyecto y cómo se actualizan sin perder lo que es propio de cada proyecto.

## Por qué un submódulo

Un submódulo es un repositorio dentro de otro, fijado en una versión concreta. Para el kit eso da tres ventajas:

- **Cada proyecto sabe exactamente qué versión del kit usa**, y la cambia cuando quiere, no cuando el kit cambia.
- **Mejorar el kit mejora todos los proyectos**, con un comando en cada uno.
- **El kit completo está siempre a mano**, incluida esta documentación, en la versión exacta que el proyecto tiene instalada.

## Por qué se copian los archivos

Las herramientas buscan sus archivos en la raíz del proyecto: el agente de código lee `AGENTS.md` ahí, git busca los hooks ahí, GitHub busca `.github/workflows/` ahí. Ninguna mira dentro de `.bowser-spec-kit-ai/`.

Por eso instalar el kit significa **copiar** sus archivos del submódulo a la raíz. El submódulo es el original; la raíz tiene las copias que usan las herramientas.

```bash
make instalar-kit      # copia desde el submódulo a la raíz
make actualizar-kit    # trae la última versión del kit y luego instala
```

## Archivos gestionados y semillas

El kit copia dos clases de archivos, y las trata de forma muy distinta:

| | Gestionados | Semillas |
|---|---|---|
| Cuáles | `AGENTS.md`, `Makefile`, `.agents/skills/`, `.githooks/`, `.github/workflows/`, la constitución, `equipo/agentes/`, `equipo/adaptadores/`, `equipo/orquestador.md`, `scripts/`, `docs/plantillas/` | `equipo/config.json`, `.github/CODEOWNERS`, `.env.example`, `docker-compose.yml` |
| Cuándo se copian | En cada instalación y en cada actualización | Una sola vez, si no existen |
| De quién son | Del kit | Del proyecto, desde que se copian |
| ¿Se editan en el proyecto? | No | Sí |

La diferencia tiene una razón. Los archivos gestionados son las reglas y los controles: deben ser iguales en todos los proyectos y mejorar con el kit. Las semillas son configuración: cada proyecto tiene sus modelos, sus dueños y sus servicios, y una actualización no debe pisarlos.

> [!NOTE]
> Como las semillas no se actualizan solas, cuando el kit cambia algo en una de ellas lo indica entre los pasos manuales de la versión, o trae un comando que muestra las diferencias y pide confirmación, como `make actualizar-modelos`.

Hay archivos del kit que **no** llegan al proyecto, porque solo tienen sentido en el repositorio del kit: su `README.md`, su registro de cambios, su licencia y esta documentación, que se lee directamente en `.bowser-spec-kit-ai/docs/`.

## El manifiesto

`.kit-manifest.json` es la lista de los archivos gestionados que hay en el proyecto, cada uno con una huella de su contenido, más la versión del kit instalada:

```json
{
  "version": "1.7.1",
  "archivos": {
    "AGENTS.md": "3f2a…",
    ".githooks/pre-commit": "9c41…"
  }
}
```

Esa huella permite dos cosas que una copia simple no podría:

- **Saber si alguien editó un archivo del kit** en el proyecto: su contenido ya no coincide con la huella.
- **Saber qué borrar:** si un archivo estaba en el manifiesto y el kit ya no lo trae, la actualización lo elimina.

El manifiesto se sube a git junto con el resto del proyecto.

## Qué pasa en una actualización

Para cada archivo gestionado, la instalación compara tres cosas: la versión nueva del kit, la huella guardada en el manifiesto y el archivo que hay hoy en el proyecto.

| Situación | Qué hace |
|---|---|
| El archivo no existe en el proyecto | Lo copia |
| Existe y nadie lo tocó desde la última instalación | Lo reemplaza por la versión nueva |
| Existe y **alguien lo modificó** en el proyecto | **Se detiene** y lo muestra. No pisa nada |
| Existía antes de que el kit lo gestionara | Lo reemplaza y guarda el anterior en `.kit-respaldo/` |
| El kit ya no lo trae | Lo borra del proyecto |

El caso que importa es el tercero: una actualización nunca destruye en silencio un cambio local. Qué hacer cuando se detiene está en la [Guía de actualización](actualizacion.md#cuando-la-actualización-se-detiene).

## Cómo se evita que alguien edite el kit

Editar un archivo gestionado dentro del proyecto es un error fácil de cometer, sobre todo para un agente que solo quiere "arreglar" algo. Hay cuatro barreras:

| Barrera | Qué hace |
|---|---|
| Las instrucciones del orquestador | Le prohíben tocar el submódulo y los archivos del manifiesto |
| Los [hooks del agente](hooks-del-agente.md) (Claude Code) | Bloquean la edición en el momento |
| El [hook de git](hooks-de-git.md) | Rechaza el commit si un archivo del kit no coincide con el submódulo |
| La [integración continua](integracion-continua.md) | Repite la comprobación en GitHub |

La comprobación se puede ejecutar a mano:

```bash
make verificar-kit
```

Si un proyecto necesita de verdad su propia versión de un archivo, lo declara en `"kit.excluir"`. Ver [Personalizar un proyecto](personalizar.md).

## Trabajar con el submódulo

Un submódulo tiene tres particularidades que sorprenden a quien no los ha usado:

| Situación | Qué hacer |
|---|---|
| Clonar un proyecto | `git clone --recursive …`. Sin esa opción, la carpeta del kit queda vacía |
| Ya clonaste sin `--recursive` | `git submodule update --init` |
| Cambias de rama y la otra rama usa otra versión del kit | `git submodule update` |
| La integración continua no puede descargar el kit | Tu copia del kit es privada: configura el secreto `KIT_TOKEN`. Ver [Configuración](configuracion.md#configuración-en-github) |

> [!WARNING]
> Nunca edites archivos dentro de `.bowser-spec-kit-ai/`. Ese cambio no llega al repositorio del kit y se pierde en la siguiente actualización. Los cambios al kit se hacen en su repositorio.

## Sin submódulo

Si un proyecto no puede usar submódulos, el kit se puede copiar a mano:

```bash
cp -r bowser-spec-kit-ai/. .
make sincronizar
make instalar-hooks
```

Funciona, pero se pierde lo que da el submódulo: no hay manifiesto, no hay actualización con un comando y no hay detección de archivos del kit modificados. Las mejoras del kit habría que traerlas a mano.

## Siguientes pasos

- [Guía de actualización](actualizacion.md): actualizar un proyecto, paso a paso.
- [Personalizar un proyecto](personalizar.md): cuándo y cómo excluir un archivo del kit.
- [Estructura de carpetas](estructura.md): la clase de cada archivo del proyecto.
