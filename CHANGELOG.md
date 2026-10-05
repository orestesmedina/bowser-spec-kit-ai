# Cambios del kit

Todos los cambios importantes de este kit se registran aquí.
Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

- **MAYOR** (2.0.0): un proyecto tiene que hacer algo a mano para seguir funcionando.
- **MENOR** (1.5.0): funciones nuevas compatibles.
- **PARCHE** (1.5.1): correcciones y documentación.

Cada versión puede incluir una sección **Al actualizar** con los pasos manuales. `make actualizar-kit` muestra las entradas nuevas al terminar; `make novedades` las muestra en cualquier momento.

> Las versiones 1.0.0 a 1.5.0 se reconstruyeron el 2026-10-03 a partir del historial de trabajo; las fechas anteriores a esa son aproximadas.

## [Sin publicar]

## [1.12.0] - 2026-10-05

Primera entrega de la etapa 2 de la hoja de ruta (el kit deja de suponer la tecnología del proyecto). No cambia nada en un proyecto que no cree su perfil.

### Agregado
- **Perfil del proyecto** (`equipo/perfil.json`, opcional): el proyecto declara sus partes, la carpeta de cada una, el rol y las skills que la trabajan, sus carpetas de terceros y los archivos que no se modifican una vez versionados. Es del proyecto: el kit no lo instala ni lo reemplaza. Página nueva: `docs/perfil-del-proyecto.md`.
- **Verbos**: `formato`, `revisar`, `probar`, `cobertura`, `auditar` y `generar`. Cada parte declara en el perfil qué comando ejecuta cada uno. Con perfil, `make test`, `make lint`, `make cobertura`, `make security`, `make generar` y `make verificar-generados` ejecutan esos comandos (`PARTE=nombre` para una sola parte). Un verbo sin definir se omite con un aviso: sirve para proyectos que todavía no tienen pruebas o formateador.
- **`/bowser-profile`** y `make profile`: el comando del chat mira el proyecto (`make profile DETECTAR=1`, solo lectura), el `arquitecto` redacta el perfil con la skill nueva `perfil-proyecto`, pregunta lo que no se puede deducir y lo propone para aprobación. `make profile` lo muestra y lo valida.
- **Controles del commit con perfil**: un cambio en el perfil se confirma con `APROBADO_PERFIL=1` (sus comandos se ejecutan en cada máquina y en la integración continua); los archivos `inmutables` de cada parte no se modifican, renombran ni borran; y el verbo `formato` corre solo en las partes que el commit toca, sin contar el código de terceros.
- `scripts/perfil.py` y `scripts/verbos.py`. Pruebas: `pruebas/nucleo/prueba_perfil.py`.

### Corregido
- **Un commit que solo eliminaba archivos se saltaba todos los controles.** Borrar una migración ya versionada, sin ningún otro cambio en el commit, pasaba sin aviso. Ahora pasa por las mismas comprobaciones que cualquier commit.

### Límites de esta entrega
- La integración continua (`ci.yml`), los roles, `make doctor` y el hook de Claude Code todavía no leen el perfil: siguen hablando de Go, React y PostgreSQL. Un proyecto con otra forma necesita por ahora su propio workflow. Llega en las entregas siguientes de la etapa 2.

### Al actualizar
- Nada obligatorio. Tu proyecto sigue funcionando igual sin perfil.
- Si quieres probarlo: `/bowser-profile` en el chat, revisa la propuesta y confirma el commit con `APROBADO_PERFIL=1 git commit ...`. Desde ese momento `make test`, `make lint` y los controles del commit usan lo que el perfil declara, así que comprueba con `make ci` que todo sigue pasando.

## [1.11.0] - 2026-10-04

