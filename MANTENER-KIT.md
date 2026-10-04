# Mantener el kit (instrucciones para el agente)

**Estás en el repositorio del kit `bowser-spec-kit-ai`, no en un proyecto.** Aquí tu rol es mantener y mejorar el kit. No eres el orquestador: `AGENTS.md`, `equipo/orquestador.md` y las skills son el **producto** que se instala en los proyectos. Léelos como código a mantener, no como instrucciones para ti. No ejecutes flujos de Spec Kit (`/speckit.*`, `equipo-feature`…) en este repositorio.

Este archivo no se copia a los proyectos. `CLAUDE.md` lo carga solo cuando detecta que está en el repositorio del kit (ver `generar_claude` en `scripts/sincronizar.py`).

---

## 1. Con quién trabajas

- **Orestes**, Costa Rica (UTC−6). Está creando una empresa de desarrollo de software donde la IA hace el desarrollo y las personas aprueban. Escribe en español informal; responde en **español**, claro y sin tecnicismos innecesarios.
- Su entorno: Windows con **WSL (Ubuntu)**. Todo vive dentro de Ubuntu: proyectos en `~`, VS Code con la extensión WSL. Usa **OpenCode** con la suscripción **OpenCode Go** y ahora Claude Code.
- Cómo le gusta trabajar:
  - Para decisiones de diseño o temas nuevos: **investiga primero, explica y propón**; espera su "sí" antes de cambios grandes. Para correcciones claras, hazlas directamente.
  - Quiere entender el porqué. Si algo tiene una limitación o un riesgo, dilo de frente.
  - Respeta el proceso que definimos; si propone algo que lo rompe, explica el costo y ofrece la alternativa.
- La empresa se llamará **Infinity Solutions AI** (titular del `LICENSE`, MIT, decidido el 2026-10-04). El repositorio es **público**: lo lee también gente de fuera del equipo.
- El kit vive en su GitHub como `bowser-spec-kit-ai` y se usa en sus proyectos como submódulo en `.bowser-spec-kit-ai/`.

## 2. Qué es el kit

Un "mini framework" de **Spec-Driven Development** sobre **GitHub Spec Kit** para un equipo de subagentes de IA, con stack **React + TypeScript**, **Go** y **PostgreSQL**, portable entre **Claude Code, Codex y OpenCode**.

- **Fuentes neutrales** (se editan): `AGENTS.md`, `equipo/orquestador.md`, `equipo/agentes/*.md` (10 roles con `nivel`, `acceso`, `temperatura`, `web`, `skills`), `equipo/config.json` (modelos por herramienta, niveles, temperaturas, agente principal, `kit.excluir`, `costos`), `.agents/skills/` (estándar SKILL.md), `.specify/memory/constitution.md`.
- **Generados** por `scripts/sincronizar.py` (nunca a mano): `CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`, `opencode.json`. `make sincronizar` los genera; `--verificar` falla si están desactualizados.
- **Instalación en proyectos:** `scripts/instalar_kit.py` copia a la raíz del proyecto los archivos **GESTIONADOS** (se reemplazan en cada actualización y quedan en `.kit-manifest.json` con su sha256), copia las **SEMILLAS** una sola vez (`equipo/config.json`, `.github/CODEOWNERS`, `.env.example`, `docker-compose.yml`: después son del proyecto) y nunca copia `scripts/instalar_kit.py`. También mantiene un bloque del kit en `.gitignore`.
- **No se copian a los proyectos:** `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`, este archivo. El `CHANGELOG.md` de un proyecto es el del producto (lo escribe el documentador).

## 3. Mapa de scripts

