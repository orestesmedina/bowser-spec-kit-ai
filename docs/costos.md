# Costos de IA

- [Introducción](#introducción)
- [Qué se registra](#qué-se-registra)
- [Costo equivalente y gasto real](#costo-equivalente-y-gasto-real)
- [Ver el costo](#ver-el-costo)
- [Cómo se registra](#cómo-se-registra)
- [Los precios](#los-precios)
- [Cerrar el costo de una funcionalidad](#cerrar-el-costo-de-una-funcionalidad)
- [Avisos y qué hacer](#avisos-y-qué-hacer)
- [Límites](#límites)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Cada funcionalidad lleva la cuenta de cuánto costó en IA: cuántos tokens gastó cada agente, con qué modelo, y cuánto equivale en dólares. La cuenta vive en `specs/<rama>/costos.json`, dentro de git.

Sirve para tres cosas: saber cuánto cuesta construir, comparar configuraciones de modelos con datos reales y cotizar trabajo futuro.

## Qué se registra

Por cada sesión de trabajo, y dentro de ella por cada combinación de agente y modelo:

- El número de respuestas, y cuántas ocurrieron en hora pico.
- Los tokens de entrada, de salida, de razonamiento, y los de lectura y escritura de caché.
- El costo equivalente, calculado con el precio vigente en el momento de cada respuesta.
- El costo que reportó la propia herramienta.

Como el archivo va en git, **suma el trabajo de todas las personas** que tocaron la funcionalidad, cada una desde su máquina.

## Costo equivalente y gasto real

El dólar que muestra el kit es un **costo equivalente a precio de API**: lo que costaría ese consumo si se pagara por token.

Con una suscripción como OpenCode Go no pagas por token: pagas una cuota, y cada modelo consume un porcentaje de tu presupuesto. Tu gasto real es ese porcentaje, que se ve en la consola de la herramienta.

El costo equivalente sigue siendo útil, porque permite comparar: una funcionalidad con otra, un modelo con otro, un agente con otro.

El informe muestra dos cifras, y es normal que no coincidan:

| Cifra | Qué es |
|---|---|
| **Equivalente** | Calculada por el kit con los precios públicos de cada modelo |
| **Según OpenCode** | La que reportó la herramienta en cada respuesta, con sus propias tarifas |

## Ver el costo

```bash
make costos              # la funcionalidad de la rama actual
make costos TODO=1       # todo el proyecto: por funcionalidad, agente y modelo
make costos PRECIOS=hoy  # cuánto costaría hoy, a precios actuales. No guarda nada
```

El informe de una funcionalidad:

```
COSTO DE LA TAREA · 001-estructura-base · abierto
  specs/001-estructura-base/costos.json · 35 registro(s) de sesión · 1 versión(es) de precios
  Agente             Modelo                    Tokens  Entrada   Salida    Caché  Equivalente
  dev-backend        deepseek-v4.1-flash       23.2 M    …
  arquitecto         mimo-v2.6-pro             15.2 M    …
  Total                                       115.7 M                                  $…
  Según OpenCode (precio del momento de cada respuesta): $6.70
```

`make costos PRECIOS=hoy` sirve para cotizar: responde "¿cuánto costaría construir algo parecido hoy?".

`make estado` también muestra el costo acumulado de la funcionalidad actual.

## Cómo se registra

**Se registra solo.** El orquestador ejecuta `make costos` al iniciar y al cerrar cada sesión. El comando lee las sesiones de la herramienta en tu computadora, incluidas las de los subagentes, y agrega lo nuevo a `costos.json`.

Tres reglas sobre a qué funcionalidad se asigna cada cosa:

- El consumo se asigna a **la rama en la que estés** al registrarlo.
- Solo cuenta lo ocurrido **desde que se creó la rama**, con un margen de 30 minutos hacia atrás. El trabajo previo en la rama principal no se carga a la funcionalidad.
- Una misma respuesta nunca se cuenta dos veces, aunque ejecutes el comando muchas veces.

> [!NOTE]
> Si trabajaste en una sesión sin pasar por el orquestador, ejecuta `make costos` en la rama de la funcionalidad **antes de cambiarte de rama**.

El archivo nunca se edita a mano. En Claude Code, el agente ni siquiera puede: un [hook del agente](hooks-del-agente.md) lo bloquea.

## Los precios

Los precios salen de [models.dev](https://models.dev), el mismo catálogo que usa OpenCode. Se consultan como máximo una vez por hora; sin conexión, se usa la última copia guardada.

**El precio de cada día queda guardado.** Cada funcionalidad lleva su propio historial de precios. Si un precio cambia, se agrega una versión nueva con su fecha, sin recalcular lo anterior: cada respuesta se valoriza con el precio vigente cuando ocurrió.

El cálculo es el mismo que usa OpenCode: la entrada sin caché, la salida (el razonamiento se cobra como salida) y la lectura y escritura de caché. La tarifa de hora pico se aplica según la hora de cada respuesta.

Para un modelo que no esté en el catálogo, o para una tarifa negociada, el precio se fija a mano en `equipo/config.json`, en dólares por millón de tokens:

```json
"costos": {
  "precios_manuales": {
    "opencode-go/mi-modelo": { "input": 0.2, "output": 0.8, "cache_read": 0.02, "cache_write": 0 }
  }
}
```

La tarifa de hora pico viene configurada para DeepSeek. Si cambia, se reemplaza en el mismo bloque:

```json
"costos": {
  "pico": [{ "modelos": "opencode-go/deepseek-*", "multiplicador": 2, "dias": [0,1,2,3,4], "horas_utc": [[1,4],[6,10]] }]
}
```

En `dias`, 0 es lunes. `"pico": []` la desactiva.

## Cerrar el costo de una funcionalidad

Cuando apruebas el Pull Request, el orquestador ejecuta:

```bash
make costos CERRAR=1
```

Registra lo pendiente, marca el costo como `cerrado` y lo guarda en un commit **antes** de integrar. Desde ahí, el costo de esa funcionalidad no cambia: el [hook de git](hooks-de-git.md) bloquea cualquier modificación.

Se cierra para que la cifra sea confiable. Un costo que puede seguir creciendo después de entregar no sirve para comparar ni para cotizar.

Cerrar el costo es una decisión que sigue a tu aprobación: ningún agente lo cierra antes.

## Avisos y qué hacer

| Aviso | Qué significa | Qué hacer |
|---|---|---|
| "No se encontró 'opencode' en esta terminal" | La terminal no es la de Ubuntu, o la herramienta no está instalada ahí | Usa la terminal de Ubuntu. Ver [Windows y WSL](windows-wsl.md) |
| "OpenCode no devolvió ninguna sesión de este proyecto" | Trabajaste con otra herramienta, o en otra carpeta | Compruébalo con `opencode session list` desde la carpeta del proyecto |
| "…todas anteriores al inicio de la tarea" | Las sesiones que hay son de antes de crear la rama | Es lo esperado si aún no se trabajó en la rama |
| "Sin precio para: …" | El modelo no está en models.dev | Agrega su precio en `costos.precios_manuales` |
| "NO se registró el consumo: no hay precio para ningún modelo usado" | No se pudo consultar los precios y no hay copia local | Vuelve a ejecutar `make costos` cuando haya conexión. No se pierde nada |
| "El costo de esta tarea está cerrado" | La funcionalidad ya se entregó | El consumo nuevo va en la funcionalidad actual |
| "El costo de … ya está cerrado" al hacer commit | Se modificó un `costos.json` cerrado | Revierte el cambio |

## Límites

- **Hoy solo registra sesiones de OpenCode.** Con Claude Code o Codex, `make costos` no encuentra consumo.
- **El registro es por máquina.** Cada persona registra el consumo de las sesiones de su computadora.
- **Es un costo equivalente, no una factura.** Ver [Costo equivalente y gasto real](#costo-equivalente-y-gasto-real).

## Siguientes pasos

- [Modelos por agente](modelos.md): cómo elegir modelos para bajar el costo sin perder calidad.
- [Retomar el trabajo](retomar.md): el otro archivo que mantiene el orquestador.
- [Comandos](comandos.md).