### Agregado
- **Comandos dentro de la herramienta** (etapa 1 de la hoja de ruta): `/bowser-status`, `/bowser-costs`, `/bowser-doctor`, `/bowser-update-kit`, `/bowser-news` y `/bowser-models`. Se escriben en el chat de Claude Code u OpenCode (en Codex, `$bowser-status`); el agente ejecuta el `make` correspondiente y explica el resultado en lenguaje simple. No cierran costos, no fuerzan instalaciones, no cambian modelos y no hacen commits por su cuenta.
- **`equipo/comandos/`**: cada comando se escribe una vez y `make sincronizar` genera `.claude/skills/bowser-*/`, `.agents/skills/bowser-*/` (Codex) y `.opencode/commands/bowser-*.md`. Un proyecto puede agregar los suyos con un archivo nuevo en esa carpeta. En Claude Code y Codex solo se cargan al escribirlos: no ocupan contexto.
- Pruebas: `pruebas/nucleo/prueba_comandos.py`.

### Cambiado
- `.agents/skills/` contiene ahora carpetas generadas (las que empiezan con `bowser-`), porque Codex solo lee skills de ahí. El instalador no las copia: cada proyecto genera las suyas según sus herramientas activas.
- `HOJA-DE-RUTA.md` y `MANTENER-KIT.md`: la etapa 0 queda cerrada (el workflow `kit.yml` se confirmó en verde en GitHub) y la etapa 1 tiene su primera entrega.

### Al actualizar
- Después de `make actualizar-kit`, el commit incluye carpetas nuevas: `equipo/comandos/`, `.opencode/commands/` y las `bowser-*` de `.claude/skills/` y `.agents/skills/`. Abre una sesión nueva de tu herramienta para que vea los comandos.
- Si tu proyecto tiene una skill propia en una carpeta `.agents/skills/bowser-…`, cámbiale el nombre **antes** de actualizar: `make sincronizar` borra las carpetas con ese prefijo.

## [1.10.1] - 2026-10-04

### Corregido
- **Publicar una versión subía el commit pero no el tag.** La documentación indicaba `git push --follow-tags`, que solo sube tags anotados, y `git tag vX.Y.Z` crea uno simple: GitHub no tenía ningún tag del kit. Por eso el workflow `kit.yml` falló en su primera ejecución (la prueba de actualización quedó omitida y el modo estricto no lo permite). `docs/contribuir.md` y `MANTENER-KIT.md` indican ahora `git push origin main --tags` y cómo comprobarlo.

Nada de esto llega a los proyectos.

## [1.10.0] - 2026-10-04

### Agregado
- **Las pruebas del kit corren solas en GitHub** (segunda entrega de la etapa 0 de la hoja de ruta). El workflow `.github/workflows/kit.yml` ejecuta `make test-kit ESTRICTO=1` en cada Pull Request y en cada push a `main`, con Go, Node y `sqlc` instalados. Es solo del repositorio del kit.
- **Pruebas de código generado y cobertura** (`pruebas/go/`): `make generar` y `make verificar-generados` con `sqlc` real y un generador de tipos mínimo (qué se omite, y que una consulta o un contrato cambiado sin regenerar hace fallar la verificación), y `make cobertura` con un perfil escrito a mano y con Go real. Las que necesitan `go`, `sqlc`, `node` o `npm` se omiten, avisando, si falta el programa. Van en un grupo aparte del núcleo porque en la 2.0 se irán con la skill de Go.

### Cambiado
- `scripts/instalar_kit.py`: `.github/workflows/kit.yml` entra en la lista de lo que nunca se copia a los proyectos, con su prueba.
- Se retiró `pruebas/borradores/`: el último script manual ya es parte de las pruebas automáticas.
- `pruebas/README.md`, `docs/contribuir.md`, `MANTENER-KIT.md` y `HOJA-DE-RUTA.md`: la etapa 0 queda hecha y sigue la etapa 1.

Nada de esto llega a los proyectos: al actualizar no cambia ningún archivo.

## [1.9.0] - 2026-10-04

