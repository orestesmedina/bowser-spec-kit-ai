# Guía de actualización

- [Introducción](#introducción)
- [Cómo se numeran las versiones](#cómo-se-numeran-las-versiones)
- [Actualizar un proyecto](#actualizar-un-proyecto)
- [Leer las novedades](#leer-las-novedades)
- [Pasos manuales](#pasos-manuales)
- [Cuando el kit recomienda otros modelos](#cuando-el-kit-recomienda-otros-modelos)
- [Cuando la actualización se detiene](#cuando-la-actualización-se-detiene)
- [Después de actualizar](#después-de-actualizar)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El kit mejora con el tiempo, y cada proyecto decide cuándo adoptar una versión nueva. Actualizar es un comando, pero conviene saber qué hace, qué no hace y qué revisar después.

## Cómo se numeran las versiones

El kit usa tres números, por ejemplo `1.7.1`:

| Cambia | Significa | Qué esperar |
|---|---|---|
| El tercero (`1.7.0` → `1.7.1`) | Correcciones y documentación | Nada que hacer |
| El segundo (`1.6.4` → `1.7.0`) | Funciones nuevas, compatibles | Puede traer pasos opcionales |
| El primero (`1.x` → `2.0.0`) | El proyecto debe hacer algo a mano para seguir funcionando | Lee los pasos antes de actualizar |

La versión instalada en un proyecto está en `.kit-manifest.json`. Cada cambio queda registrado en las [novedades de cada versión](../CHANGELOG.md).

## Actualizar un proyecto

Desde la raíz del proyecto, con la rama al día y sin cambios pendientes:

```bash
make actualizar-kit
```

El comando hace tres cosas:

1. Trae la última versión del kit al submódulo.
2. Instala: reemplaza los archivos del kit que cambiaron, agrega los nuevos y borra los que el kit eliminó.
3. Regenera la configuración de los agentes y muestra las novedades.

Lo que **no** hace: tocar las semillas (`equipo/config.json`, `.github/CODEOWNERS`, `.env.example`, `docker-compose.yml`) ni ningún archivo propio del proyecto.

Al terminar, revisa los cambios y guárdalos:

```bash
git status
git add . && git commit -m "chore: actualiza kit de desarrollo"
```

## Leer las novedades

`make actualizar-kit` muestra al final lo que cambió entre la versión que tenías y la nueva. Para volver a verlo en cualquier momento:

```bash
make novedades                # historial completo
make novedades DESDE=1.6.0    # solo desde una versión
```

## Pasos manuales

Algunas versiones traen una sección **Al actualizar**: cosas que el kit no puede hacer por ti. `make actualizar-kit` las reúne al final, de la versión más antigua a la más nueva:

```
⚠ PASOS MANUALES AL ACTUALIZAR:
  - docker-compose.yml es una semilla y no se actualiza solo. Si tu proyecto todavía tiene…  (1.6.2)
  - En local, instala Node 24 (nvm install 24)…  (1.6.2)
```

Hazlos **antes** del commit de la actualización. Suelen ser de tres tipos: un cambio a una semilla que el kit no puede tocar, una herramienta que hay que instalar en cada máquina, o un comando que hay que ejecutar una vez.

## Cuando el kit recomienda otros modelos

Los modelos de cada agente están en `equipo/config.json`, que es del proyecto. Si la versión nueva del kit recomienda una distribución distinta, `make actualizar-kit` lo avisa pero no cambia nada. Para adoptarla:

```bash
make actualizar-modelos
```

Muestra qué cambiaría, pide confirmación y copia **solo** la asignación de modelos. El resto de tu configuración (herramientas activas, temperaturas, exclusiones) se conserva. Después, reinicia el agente de código.

## Cuando la actualización se detiene

```
✗ Estos archivos del kit fueron modificados en este proyecto:
    .githooks/pre-commit
```

Alguien editó en el proyecto un archivo que viene del kit. La actualización no lo pisa: se detiene y te deja decidir.

| Si el cambio… | Haz esto |
|---|---|
| Le sirve a todos los proyectos | Llévalo al repositorio del kit y vuelve a actualizar. Ver [Cómo contribuir](contribuir.md) |
| Es propio de este proyecto | Agrega el archivo a `"kit.excluir"` en `equipo/config.json`. Ver [Personalizar un proyecto](personalizar.md) |
| Fue un error | Descártalo con `make instalar-kit FORZAR=1`. Guarda una copia en `.kit-respaldo/` |

> [!WARNING]
> `FORZAR=1` es una decisión de una persona, no de un agente. Antes de usarlo, mira qué cambió: ese cambio local puede ser importante.

## Después de actualizar

Tres comprobaciones rápidas:

```bash
make doctor          # el entorno y el kit, al día
make verificar-kit   # los archivos del proyecto coinciden con el kit
make ci              # lo mismo que hará la integración continua
```

Si la versión nueva trae controles nuevos, el primer commit o el primer Pull Request puede ser rechazado por algo que antes no se revisaba. Es lo esperado: corrige lo que indique el mensaje.

## Siguientes pasos

- [Novedades de cada versión](../CHANGELOG.md): el historial completo.
- [El kit como submódulo](submodulo.md): cómo funciona la instalación por dentro.
- [Problemas comunes](problemas-comunes.md): errores frecuentes al actualizar.
