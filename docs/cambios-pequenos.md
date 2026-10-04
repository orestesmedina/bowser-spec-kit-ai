# Cambios pequeños

- [Introducción](#introducción)
- [Qué es un cambio pequeño](#qué-es-un-cambio-pequeño)
- [Cómo pedirlo](#cómo-pedirlo)
- [Qué pasa por dentro](#qué-pasa-por-dentro)
- [Cuando el orquestador dice que no es pequeño](#cuando-el-orquestador-dice-que-no-es-pequeño)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

No todo cambio merece una especificación y un plan. Corregir una errata o cambiar el texto de un botón con el flujo completo sería un desperdicio. Para eso existe un camino corto: el cambio se hace directo y se valida.

La parte importante es saber **qué cuenta como pequeño**, porque el camino corto se salta las dos aprobaciones que más protegen.

## Qué es un cambio pequeño

Una sola pregunta lo decide: **¿cambia el comportamiento, los datos, la API, los permisos o la seguridad?** Si la respuesta es sí a cualquiera, no es pequeño.

| Es pequeño | No es pequeño |
|---|---|
| Corregir una errata | Cambiar una regla de validación |
| Cambiar el texto de un botón o de un mensaje | Agregar un campo a un formulario |
| Cambiar un color o un espaciado | Cambiar qué datos devuelve un endpoint |
| Reordenar elementos sin cambiar lo que hacen | Cambiar quién puede ver o hacer algo |
| Actualizar un comentario o la documentación | Agregar o cambiar una columna de la base de datos |

El tamaño del cambio en líneas no importa. Cambiar un `>` por un `>=` es una línea y cambia el comportamiento: no es pequeño.

## Cómo pedirlo

> Cambia el texto del botón "Enviar" por "Crear cuenta" en la pantalla de registro.

No hace falta decir que es pequeño ni nombrar ningún flujo: el orquestador lo reconoce.

## Qué pasa por dentro

1. El orquestador delega el cambio directamente en el desarrollador de esa capa.
2. Después aplica la validación: QA, revisión de código y seguridad.
3. Abre el Pull Request, que apruebas como siempre.

Lo que se omite es la especificación, el plan y las tareas. Lo que **no** se omite: las pruebas, los revisores, los [hooks de git](hooks-de-git.md), la [integración continua](integracion-continua.md) y tu aprobación del Pull Request.

## Cuando el orquestador dice que no es pequeño

Si pides algo como cambio pequeño y el orquestador responde que requiere el flujo completo, es porque encontró que toca comportamiento, datos o la API.

Es una de las situaciones en que conviene hacerle caso. Los cambios "de cinco minutos" que resultan no serlo son la fuente clásica de errores en producción: nadie escribió qué debía pasar, así que nadie comprobó que pasara.

Si aun así quieres seguir, el orquestador te explica el riesgo, te ofrece una especificación mínima de pocas líneas y, solo si confirmas explícitamente, procede y lo deja anotado en el Pull Request. Ver [El orquestador](el-orquestador.md#cuando-le-pides-saltarse-el-proceso).

## Siguientes pasos

- [Corregir un bug](bugs.md): cuando algo no funciona como dice la especificación.
- [Construir una funcionalidad](funcionalidad.md): cuando el cambio no es pequeño.
- [Reglas de oro](reglas-de-oro.md).