### Agregado
- **Pruebas automáticas del kit** (`make test-kit`, primera entrega de la etapa 0 de la hoja de ruta). Un comando instala el kit en proyectos temporales, lo actualiza desde la versión anterior publicada con el `Makefile` viejo, y comprueba la instalación sobre un proyecto existente, los archivos editados en el proyecto, `kit.excluir`, los hooks de git (mensajes de commit, secretos, constitución, migraciones, costo cerrado, falta de `python3`), el hook de Claude Code, `make costos` con un OpenCode simulado en formato 1.x y 2.x, los archivos generados, la versión y los enlaces internos de la documentación. Termina con error si algo falla. Detalle en `pruebas/README.md`.
- `kit.mk`: comandos para mantener el kit. Solo existe en el repositorio del kit; el `Makefile` lo incluye si lo encuentra.

### Cambiado
- Los borradores de `pruebas/borradores/` que ya son pruebas automáticas se retiraron. `enlaces.py` pasó a `pruebas/enlaces.py`. Queda como borrador el de código generado y cobertura, para la segunda entrega.
- `docs/contribuir.md`: la sección "Probar un cambio" usa `make test-kit`; la regla de idioma dice que los nombres de comandos nuevos van en inglés.
- `MANTENER-KIT.md` y `HOJA-DE-RUTA.md`: estado de la etapa 0.

Nada de esto llega a los proyectos: `pruebas/` y `kit.mk` no se copian. En el `Makefile` de los proyectos solo cambia una línea, que busca `kit.mk` y no lo encuentra.

## [1.8.2] - 2026-10-04

### Agregado
- `HOJA-DE-RUTA.md`: el plan del kit. El norte (cualquier tecnología, para quien programa y quien no, y un freelancer con el kit como empresa de desarrollo), los principios de diseño (el kit no dicta la arquitectura del proyecto; roles como especialistas y tecnologías como skills; ligero y medido), las etapas con su estado y las decisiones tomadas y abiertas. No se copia a los proyectos.
- `pruebas/borradores/`: los scripts usados a mano para validar las versiones 1.6.2 a 1.8.0, como punto de partida de las pruebas automáticas (etapa 0 de la hoja de ruta). No se copian a los proyectos.

### Cambiado
- `MANTENER-KIT.md`: empieza por la hoja de ruta; los nombres de comandos pasan a ser en inglés para todo comando nuevo (los actuales se renombran en la 2.0).

## [1.8.1] - 2026-10-04

### Cambiado
- `.obsidian/` (configuración personal del editor Obsidian) sale del repositorio del kit y se agrega al `.gitignore`. Como el bloque del kit en `.gitignore` se copia a los proyectos, ahí también queda ignorada.

## [1.8.0] - 2026-10-04

La documentación pasa a ser una wiki por temas, en `docs/`, y es la única fuente: no se copia a los proyectos.

### Agregado
- **Documentación por temas** (`docs/README.md` es el índice): 36 páginas en siete secciones (prólogo, primeros pasos, conceptos, el flujo de trabajo, profundizando, controles y referencia). Cada página explica qué es una pieza del kit, para qué sirve, cuándo se usa y qué hacer cuando falla.
- Páginas nuevas, que no existían en ninguna forma: integrar el kit en un proyecto existente, capas de control, hooks de git, hooks del agente, integración continua, comandos, guía de actualización, cómo contribuir, personalizar un proyecto, roles y skills.
- `make doctor` revisa que `sqlc` esté instalado (recomendado).

### Cambiado
- **`docs/GUIA-INICIO.md` y `equipo/MODELOS.md` se retiran:** su contenido está repartido en las páginas de `docs/`. En los proyectos, la documentación se lee en `.bowser-spec-kit-ai/docs/`, siempre en la versión instalada.
- El orquestador toma las checklists de aprobación de `.bowser-spec-kit-ai/docs/aprobaciones.md`.
- Los mensajes de `make doctor` y del pre-commit apuntan a las páginas nuevas.
- `README.md` del kit: queda como portada corta, con la instalación y el índice de la documentación.
- `make doctor` exige Go 1.26 y Node 24, los mismos mínimos que la documentación y el CI desde la 1.6.2 (antes aceptaba Go 1.23 y Node 22).

