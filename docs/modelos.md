# Modelos por agente

- [Introducción](#introducción)
- [Cómo se decide el modelo de un agente](#cómo-se-decide-el-modelo-de-un-agente)
- [Criterios para asignar modelos](#criterios-para-asignar-modelos)
- [La distribución que trae el kit](#la-distribución-que-trae-el-kit)
- [OpenCode Go: cómo funciona el presupuesto](#opencode-go-cómo-funciona-el-presupuesto)
    - [Rendimiento por modelo](#rendimiento-por-modelo)
    - [Horario pico de DeepSeek](#horario-pico-de-deepseek)
    - [Privacidad](#privacidad)
- [El orquestador en OpenCode](#el-orquestador-en-opencode)
- [Temperatura](#temperatura)
- [Verificar que los modelos existan](#verificar-que-los-modelos-existan)
- [Medir y ajustar](#medir-y-ajustar)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Cada agente del equipo puede usar un modelo distinto. No es un lujo: los roles tienen necesidades muy diferentes. El arquitecto se usa poco y un error suyo es carísimo; los desarrolladores consumen la mayor parte de los tokens; el documentador solo redacta.

Todo se configura en `equipo/config.json`. Los roles no nombran modelos, solo un **nivel** (`alto`, `medio` o `bajo`), y así se puede cambiar de modelo sin tocar ningún rol.

> [!NOTE]
> Los nombres de modelos, sus precios y su rendimiento cambian con frecuencia. Los datos de esta página se verificaron en septiembre y octubre de 2026; tómalos como orientación y comprueba el estado actual antes de decidir.

## Cómo se decide el modelo de un agente

Para cada herramienta, en este orden de prioridad:

1. **`agentes`**: una excepción explícita para ese agente.
2. **`niveles`**: el modelo asignado al nivel del agente.
3. **Vacío**: el agente usa el mismo modelo que la sesión principal.

Además:

- **`orquestador`** es el modelo de la sesión principal, la que coordina. En Codex se elige al iniciar la sesión.
- **`ligero`** (solo OpenCode) es el modelo para tareas auxiliares, como generar títulos.

```json
"opencode": {
  "orquestador": "opencode-go/deepseek-v4.1-flash",
  "ligero":      "opencode-go/mimo-v2.6-flash",
  "niveles": { "alto": "opencode-go/mimo-v2.6-pro", "medio": "opencode-go/glm-5.3-flash", "bajo": "opencode-go/mimo-v2.6-flash" },
  "agentes": { "revisor-codigo": "opencode-go/mimo-v2.6-pro" }
}
```

Después de cualquier cambio:

```bash
make sincronizar   # regenera la configuración
make modelos       # muestra qué modelo usa cada agente y de dónde sale
```

## Criterios para asignar modelos

| Rol | Volumen de tokens | Qué necesita | Recomendación |
|---|---|---|---|
| `analista-producto`, `arquitecto` | Bajo | Razonamiento y criterio | El modelo más capaz. Se usan poco, así que el costo es bajo, y un error aquí es el más caro |
| `dev-backend`, `dev-frontend` | **Muy alto** | Código y uso de herramientas | Un modelo especializado en código y de bajo costo por token. Aquí se va la mayor parte del presupuesto |
| `qa-tester` | Alto | Código de pruebas | Modelo medio |
| `revisor-codigo`, `seguridad` | Medio | Detectar errores | Un modelo capaz **de una familia distinta a la de los desarrolladores**, para que no comparta sus puntos ciegos |
| `disenador-ux`, `devops` | Medio | Criterio práctico | Modelo medio |
| `documentador` | Bajo | Redacción | El más barato y rápido |
| Orquestador | Medio | Seguir el proceso y delegar | Un modelo confiable siguiendo instrucciones largas |

**Regla clave: quien revisa no debería usar el mismo modelo que quien escribió.** Así como quien escribe no aprueba, un modelo tiende a no ver sus propios errores.

## La distribución que trae el kit

Para OpenCode Go:

| Rol | Modelo | Motivo |
|---|---|---|
| Orquestador | `deepseek-v4.1-flash` | El mejor en uso real, y mucha capacidad para el rol de más volumen |
| `dev-backend`, `dev-frontend` | `deepseek-v4.1-flash` | La mejor calidad por costo para programar |
| `qa-tester`, `devops`, `disenador-ux` (nivel medio) | `glm-5.3-flash` | Barato y fiable para trabajo repetitivo |
| `revisor-codigo` | `mimo-v2.6-pro` | Alta calidad, y otra familia que los desarrolladores |
| `seguridad` | `glm-5.3` | Poco volumen; una tercera familia para una revisión independiente |
| `analista-producto`, `arquitecto` (nivel alto) | `mimo-v2.6-pro` | La mejor calidad con una capacidad razonable |
| `documentador` (nivel bajo) y tareas ligeras | `mimo-v2.6-flash` | El más barato |

Para Claude Code, los niveles van a `opus`, `sonnet` y `haiku`. Para Codex quedan vacíos: cada agente usa el modelo de la sesión, con un esfuerzo de razonamiento según su nivel.

**En un proyecto ya instalado**, esta distribución no se aplica sola al actualizar el kit, porque tu `equipo/config.json` se respeta. Para adoptar la que recomienda la versión actual:

```bash
make actualizar-modelos
```

Muestra los cambios y pide confirmación. Conserva las temperaturas, el agente principal y las exclusiones.

## OpenCode Go: cómo funciona el presupuesto

Verificado con la consola de OpenCode y su [documentación](https://opencode.ai/docs/es/go/) en septiembre de 2026:

- Hay **un solo presupuesto**, que la consola muestra en porcentaje, con tres ventanas: **Rolling** (5 horas, 20 % del mensual), **Weekly** (50 %) y **Monthly** (100 %).
- Cada modelo tiene un **precio por token** y un **límite mensual** propio ($15, $30 o $60). Ambos determinan cuánto del presupuesto consume: un modelo caro y con límite bajo lo agota muchísimo más rápido que uno barato con límite alto.
- **Repartir el trabajo entre muchos modelos no da más capacidad.** Lo que la estira es usar modelos con buen rendimiento por token donde hay más volumen: orquestador, desarrolladores y QA.
- **"Extra Usage":** si tienes crédito, al agotar el presupuesto se cobra de ese crédito en lugar de bloquearse.

### Rendimiento por modelo

Tokens aproximados que rinde cada modelo en una ventana de 5 horas, con una carga típica de agente de código (60 % lectura de caché, 32 % entrada, 8 % salida), y señales de calidad de programación de fuentes independientes:

| Modelo | Tokens en 5 h | Calidad de código | Uso recomendado |
|---|---|---|---|
| `deepseek-v4.1-flash` | ~122 M fuera de pico, ~61 M en pico | La mejor del plan en uso real (KiloBench 75 %), DeepSWE 74 | Orquestador y desarrolladores |
| `mimo-v2.6-pro` | ~14 M | DeepSWE 72, Terminal-Bench 90 | Analista, arquitecto y revisor |
| `glm-5.3-flash` | ~113 M | DeepSWE 63, Terminal-Bench 84 | QA, UX y DevOps |
| `mimo-v2.6-flash` | ~174 M | DeepSWE 68; en pruebas prácticas falla más en ejecución real | Documentador y tareas ligeras |
| `glm-5.3` | ~3 M | DeepSWE 67, Terminal-Bench 88 | Solo roles de muy poco volumen, como seguridad |
| `kimi-k3` | ~1.3 M | La más alta en pruebas reales (KiloBench 73 %) | Solo tareas cortas y críticas |
| `kimi-k2.7-code` | ~16 M | Resultados inconsistentes entre benchmarks | No recomendado por costo |
| `minimax-m3` | ~53 M | SWE-bench alto (dato del fabricante), bajo en uso real (KiloBench 48 %) | No recomendado |

Los benchmarks de modelos recientes son escasos y a veces contradictorios. Úsalos como orientación y valida con tu propio proyecto.

> [!WARNING]
> Fíjate en la columna de tokens antes de asignar un modelo caro a un rol con mucho volumen. Poner `kimi-k3` o `glm-5.3` en el orquestador o en un desarrollador agota la ventana de 5 horas en muy poco trabajo.

### Horario pico de DeepSeek

Los modelos DeepSeek cuestan el **doble en hora pico**: de 01:00 a 04:00 y de 06:00 a 10:00 UTC, de lunes a viernes. En Costa Rica (UTC−6) eso es de 7:00 a 10:00 p.m. y de 12:00 a 4:00 a.m. El horario laboral diurno es tarifa normal.

Conviene hacer el trabajo pesado (implementación y validación) de día, y dejar para la noche lo liviano: revisar especificaciones y planes, aprobar, escribir ideas y roadmaps. No hace falta cambiar de modelo por horario.

### Privacidad

Revisa la política de datos de cada modelo antes de usarlo con código de clientes. La mayoría no retiene datos, pero hay excepciones: algunos usan los datos para entrenamiento y otros guardan registros durante un tiempo.

**No asignes esos modelos a proyectos de clientes sin su autorización.** La lista actualizada está en [opencode.ai/docs/go](https://opencode.ai/docs/go/).

## El orquestador en OpenCode

En OpenCode, el kit crea un agente principal llamado `orquestador` y lo deja como **agente por defecto** al abrir la herramienta. Los agentes integrados `build` y `plan` siguen disponibles con la tecla `Tab`.

```json
"opencode": {
  "orquestador": "opencode-go/deepseek-v4.1-flash",
  "agente_principal": {
    "nombre": "orquestador",
    "ocultar": [],
    "temperatura": 0.2
  }
}
```

| Ajuste | Efecto |
|---|---|
| Sin la sección `agente_principal` | Se activa igual, con estos valores |
| `"ocultar": ["build", "plan"]` | Esconde los agentes integrados |
| `"nombre": ""` | Desactiva el orquestador y vuelve a los agentes integrados |

En Claude Code y en Codex no hay un agente con nombre: el orquestador es la sesión principal, que carga las mismas instrucciones.

## Temperatura

La temperatura controla cuánto azar usa el modelo. Baja (de 0 a 0.2) da respuestas consistentes y repetibles; media (de 0.3 a 0.6) da más variedad.

Hoy solo **OpenCode** permite fijarla por subagente. En Claude Code y Codex se omite.

Se decide en este orden de prioridad:

1. **`sin_temperatura`**: si el modelo del agente está en esta lista, no se envía temperatura y se usa la que exige el modelo.
2. **`temperatura.agentes`** en `config.json`: una excepción para ese agente.
3. **`temperatura:`** en el archivo del rol: el valor por defecto del agente.
4. **Nada:** la temperatura por defecto del modelo.

Los valores por defecto de cada rol:

| Agente | Temperatura | Motivo |
|---|---|---|
| `dev-backend`, `dev-frontend`, `devops` | 0.1 | Código consistente y repetible |
| `qa-tester`, `revisor-codigo`, `seguridad` | 0.1 | Un revisor no debe dar veredictos distintos cada vez |
| `arquitecto` | 0.2 | Algo de amplitud para evaluar alternativas |
| `documentador` | 0.3 | Redacción natural, sin inventar |
| `analista-producto`, `disenador-ux` | 0.4 | Pensar en más casos límite y más opciones |

Un ejemplo de excepciones:

```json
"opencode": {
  "temperatura": {
    "agentes": { "revisor-codigo": 0 },
    "sin_temperatura": ["opencode-go/kimi-k3"]
  }
}
```

> [!WARNING]
> Muchos modelos de razonamiento recomiendan o exigen una temperatura concreta, y otro valor puede empeorar los resultados. Revisa la ficha de cada modelo; si indica un valor fijo, agrégalo a `sin_temperatura`.

`make modelos` muestra la temperatura final de cada agente y de dónde sale.

## Verificar que los modelos existan

Los catálogos cambian con frecuencia. Para ver los identificadores exactos disponibles en tu cuenta:

```bash
opencode models opencode-go
```

`make modelos` marca con ⚠ cualquier modelo configurado que tu instalación de OpenCode no reconozca.

## Medir y ajustar

`make costos` registra los tokens y el costo de cada agente y modelo por funcionalidad. Es la base para comparar configuraciones con datos reales. Ver [Costos de IA](costos.md).

1. Anota el porcentaje de **Rolling** y de **Weekly** antes y después de construir una funcionalidad, y compáralo con `make costos`.
2. Para comparar dos configuraciones, construye la misma funcionalidad pequeña con cada una y compara: cuántos ciclos de corrección necesitó, qué encontró el revisor y cuánto consumió.
3. Anota el resultado en `docs/decisiones/`, ajusta `equipo/config.json` y ejecuta `make sincronizar && make modelos`.

Si el presupuesto se agota rápido, revisa primero el orquestador: abre una sesión nueva por funcionalidad y comprueba que esté delegando en los subagentes en lugar de hacer el trabajo él.

## Siguientes pasos

- [Costos de IA](costos.md): cuánto cuesta cada funcionalidad, por agente y modelo.
- [Configuración](configuracion.md): el resto de `equipo/config.json`.
- [Roles](roles.md): el nivel de cada rol.