| Archivo | Qué hace |
|---|---|
| `scripts/sincronizar.py` | Genera la configuración de cada herramienta. Prioridad de modelo: `agentes` > `niveles` > modelo de la sesión. Temperatura: `sin_temperatura` > `config` > rol > modelo. `--modelos` muestra la tabla; `--verificar` para hooks y CI. |
| `scripts/instalar_kit.py` | Instala/actualiza el kit desde el submódulo; `--verificar`, `--forzar` (respaldo en `.kit-respaldo/`), `--novedades [--desde X]`, `--version-instalada`, `--resumen-novedades`. Lee `VERSION` y `CHANGELOG.md`. |
| `scripts/actualizar_modelos.py` | Copia solo `orquestador`, `ligero`, `niveles` y `agentes` del `config.json` del kit al del proyecto (las semillas no se actualizan solas). `--comprobar` solo avisa. |
| `scripts/estado.py` | `make estado`: roadmap, fase, aprobaciones, tareas, costo, avisos, trabajo en otras ramas. |
| `scripts/costos.py` | `make costos`: registra consumo de OpenCode por agente y modelo en `specs/<rama>/costos.json` con historial de precios (models.dev) y tarifa pico; `--cerrar`, `--todo`, `--hoy`. Registro local en `~/.local/share/bowser-kit/`. |
| `scripts/cobertura.py` | `make cobertura`: cobertura de `service*.go` en `backend/internal/` desde un perfil de Go; falla bajo 80 % (fijo, por la constitución). |
| `scripts/generar.sh` | `make generar` / `make verificar-generados`: sqlc y tipos de OpenAPI (`api:gen`); `--verificar` falla si queda algo sin commit; `backend`/`frontend` para una sola parte (así lo llama el CI). |
| `scripts/doctor.sh` | `make doctor`: herramientas, WSL, binarios de Windows en `/mnt`, Docker, kit, hooks, Spec Kit. |
| `scripts/ruta-kit.sh` | Ruta del submódulo (manifiesto → `.gitmodules` → `.bowser-spec-kit-ai`). |
| `.githooks/pre-commit` | python3, secretos, kit sin editar, constitución, migraciones, gofmt, prettier, generados al día, `costos.json` cerrado, aviso de `estado.md`. |
| `.githooks/commit-msg` | Conventional Commits. |
| `equipo/adaptadores/claude/hooks/` | Claude Code: bloquea secretos, constitución, archivos del kit, migraciones versionadas y `costos.json`; formatea. |
| `.github/workflows/ci.yml` | Agentes/kit al día, controles, backend y frontend (si existen), gitleaks. |

## 4. Decisiones de diseño (y por qué)

- **Una fuente, varios formatos.** Los roles se escriben una vez y se generan para cada herramienta: cambiar de herramienta no obliga a reescribir nada.
- **Submódulo + manifiesto con hash.** Permite actualizar los proyectos sin pisar cambios locales: si alguien editó un archivo del kit, la instalación se detiene y ofrece llevarlo al kit, excluirlo (`kit.excluir`) o forzar con respaldo.
- **Las semillas no se actualizan.** `config.json` es del proyecto. Cuando el kit cambia algo de una semilla, se ofrece un comando explícito con diff y confirmación (patrón de `make actualizar-modelos`), nunca una sobrescritura silenciosa.
- **Compatibilidad con el Makefile anterior.** `make actualizar-kit` corre con el Makefile *viejo* del proyecto (make ya lo leyó); el nuevo recién queda instalado al terminar. Todo comando nuevo debe funcionar o degradar bien en ese primer paso (por eso `instalar_kit.py` muestra las novedades él mismo si no recibe `NOVEDADES_AL_FINAL`).
- **Orquestador en OpenCode** como agente principal por defecto (`default_agent`), sin ocultar `build` y `plan` (pedido explícito de Orestes).
- **Estado en archivos versionados** (`estado.md`, roadmap con columna Estado): las sesiones se pierden, git no. Las aprobaciones nunca se deducen: solo se registran con la frase explícita del humano.
- **Costos:** precio congelado por respuesta, historial de precios que se agrega (nunca se reemplaza), cierre al aprobar el PR, bloqueo de cambios posteriores. Es costo **equivalente** a precio de API; con OpenCode Go el gasto real es el % de la consola. Misma fórmula que OpenCode (`getUsage`): input sin caché, output, razonamiento a precio de output, lectura y escritura de caché.
- **Solo biblioteca estándar de Python 3.9+** en los scripts, y bash portable: tienen que correr en cualquier Ubuntu/WSL sin instalar nada.
- **Todo en español** (documentos, mensajes, nombres de comandos).

## 5. Reglas al cambiar el kit