### Corregido
- pre-commit: un proyecto que excluye la constitución del kit (`kit.excluir`) podía modificarla sin `APROBADO_CONSTITUCION=1`. Ahora la aprobación se omite solo cuando la constitución es la del kit y coincide con él.

### Al actualizar
- `docs/GUIA-INICIO.md` y `equipo/MODELOS.md` desaparecen del proyecto. Si alguien los tenía en favoritos, la documentación está ahora en `.bowser-spec-kit-ai/docs/README.md`.
- Si `make doctor` marca Go o Node como antiguos, actualízalos (Go 1.26+, `nvm install 24`).
- Si tu `equipo/config.json` menciona `equipo/MODELOS.md` en sus comentarios, puedes corregirlo a mano: es solo un comentario.

## [1.7.1] - 2026-10-04

### Agregado
- `LICENSE`: el kit se publica bajo licencia MIT (Infinity Solutions AI), la misma de Spec Kit. Cualquiera puede usarlo, modificarlo y distribuirlo conservando el aviso de autoría. No se copia a los proyectos: la licencia del kit no cambia la del código de cada proyecto.

## [1.7.0] - 2026-10-04

Dos reglas que el kit ya exigía, pero que nadie verificaba automáticamente, ahora las revisa el CI.

### Agregado
- **Cobertura de la capa de servicio:** `make cobertura` mide la cobertura de los archivos `service*.go` de `backend/internal/` (todos los dominios sumados) y falla por debajo del 80 % que fija la constitución. El CI lo ejecuta después de las pruebas. Script: `scripts/cobertura.py`.
- **Código generado al día:** `make generar` regenera las consultas de sqlc y los tipos de la API (script `api:gen` del frontend); `make verificar-generados` además falla si quedó algo sin commit. El CI lo comprueba en los jobs de backend y frontend. Cada parte se omite si el proyecto todavía no la tiene (sin `sqlc.yaml`, sin consultas o sin `api:gen`). Script: `scripts/generar.sh`.
- CI: `sqlc` con versión fija (`v1.31.1`), configurable con la variable `SQLC_VERSION`.

### Cambiado
- `make ci` incluye `verificar-generados` y `cobertura`.
- Roles `dev-backend` y `dev-frontend` y skills `go-backend` y `react-frontend`: indican cuándo ejecutar `make generar` y el mínimo de cobertura.

### Al actualizar
- Antes de subir, ejecuta `make verificar-generados` y `make cobertura` en tu proyecto: si alguno falla en local, también fallará el CI.
- Para que el CI verifique los tipos de la API, el frontend debe tener el script `api:gen` en `package.json` y dejar su salida en `frontend/src/api/`.
- Instala sqlc en local: `go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.31.1`.
- Si tu `proyecto.mk` ya tenía comandos propios para esto (por ejemplo `sqlc-gen`, `sqlc-verify`, `api-gen`), puedes borrarlos y usar los del kit; si los dejas, no chocan.

## [1.6.4] - 2026-10-03

### Corregido
- **`make costos` no conseguía precios** ("no se pudo consultar https://models.dev/api.json (HTTPError)" y "Sin precio para: …" en todos los modelos): models.dev rechaza con 403 las peticiones con la identificación por defecto de Python. Ahora el script se identifica con un `User-Agent` propio.
- Si no hay precio para ningún modelo usado (models.dev caído y sin copia local), `make costos` ya **no registra** el consumo sin costo: avisa y lo deja pendiente para la próxima ejecución.

