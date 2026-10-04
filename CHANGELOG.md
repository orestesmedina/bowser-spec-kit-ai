# Cambios del kit

Todos los cambios importantes de este kit se registran aquí.
Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

- **MAYOR** (2.0.0): un proyecto tiene que hacer algo a mano para seguir funcionando.
- **MENOR** (1.5.0): funciones nuevas compatibles.
- **PARCHE** (1.5.1): correcciones y documentación.

Cada versión puede incluir una sección **Al actualizar** con los pasos manuales. `make actualizar-kit` muestra las entradas nuevas al terminar; `make novedades` las muestra en cualquier momento.

> Las versiones 1.0.0 a 1.5.0 se reconstruyeron el 2026-10-03 a partir del historial de trabajo; las fechas anteriores a esa son aproximadas.

## [Sin publicar]

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
