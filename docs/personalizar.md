# Personalizar un proyecto

- [Introducción](#introducción)
- [Qué se puede personalizar sin tocar el kit](#qué-se-puede-personalizar-sin-tocar-el-kit)
- [Comandos propios](#comandos-propios)
- [Roles y skills propios](#roles-y-skills-propios)
- [Workflows propios](#workflows-propios)
- [Tu propia versión de un archivo del kit](#tu-propia-versión-de-un-archivo-del-kit)
    - [Cómo excluir un archivo](#cómo-excluir-un-archivo)
    - [Lo que se pierde](#lo-que-se-pierde)
- [¿Excluir, o llevarlo al kit?](#excluir-o-llevarlo-al-kit)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Cada proyecto tiene necesidades que el kit no conoce: un comando de despliegue, una integración con un servicio externo, una regla propia del negocio. Esta página explica cómo agregarlas sin pelearse con las actualizaciones.

La idea central: **lo que tú agregas es tuyo, y el kit nunca lo toca**. Solo hay fricción cuando quieres cambiar un archivo que viene del kit.

## Qué se puede personalizar sin tocar el kit

| Quieres… | Dónde | ¿Lo afecta una actualización? |
|---|---|---|
| Comandos `make` propios | `proyecto.mk` | No |
| Un rol adicional | Un archivo nuevo en `equipo/agentes/` | No |
| Una skill adicional | Una carpeta nueva en `.agents/skills/` | No |
| Otro workflow de GitHub | Un archivo nuevo en `.github/workflows/` | No |
| Modelos, herramientas, temperaturas | `equipo/config.json` | No: es una semilla |
| Servicios locales adicionales | `docker-compose.yml` | No: es una semilla |
| Quién aprueba los cambios a las reglas | `.github/CODEOWNERS` | No: es una semilla |
| Versiones de las herramientas en la integración continua | Variables del repositorio en GitHub | No |

## Comandos propios

El `Makefile` viene del kit y no se edita. Al final incluye, si existe, un archivo llamado `proyecto.mk`: ahí van los comandos del proyecto.

```makefile
# proyecto.mk
.PHONY: e2e desplegar-staging

e2e: ## Pruebas de punta a punta con Playwright (requiere make up)
	cd frontend && npx playwright test

desplegar-staging: ## Despliega la rama actual al entorno de pruebas
	./scripts-proyecto/desplegar.sh staging
```

El comentario que empieza con `##` es la descripción que muestra `make help`.

> [!WARNING]
> No uses en `proyecto.mk` el nombre de un comando que ya existe en el kit. Los dos se ejecutarían o uno pisaría al otro, y una versión futura del kit puede agregar un comando con ese nombre. La lista está en [Comandos](comandos.md).

## Roles y skills propios

Un archivo nuevo en `equipo/agentes/` o una carpeta nueva en `.agents/skills/` es del proyecto desde que se crea. Después, `make sincronizar`.

- Cómo escribir un rol: [Roles](roles.md#agregar-un-rol).
- Cómo escribir una skill: [Skills](skills.md#agregar-una-skill-propia).

Lo más frecuente es una skill con las convenciones de algo propio del proyecto: una pasarela de pagos, un sistema externo, las reglas de un dominio de negocio.

## Workflows propios

El kit gestiona un solo archivo de `.github/workflows/`: `ci.yml`. Cualquier otro workflow en esa carpeta es del proyecto, por ejemplo uno de despliegue.

Para cambiar la versión de una herramienta dentro de `ci.yml` no hace falta tocar el archivo: se hace con variables del repositorio. Ver [Integración continua](integracion-continua.md#cambiar-la-versión-de-una-herramienta).

## Tu propia versión de un archivo del kit

A veces el proyecto necesita que un archivo del kit sea distinto: un paso extra en el hook, una convención diferente en una skill, una constitución con otras reglas.

Editarlo sin más no funciona: el [hook de git](hooks-de-git.md) rechaza el commit, y la siguiente actualización se detiene al encontrarlo modificado. La forma correcta es declararlo.

### Cómo excluir un archivo

En `equipo/config.json`:

```json
"kit": {
  "excluir": [
    ".githooks/pre-commit",
    ".agents/skills/go-backend/"
  ]
}
```

Una carpeta termina en `/`. Después:

```bash
make instalar-kit    # actualiza el manifiesto: esos archivos ya no figuran como del kit
```

Desde ese momento el archivo es del proyecto: lo editas con libertad, el hook deja de vigilarlo y las actualizaciones no lo tocan.

### Lo que se pierde

Excluir un archivo es una decisión con costo, y el costo llega más tarde:

- **Deja de recibir mejoras.** Si el kit corrige un error en ese archivo o le agrega un control, tu proyecto no lo recibe.
- **Puede quedar desalineado.** Una versión nueva del kit puede asumir algo que tu versión vieja de ese archivo no hace.
- **Nadie te avisa.** No hay un aviso de "el kit cambió un archivo que tú excluiste".

Por eso conviene excluir lo menos posible, y revisar las [novedades de cada versión](../CHANGELOG.md) para traer a mano lo que aplique a los archivos excluidos.

## ¿Excluir, o llevarlo al kit?

| Situación | Lo mejor |
|---|---|
| El cambio le serviría a cualquier proyecto | Llevarlo al repositorio del kit. Ver [Cómo contribuir](contribuir.md) |
| Es algo que el kit hace mal | Llevarlo al kit: es un error, no una preferencia |
| Es propio de este proyecto y cabe en un archivo nuevo | Un rol, una skill, un comando o un workflow propios. Sin excluir nada |
| Es propio de este proyecto y exige cambiar un archivo del kit | Excluirlo |
| Tu equipo quiere reglas distintas en todos sus proyectos | Mantener una copia propia del kit. Ver [Cómo contribuir](contribuir.md#usar-tu-propia-copia-del-kit) |

## Siguientes pasos

- [El kit como submódulo](submodulo.md): cómo distingue el kit sus archivos de los tuyos.
- [Configuración](configuracion.md): las semillas, que son tuyas desde el principio.
- [Guía de actualización](actualizacion.md): qué pasa con las personalizaciones al actualizar.