### Al actualizar
- Si ejecutaste `make costos` con la 1.6.3 y quedó "Sin precio para: …" en todos los modelos, ese `costos.json` se guardó sin costos. Si todavía no lo subiste, bórralo junto con el registro local y vuelve a generarlo: `rm specs/<rama>/costos.json ~/.local/share/bowser-kit/costos-registro.json && make costos`.

## [1.6.3] - 2026-10-03

### Corregido
- **`make costos` no registraba nada con OpenCode 2.x** (mostraba "Aún no hay consumo registrado" sin ningún aviso). Tres causas, verificadas con OpenCode 2.0.22 y las sesiones reales de `simiente-santa-webside`:
  - `opencode session list` consulta un servicio en segundo plano que puede devolver la lista vacía; ahora, si viene vacía, se vuelve a pedir con `--standalone`.
  - `opencode export <id>` pasó a ser `opencode session export <id>`, con otro formato de mensajes y de subagentes; el script entiende los dos formatos (1.x y 2.x).
  - OpenCode 2.x corta los JSON grandes cuando escribe a una tubería; la salida ahora se lee desde un archivo temporal.
- `make costos` avisa cuando OpenCode no devuelve sesiones del proyecto, o cuando todas son anteriores al inicio de la tarea, en lugar de quedarse callado.

### Al actualizar
- Ejecuta `make costos` en la rama de tu funcionalidad: va a registrar todo el consumo acumulado desde que se creó la rama. Haz commit de `specs/<rama>/costos.json`.

## [1.6.2] - 2026-10-03

Correcciones al CI detectadas en el primer proyecto real (`simiente-santa-webside`, Go 1.27).

### Corregido
- **Hooks inactivos sin aviso:** los hooks de git (`.githooks/`) y los de Claude Code (`equipo/adaptadores/claude/hooks/`) estaban guardados en el kit sin permiso de ejecución, y git los ignoraba en silencio: los commits pasaban sin ningún control. Ahora están marcados como ejecutables, `make instalar-kit` repara el permiso en cada instalación y `make doctor` avisa si falta.
- **CI roto con Go 1.25 o superior:** `golangci-lint-action@v6` instalaba golangci-lint v1 (compilado con Go 1.24), que se niega a analizar módulos con un Go más nuevo. Ahora usa `golangci-lint-action@v9` con golangci-lint `v2.14.0`, la misma línea v2 que la guía instala en local.
- CI: `migrate` y `govulncheck` ya no se instalan con `@latest`; quedan fijados en `v4.20.1` y `v1.8.0`.
- CI: actions actualizadas a los majors con Node 24 (`checkout@v7`, `setup-go@v7`, `setup-node@v7`, `setup-python@v7`, `gitleaks-action@v3`); las anteriores corrían sobre Node 20, ya obsoleto.
- CI y `docker-compose.yml`: PostgreSQL pasa de `16.4-alpine` (agosto de 2024) a `16-alpine`, que recibe los parches de seguridad de la rama 16.
- `make help` ahora muestra los comandos con dígitos en el nombre (ej. `e2e` en `proyecto.mk`).

### Cambiado
- CI: Node 24 (LTS) en lugar de Node 22, que deja de tener soporte el 2027-04-30.
- CI: las versiones de las herramientas están en un solo bloque `env` y un proyecto puede cambiarlas sin tocar el archivo, con variables del repositorio en GitHub: `GOLANGCI_LINT_VERSION`, `MIGRATE_VERSION`, `GOVULNCHECK_VERSION`, `NODE_VERSION`.
- Requisitos en README, guía y skill `go-backend`: Go 1.26+ (1.23 está sin soporte desde 2025-08-12) y Node 24. La guía instala las herramientas de Go con versión fija.
- Rol `devops`: la regla de fijar versiones incluye herramientas y aclara que en imágenes de base de datos se fija la versión mayor.

