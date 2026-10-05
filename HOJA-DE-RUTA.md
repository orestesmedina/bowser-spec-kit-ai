# Hoja de ruta

Hacia dónde va el kit, por qué, y en qué punto estamos. Este archivo es la memoria del plan: cualquier persona o sesión de IA que retome el trabajo empieza por aquí.

**Estado actual:** versión 1.8.x publicada. **Próximo paso: etapa 0** (pruebas automáticas del kit).
**Última actualización:** 2026-10-04.

- [El norte](#el-norte)
- [Principios de diseño](#principios-de-diseño)
- [Dónde está el valor diferencial](#dónde-está-el-valor-diferencial)
- [Las etapas](#las-etapas)
- [Decisiones tomadas](#decisiones-tomadas)
- [Decisiones abiertas](#decisiones-abiertas)
- [Riesgos conocidos](#riesgos-conocidos)
- [Cómo retomar](#cómo-retomar)

## El norte

El kit nació atado a React + TypeScript, Go y PostgreSQL. Ese no es el objetivo. Los tres objetivos reales, definidos por Orestes el 2026-10-04:

1. **Cualquier persona, programe o no, puede construir aplicaciones con el kit.** Los agentes de IA son los equipos y departamentos de la empresa.
2. **Funciona con cualquier lenguaje o tecnología.** Cada agente es un especialista con experiencia en su área (backend, frontend, base de datos…) que no está atado a una tecnología: la tecnología la aportan las skills. El de backend usa la skill de Go, de PHP, de C# o de Laravel; el de frontend, la de React, Angular, Vue o JavaScript puro; el de base de datos, la de PostgreSQL, MySQL, SQL Server o MongoDB.
3. **Un freelancer con el kit es una empresa de desarrollo de software.** No solo escribir código: cotizar, reportar al cliente, entregar.

Y una condición sobre los tres: **que aporte un valor que otros frameworks no dan**, y que no se vuelva pesado ni caro de usar.

## Principios de diseño

Estos principios mandan sobre cualquier decisión de las etapas.

### 1. El kit no dicta la arquitectura del proyecto

Detectado en `simiente-santa-webside`: un agente no pudo agregar Redis a la integración continua porque `ci.yml` era un archivo del kit. Cada proyecto tiene su arquitectura; el kit no la impone.

| Es del kit | Es del proyecto |
|---|---|
| El proceso, los roles y los flujos | Qué tecnologías usa y en qué versiones |
| El estado, los costos y la instalación | Su integración continua |
| Los controles que no dependen de la tecnología (secretos, mensajes de commit, aprobaciones, archivos del kit) | Cómo se levanta, se prueba y se despliega |
| El catálogo de skills por tecnología | Sus reglas de arquitectura |
| Los agentes y comandos que **generan** lo de la columna derecha | Sus requisitos mínimos |

Cada proyecto tiene un **perfil** que registra sus tecnologías, sus carpetas y sus comandos. A partir de él, los agentes generan la integración continua, las reglas de arquitectura y los requisitos; esos archivos quedan en el proyecto y se editan ahí.

Para no perder la garantía de los controles: el kit conserva una parte pequeña e intocable (lo que no depende de la tecnología) y verifica que la integración continua del proyecto exista y cubra lo mínimo.

### 2. Roles sin tecnología, skills con tecnología

Los roles describen un oficio. Las skills describen una tecnología. Un proyecto recibe solo las skills de lo que usa.

### 3. Un contrato de verbos

El núcleo solo sabe pedir: formatear, revisar, probar, medir cobertura, auditar dependencias, generar. Cada proyecto declara cómo se hace cada verbo en su tecnología. El orquestador, los hooks y los controles no cambian cuando cambia el lenguaje.

### 4. Ligero por diseño

Medido el 2026-10-04: lo que el kit carga siempre en la sesión principal son unos 6 000 tokens; cada rol, unos 400; cada skill, unos 900 y solo cuando se usa. El kit es liviano. En `simiente-santa-webside`, la primera funcionalidad consumió 115 millones de tokens y el orquestador promedió unos 110 000 por respuesta: **el peso viene de las sesiones largas, no de las instrucciones**.

- Cargar solo lo necesario: skills bajo demanda, instrucciones permanentes cortas.
- Aislar el trabajo en subagentes, que devuelven un resumen.
- Una sesión por funcionalidad, y cortar a tiempo. El estado vive en archivos.
- Ceremonia proporcional al tamaño del cambio: no aplicar todo el proceso a todo.
- Modelos baratos donde hay volumen.
- **Medir:** un presupuesto de tokens por funcionalidad y una funcionalidad de referencia que se mide en cada versión, para detectar si el kit se volvió más pesado.

### 5. Controles que no dependen de que el agente obedezca

Lo que importa se hace cumplir en git y en la integración continua, no solo en las instrucciones.

### 6. Una fuente, varios formatos

Todo se escribe una vez y se genera para cada herramienta: roles, skills y, desde la etapa 1, comandos.

### 7. Idioma

Documentación y mensajes en español. **Nombres de comandos en inglés**, tanto los de la herramienta (`/bowser-update-kit`) como los de terminal (`make …`).

## Dónde está el valor diferencial

Revisado el 2026-10-04 (orientación, no estudio de mercado): Spec Kit cubre el proceso; BMAD, el equipo de roles, pero es pesado y caro en tokens; OpenSpec, las especificaciones vivas y los proyectos existentes, sin coordinar agentes; Agent OS, estándares que solo son consejos.

Lo que no se vio junto en ninguno:

- Controles que no dependen del agente. **Ya existe.**
- Contabilidad de costos por funcionalidad, agente y modelo. **Ya existe.**
- Un modelo distinto por rol, optimizando presupuesto. **Ya existe.**
- La capa de negocio: cotizar, reportar, entregar. **Etapa 6.**
- En español de principio a fin.
- Ligereza medida, no prometida. **Transversal.**

## Las etapas

Cada etapa es una versión que se puede publicar y usar sola.

| # | Etapa | Estado |
|---|---|---|
| 0 | Pruebas automáticas del kit | **Siguiente** |
| 1 | Comandos dentro de la herramienta | Pendiente |
| 2 | Núcleo sin tecnología y perfil del proyecto (versión 2.0) | Pendiente |
| 2b | Catálogo de skills y contribuciones | Pendiente |
| 3 | Memoria del producto, con diagramas | Pendiente |
| 4 | Descubrimiento de proyectos existentes | Pendiente |
| 5 | Para quien no programa | Pendiente |
| 6 | La empresa: cotizar, reportar, entregar | Pendiente |
| — | Ligereza: niveles de ceremonia y medición de tokens | Transversal |

### Etapa 0. Pruebas automáticas del kit

**Qué:** `make probar-kit` (nombre final en inglés, ver etapa 2) y un workflow de integración continua para el repositorio del kit.
**Por qué primero:** la etapa 2 es una cirugía mayor. Sin pruebas no se sabe si rompe los proyectos que ya usan el kit.
**De dónde parte:** los scripts de `pruebas/borradores/`, usados a mano para validar las versiones 1.6.2 a 1.8.0.
**Hecho cuando:** un comando instala el kit en un proyecto temporal, lo actualiza desde la versión anterior, comprueba hooks, costos (con OpenCode simulado en 1.x y 2.x), cobertura, código generado y enlaces de la documentación, y falla si algo no cuadra.

### Etapa 1. Comandos dentro de la herramienta

**Qué:** comandos como `/bowser-update-kit`, `/bowser-status`, `/bowser-doctor`, `/bowser-costs`, para no salir a la terminal.
**Cómo:** se escriben una vez y `sincronizar.py` genera el formato de cada herramienta. Verificado el 2026-10-04: en Claude Code y Codex los comandos propios se definen como skills; en OpenCode, como archivos en `.opencode/commands/`.
**Hecho cuando:** cada comando de `make` que usa una persona tiene su equivalente en las tres herramientas, documentado en `docs/comandos.md`.

### Etapa 2. Núcleo sin tecnología y perfil del proyecto (versión 2.0)

**Qué:**
- Roles como especialistas sin tecnología fija. Rol nuevo de base de datos.
- Perfil del proyecto: tecnologías, versiones, carpetas y cómo se ejecuta cada verbo.
- La integración continua, las reglas de arquitectura y los requisitos pasan a ser del proyecto, generados por los agentes a partir del perfil.
- La constitución se parte en principios universales (del kit) y reglas del proyecto.
- El kit conserva un workflow propio, pequeño, con los controles que no dependen de la tecnología.
- Los comandos de `make` pasan a inglés, con los nombres en español funcionando como alias un tiempo.

**Validación:** un proyecto existente de Orestes en **PHP puro, con HTML, CSS y JavaScript puros, y MySQL** (decidido el 2026-10-04; falta que indique cuál es y dónde está). No es para meter esa combinación en el kit, sino para comprobar que el núcleo funciona sin la tecnología original: otro lenguaje, otra base de datos y un proyecto que no tiene la forma "backend y frontend separados". De ahí salen además las primeras skills que no son de Go. Como es un proyecto existente, es también el caso de prueba de la etapa 4.
**Migración:** `simiente-santa-webside` debe poder pasar a la 2.0 con un comando, probado antes contra una copia.
**Hecho cuando:** el kit no menciona ninguna tecnología fuera del catálogo de skills, y los dos proyectos (`simiente-santa-webside` y el de PHP) funcionan con él: instalación, controles y un cambio real de punta a punta.

### Etapa 2b. Catálogo de skills y contribuciones

**Qué:**
- `/bowser-create-skill`: redacta la skill de una tecnología a partir de su documentación oficial y del código del proyecto. La persona la aprueba y queda **solo en su proyecto**.
- `/bowser-contribute-skill`: la propone al kit mediante un Pull Request, sin que la persona tenga que saber git.
- Revisión en tres capas antes de aceptar una contribución: comprobaciones automáticas (comandos peligrosos, direcciones externas, texto oculto), un agente revisor que trata la skill como datos y no como instrucciones, y la aprobación final de una persona de confianza.
- Etiqueta de madurez en cada skill: probada en un proyecto real, o solo redactada.

**Por qué:** "cualquier tecnología" no es viable escribiendo decenas de skills a mano. Con esto el catálogo crece con el uso.
**Hecho cuando:** alguien de fuera del equipo puede crear una skill, usarla y proponerla sin ayuda.

### Etapa 3. Memoria del producto, con diagramas

**El problema:** cada funcionalidad deja su especificación, pero ningún documento dice qué hace el sistema completo hoy. Con veinte funcionalidades, un agente tendría que leer veinte carpetas.
**Qué:** documentos vivos que el equipo actualiza al cerrar cada funcionalidad: catálogo de funcionalidades, modelo de datos actual, mapa de la API, reglas del dominio y decisiones tomadas. Un control avisa si quedaron desactualizados.
**Diagramas:** una skill de diagramas en Mermaid (texto que GitHub y Obsidian dibujan solos, versionable y barato en tokens), usada por el arquitecto y el documentador. No un agente nuevo. Diagramas de arquitectura general, modelo de datos, mapa de funcionalidades y flujo de las funcionalidades importantes. **El de base de datos se genera del esquema real**, para que no pueda contradecir a la realidad.
**Hecho cuando:** un agente que llega a un proyecto con muchas funcionalidades sabe qué existe leyendo una carpeta, no todas las especificaciones.

### Etapa 4. Descubrimiento de proyectos existentes

**Qué:** un flujo de ingeniería inversa para un proyecto que ya tiene código: detecta tecnologías, inventaría funcionalidades, lee el esquema de la base de datos (del script que entregue la persona), mapea la API y señala riesgos.
**Clave:** produce el **perfil del proyecto** (etapa 2) y la **memoria del producto** (etapa 3). Un proyecto nuevo las construye de a poco; uno existente las obtiene de golpe. Por eso va después de ambas.
**Caso de prueba:** el proyecto de PHP y MySQL de la etapa 2, que ya tiene código y base de datos.
**Hecho cuando:** en un proyecto existente, un comando deja el perfil y la memoria listos para que una persona los revise y apruebe.

### Etapa 5. Para quien no programa

**Qué:** un asistente de inicio que pregunta qué se quiere construir y arma el proyecto; resúmenes en lenguaje simple en cada aprobación; una segunda opinión técnica de un agente independiente antes de aprobar un plan.
**Límite conocido:** ver [Riesgos conocidos](#riesgos-conocidos).

### Etapa 6. La empresa

**Qué:** cotizaciones basadas en el costo real de funcionalidades anteriores, reportes de avance para el cliente y actas de entrega.

## Decisiones tomadas

| Fecha | Decisión | Quién |
|---|---|---|
| 2026-10-04 | Los tres objetivos de [El norte](#el-norte) | Orestes |
| 2026-10-04 | El kit no dicta la arquitectura: la integración continua, las tecnologías y los requisitos viven en el proyecto | Orestes |
| 2026-10-04 | Roles como especialistas y tecnologías como skills | Orestes |
| 2026-10-04 | Nombres de comandos en inglés, en la herramienta y en `make` | Orestes |
| 2026-10-04 | Skills creadas por el usuario, con opción de quedarse en el proyecto o proponerse al kit | Orestes |
| 2026-10-04 | No volverse pesado: la ligereza es un principio y se mide | Orestes |
| 2026-10-04 | Diagramas como skill en Mermaid, no como agente nuevo | Propuesto por Claude; confirmado por Orestes |
| 2026-10-04 | El proyecto de validación de la 2.0 es uno existente en PHP puro, HTML, CSS y JavaScript puros, y MySQL | Orestes |
| 2026-10-04 | Documentación como wiki por temas en `docs/`, única fuente | Orestes |
| 2026-10-04 | Licencia MIT, a nombre de Infinity Solutions AI | Orestes |
| 2026-10-04 | **El nombre se queda en "bowser" por ahora** (es el nombre de su perro). Los comandos usan el prefijo `/bowser-`. Si más adelante aparece un nombre mejor, se cambia | Orestes |

## Decisiones abiertas

| Decisión | Bloquea | Notas |
|---|---|---|
| Distribuir el kit también como extensión o preset de Spec Kit | Nada. Evaluar antes de la etapa 2 | Spec Kit tiene sistema de extensiones y presets; no se investigó a fondo |
| La documentación en inglés, además de en español | Nada | Ampliaría el alcance de las contribuciones |
| Cuál es el proyecto de PHP y MySQL de validación, y dónde está | La etapa 2 | Orestes lo indica cuando se llegue a esa etapa |

### Sobre el nombre

No es una decisión abierta: se queda "bowser". Esto queda como registro de lo ya revisado el 2026-10-04, para no repetir la búsqueda si se retoma:

| Nombre | Resultado |
|---|---|
| Bowser | Personaje de Nintendo; `bowser-js/bowser` (detector de navegadores, 5 800 estrellas); `disler/bowser` (automatización de navegador con agentes de IA, 265 estrellas) |
| infinity-spec-kit-ai | Libre como repositorio, pero "Infinity" es genérico y muy usado en IA, y "spec-kit" ata el nombre al producto de GitHub |
| Ghostware AI | Descartado: "ghostware" es un tipo de malware, y existe "GhostAI by Ghostware Labs", un agente de IA para programar |
| Cadejo | Libre donde se revisó (GitHub, npm). Perro fantasma de la leyenda centroamericana; tiene una versión protectora y otra maligna |
| Jauría | Libre donde se revisó. Difícil de pronunciar en inglés |
| Zaguate, Sabueso | Libres donde se revisó |
| Capataz, Nahual, Trasgo, Duende, Fragua | Ya usados por herramientas de desarrollo o de IA |

No se revisaron marcas registradas ni dominios. Existe además una empresa anterior llamada "Infinity Solutions AI", con el dominio `infinitysolutions.ai` hoy en venta: conviene una búsqueda formal antes de constituir la empresa.

Si el nombre cambia, es más barato antes de que haya muchos comandos y proyectos usándolo: el prefijo debe vivir en un solo lugar del generador.

## Riesgos conocidos

- **Una persona que no programa aprobando un plan técnico.** Hoy la seguridad del proceso descansa en que alguien con criterio aprueba el plan. Se puede mitigar con una segunda opinión independiente y con los riesgos explicados en simple; no se elimina.
- **Una tecnología sin proyecto real no está probada.** El catálogo debe decir cuáles lo están.
- **Una skill contribuida es un conjunto de instrucciones que los agentes obedecen.** Una maliciosa podría filtrar secretos o instalar algo dañino. Un agente revisor ayuda, pero puede ser engañado por el mismo texto que revisa: la aprobación final es siempre de una persona.
- **El alcance es de varios meses.** Por eso cada etapa sirve sola.
- **Generalizar a partir de un solo ejemplo.** El diseño de la etapa 2 se valida con un segundo proyecto real antes de darlo por bueno.

## Cómo retomar

En una sesión nueva, en la carpeta del kit:

1. Leer este archivo y `MANTENER-KIT.md` (Claude Code carga el segundo automáticamente).
2. Mirar la tabla de [Las etapas](#las-etapas): la marcada como **Siguiente** es por donde se sigue.
3. Revisar [Decisiones abiertas](#decisiones-abiertas): si alguna bloquea la etapa siguiente, se resuelve primero con Orestes.

Al terminar una etapa: actualizar su estado en la tabla, la línea de **Estado actual** del inicio y la fecha.
