# Corregir un bug

- [Introducción](#introducción)
- [Cómo reportarlo](#cómo-reportarlo)
- [Los cinco pasos](#los-cinco-pasos)
- [Por qué la prueba va antes que el arreglo](#por-qué-la-prueba-va-antes-que-el-arreglo)
- [Tu papel](#tu-papel)
- [Cuando el bug es en realidad otra cosa](#cuando-el-bug-es-en-realidad-otra-cosa)
- [Bugs que no se terminan en una sesión](#bugs-que-no-se-terminan-en-una-sesión)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Un bug es algo que la especificación dice que debe funcionar de una manera y funciona de otra. Corregirlo tiene su propio flujo, más corto que el de una funcionalidad, pero con el mismo principio: nada se arregla a ciegas y nada se integra sin revisión.

## Cómo reportarlo

Cuéntaselo al orquestador con tus palabras:

> Al editar un pedido, la dirección de envío se borra.

Cuanto más concreto, mejor diagnóstico:

- **Qué hiciste:** los pasos para que ocurra.
- **Qué esperabas** y **qué pasó**.
- **Si pasa siempre** o solo a veces.
- Lo que tengas: un mensaje de error, una captura, el registro de la aplicación.

## Los cinco pasos

| Paso | Qué pasa | Quién |
|---|---|---|
| 1. Diagnóstico | Se busca la causa raíz leyendo el código y los registros, y se explica **antes de tocar nada** | Orquestador |
| 2. Reproducción | Se escribe una prueba automática que falla por este bug | `qa-tester` |
| 3. Arreglo | El cambio mínimo que hace pasar la prueba sin romper las demás | `dev-backend` o `dev-frontend` |
| 4. Validación | QA, revisión y seguridad sobre el cambio | Los tres revisores |
| 5. Registro | Una entrada en el registro de cambios, en la sección "Corregido" | `documentador` |

## Por qué la prueba va antes que el arreglo

Escribir primero una prueba que falla tiene tres efectos:

- **Demuestra que el diagnóstico es correcto.** Si la prueba no falla, el bug no está donde se creía.
- **Demuestra que el arreglo funciona.** La misma prueba, que antes fallaba, ahora pasa.
- **Impide que el bug vuelva.** La prueba se queda en el proyecto y avisa si alguien lo reintroduce.

Sin ese paso, un agente puede "arreglar" un síntoma, declarar el problema resuelto y dejar la causa intacta.

## Tu papel

Tienes un momento clave: **revisar el diagnóstico antes de que se arregle nada**.

El orquestador te explica la causa que encontró. Pregúntate si tiene sentido con lo que observaste. Un diagnóstico vago ("puede ser un problema de estado") o que no explica todos los síntomas es señal de que no encontró la causa real.

Después, lo mismo que en cualquier cambio: revisar el Pull Request y aprobarlo. Ver [Aprobaciones](aprobaciones.md#el-pull-request).

> [!WARNING]
> Desconfía de un arreglo grande para un bug chico. El paso 3 pide el cambio **mínimo**. Si el arreglo reescribe medio módulo, o el diagnóstico estaba incompleto o el agente aprovechó para "mejorar" cosas que nadie pidió.

## Cuando el bug es en realidad otra cosa

A veces el código hace exactamente lo que dice la especificación, y lo que está mal es la especificación: faltaba un caso, o la regla no era la que el cliente necesitaba.

En ese caso el orquestador se detiene y **propone el cambio a la especificación** antes de tocar el código. No es un bug: es un cambio de comportamiento, y pasa por su aprobación como cualquier otro. Ver [Cambiar algo ya aprobado](funcionalidad.md#cambiar-algo-ya-aprobado).

| Situación | Flujo |
|---|---|
| El código no hace lo que dice la especificación | Bug |
| El código hace lo que dice la especificación, pero la especificación estaba mal | Cambio a la especificación, y luego funcionalidad |
| Se quiere que haga algo que nunca se pidió | Funcionalidad nueva |

## Bugs que no se terminan en una sesión

Si el arreglo queda a medias, el orquestador crea un `estado.md` para el bug en `specs/bugs/<fecha>-<nombre>/`, con el paso en que va y el próximo paso. Se retoma igual que una funcionalidad. Ver [Retomar el trabajo](retomar.md).

Si el bug es de una funcionalidad que todavía está en curso, se anota en el `estado.md` de esa funcionalidad.

## Siguientes pasos

- [Cambios pequeños](cambios-pequenos.md): cuando ni siquiera hace falta este flujo.
- [Construir una funcionalidad](funcionalidad.md): cuando el "bug" resulta ser un cambio de alcance.
- [Roles](roles.md): qué hace cada agente que participa.