### Al actualizar
- **Los hooks empiezan a ejecutarse de verdad.** Tras `make actualizar-kit`, `git status` mostrará `.githooks/*` y los `.sh` como modificados (solo cambia el permiso): inclúyelos en el commit. Si el primer commit se rechaza, es un control que antes no corría; corrige lo que indique.
- **`docker-compose.yml` es una semilla y no se actualiza solo.** Si tu proyecto todavía tiene `postgres:16.4-alpine`, cámbialo a mano por `postgres:16-alpine` y ejecuta `docker compose pull db && make up` (conserva los datos: es la misma versión mayor).
- Si tu proyecto tiene un `backend/.golangci.yml` con formato de la v1, conviértelo con `golangci-lint migrate`.
- En local, instala Node 24 (`nvm install 24`) y reinstala las herramientas de Go con las versiones de la guía (sección 3.2).

## [1.6.1] - 2026-10-03

### Agregado
- `MANTENER-KIT.md`: manual para el agente que mantiene el kit (contexto, arquitectura, decisiones de diseño, reglas de cambio, cómo probar, hechos verificados y pendientes). No se copia a los proyectos.

### Cambiado
- En el repositorio del kit, `CLAUDE.md` carga `MANTENER-KIT.md` en lugar del manual del orquestador, para que Claude Code mantenga el kit en vez de tratarlo como un proyecto. En los proyectos no cambia nada.

## [1.6.0] - 2026-10-03

### Agregado
- `CHANGELOG.md` (este archivo) y `VERSION` con la versión del kit.
- `make actualizar-kit` muestra las novedades entre la versión instalada y la nueva, incluidos los pasos manuales.
- `make novedades` muestra el historial de cambios del kit (`DESDE=1.4.0` para ver desde una versión).
- `.kit-manifest.json` guarda la versión del kit (`1.6.0`) además del commit.

## [1.5.0] - 2026-10-03

### Agregado
- **Costo de IA por funcionalidad:** `make costos` registra tokens y costo equivalente en dólares por agente y modelo en `specs/<rama>/costos.json`, a partir de las sesiones de OpenCode (incluidos los subagentes).
- Precios desde models.dev, con historial por tarea: cada cambio de precio se agrega con su fecha y cada respuesta se valoriza con el precio vigente cuando ocurrió. Tarifa de hora pico de DeepSeek configurable.
- `make costos CERRAR=1` congela el costo al aprobar el PR; `TODO=1` resume el proyecto; `PRECIOS=hoy` cotiza a precios actuales sin guardar.
- `make estado` muestra el costo acumulado de la tarea.
- Precios manuales opcionales en `equipo/config.json` → `costos.precios_manuales`.

### Cambiado
- El orquestador ejecuta `make costos` al iniciar y al cerrar cada sesión, y lo cierra cuando el humano aprueba el PR.
- pre-commit: bloquea modificar un `costos.json` cerrado (excepción humana: `APROBADO_COSTOS=1`).
- Claude Code: los agentes no pueden editar `costos.json` a mano.

### Al actualizar
- Ejecuta `make costos` en la rama de tu funcionalidad y compara el total con la consola de OpenCode.

## [1.4.0] - 2026-10-03

### Agregado
- **Estado del trabajo:** `specs/<rama>/estado.md` (fase, aprobaciones, ciclo de corrección, hallazgos abiertos, decisiones y próximo paso) y plantillas `docs/plantillas/estado.md` y `docs/plantillas/roadmap.md` (con columna Estado).
- Skill `equipo-retomar`: reconstruye dónde quedó el trabajo a partir del estado, los archivos de Spec Kit y git.
- `make estado`: roadmap, fase, aprobaciones, tareas y próximo paso, con avisos si algo no cuadra; también muestra el trabajo en curso de otras ramas y avisa si el submódulo del kit no coincide con la rama.

### Cambiado
- El orquestador revisa el estado al iniciar cada sesión y lo actualiza en cada fase, puerta y ciclo de corrección, y al cerrar.
- pre-commit: avisa (sin bloquear) si cambian spec, plan o tareas sin actualizar `estado.md`.

