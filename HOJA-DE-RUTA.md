# Hoja de ruta

Hacia dónde va el kit, por qué, y en qué punto estamos. Este archivo es la memoria del plan: cualquier persona o sesión de IA que retome el trabajo empieza por aquí.

**Estado actual:** versión 1.16.0 en la rama `etapa-2` (en `main`, la 1.12.1). Etapa 0 hecha. Etapa 1: los seis comandos están hechos y probados en OpenCode; la prueba a mano en Claude Code y Codex queda aplazada. **Etapa 2 en curso** (núcleo sin tecnología): diseño aprobado; hecha la entrega A (perfil del proyecto y verbos), que no rompe los proyectos actuales, y validada sobre copias de los dos proyectos. La entrega B va en la rama `etapa-2`: hechos los pasos B1, B2 (catálogo de skills), B3 (roles sin tecnología y rol `dev-dba`) y B4 (las skills del catálogo pasan a ser el estándar oficial de cada tecnología, tres skills nuevas y `/bowser-conventions` para lo propio de cada proyecto), sigue el B5 (pasos en la [etapa 2](#etapa-2-núcleo-sin-tecnología-y-perfil-del-proyecto-versión-20)).
**Última actualización:** 2026-10-09.

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
| 0 | Pruebas automáticas del kit | Hecha (1.10.1) |
| 1 | Comandos dentro de la herramienta | Primera entrega hecha (1.11.0). Prueba a mano en Claude Code y Codex: aplazada |
| 2 | Núcleo sin tecnología y perfil del proyecto (versión 2.0) | **En curso** (entrega A: 1.12.0) |
| 2b | Catálogo de skills y contribuciones | Pendiente |
| 3 | Memoria del producto, con diagramas | Pendiente |
| 4 | Descubrimiento de proyectos existentes | Pendiente |
| 5 | Para quien no programa | Pendiente |
| 6 | La empresa: cotizar, reportar, entregar | Pendiente |
| — | Ligereza: niveles de ceremonia y medición de tokens | Transversal |

### Etapa 0. Pruebas automáticas del kit

**Qué:** `make test-kit` y un workflow de integración continua para el repositorio del kit.
**Por qué primero:** la etapa 2 es una cirugía mayor. Sin pruebas no se sabe si rompe los proyectos que ya usan el kit.
**De dónde partió:** los scripts usados a mano para validar las versiones 1.6.2 a 1.8.0 (estaban en `pruebas/borradores/`; ya son pruebas automáticas).
**Hecho cuando:** un comando instala el kit en un proyecto temporal, lo actualiza desde la versión anterior, comprueba hooks, costos (con OpenCode simulado en 1.x y 2.x), cobertura, código generado y enlaces de la documentación, y falla si algo no cuadra.

| Entrega | Contenido | Estado |
|---|---|---|
| A | El ejecutor, las pruebas del núcleo (instalación, actualización, controles, costos, enlaces) y `make test-kit` | Hecha (1.9.0) |
| B | El workflow del repositorio del kit (`kit.yml`) y el grupo de pruebas de Go (`pruebas/go/`: código generado y cobertura) | Hecha (1.10.0). El workflow quedó en verde en GitHub con la 1.10.1, al subir los tags |

Las pruebas de código generado y cobertura son de Go y sqlc, que en la etapa 2 dejan de ser del núcleo. Se prueban igual, porque hoy esos scripts llegan a los proyectos, pero en un grupo aparte que en la etapa 2 se va con la skill de Go (decidido con Orestes el 2026-10-04). `make test-kit` y `pruebas/` son solo del repositorio del kit: no llegan a los proyectos.

### Etapa 1. Comandos dentro de la herramienta

**Qué:** comandos como `/bowser-update-kit`, `/bowser-status`, `/bowser-doctor`, `/bowser-costs`, para no salir a la terminal.
**Cómo:** se escriben una vez y `sincronizar.py` genera el formato de cada herramienta. Verificado el 2026-10-04: en Claude Code y Codex los comandos propios se definen como skills; en OpenCode, como archivos en `.opencode/commands/`.
**Hecho cuando:** cada comando de `make` que usa una persona tiene su equivalente en las tres herramientas, documentado en `docs/comandos.md`.

| Entrega | Contenido | Estado |
|---|---|---|
| A | `equipo/comandos/`, el generador para las tres herramientas y seis comandos: `/bowser-status`, `/bowser-costs`, `/bowser-doctor`, `/bowser-update-kit`, `/bowser-news`, `/bowser-models` | Hecha (1.11.0) |
| B | Probarlos a mano en Claude Code, Codex y OpenCode reales y corregir lo que aparezca | OpenCode: probado por Orestes el 2026-10-04. Claude Code y Codex: aplazado (decisión del 2026-10-05) |

Quedan fuera a propósito `up`, `test`, `lint`, `ci` y `generar`: dependen de la tecnología y en la etapa 2 pasan a ser del proyecto. Sus comandos se definen ahí, sobre el contrato de verbos.

Detalles que salieron al implementar (2026-10-04):

- Las fuentes viven en `equipo/comandos/` (decisión de Orestes: más ordenado que mezclarlas con las skills). El prefijo `bowser-` está en un solo lugar: `PREFIJO_COMANDOS` de `scripts/sincronizar.py`.
- Codex solo lee skills de `.agents/skills/`, así que sus comandos se generan ahí, en carpetas `bowser-*`. Es la única carpeta de fuentes con contenido generado; el instalador no las copia a los proyectos.
- Peso: en Claude Code y Codex el comando se carga solo al escribirlo (cero contexto permanente). En OpenCode cada comando suma una línea de descripción, porque OpenCode también lista como skills lo que hay en `.claude/skills/` y `.agents/skills/`.

### Etapa 2. Núcleo sin tecnología y perfil del proyecto (versión 2.0)

**Qué:**
- Roles como especialistas sin tecnología fija. Rol nuevo de base de datos.
- Perfil del proyecto: tecnologías, versiones, carpetas y cómo se ejecuta cada verbo.
- La integración continua, las reglas de arquitectura y los requisitos pasan a ser del proyecto, generados por los agentes a partir del perfil.
- La constitución se parte en principios universales (del kit) y reglas del proyecto.
- El kit conserva un workflow propio, pequeño, con los controles que no dependen de la tecnología.
- Los comandos de `make` pasan a inglés, con los nombres en español funcionando como alias un tiempo.

| Entrega | Contenido | Estado |
|---|---|---|
| A | Perfil del proyecto (`equipo/perfil.json`), los seis verbos, `make profile`, `/bowser-profile` con detección automática, y los controles del commit según el perfil. Sin perfil, todo se comporta como antes | Hecha (1.12.0) |
| B | Roles sin tecnología, rol nuevo de base de datos, skills asignadas por el perfil y catálogo de skills: cada proyecto recibe solo las suyas | Pendiente |
| C | La integración continua pasa a ser del proyecto, generada desde el perfil; el kit conserva un workflow pequeño con los controles que no dependen de la tecnología. Constitución en dos partes (falta la aprobación de Orestes). `make doctor` y el hook de Claude Code según el perfil | Pendiente |
| D | Comandos de `make` en inglés con los nombres viejos como alias, comando de migración a la 2.0, documentación, y validación en los dos proyectos (versión 2.0.0) | Pendiente |

La entrega A se publica sola en `main`. B, C y D rompen proyectos existentes: se trabajan en una rama hasta que los dos proyectos de validación funcionen (acordado con Orestes el 2026-10-05).

Detalles que salieron al implementar la entrega A (2026-10-05):

- El perfil lo redacta un agente y lo corrige una persona (pedido de Orestes). No hay un agente nuevo: es un comando, una skill y el `arquitecto`, porque la tarea es ocasional y un agente más pesaría en todas las sesiones. Un script hace la detección sin IA (gratis y repetible) y el agente completa lo que hace falta criterio.
- El formato es JSON porque los scripts solo usan la biblioteca estándar de Python.
- Los verbos son seis: `formato`, `revisar`, `probar`, `cobertura`, `auditar` y `generar`. Uno sin definir avisa y no falla.
- Un cambio en el perfil lo confirma una persona en el commit (`APROBADO_PERFIL=1`), como la constitución: sus comandos se ejecutan en cada máquina y en la integración continua.

Validación de la entrega A sobre copias de los dos proyectos (2026-10-08, en `~/validacion-kit/` de WSL; los originales no se tocaron):

- **`simiente-santa-webside`** (pasó de la 1.6.4 a la 1.12.0 en la copia): con un perfil de dos partes, `make lint`, `make verificar-generados`, `make test` (176 pruebas del frontend y las de integración) y `make cobertura` (87 %) dan lo mismo que sin perfil. `make security` falla igual en los dos casos, por el Go 1.27.1 de la máquina (corregido en 1.27.2): no es del kit.
- **p2p Controller**: perfil de tres partes (`api`, `base-de-datos`, `panel`). El único verbo que el proyecto puede tener hoy es `revisar`: sintaxis de PHP 7.4 dentro de Docker, 103 archivos propios sin errores. Los otros cinco quedan sin definir y `make ci` termina bien. Los controles del commit funcionan.
- No se probó: `/bowser-profile` dentro de una herramienta real (los dos perfiles los redactó Claude Code a mano siguiendo la skill), ni un cambio real de punta a punta.

Lo que la validación deja para las entregas siguientes:

| Hallazgo | Dónde se atiende |
|---|---|
| No hay skills de PHP, MySQL ni JavaScript puro: en p2p las tres partes quedan con `skills: []` | B (primeras skills fuera de Go) |
| La base de datos no tiene quién la trabaje: 67 procedimientos almacenados y ningún rol | B (rol de base de datos) |
| El panel es PHP que genera HTML, más CSS y JavaScript: ni "backend" ni "frontend" lo describen solos | B (decisión abierta: roles por parte) |
| Las semillas traen tecnología: a un proyecto de PHP y MySQL le llegan un `docker-compose.yml` con PostgreSQL, un `.gitignore` de Go y Node y un `ci.yml` de Go y React | B y C |
| La lista de terceros se escribe dos veces: en `terceros` y otra vez en el comando del verbo, para excluirlos | B (pasar al comando las variables `PERFIL_TERCEROS` y `PERFIL_RAIZ`) |
| Un proyecto sin herramientas necesita un script propio para un verbo, y `scripts/` es del kit: en la copia se usó `herramientas/` | B (definir la carpeta y documentarla) |
| `make ci` en verde con cinco de seis verbos sin definir se lee como "todo bien" | B (resumen final: qué se comprobó y qué no) |
| `make doctor` exige golangci-lint, sqlc y migrate en un proyecto de PHP | C (ya previsto) |
| Tecnologías nombradas fuera de las skills, el 2026-10-08: `dev-backend` 14 menciones, constitución 13, `dev-frontend` 11, `AGENTS.md` 9, orquestador 7, `arquitecto` 5, otros roles 10 | Medida de partida del "Hecho cuando" |

Pasos de la entrega B, en orden (rama `etapa-2`, que sale de `main` con la 1.12.1 ya en el historial). Cada paso termina con `make test-kit` en verde:

| Paso | Contenido | Estado |
|---|---|---|
| B1 | Perfil: `roles` (lista) por parte, aceptando el `rol` de la entrega A; las skills de cada rol dentro de la parte; variables `PERFIL_RAIZ` y `PERFIL_TERCEROS` para los comandos de los verbos; carpeta del proyecto para sus propios scripts; resumen al final de `make ci` con lo comprobado y lo que quedó sin comprobar | Hecho (1.13.0, 2026-10-08) |
| B2 | Catálogo: las skills de tecnología salen de `.agents/skills/` a una carpeta de catálogo del kit, con etiqueta de madurez; `make instalar-kit` copia solo las que el perfil nombra (sin perfil, las tres de siempre) y avisa si el perfil pide una que no existe | Hecho (1.14.0, 2026-10-09) |
| B3 | Roles sin tecnología: `dev-backend`, `dev-frontend`, `arquitecto`, `qa-tester`, `devops` y el resto dejan de nombrar Go, React y PostgreSQL y leen el perfil (carpetas, skills y verbos); rol nuevo de base de datos; `sincronizar.py` ya no saca las skills del rol sino del perfil; orquestador y `AGENTS.md` al día | Hecho (1.15.0, 2026-10-09) |
| B4 | Skills `php`, `mysql` y `web-sin-framework`, redactadas con la documentación oficial. Las tres originales, reescritas con el mismo criterio. Comando `/bowser-conventions`, que redacta las convenciones propias de cada proyecto leyendo su código | Hecho (1.16.0, 2026-10-09) |
| B5 | Semillas sin tecnología: `docker-compose.yml`, `.env.example` y el bloque de `.gitignore` dejan de traer PostgreSQL, Go y Node a quien no los usa | Pendiente |
| B6 | Repetir la validación de las dos copias con la rama y un cambio pequeño de verdad en cada una | Pendiente |

Detalles que salieron al implementar el paso B1 (2026-10-08):

- Un rol recibe las `skills` de la parte más las suyas. Así el perfil de la entrega A (`rol` y `skills`) significa lo mismo que antes y no hay que migrarlo.
- `PERFIL_TERCEROS` va con una carpeta por línea, no separadas por espacios, porque una carpeta puede tener espacios.
- La carpeta para los scripts propios del proyecto se llama `tools/` (decisión de Orestes, 2026-10-09; en la copia de p2p Controller se había usado `herramientas/`, que hay que renombrar en el paso B6). El kit no la crea, no la copia y no la valida: solo está documentada. La detección la lista como carpeta con código, y la skill avisa que no es una parte.
- Con perfil, `make ci` es una sola ejecución de los seis verbos y ya no se detiene en el primer fallo; sin perfil sigue encadenando los comandos de siempre.
- Las versiones de la rama (1.13.0 en adelante) no se publican con tag: existen porque una prueba exige que `VERSION` tenga su entrada en el `CHANGELOG`. Al publicar la 2.0.0 se decide si se conservan como historial o se funden en una sola entrada.
- Para B3: `roles_de(parte)` de `scripts/perfil.py` ya devuelve cada rol con sus skills; es lo que `sincronizar.py` debe leer.

Detalles que salieron al implementar el paso B2 (2026-10-09):

- El catálogo está en `catalogo/skills/`. La madurez va dentro del `SKILL.md` de cada skill (`metadata: madurez`, `probada` o `redactada`), no en un índice aparte: así una skill es una carpeta completa, que es lo que hará falta para las contribuciones de la etapa 2b.
- En el proyecto, una skill del catálogo queda en `.agents/skills/` como cualquier archivo del kit: no se edita ahí, se puede excluir y se retira sola cuando el perfil deja de nombrarla.
- Cambiar las skills del perfil (o crear o quitar el perfil) obliga a ejecutar `make instalar-kit` antes del commit. Se eligió lo estricto: si no, el perfil diría una cosa y los agentes tendrían otra. `/bowser-profile` lo hace solo.
- Comando nuevo `make skills`, que no estaba en el diseño: sin él, la madurez solo se vería abriendo cada archivo.
- Puente hasta el B3: como los roles todavía llevan sus skills escritas, `sincronizar.py` les quita las que el proyecto no tiene. El texto del rol las sigue nombrando; eso se va en el B3.
- Para B4: una skill nueva es una carpeta en `catalogo/skills/` con `madurez: redactada`; `make test-kit` comprueba el formato.
- Para B6: en la copia de `simiente-santa-webside`, comprobar que el perfil nombra `go-backend`, `postgres-db` y `react-frontend`; si no, la actualización se las retira.

Detalles que salieron al implementar el paso B3 (2026-10-09):

- El rol de base de datos se llama `dev-dba` (decisión de Orestes). Y una regla suya que manda sobre los perfiles: **el backend no hace backend y base de datos; la base de datos es de `dev-dba`**. La skill `perfil-proyecto` ya lo recomienda así.
- Los roles no leen el perfil al trabajar: `sincronizar.py` les escribe una sección "Este proyecto" al generarlos. Se eligió así porque no gasta tokens en cada tarea y no depende de que el agente obedezca. El costo: cambiar el perfil obliga a regenerar (`make instalar-kit` o `make sincronizar`), y el commit se rechaza si no se hizo.
- Cada rol declara qué ve con el campo `proyecto`: `partes` (los tres `dev-*`), `mapa` (los demás) o nada (`analista-producto`).
- Las tareas se marcan con el nombre de la parte (`[api]`), y con el rol si la parte tiene varios (`[api:dev-dba]`).
- Sin perfil, el generador usa un perfil supuesto (`SIN_PERFIL` en `scripts/perfil.py`): `backend/` con `dev-backend`, que ahí sigue llevando la base de datos, y `frontend/` con `dev-frontend`. Es el único lugar fuera del catálogo y de la rama vieja del `Makefile` donde quedan nombres de tecnología ligados a los roles; se retira en la 2.0.
- Medida del "Hecho cuando": los roles pasaron de 40 menciones de tecnología a 0, y una prueba lo vigila. Quedan: constitución (13, entrega C), `AGENTS.md` (1, la nota de "sin perfil"), orquestador (`make up`, `make generar`, el texto de la CI: B5 y C).
- `dev-dba` usa el modelo del nivel medio (en OpenCode, `glm-5.3-flash`), sin modelo propio en `equipo/config.json`: confirmado por Orestes el 2026-10-09.
- Para B4: las skills `php`, `mysql` y `web-sin-framework` deben decir dónde van las pruebas y los archivos de cambio, porque los roles ya no lo dicen.
- Para B6: en la copia de `simiente-santa-webside`, darle a `backend` los roles `dev-backend` (`go-backend`) y `dev-dba` (`postgres-db`); en la de p2p Controller, `dev-dba` en la parte `base-de-datos`. Y probar ahí lo que las pruebas automáticas no ven: que un agente real trabaje bien con el rol nuevo y que el orquestador delegue por parte.

Detalles que salieron al implementar el paso B4 (2026-10-09):

- **El paso creció por dos correcciones de Orestes, que son ahora reglas del kit.** La primera versión de las skills nuevas giraba alrededor de "en un proyecto existente manda lo que ya hay", que era p2p Controller con otro nombre. Primera corrección: una skill del catálogo es el estándar oficial, no un proyecto. Segunda: eso vale para todas, también las tres originales, y lo propio de cada proyecto debe generarse en el proyecto. De ahí salió la separación en dos piezas:

  | | Qué dice | De dónde sale | De quién es |
  |---|---|---|---|
  | Skill del catálogo | El estándar de la tecnología | Su documentación oficial | Del kit |
  | `convenciones-de-<parte>` | Cómo lo hace este proyecto | Su código, leído por un agente | Del proyecto |

- **Fuentes de cada skill** (las nombra al inicio, con la fecha): `go-backend`, Effective Go, Go Code Review Comments y las guías de go.dev (organización de módulos, base de datos, seguridad); `react-frontend`, react.dev; `postgres-db`, el manual y la lista "Don't Do This" de la wiki; `php`, el manual de PHP y PHP-FIG (PSR-1, PSR-4, PER Coding Style 3.1); `mysql`, el manual de referencia 8.4; `web-sin-framework`, el estándar HTML, MDN, WCAG 2.2 y OWASP.
- Las tres originales perdieron lo que era elección de `simiente-santa-webside` y no estándar: `sqlc`, `pgx`, `golang-migrate`, Tailwind, TanStack Query, React Hook Form, Zod, shadcn/ui, Vitest, Playwright, las carpetas `backend/` y `frontend/` y el 80 % de cobertura. **Los nombres `go-backend`, `react-frontend` y `postgres-db` se quedaron** porque los usan `SIN_PERFIL` y los proyectos; `go-backend` ya no habla solo de "backend" y convendría renombrarlas en la 2.0 (`go`, `react`, `postgres`), con la migración.
- Las seis quedaron `redactada`: el texto de las tres originales es nuevo. Efecto visible: `make instalar-kit` avisa de las tres en cualquier proyecto que actualice.
- Donde la fuente oficial no fija nada, la skill lo dice: ni MySQL ni PostgreSQL traen herramienta de migraciones, así que el formato de los archivos de cambio (`migrations/`, `.up.sql` y `.down.sql`) es convención del kit, y cede ante la del proyecto. Composer, PHPUnit, PHPStan y Testing Library no son "oficiales", y las skills los nombran como lo habitual.
- **`/bowser-conventions`** sigue el patrón de `/bowser-profile`: un comando, una skill con el método (`convenciones-proyecto`) y el `arquitecto`; sin agente nuevo. No hay script de detección: reconocer un patrón de diseño necesita criterio, no conteo. El resultado es una skill del proyecto, así que llega a los roles por el mecanismo que ya existe (el perfil la nombra) y no hubo que tocar el generador ni el instalador.
- El prefijo `convenciones-de-` está en un solo lugar del código (`CONVENCIONES` en `scripts/perfil.py`), que es lo que usa `make profile` para recordar qué partes no las tienen.
- La deuda de seguridad no se escribe como convención: va en una sección aparte de cada archivo. Es, de paso, el primer inventario de seguridad de un proyecto existente.
- En un proyecto nuevo no hay código que leer: las convenciones se redactan después de la primera funcionalidad. **Queda abierto** dónde viven hasta entonces las elecciones de bibliotecas del plan (hoy, en `plan.md` y en la constitución); se cruza con partir la constitución, en la entrega C.
- Se cruza también con la etapa 4 (descubrimiento de proyectos existentes): `/bowser-conventions` es su primera pieza. La etapa 4 agrega el inventario de funcionalidades, el esquema y el mapa de la API.
- Hechos verificados el 2026-10-09: php.net/supported-versions; PER Coding Style 3.1 "extiende y reemplaza" PSR-12, que sigue figurando como aceptado; endoflife.date/mysql y las notas de versión de MySQL 9.7; cuatro páginas del manual de MySQL 8.4 (buenas prácticas de InnoDB, mayúsculas en identificadores, seguridad de objetos almacenados, variables locales); go.dev/doc/modules/layout y Go Code Review Comments; react.dev/reference/rules; postgresql.org/support/versioning y la wiki "Don't Do This". No se abrieron hoy, y se escribieron de conocimiento previo: Effective Go, las páginas de react.dev sobre estado y efectos, las guías de seguridad de Go, MDN, WCAG y OWASP.
- Una prueba inventaba una skill llamada `php` para probar el catálogo: ahora se llama `pascal`.
- **Para B6:** ejecutar `/bowser-conventions` de verdad en las dos copias. En `simiente-santa-webside` debe recuperar como convenciones lo que las skills perdieron (`sqlc`, Tailwind, TanStack Query…). En p2p Controller debe encontrar: PHP 7.4 sin Composer, cargador de clases propio, capa de datos que arma el `CALL` reemplazando `{parametro}` por el valor escapado, lógica en procedimientos almacenados con prefijos `cp`, `p` y `v`, tablas con mayúsculas (`caSender`), un solo script con el esquema, jQuery y una plantilla comprada. Si no encuentra eso, la skill `convenciones-proyecto` necesita ajuste. El cambio pequeño de verdad en p2p debería tocar un procedimiento almacenado y su llamada desde PHP.
- **Deuda de seguridad ya vista en p2p Controller** (debe aparecer en la sección "Deuda" de sus convenciones): el panel imprime datos sin escapar, el proxy apaga la verificación del certificado, la configuración trae credenciales cifradas dentro del código, `.htaccess` enciende `display_errors`, y PHP 7.4 no recibe correcciones desde noviembre de 2022.
- No se hizo: ninguna skill para PHP con framework, ni para MariaDB.

**Validación:** un proyecto existente de Orestes en **PHP puro, con HTML, CSS y JavaScript puros, y MySQL** (decidido el 2026-10-04): **p2p Controller**, en `D:\IA\environment\wsl\code\p2p Controller` (en WSL, `/mnt/d/IA/environment/wsl/code/p2p Controller`), con el script de MySQL en `api.p2pcontroller/@database/p2pcontroller.sql`. No es para meter esa combinación en el kit, sino para comprobar que el núcleo funciona sin la tecnología original: otro lenguaje, otra base de datos y un proyecto que no tiene la forma "backend y frontend separados". De ahí salen además las primeras skills que no son de Go. Como es un proyecto existente, es también el caso de prueba de la etapa 4.
**Lo que se encontró en p2p Controller (2026-10-05, solo lectura):** dos carpetas hermanas (`api.p2pcontroller`, la API, y `p2pcontroller.com/http`, el panel web), unas 13 000 líneas de PHP propio, 25 tablas y 67 procedimientos almacenados. No es un repositorio de git, y no tiene pruebas, Composer, formateador ni Docker. Trae bibliotecas de terceros copiadas dentro (`libraries/`, `bower_components/`). Consecuencias para el diseño: un verbo puede no estar definido en un proyecto, el perfil debe declarar las carpetas de terceros, y reglas como "80 % de cobertura" son del proyecto, no del núcleo. Se trabaja siempre sobre una copia.
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
| 2026-10-04 | Los comandos de la herramienta se escriben en `equipo/comandos/`, no como skills en `.agents/skills/` | Orestes |
| 2026-10-05 | El proyecto de validación de la 2.0 es p2p Controller | Orestes |
| 2026-10-05 | El kit **no** se distribuye como extensión ni preset de Spec Kit | Orestes |
| 2026-10-05 | La prueba a mano de los comandos en Claude Code y Codex se aplaza; se empieza la etapa 2 | Orestes |
| 2026-10-05 | Diseño de la etapa 2 en cuatro entregas (A a D); la A en `main` y el resto en una rama | Propuesto por Claude; aprobado por Orestes |
| 2026-10-05 | El perfil del proyecto lo redacta un agente de primera instancia; la persona lo corrige y lo aprueba | Orestes |
| 2026-10-08 | Entrega B: una parte del perfil puede declarar varios roles, y cada rol recibe las skills de esa parte que le corresponden | Propuesto por Claude; aprobado por Orestes |
| 2026-10-08 | Entrega B: las únicas skills nuevas son las de p2p Controller (`php`, `mysql`, `web-sin-framework`), marcadas "solo redactadas" hasta que haya un cambio real hecho con ellas | Propuesto por Claude; aprobado por Orestes |
| 2026-10-08 | Entrega B: el catálogo de skills vive en el kit y la instalación copia solo las que el perfil nombra; sin perfil, las tres de siempre | Propuesto por Claude; aprobado por Orestes |
| 2026-10-09 | El rol de base de datos se llama `dev-dba`, y la base de datos es suya, no de `dev-backend`. `simiente-santa-webside` lo incorpora cuando tenga perfil | Orestes |
| 2026-10-09 | Lo que cada rol sabe del proyecto se escribe en el rol al generarlo, desde el perfil; las tareas se marcan con el nombre de la parte | Propuesto por Claude; Orestes no lo objetó al decidir el nombre del rol |
| 2026-10-09 | **El kit siempre es general: una skill del catálogo recoge el estándar oficial de su tecnología** (cómo se programa, qué patrones seguir), nunca la forma de un proyecto ni una elección de bibliotecas. Vale para todas las skills, las actuales y las futuras | Orestes |
| 2026-10-09 | **Lo propio de cada proyecto se genera en el proyecto:** al instalar el kit en uno existente, un agente redacta sus convenciones (nombres de variables, tablas y columnas, patrones de diseño) leyendo el código. Comando aparte, `/bowser-conventions`, después del perfil | Orestes |
| 2026-10-09 | Cuando el estándar y la convención del proyecto se contradicen: manda el proyecto, salvo en seguridad, donde manda siempre el estándar | Propuesto por Claude; aprobado por Orestes |
| 2026-10-09 | `dev-dba` se queda con el modelo del nivel medio (en OpenCode, `glm-5.3-flash`), sin modelo propio | Propuesto por Claude; confirmado por Orestes |
| 2026-10-04 | **El nombre se queda en "bowser" por ahora** (es el nombre de su perro). Los comandos usan el prefijo `/bowser-`. Si más adelante aparece un nombre mejor, se cambia | Orestes |

## Decisiones abiertas

| Decisión | Bloquea | Notas |
|---|---|---|
| La documentación en inglés, además de en español | Nada | Ampliaría el alcance de las contribuciones |
| Partir la constitución en principios universales (del kit) y reglas del proyecto, generando el archivo que lee Spec Kit | La entrega C de la etapa 2 | Cambia la constitución: necesita la aprobación explícita de Orestes sobre un texto concreto |
| Cómo levantar p2p Controller para la validación | La validación de la etapa 2 (entrega D) | Orestes, 2026-10-05: corre en XAMPP con PHP 7.4 y no lo tiene instalado en local. Acordado ese día: Docker con PHP 7.4 y MySQL, sobre una copia temporal con su propio repositorio de git local (sin GitHub). La carpeta original no se toca |

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
2. Mirar la tabla de [Las etapas](#las-etapas): la marcada como **Siguiente** o **En curso** es por donde se sigue.
3. Revisar [Decisiones abiertas](#decisiones-abiertas): si alguna bloquea la etapa siguiente, se resuelve primero con Orestes.

Al terminar una etapa: actualizar su estado en la tabla, la línea de **Estado actual** del inicio y la fecha.