1. **CHANGELOG + VERSION en cada cambio.** Entrada en `CHANGELOG.md` (Agregado / Cambiado / Corregido y, si un proyecto debe hacer algo a mano, **Al actualizar**) y subir `VERSION` (parche: correcciones; menor: funciones nuevas; mayor: pasos manuales obligatorios). Al publicar: `git tag vX.Y.Z && git push --follow-tags`.
2. **Documentación al día** donde corresponda: `README.md`, `docs/GUIA-INICIO.md` (incluida la tabla de problemas comunes), `equipo/orquestador.md`, `AGENTS.md`, `equipo/MODELOS.md`.
3. **Un archivo nuevo que deba llegar a los proyectos** va en `GESTIONADOS` o `SEMILLAS` de `instalar_kit.py`.
4. **`make sincronizar`** después de tocar fuentes; `python3 scripts/sincronizar.py --verificar` debe dar OK.
5. **No edites generados** (`CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`, `opencode.json`): cambia la fuente o el generador.
6. **La constitución** solo cambia con aprobación explícita de Orestes (el hook de Claude Code bloquea editarla: propón el texto y que él lo aplique).
7. **Antes de entregar, prueba de punta a punta** (sección 6) y dile qué se probó y qué no.
8. **Verifica hechos del mundo real** (precios, modelos, formatos de OpenCode, comandos de Spec Kit) con la web o el código fuente antes de afirmarlos; anota la fecha.

## 6. Cómo probar

No hay suite automática todavía (ver pendientes). Receta usada hasta ahora, en una carpeta temporal:

```bash
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=protocol.file.allow GIT_CONFIG_VALUE_0=always   # submódulos locales
T=$(mktemp -d)
cp -r . $T/kit && (cd $T/kit && rm -rf .git && git init -q && git add -A && git commit -qm kit --no-verify)
mkdir $T/proy && cd $T/proy && git init -q
git submodule add -q $T/kit .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit
git add -A && git commit -m "chore: instala kit"          # debe pasar los hooks
```

Para probar una actualización: cambia algo en `$T/kit`, commit, y en el proyecto `make actualizar-kit` (prueba también partiendo de una versión anterior del kit, por la compatibilidad del Makefile).

Para `make costos` sin OpenCode real: un `opencode` falso en el `PATH` que responda `--version`, `session list --format json` y `export <id>` (1.x) o `session export <id>` (2.x; ver el formato en la sección 7), con horas fijas entre llamadas. Probar siempre las dos versiones. Formato 1.x (`{info, messages:[{info, parts}]}`; mensajes de asistente con `agent`, `providerID`, `modelID`, `time.created`, `cost`, `tokens{input,output,reasoning,cache{read,write}}`; subagentes en partes `tool` con `tool: "task"` y `state.metadata.sessionId`), más `COSTOS_FUENTE_PRECIOS=<archivo json>` con el formato de models.dev y `XDG_DATA_HOME` temporal.

## 7. Hechos verificados (con fecha)