### Al actualizar
- Pide al orquestador: "Pasa docs/producto/roadmap.md al formato de docs/plantillas/roadmap.md, con el estado actual de cada funcionalidad".
- En cada funcionalidad en curso, cámbiate a su rama y dile "retomemos" para crear su `estado.md`.

## [1.3.1] - 2026-09-30

### Agregado
- `make actualizar-modelos`: aplica al proyecto los modelos recomendados por el kit, mostrando antes los cambios y conservando el resto de la configuración. `make actualizar-kit` avisa cuando el kit recomienda modelos distintos.

### Al actualizar
- Ejecuta `make actualizar-modelos` y reinicia OpenCode.

## [1.3.0] - 2026-09-30

### Cambiado
- Nueva distribución de modelos para OpenCode Go según calidad y costo: `deepseek-v4.1-flash` para orquestador y desarrolladores, `mimo-v2.6-pro` para analista, arquitecto y revisor, `glm-5.3-flash` para QA, UX y DevOps, `glm-5.3` para seguridad y `mimo-v2.6-flash` para documentación.
- `equipo/MODELOS.md`: cómo funciona el presupuesto de OpenCode Go, rendimiento por modelo, horario pico de DeepSeek y privacidad por modelo.

## [1.2.0] - 2026-09-28

### Agregado
- Agente principal `orquestador` en OpenCode, por defecto al abrir (`default_agent`), con su manual en `equipo/orquestador.md`: experto en Spec Kit y en el kit, y obligado a respetar el proceso. `build` y `plan` siguen disponibles.
- Claude Code y Codex cargan el mismo manual.

### Al actualizar
- Reinicia OpenCode.

## [1.1.1] - 2026-09-27

### Corregido
- `docker-compose.yml`: puerto de PostgreSQL configurable (`POSTGRES_PORT`) para no chocar con un PostgreSQL instalado en Windows.
- pre-commit: mensaje claro cuando falta `python3` (commit hecho desde Windows en lugar de WSL).
- `make doctor`: detecta herramientas instaladas del lado de Windows (`/mnt/c/...`) y proyectos guardados en `/mnt`.

### Documentación
- Guía de inicio: trabajar todo dentro de Ubuntu/WSL (VS Code con la extensión WSL), conexión a la base de datos, clientes que no soportan SCRAM (Navicat), `jq`, y tabla ampliada de problemas comunes.
- Plantilla `docs/plantillas/idea.md` y sección "De la idea a la primera funcionalidad".

## [1.1.0] - 2026-09-26

### Agregado
- Instalación como submódulo git en `.bowser-spec-kit-ai/`: `make instalar-kit`, `make actualizar-kit` y `make verificar-kit`, con `.kit-manifest.json` (archivos del kit y su hash), semillas que pasan a ser del proyecto y `kit.excluir`.
- Protección de los archivos del kit en pre-commit, CI y Claude Code.
- `proyecto.mk` para comandos propios de cada proyecto.

## [1.0.0] - 2026-09-26

### Agregado
- Kit base de Spec-Driven Development con GitHub Spec Kit para React + TypeScript, Go y PostgreSQL.
- 10 roles en `equipo/agentes/`: analista de producto, arquitecto, diseñador UX, desarrollador backend y frontend, QA, revisor de código, seguridad, DevOps y documentador.
- Skills del stack (`go-backend`, `react-frontend`, `postgres-db`) y flujos del equipo (`equipo-feature`, `equipo-bug`, `equipo-revision`).
- Generador `make sincronizar` para Claude Code, Codex y OpenCode desde una sola fuente, con modelo y temperatura por agente y valores por defecto por rol.
- Constitución, hooks de git (secretos, migraciones, formato, Conventional Commits), CI en GitHub Actions y `make doctor`.
- Guía de inicio para personas nuevas.
