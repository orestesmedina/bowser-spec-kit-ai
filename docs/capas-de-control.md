# Capas de control

- [Introducción](#introducción)
- [Por qué varias capas](#por-qué-varias-capas)
- [Las seis capas](#las-seis-capas)
- [Qué protege cada regla](#qué-protege-cada-regla)
- [Dónde está la protección real](#dónde-está-la-protección-real)
- [Cuando un control falla](#cuando-un-control-falla)
- [Agregar un control](#agregar-un-control)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

En este proceso el código lo escribe una IA, y las personas no leen cada línea. Lo que hace que eso sea razonable son los **controles automáticos**: comprobaciones que no dependen de que alguien se acuerde ni de que el agente obedezca.

Esta página da la vista de conjunto. Cada capa tiene su propia página con el detalle.

## Por qué varias capas

Ningún control es perfecto. Las instrucciones se pueden malinterpretar, un hook se puede saltar, una revisión humana se puede hacer con prisa. Lo que funciona es ponerlos **en serie**: lo que se le escapa a uno lo detiene el siguiente.

Las capas van de la más temprana y barata a la más tardía y segura:

```
el agente trabaja → intenta editar → hace commit → abre un Pull Request → una persona aprueba
        │                  │              │                 │                       │
  instrucciones     hooks del agente  hooks de git   integración continua     aprobación
                                                      y CODEOWNERS
```

Cuanto antes se detiene un error, menos cuesta corregirlo. Cuanto más tarde está el control, más difícil es saltárselo.

## Las seis capas

| Capa | Dónde vive | Cuándo actúa | Protege contra | ¿Se puede saltar? |
|---|---|---|---|---|
| **Instrucciones** | `AGENTS.md`, roles, skills, constitución | Mientras el agente piensa | Errores de criterio | Sí: el agente puede equivocarse |
| **[Hooks del agente](hooks-del-agente.md)** | `equipo/adaptadores/claude/hooks/` | Cuando el agente intenta editar un archivo | Ediciones a archivos protegidos | Solo existen en Claude Code |
| **[Hooks de git](hooks-de-git.md)** | `.githooks/` | En cada commit | Secretos, migraciones editadas, formato, mensajes mal escritos, archivos del kit modificados | Con `--no-verify`, o si no están activos |
| **[Integración continua](integracion-continua.md)** | `.github/workflows/ci.yml` | En cada Pull Request | Todo lo anterior, más pruebas, cobertura, código generado y vulnerabilidades | No |
| **CODEOWNERS** | `.github/CODEOWNERS` | Al aprobar un Pull Request | Cambios a las reglas y a los agentes sin la aprobación de quien decide | No, si la rama está protegida |
| **[Aprobación de una persona](aprobaciones.md)** | El chat y GitHub | En las cuatro puertas | Que se construya algo que nadie pidió | No |

Hay una capa más, que no es automática pero funciona igual: los **agentes revisores**. Todo el código pasa por `qa-tester`, `revisor-codigo` y `seguridad` antes de llegar a una persona. Ver [El equipo de agentes](equipo-de-agentes.md#quién-escribe-no-aprueba).

## Qué protege cada regla

Las reglas más importantes están protegidas en varias capas a la vez:

| Regla | Instrucciones | Hook del agente | Hook de git | Integración continua |
|---|:-:|:-:|:-:|:-:|
| No subir secretos | ✓ | ✓ | ✓ | ✓ |
| No modificar una migración aplicada | ✓ | ✓ | ✓ | ✓ |
| No editar la constitución | ✓ | ✓ | ✓ | Avisa |
| No editar archivos del kit | ✓ | ✓ | ✓ | ✓ |
| No editar `costos.json` a mano | ✓ | ✓ | Si está cerrado | |
| Configuración de agentes al día | ✓ | | ✓ | ✓ |
| Código formateado | ✓ | Lo formatea | ✓ | ✓ |
| Mensajes de commit con formato | ✓ | | ✓ | |
| Pruebas pasando | ✓ | | | ✓ |
| Cobertura mínima de la capa de servicio | ✓ | | | ✓ |
| Código generado al día | ✓ | | | ✓ |
| Sin vulnerabilidades conocidas | ✓ | | | ✓ |

## Dónde está la protección real

**En git y en la integración continua.** Las otras capas son ayuda adicional.

- Las instrucciones evitan la mayoría de los errores, pero un agente puede no seguirlas.
- Los hooks del agente detienen el error antes, pero solo existen en una herramienta.
- Los hooks de git cubren a cualquier herramienta y a cualquier persona, pero solo donde están activos.
- La integración continua corre en GitHub, fuera del alcance de quien hizo el cambio. Es la única que no se puede saltar.

La consecuencia práctica: **proteger la rama principal** en GitHub, exigiendo que la integración continua pase y la aprobación de `CODEOWNERS`. Sin eso, las capas anteriores son la única barrera. Ver [Configuración](configuracion.md#configuración-en-github).

## Cuando un control falla

La regla es la misma en todas las capas: **se corrige la causa, no el control**.

| Tentación | Por qué no |
|---|---|
| `git commit --no-verify` | La integración continua repite la comprobación. Solo se pospone el rechazo |
| Desactivar o debilitar una prueba | La prueba estaba diciendo algo. Ahora nadie lo va a oír |
| Editar un archivo generado para que coincida | La próxima generación lo borra |
| Quitar un paso de la integración continua | `ci.yml` viene del kit: el hook lo detecta |
| Pedirle al agente que "lo resuelva como sea" | Va a encontrar la forma de que el control pase, que no es lo mismo que resolver el problema |

Si un control está mal (rechaza algo que debería aceptar), eso es un error del kit: se reporta y se corrige en el kit. Ver [Cómo contribuir](contribuir.md).

## Agregar un control

Cuando algo no debe pasar nunca, no alcanza con escribirlo en las instrucciones. La receta:

1. **Escríbelo en la skill o en la constitución,** para que los agentes lo eviten.
2. **Agrégalo al hook de git,** para detenerlo en el commit.
3. **Agrégalo a la integración continua,** para que no se pueda saltar.

Los pasos 2 y 3 se hacen en el repositorio del kit. Ver [Cómo contribuir](contribuir.md).

## Siguientes pasos

- [Hooks de git](hooks-de-git.md), [Hooks del agente](hooks-del-agente.md) e [Integración continua](integracion-continua.md): cada capa en detalle.
- [Cobertura y código generado](cobertura-y-codigo-generado.md): dos controles que solo viven en la integración continua.
- [La constitución](la-constitucion.md): las reglas que todos estos controles hacen cumplir.