- **Spec Kit 1.0:** `uv tool install specify-cli`; `specify init --here --integration claude|codex|opencode`; comandos `/speckit.constitution, specify, clarify, plan, tasks, analyze, implement, converge, checklist, taskstoissues` (`$speckit-*` en Codex); extensiones `bug`, `assess`.
- **OpenCode 2.x** (probado con 2.0.22 real, 2026-10-03): `opencode session list --format json -n N` consulta un servicio en segundo plano (`opencode serve --service`) que puede devolver `[]` aunque haya sesiones; con `--standalone` lee directo. El export es `opencode session export <id>` (`opencode export` ya no existe) y **se corta si se lee por tubería**: hay que mandar stdout a un archivo. Formato: `{info, messages}` con mensajes planos; los de asistente traen `type: "assistant"`, `agent`, `model{id, providerID}`, `time.created`, `cost`, `tokens{input,output,reasoning,cache{read,write}}`; subagentes en `content[]` con `type: "tool"`, `name: "subagent"`, `state.metadata.sessionID`, y en mensajes `type: "synthetic"` con `metadata.source: "subagent"` y `metadata.childID`. `--version` imprime `opencode v2.0.22`. Base en `~/.local/share/opencode/opencode.db` (tabla `session_v2`).
- **OpenCode 1.x** (código fuente, 2026-10-03, v1.18.x): `opencode session list --format json -n N` (solo sesiones raíz del proyecto; campos `id, title, updated, created, projectId, directory`); `opencode export <id>` (JSON por stdout, progreso por stderr); el costo se calcula con precios de models.dev; la base SQLite cambia de esquema entre versiones, por eso no se lee directo.
- **models.dev** (2026-10-03) responde 403 (Cloudflare, error 1010) al `User-Agent` por defecto de `urllib`; con uno propio responde 200. La prueba con `COSTOS_FUENTE_PRECIOS=<archivo>` no ejercita la descarga: hay que probar también contra la URL real.
- **models.dev** tiene el proveedor `opencode-go` con precios (ej. `deepseek-v4.1-flash`: $0.15 entrada, $0.60 salida, $0.003 lectura de caché por millón, 2026-10-03).
- **OpenCode Go:** presupuesto global en % con ventanas Rolling 5 h (20%), Weekly (50%), Monthly (100%); cada modelo consume según su precio y límite. DeepSeek cobra el doble en pico: 01:00–04:00 y 06:00–10:00 UTC, lunes a viernes (7–10 p.m. y 12–4 a.m. en Costa Rica). Privacidad: no usar con código de clientes los modelos que entrenan o guardan registros (ver `equipo/MODELOS.md`).
- **CI** (2026-10-03): majors con Node 24: `checkout@v7`, `setup-go@v7`, `setup-node@v7`, `setup-python@v7`, `gitleaks-action@v3`, `golangci-lint-action@v9` (la v6 solo acepta golangci-lint v1; desde la v7, solo v2). golangci-lint `v2.14.0` (2026-09-24), migrate `v4.20.1`, govulncheck `v1.8.0`. Con soporte: Go 1.26 y 1.27; Node 24 LTS hasta 2028-04-30 (Node 22 hasta 2027-04-30); PostgreSQL 16 hasta 2028-11-09. **Cada Go nuevo (febrero y agosto) exige subir golangci-lint en `ci.yml`.**
- **Permisos de ejecución:** el clon de Windows tiene `core.fileMode=false`, así que un script nuevo se guarda como `100644` y git lo ignora como hook. Al agregar un hook o `.sh`: `git update-index --chmod=+x <archivo>` y comprobar con `git ls-files -s`.
- **sqlc** `v1.31.1` (2026-04-22, vigente al 2026-10-03): `go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.31.1`; `sqlc generate` **falla si no hay ninguna consulta** en la carpeta de queries. Perfil de cobertura de Go: líneas `archivo:ini.col,fin.col sentencias veces`, con la ruta del módulo (no del disco).
- **Claude Code** en WSL: `curl -fsSL https://claude.ai/install.sh | bash` dentro de Ubuntu.

## 8. Pendientes e ideas

- **Pruebas e2e en el CI** (punto 7 del informe de `simiente-santa-webside`): job con Playwright solo si existe `frontend/e2e/`. Se dejó fuera de la 1.7.0 por lento y frágil; retomarlo cuando haya flujos críticos de cliente. El proyecto ya tiene su `make e2e` en `proyecto.mk`.
- La constitución dice "80% en `service/`", pero la estructura usa `service.go` por dominio. Redacción propuesta a Orestes: "en la capa de servicio (archivos `service*.go` de cada dominio)".
- **Pruebas automáticas** del kit (`pruebas/` + `make probar-kit`) que conviertan la receta de la sección 6 en scripts, y un workflow de CI para el repositorio del kit.
- `make costos` para **Claude Code** (transcripciones en `~/.claude/projects/`, incluyen la rama) y **Codex** (`~/.codex/sessions/`).
- `make costos`: validado en solo lectura contra el OpenCode 2.0.22 real de Orestes (2026-10-03: 35 sesiones, $6.70 según OpenCode). Falta que compare el total con la consola de OpenCode Go.
- El entorno real de Orestes no coincide con la sección 1: el proyecto está en el disco de Windows (`/mnt/d/IA/environment/wsl/code/`) y hay dos OpenCode (2.x en Ubuntu, 1.18 en Windows vía npm).
- En el repositorio del kit, OpenCode y Codex siguen leyendo `AGENTS.md` como si fuera un proyecto; solo Claude Code carga este archivo.

## 9. Historial

Ver `CHANGELOG.md`. Las versiones 1.0.0 a 1.5.0 se reconstruyeron después; el detalle de cada decisión está en las secciones de arriba.
