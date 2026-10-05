# Pruebas del kit

Comprueban que un cambio en el kit no rompe los proyectos que lo usan. Instalan el kit en proyectos temporales, lo actualizan desde la versión anterior publicada y revisan que los controles sigan bloqueando lo que deben bloquear.

Esta carpeta es solo del repositorio del kit: no se copia a los proyectos. Cómo usarlas al cambiar el kit está en [Cómo contribuir](../docs/contribuir.md#probar-un-cambio).

## Ejecutarlas

En Linux o WSL, desde la raíz del repositorio del kit:

```bash
make test-kit
```

| Opción | Para qué |
|---|---|
| `make test-kit SOLO=costos` | Solo las pruebas que tengan ese texto en el grupo o en la descripción |
| `make test-kit DESDE=v1.7.0` | Probar la actualización desde otra versión anterior (por defecto, el último tag) |
| `make test-kit ESTRICTO=1` | Una prueba omitida cuenta como fallo. Es lo que usa la integración continua |
| `make test-kit CONSERVAR=1` | No borra la carpeta temporal, para investigar un fallo |
| `python3 pruebas/ejecutar.py --lista` | Muestra las pruebas sin ejecutarlas |

Prueban la carpeta de trabajo **tal como está**, con los cambios sin commit y los archivos nuevos. No hace falta hacer commit antes.

## Qué hay

| Archivo | Qué es |
|---|---|
| `ejecutar.py` | El ejecutor: corre las pruebas, muestra el resultado de cada una y termina con error si alguna falla |
| `apoyo.py` | Lo que usan las pruebas: copias del kit, proyectos temporales y comprobaciones |
| `nucleo/` | Las pruebas de lo que no depende de ninguna tecnología |
| `go/` | Las pruebas de lo que hoy es propio de Go, sqlc y los tipos de la API: código generado y cobertura |
| `opencode_simulado.py` | Un OpenCode falso, en formato 1.x y 2.x, para probar `make costos` sin gastar |
| `enlaces.py` | Revisor de enlaces de la documentación. Con `--externos` revisa también los enlaces a otros sitios; eso se hace a mano, porque depende de la red |

Las pruebas de `nucleo/`:

| Archivo | Qué comprueba |
|---|---|
| `prueba_repositorio.py` | Archivos generados al día, `VERSION` con su entrada en el `CHANGELOG`, lista del instalador y enlaces internos de la documentación |
| `prueba_instalacion.py` | Instalación en un proyecto nuevo y en uno existente, qué llega y qué no llega al proyecto, y permisos de los hooks |
| `prueba_actualizacion.py` | Actualización desde la versión anterior con el `Makefile` viejo, archivos editados en el proyecto, `kit.excluir`, archivos retirados y novedades |
| `prueba_controles.py` | Mensajes de commit, secretos, constitución, migraciones, falta de `python3` y el hook de Claude Code |
| `prueba_comandos.py` | Comandos del chat: generados para las tres herramientas, retirados al desactivar una, comandos propios, errores de formato y llegada al actualizar |
| `prueba_costos.py` | `make costos` con OpenCode 1.x y 2.x, avisos y costo cerrado |
| `prueba_perfil.py` | Perfil del proyecto: `make` ejecuta los verbos de cada parte, perfiles mal escritos, controles del commit (confirmación, inmutables, formato) y `make profile DETECTAR=1` |

Las pruebas de `go/`:

| Archivo | Qué comprueba | Necesita |
|---|---|---|
| `prueba_generados.py` | `make generar` y `make verificar-generados`: qué se omite, y que una consulta o un contrato cambiado sin regenerar hace fallar la verificación | `sqlc`, `node` y `npm` |
| `prueba_cobertura.py` | `make cobertura`: qué archivos se miden, el mínimo de 80 % y una ejecución con Go real | `go` |

Van en un grupo aparte porque en la versión 2.0 dejan de ser del núcleo: se irán con la skill de Go (ver la [hoja de ruta](../HOJA-DE-RUTA.md)). Si en tu máquina falta alguno de esos programas, las pruebas que lo necesitan se omiten y el resultado lo dice. Las demás del grupo no necesitan nada instalado.

## En GitHub

El workflow `.github/workflows/kit.yml` ejecuta `make test-kit ESTRICTO=1` en cada Pull Request y en cada push a `main`, con Go, Node y `sqlc` instalados: ahí ninguna prueba puede quedar omitida. Es solo del repositorio del kit: no se copia a los proyectos, aunque esté en una carpeta que sí se copia (`scripts/instalar_kit.py` lo tiene en la lista `NUNCA`).

## Agregar una prueba

Una prueba es una función con el decorador `@prueba` en un archivo `prueba_<tema>.py`, dentro de `nucleo/` o de `go/`. Recibe el entorno, con el que pide un kit y crea proyectos:

```python
from apoyo import afirmar, contiene, prueba


@prueba("instalar por segunda vez no cambia nada")
def instalar_dos_veces(e):
    p = e.proyecto()                       # proyecto nuevo, con el kit instalado y su commit
    r = p.make("instalar-kit")
    contiene(r.salida, "Sin cambios: el proyecto ya estaba al día.")
    afirmar(not p.pendientes(), f"la segunda instalación dejó cambios: {p.pendientes()}")
```

- `e.kit()` devuelve una copia del kit que la prueba puede modificar; `e.kit("anterior")`, la de la versión anterior publicada.
- `p.make(...)`, `p.git(...)` y `p.commit(...)` fallan solos si el comando falla. Con `espera=1` se comprueba lo contrario: que el comando falle.
- `@prueba("…", requiere=("jq",))` omite la prueba, con el motivo, si falta ese programa.

Después de escribir una prueba, **rompe a propósito lo que comprueba** y mira que falle. Una prueba que nunca falló no demuestra nada.

## Límites

- `make costos` se prueba contra un OpenCode simulado. Detecta si se rompe el código del kit, no si OpenCode cambia su formato en una versión nueva.
- La descarga de precios de models.dev no se prueba: las pruebas usan un archivo local de precios.
- El workflow `ci.yml` que se copia a los proyectos solo se prueba de verdad en GitHub.
- La prueba de actualización necesita los tags del repositorio. En un clon sin tags se omite: `git fetch --tags`.
- `make generar` se prueba con `sqlc` real y con un generador de tipos mínimo, no con el de un proyecto real. Que falte `sqlc` en la máquina no se prueba.
- `make doctor`, `make estado` y `make actualizar-modelos` todavía no tienen pruebas automáticas.
