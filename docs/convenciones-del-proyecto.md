# Convenciones del proyecto

- [Introducción](#introducción)
- [Estándar y convenciones: quién manda](#estándar-y-convenciones-quién-manda)
- [Redactarlas con el agente](#redactarlas-con-el-agente)
- [Cómo queda el archivo](#cómo-queda-el-archivo)
- [Dónde se aparta del estándar, y la deuda](#dónde-se-aparta-del-estándar-y-la-deuda)
- [En un proyecto nuevo](#en-un-proyecto-nuevo)
- [Cuando algo falla](#cuando-algo-falla)
- [Límites](#límites)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Los agentes reciben dos clases de instrucciones sobre cómo escribir código, y conviene no confundirlas:

| | Qué dice | De dónde sale | De quién es |
|---|---|---|---|
| **El estándar** | Cómo se programa bien en una tecnología: estilo, patrones recomendados, seguridad | De su documentación oficial | Del kit: las [skills del catálogo](skills.md#el-catálogo-de-skills-de-tecnología) |
| **Las convenciones del proyecto** | Cómo lo hace *este* proyecto: cómo nombra variables, tablas y columnas, cómo se organiza, qué patrones de diseño y qué bibliotecas usa | De leer su código | Del proyecto |

El kit no puede traer las segundas: no conoce tu proyecto. Lo que trae es el comando que las redacta, **`/bowser-conventions`**. Un agente lee el código, escribe lo que el proyecto repite, lo compara con el estándar y te lo propone. Quedan en una skill propia del proyecto por cada parte, y desde ahí las reciben los agentes que trabajan esa parte.

Sirven para dos cosas: que el código nuevo se parezca al que ya hay, y que quede escrito, desde el primer día, en qué se aparta el proyecto del estándar.

## Estándar y convenciones: quién manda

Cuando las dos dicen cosas distintas, el agente sigue este orden:

1. **En seguridad, siempre el estándar.** Ninguna costumbre del proyecto autoriza a saltarse una regla de seguridad.
2. **En nombres, estructura, patrones y bibliotecas, el proyecto.** Si las tablas del proyecto empiezan con un prefijo, la tabla nueva también, aunque el estándar recomiende otra cosa: dos estilos mezclados son peores que uno imperfecto.
3. **En lo que el proyecto no define, el estándar.**

Y una regla más, para cualquier caso: un agente no reescribe lo que su tarea no toca. Lo que encuentra fuera del estándar lo anota como deuda.

## Redactarlas con el agente

Primero el proyecto necesita su [perfil](perfil-del-proyecto.md), porque las convenciones se redactan por parte. Después, en el chat de la herramienta:

```text
/bowser-conventions
```

(En Codex, `$bowser-conventions`.) Para una sola parte: `/bowser-conventions api`. El agente hace esto:

1. Lee el perfil para saber qué partes hay, dónde están y qué carpetas son de terceros (esas no se leen).
2. Para cada parte, el `arquitecto` recorre el código propio y anota lo que el proyecto **repite**: algo que aparece una sola vez no es una convención. Cada regla lleva un ejemplo real y el archivo de donde salió.
3. Donde el código hace lo mismo de dos formas, te pregunta cuál vale para lo nuevo. No lo decide él.
4. Compara con la skill del catálogo de esa tecnología y lista las diferencias.
5. Te muestra la propuesta en lenguaje simple y espera tu aprobación.
6. Con tu "sí", escribe `.agents/skills/convenciones-de-<parte>/SKILL.md`, agrega esa skill a la parte en el perfil y ejecuta `make instalar-kit` para que los roles la reciban.

El commit lo confirmas tú con `APROBADO_PERFIL=1`, porque cambió el perfil. Ver [Aprobar un cambio en el perfil](perfil-del-proyecto.md).

`make profile` recuerda qué partes todavía no las tienen:

```text
Sin convenciones propias: api, panel. Las skills del catálogo dicen el estándar de cada tecnología; lo propio del proyecto se redacta con /bowser-conventions.
```

Repite el comando cuando el proyecto cambie su forma de hacer algo: las convenciones se actualizan, no se rehacen.

## Cómo queda el archivo

Una skill normal, que es del proyecto: el kit no la reemplaza ni la toca en las actualizaciones.

```markdown
---
name: convenciones-de-api
description: Convenciones propias de la parte api de este proyecto (nombres, estructura, patrones, bibliotecas). Usar siempre que se cree o modifique código en api/.
---
# Convenciones de api

## Nombres
## Estructura
## Patrones
## Bibliotecas y herramientas
## Dónde se aparta del estándar
## Deuda
```

Y en el perfil, junto a la del catálogo:

```json
{ "nombre": "api", "carpeta": "api", "roles": ["dev-backend"], "skills": ["php", "convenciones-de-api"] }
```

Solo dice lo propio. Lo que el proyecto hace igual que el estándar no se repite ahí, para que el archivo sea corto: se carga en cada tarea.

Puedes editarlo a mano cuando quieras. Es texto, y es tuyo.

## Dónde se aparta del estándar, y la deuda

Cada archivo trae una tabla con las diferencias:

| El estándar dice | Aquí se hace | En código nuevo |
|---|---|---|
| Tablas en minúsculas | Tablas con prefijo y mayúsculas | Se sigue el proyecto |
| Pruebas junto al código | Pruebas en una carpeta aparte | Se sigue el proyecto |

La columna "En código nuevo" la decides tú al aprobar: lo normal es seguir al proyecto, pero puedes pedir que lo nuevo adopte el estándar en un punto.

**Las diferencias de seguridad no entran en esa tabla.** Si el proyecto guarda contraseñas de una forma insegura o arma consultas uniendo texto, eso no es una convención que respetar: va a la sección "Deuda", con dónde ocurre y qué pide el estándar. El código nuevo cumple el estándar; cuándo y cómo se corrige lo viejo lo decides tú, como cualquier otro trabajo.

> [!WARNING]
> Lee la sección "Deuda" antes de aprobar. Es el primer inventario de problemas de seguridad del proyecto, y es probable que nadie lo haya hecho antes.

## En un proyecto nuevo

No hay código que leer, así que no hay convenciones que encontrar. Nacen de lo que decide el plan de la primera funcionalidad (qué bibliotecas, qué estructura). Ejecuta `/bowser-conventions` cuando esa funcionalidad esté terminada: antes, lo que se escribiera sería un deseo.

Mientras tanto, los agentes trabajan con el estándar de las skills del catálogo y con el plan.

## Cuando algo falla

| Lo que ves | Qué significa | Qué hacer |
|---|---|---|
| El agente dice que no hay perfil | Las convenciones se redactan por parte, y las partes las dice el perfil | `/bowser-profile` primero |
| `la skill «convenciones-de-x» no está en .agents/skills/` | El perfil la nombra y el archivo no existe (se borró, o el nombre de la parte cambió) | Vuelve a ejecutar `/bowser-conventions x`, o quítala del perfil |
| `Las skills instaladas no son las que pide el perfil` o `La configuración de agentes está desactualizada` | Se cambió el perfil y no se instaló | `make instalar-kit` |
| Las convenciones describen código de una biblioteca copiada | Esa carpeta no está declarada como de terceros | Agrégala a `terceros` en el perfil y repite |
| Un agente sigue el estándar donde el proyecto hace otra cosa | Esa costumbre no quedó escrita | Agrégala al archivo, con un ejemplo |

## Límites

- **Las redacta un agente leyendo una muestra del código, no todo.** Puede tomar por convención algo que no lo es, o no ver una. Por eso cada regla lleva su ejemplo y la aprobación es tuya.
- No hay un control que verifique que el código nuevo las cumple: las aplican los agentes que desarrollan y las revisa `revisor-codigo`. Lo que deba cumplirse sin excepción va en la [constitución](la-constitucion.md).
- No se actualizan solas. Si el proyecto cambia de costumbre y nadie repite el comando, quedan viejas.
- **Pesan en cada tarea**, porque el rol las carga siempre que trabaja la parte. Por eso el agente tiene un límite de unos 7 000 caracteres por archivo (lo que mide una skill del catálogo). Compruébalo con `wc -c .agents/skills/convenciones-de-*/SKILL.md`; si un archivo pasa, pide que lo recorte.
- Si una parte la trabajan `dev-dba` y otro rol, los dos reciben el archivo entero. Lo de la base de datos va en su propia sección, "Base de datos", para que `dev-dba` la encuentre sin leer el resto.
- Probado el 2026-10-10 en OpenCode real, sobre copias de dos proyectos existentes (uno en Go, React y PostgreSQL; otro en PHP y MySQL). En Claude Code y Codex solo se comprobó que el comando se genera.

## Siguientes pasos

- [Perfil del proyecto](perfil-del-proyecto.md): las partes, sus roles y sus skills.
- [Skills](skills.md): el catálogo y de dónde sale el estándar de cada tecnología.
- [Integrar el kit en un proyecto existente](proyecto-existente.md).
