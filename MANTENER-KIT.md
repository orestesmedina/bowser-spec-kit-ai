# Mantener el kit (instrucciones para el agente)

**Estás en el repositorio del kit `bowser-spec-kit-ai`, no en un proyecto.** Aquí tu rol es mantener y mejorar el kit. No eres el orquestador: `AGENTS.md`, `equipo/orquestador.md` y las skills son el **producto** que se instala en los proyectos. Léelos como código a mantener, no como instrucciones para ti. No ejecutes flujos de Spec Kit (`/speckit.*`, `equipo-feature`…) en este repositorio.

Este archivo no se copia a los proyectos. `CLAUDE.md` lo carga solo cuando detecta que está en el repositorio del kit (ver `generar_claude` en `scripts/sincronizar.py`).

---

## 0. Hacia dónde va el kit (léelo primero)

El plan vigente está en **`HOJA-DE-RUTA.md`**: el norte (tres objetivos), los principios de diseño, las etapas con su estado, las decisiones tomadas y las abiertas. **Al iniciar una sesión, léelo y dile a Orestes en qué etapa estamos y cuál es el próximo paso.** Si una decisión abierta bloquea la etapa siguiente, resuélvela con él antes de empezar.

Resumen del norte (2026-10-04): el kit deja de estar atado a React, Go y PostgreSQL. Debe servir para cualquier tecnología (roles como especialistas, tecnologías como skills), para personas que programan y que no, y para que un freelancer con el kit sea una empresa de desarrollo. **El kit no dicta la arquitectura del proyecto:** la integración continua, las tecnologías y los requisitos son del proyecto, y el kit aporta los agentes, skills y comandos que los generan. Y no debe volverse pesado: la ligereza se mide.

Mientras no llegue la versión 2.0, el kit sigue funcionando como describen las secciones de abajo. Las sesiones largas rinden peor y cuestan más: cuando una conversación se alargue, deja el estado escrito en `HOJA-DE-RUTA.md` y propón seguir en una sesión nueva.

## 1. Con quién trabajas

- **Orestes**, Costa Rica (UTC−6). Está creando una empresa de desarrollo de software donde la IA hace el desarrollo y las personas aprueban. Escribe en español informal; responde en **español**, claro y sin tecnicismos innecesarios.
- Su entorno: Windows con **WSL (Ubuntu)**. Todo vive dentro de Ubuntu: proyectos en `~`, VS Code con la extensión WSL. Usa **OpenCode** con la suscripción **OpenCode Go** y ahora Claude Code.
- Cómo le gusta trabajar:
  - Para decisiones de diseño o temas nuevos: **investiga primero, explica y propón**; espera su "sí" antes de cambios grandes. Para correcciones claras, hazlas directamente.
  - Quiere entender el porqué. Si algo tiene una limitación o un riesgo, dilo de frente.
  - Respeta el proceso que definimos; si propone algo que lo rompe, explica el costo y ofrece la alternativa.
- La empresa se llamará **Infinity Solutions AI** (titular del `LICENSE`, MIT, decidido el 2026-10-04). El repositorio es **público**: lo lee también gente de fuera del equipo.
- "Bowser" es el nombre de su perro, y el kit se queda con ese nombre por ahora (decisión del 2026-10-04; lo ya revisado sobre nombres está en `HOJA-DE-RUTA.md`).
- Explica para qué sirve cada cosa en lenguaje simple antes de proponer el cómo (el 2026-10-04 contó que no había entendido una propuesta técnica de otra IA y la pegó para que se la explicaran; también pidió que le explicaran cómo funcionan en la práctica las contribuciones de terceros). Los commits los pide él, con la frase "haz el commit"; el push y los tags los hace él.
- El kit vive en su GitHub como `bowser-spec-kit-ai` y se usa en sus proyectos como submódulo en `.bowser-spec-kit-ai/`.

## 2. Qué es el kit

Un "mini framework" de **Spec-Driven Development** sobre **GitHub Spec Kit** para un equipo de subagentes de IA, con stack **React + TypeScript**, **Go** y **PostgreSQL**, portable entre **Claude Code, Codex y OpenCode**.

- **Fuentes neutrales** (se editan): `AGENTS.md`, `equipo/orquestador.md`, `equipo/agentes/*.md` (10 roles con `nivel`, `acceso`, `temperatura`, `web`, `skills`), `equipo/comandos/*.md` (comandos del chat: `nombre`, `descripcion`, `argumentos`), `equipo/config.json` (modelos por herramienta, niveles, temperaturas, agente principal, `kit.excluir`, `costos`), `.agents/skills/` (estándar SKILL.md: flujos del equipo y `perfil-proyecto`), `catalogo/skills/` (las skills de tecnología, con `metadata: madurez`), `.specify/memory/constitution.md`.
- **Generados** por `scripts/sincronizar.py` (nunca a mano): `CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`, `opencode.json` y las carpetas `.agents/skills/bowser-*/` (comandos para Codex, dentro de una carpeta de fuentes). `make sincronizar` los genera; `--verificar` falla si están desactualizados.
- **Instalación en proyectos:** `scripts/instalar_kit.py` copia a la raíz del proyecto los archivos **GESTIONADOS** (se reemplazan en cada actualización y quedan en `.kit-manifest.json` con su sha256), más las skills de `catalogo/skills/` que nombra el perfil del proyecto (sin perfil, `SIN_PERFIL` de `scripts/catalogo.py`), que quedan en su `.agents/skills/` igual de gestionadas, copia las **SEMILLAS** una sola vez (`equipo/config.json`, `.github/CODEOWNERS`, `.env.example`, `docker-compose.yml`: después son del proyecto) y nunca copia `scripts/instalar_kit.py`. También mantiene un bloque del kit en `.gitignore`.
- **No se copian a los proyectos:** `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`, `HOJA-DE-RUTA.md`, `kit.mk`, `pruebas/`, `.github/workflows/kit.yml`, este archivo y la documentación (`docs/*.md`), que en los proyectos se lee desde el submódulo (`.bowser-spec-kit-ai/docs/`). De `docs/` solo se copia `docs/plantillas/`. El `CHANGELOG.md` de un proyecto es el del producto (lo escribe el documentador).

## 3. Mapa de scripts

| Archivo | Qué hace |
|---|---|
| `scripts/sincronizar.py` | Genera la configuración de cada herramienta. Prioridad de modelo: `agentes` > `niveles` > modelo de la sesión. Temperatura: `sin_temperatura` > `config` > rol > modelo. `--modelos` muestra la tabla; `--verificar` para hooks y CI. También genera los comandos del chat desde `equipo/comandos/`; el prefijo está en `PREFIJO_COMANDOS`. |
| `scripts/instalar_kit.py` | Instala/actualiza el kit desde el submódulo; `--verificar`, `--forzar` (respaldo en `.kit-respaldo/`), `--novedades [--desde X]`, `--version-instalada`, `--resumen-novedades`. Lee `VERSION` y `CHANGELOG.md`. |
| `scripts/actualizar_modelos.py` | Copia solo `orquestador`, `ligero`, `niveles` y `agentes` del `config.json` del kit al del proyecto (las semillas no se actualizan solas). `--comprobar` solo avisa. |
| `scripts/perfil.py` | `make profile`: lee, valida y muestra `equipo/perfil.json` (partes, carpetas, roles, skills, terceros, inmutables y verbos). `roles_de(parte)` da cada rol con sus skills (las de la parte más las suyas). `--detectar` describe el proyecto en JSON sin escribir nada; `--verificar` para hooks. La lista `VERBOS` es el contrato del núcleo. |
| `scripts/catalogo.py` | `make skills`: lee y valida el catálogo (`catalogo/skills/`), con la madurez de cada skill; `--verificar` falla si una está mal escrita. Lo usan `instalar_kit.py` (qué copiar) y `perfil.py` (avisos y detección). En un proyecto encuentra el catálogo dentro del submódulo, por `ruta_kit` del manifiesto. |
| `scripts/verbos.py` | Ejecuta los verbos del perfil en la carpeta de cada parte, con `PERFIL_RAIZ` y `PERFIL_TERCEROS` en el entorno (`--parte`, `--verificar` para `generar`, `--resumen` para `make ci`). `--pre-commit` son los controles del perfil en cada commit: `APROBADO_PERFIL`, inmutables y formato de las partes tocadas. |
| `scripts/estado.py` | `make estado`: roadmap, fase, aprobaciones, tareas, costo, avisos, trabajo en otras ramas. |
| `scripts/costos.py` | `make costos`: registra consumo de OpenCode por agente y modelo en `specs/<rama>/costos.json` con historial de precios (models.dev) y tarifa pico; `--cerrar`, `--todo`, `--hoy`. Registro local en `~/.local/share/bowser-kit/`. |
| `scripts/cobertura.py` | `make cobertura`: cobertura de `service*.go` en `backend/internal/` desde un perfil de Go; falla bajo 80 % (fijo, por la constitución). |
| `scripts/generar.sh` | `make generar` / `make verificar-generados`: sqlc y tipos de OpenAPI (`api:gen`); `--verificar` falla si queda algo sin commit; `backend`/`frontend` para una sola parte (así lo llama el CI). |
| `scripts/doctor.sh` | `make doctor`: herramientas, WSL, binarios de Windows en `/mnt`, Docker, kit, hooks, Spec Kit. |
| `scripts/ruta-kit.sh` | Ruta del submódulo (manifiesto → `.gitmodules` → `.bowser-spec-kit-ai`). |
| `pruebas/ejecutar.py` | `make test-kit` (definido en `kit.mk`): pruebas automáticas del kit en proyectos temporales. Solo del repositorio del kit; no se copia a los proyectos. |
| `.githooks/pre-commit` | python3, secretos, kit sin editar, constitución, migraciones, gofmt, prettier (con perfil, esos tres los reemplaza `verbos.py --pre-commit`), generados al día, `costos.json` cerrado, aviso de `estado.md`. |
| `.githooks/commit-msg` | Conventional Commits. |
| `equipo/adaptadores/claude/hooks/` | Claude Code: bloquea secretos, constitución, archivos del kit, migraciones versionadas y `costos.json`; formatea. |
| `.github/workflows/ci.yml` | Agentes/kit al día, controles, backend y frontend (si existen), gitleaks. |
| `.github/workflows/kit.yml` | Solo del repositorio del kit (está en `NUNCA` de `instalar_kit.py`): `make test-kit ESTRICTO=1` en cada PR y push a `main`, con Go, Node y sqlc. |

## 4. Decisiones de diseño (y por qué)

- **Una fuente, varios formatos.** Los roles se escriben una vez y se generan para cada herramienta: cambiar de herramienta no obliga a reescribir nada.
- **Submódulo + manifiesto con hash.** Permite actualizar los proyectos sin pisar cambios locales: si alguien editó un archivo del kit, la instalación se detiene y ofrece llevarlo al kit, excluirlo (`kit.excluir`) o forzar con respaldo.
- **Las semillas no se actualizan.** `config.json` es del proyecto. Cuando el kit cambia algo de una semilla, se ofrece un comando explícito con diff y confirmación (patrón de `make actualizar-modelos`), nunca una sobrescritura silenciosa.
- **Compatibilidad con el Makefile anterior.** `make actualizar-kit` corre con el Makefile *viejo* del proyecto (make ya lo leyó); el nuevo recién queda instalado al terminar. Todo comando nuevo debe funcionar o degradar bien en ese primer paso (por eso `instalar_kit.py` muestra las novedades él mismo si no recibe `NOVEDADES_AL_FINAL`).
- **Comandos del chat en `equipo/comandos/`** (decisión de Orestes, 2026-10-04), generados para cada herramienta. En Claude Code y Codex son skills con la invocación automática desactivada, para que no ocupen contexto. Como Codex solo lee `.agents/skills/`, los suyos se generan ahí en carpetas `bowser-*`: `sincronizar.py` las controla por comodín, `generar_claude` no las copia e `instalar_kit.py` no las lleva a los proyectos (cada uno genera las suyas según sus herramientas activas). Los comandos envuelven a `make` y nunca toman las decisiones reservadas a una persona (`CERRAR=1`, `FORZAR=1`, modelos, commits).
- **Perfil y verbos** (etapa 2, entrega A, 2026-10-05). El perfil es del proyecto: no está en `GESTIONADOS` ni en `SEMILLAS`, lo redacta un agente (`/bowser-profile`, rol `arquitecto`, skill `perfil-proyecto`; no hay un agente nuevo porque es una tarea ocasional) y lo confirma una persona en el commit con `APROBADO_PERFIL=1`, porque sus comandos se ejecutan en cada máquina y en el CI. Va en JSON porque los scripts solo usan la biblioteca estándar (sin YAML; `tomllib` exige Python 3.11). Un verbo sin definir avisa y no falla: hay proyectos sin pruebas ni formateador. **Sin perfil todo se comporta como antes**: el `Makefile` elige con `ifdef CON_PERFIL` y el pre-commit con un `if`; esa rama vieja se retira en la 2.0.
- **Catálogo de skills** (etapa 2, paso B2, 2026-10-09). Las skills de tecnología no están en `GESTIONADOS`: `instalar_kit.py` las agrega aparte, cambiando la ruta (`catalogo/skills/x/` → `.agents/skills/x/`), y desde ahí siguen las reglas de cualquier archivo del kit (manifiesto, conflictos, `kit.excluir`, retiro). La madurez va en `metadata` porque es el campo que el estándar Agent Skills reserva para datos propios (agentskills.io/specification, verificado el 2026-10-09). Cambiar las skills del perfil sin instalar hace fallar `--verificar`: se eligió lo estricto para que el perfil y lo instalado no se separen entre máquinas. Con un perfil ilegible no se agrega ni se retira nada. Hasta el B3, `sincronizar.py` le quita a cada rol las skills que el proyecto no tiene.
- **Orquestador en OpenCode** como agente principal por defecto (`default_agent`), sin ocultar `build` y `plan` (pedido explícito de Orestes).
- **Estado en archivos versionados** (`estado.md`, roadmap con columna Estado): las sesiones se pierden, git no. Las aprobaciones nunca se deducen: solo se registran con la frase explícita del humano.
- **Costos:** precio congelado por respuesta, historial de precios que se agrega (nunca se reemplaza), cierre al aprobar el PR, bloqueo de cambios posteriores. Es costo **equivalente** a precio de API; con OpenCode Go el gasto real es el % de la consola. Misma fórmula que OpenCode (`getUsage`): input sin caché, output, razonamiento a precio de output, lectura y escritura de caché.
- **Solo biblioteca estándar de Python 3.9+** en los scripts, y bash portable: tienen que correr en cualquier Ubuntu/WSL sin instalar nada.
- **Documentos y mensajes en español; nombres de comandos en inglés** (decisión de Orestes, 2026-10-04). Aplica a los comandos de la herramienta (`/bowser-update-kit`) y a los de `make`. Los de `make` hoy siguen en español: se renombran en la 2.0, dejando los nombres viejos como alias un tiempo. Todo comando nuevo nace en inglés.
- **Documentación como wiki en `docs/`, al estilo de la de Laravel** (pedido de Orestes, 2026-10-04): Markdown plano, una página por tema, única fuente de verdad. Público: gente técnica que se une al equipo y quien encuentra el kit en GitHub; la vara es que quien la lea termine dominando el kit. Cada página: título, mini índice, introducción (qué es), para qué sirve, cómo y cuándo se usa con comandos copiables y salida real, qué hacer cuando falla (mensaje exacto), límites, cómo cambiarlo, "Siguientes pasos". Notas con `> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`. Sin "la empresa": se habla de "el equipo" y de "dirección técnica" (definida en el glosario). El orquestador depende de `docs/aprobaciones.md`: su nombre no cambia. Un sitio web (Starlight, VitePress) queda como paso posterior opcional, generado desde estas mismas páginas.

## 5. Reglas al cambiar el kit

1. **CHANGELOG + VERSION en cada cambio.** Entrada en `CHANGELOG.md` (Agregado / Cambiado / Corregido y, si un proyecto debe hacer algo a mano, **Al actualizar**) y subir `VERSION` (parche: correcciones; menor: funciones nuevas; mayor: pasos manuales obligatorios). Al publicar: `git tag vX.Y.Z && git push origin main --tags` (no `--follow-tags`: solo sube tags anotados y estos son simples; el 2026-10-04 GitHub no tenía ningún tag y `kit.yml` falló por eso).
2. **Documentación al día** donde corresponda: la página del tema en `docs/` (índice en `docs/README.md`; `docs/problemas-comunes.md` y `docs/comandos.md` casi siempre), `README.md`, `equipo/orquestador.md` y `AGENTS.md`. Convenciones de las páginas en la sección 4.
3. **Un archivo nuevo que deba llegar a los proyectos** va en `GESTIONADOS` o `SEMILLAS` de `instalar_kit.py`.
4. **`make sincronizar`** después de tocar fuentes; `python3 scripts/sincronizar.py --verificar` debe dar OK.
5. **No edites generados** (`CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`, `opencode.json`): cambia la fuente o el generador.
6. **La constitución** solo cambia con aprobación explícita de Orestes (el hook de Claude Code bloquea editarla: propón el texto y que él lo aplique).
7. **Antes de entregar, `make test-kit` debe pasar** (sección 6). Si el cambio agrega o cambia un comportamiento, agrega su prueba. Dile qué se probó y qué no.
8. **Verifica hechos del mundo real** (precios, modelos, formatos de OpenCode, comandos de Spec Kit) con la web o el código fuente antes de afirmarlos; anota la fecha.

## 6. Cómo probar

```bash
make test-kit
```

Instala el kit en proyectos temporales, lo actualiza desde el último tag publicado y comprueba hooks, controles, costos (OpenCode simulado 1.x y 2.x), archivos generados, enlaces de la documentación y, en el grupo `pruebas/go/`, `make generar`, `make verificar-generados` y `make cobertura` (se omiten si falta `go`, `sqlc`, `node` o `npm`; en WSL hay que tener `~/.local/bin` y `~/go/bin` en el `PATH`). Prueba la carpeta de trabajo tal como está, sin necesidad de commit. Termina con error si algo falla. Opciones y cómo agregar una prueba: `pruebas/README.md`.

- **Cada cambio de comportamiento lleva su prueba**, y la prueba se valida rompiendo a propósito lo que comprueba: una prueba que nunca falló no demuestra nada.
- `make test-kit` solo existe en el repositorio del kit: vive en `kit.mk`, que no se copia a los proyectos. `pruebas/` tampoco se copia.
- **Lo que no cubre** (hay que probarlo a mano y decirlo al entregar): el comando `/bowser-profile` dentro de una herramienta real (solo se prueban `make profile`, la detección, los verbos y la instalación de skills según el perfil), `make doctor`, `make estado`, `make actualizar-modelos`, la descarga real de precios de models.dev, el `ci.yml` que se copia a los proyectos y el `kit.yml` del kit (solo se prueban de verdad en GitHub), `make generar` contra un proyecto real y el OpenCode real.
- Para probar a mano contra el proyecto real, clonarlo a una carpeta temporal: nunca sobre la carpeta de trabajo de Orestes.

## 7. Hechos verificados (con fecha)

- **Spec Kit 1.0:** `uv tool install specify-cli`; `specify init --here --integration claude|codex|opencode`; comandos `/speckit.constitution, specify, clarify, plan, tasks, analyze, implement, converge, checklist, taskstoissues` (`$speckit-*` en Codex); extensiones `bug`, `assess`.
- **Comandos propios** (documentación oficial, 2026-10-04; sin probar en las herramientas reales): **Claude Code**, skill en `.claude/skills/<nombre>/SKILL.md` que se invoca con `/<nombre>`; `disable-model-invocation: true` saca su descripción del contexto; `argument-hint`; sustituye `$ARGUMENTS`. **Codex**, skills solo en `.agents/skills/` (carpeta actual, raíz del repositorio, `~/.agents/skills`, `/etc/codex/skills`), se invocan con `$nombre`, no reciben argumentos y `agents/openai.yaml` con `policy.allow_implicit_invocation: false` evita que se carguen solas. **OpenCode**, `.opencode/commands/<nombre>.md` con `description` (opcionales `agent`, `model`, `subtask`) y el cuerpo como plantilla; sustituye `$ARGUMENTS`; sus skills no son comandos y las busca en `.opencode/skills/`, `.claude/skills/` y `.agents/skills/`.
- **OpenCode 2.x** (probado con 2.0.22 real, 2026-10-03): `opencode session list --format json -n N` consulta un servicio en segundo plano (`opencode serve --service`) que puede devolver `[]` aunque haya sesiones; con `--standalone` lee directo. El export es `opencode session export <id>` (`opencode export` ya no existe) y **se corta si se lee por tubería**: hay que mandar stdout a un archivo. Formato: `{info, messages}` con mensajes planos; los de asistente traen `type: "assistant"`, `agent`, `model{id, providerID}`, `time.created`, `cost`, `tokens{input,output,reasoning,cache{read,write}}`; subagentes en `content[]` con `type: "tool"`, `name: "subagent"`, `state.metadata.sessionID`, y en mensajes `type: "synthetic"` con `metadata.source: "subagent"` y `metadata.childID`. `--version` imprime `opencode v2.0.22`. Base en `~/.local/share/opencode/opencode.db` (tabla `session_v2`).
- **OpenCode 1.x** (código fuente, 2026-10-03, v1.18.x): `opencode session list --format json -n N` (solo sesiones raíz del proyecto; campos `id, title, updated, created, projectId, directory`); `opencode export <id>` (JSON por stdout, progreso por stderr); el costo se calcula con precios de models.dev; la base SQLite cambia de esquema entre versiones, por eso no se lee directo.
- **models.dev** (2026-10-03) responde 403 (Cloudflare, error 1010) al `User-Agent` por defecto de `urllib`; con uno propio responde 200. La prueba con `COSTOS_FUENTE_PRECIOS=<archivo>` no ejercita la descarga: hay que probar también contra la URL real.
- **models.dev** tiene el proveedor `opencode-go` con precios (ej. `deepseek-v4.1-flash`: $0.15 entrada, $0.60 salida, $0.003 lectura de caché por millón, 2026-10-03).
- **OpenCode Go:** presupuesto global en % con ventanas Rolling 5 h (20%), Weekly (50%), Monthly (100%); cada modelo consume según su precio y límite. DeepSeek cobra el doble en pico: 01:00–04:00 y 06:00–10:00 UTC, lunes a viernes (7–10 p.m. y 12–4 a.m. en Costa Rica). Privacidad: no usar con código de clientes los modelos que entrenan o guardan registros (ver `docs/modelos.md`).
- **CI** (2026-10-03): majors con Node 24: `checkout@v7`, `setup-go@v7`, `setup-node@v7`, `setup-python@v7`, `gitleaks-action@v3`, `golangci-lint-action@v9` (la v6 solo acepta golangci-lint v1; desde la v7, solo v2). golangci-lint `v2.14.0` (2026-09-24), migrate `v4.20.1`, govulncheck `v1.8.0`. Con soporte: Go 1.26 y 1.27; Node 24 LTS hasta 2028-04-30 (Node 22 hasta 2027-04-30); PostgreSQL 16 hasta 2028-11-09. **Cada Go nuevo (febrero y agosto) exige subir golangci-lint en `ci.yml`.**
- **Permisos de ejecución:** el clon de Windows tiene `core.fileMode=false`, así que un script nuevo se guarda como `100644` y git lo ignora como hook. Al agregar un hook o `.sh`: `git update-index --chmod=+x <archivo>` y comprobar con `git ls-files -s`.
- **sqlc** `v1.31.1` (2026-04-22, vigente al 2026-10-03): `go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.31.1`; `sqlc generate` **falla si no hay ninguna consulta** en la carpeta de queries. Perfil de cobertura de Go: líneas `archivo:ini.col,fin.col sentencias veces`, con la ruta del módulo (no del disco).
- **Claude Code** en WSL: `curl -fsSL https://claude.ai/install.sh | bash` dentro de Ubuntu.

## 8. Pendientes e ideas

- **Etapa 2, entrega A (1.12.1):** falta probar `/bowser-profile` en una herramienta real. El perfil de los dos proyectos de validación (`simiente-santa-webside` y p2p Controller) se escribió y se probó sobre copias el 2026-10-08 (`~/validacion-kit/` en WSL); los hallazgos y lo que sigue (entregas B, C y D) están en `HOJA-DE-RUTA.md`. El diseño de la entrega B está aprobado (2026-10-08) y sus pasos, B1 a B6, están en la hoja de ruta: se trabaja en la rama `etapa-2`. Hechos el B1 (1.13.0) y el B2 (1.14.0); sigue el B3.
- **Etapa 1, entrega B:** probar a mano los seis comandos `bowser-*` en Claude Code, Codex y OpenCode reales (que aparezcan, que reciban los argumentos y que OpenCode no los muestre duplicados entre comando y skill). `make test-kit` solo comprueba los archivos generados. Comprobado por Orestes el 2026-10-04 en OpenCode, dentro del repositorio del kit: `/bowser-news` aparece, se ejecuta y resume bien (ahí `make novedades` se niega, como corresponde, y el agente leyó `CHANGELOG.md`). Y en un proyecto temporal de `make test-kit CONSERVAR=1`: `/bowser-news 1.9.0` recibió la versión como argumento y mostró solo lo posterior, con los pasos manuales aparte. En la lista de `/` de OpenCode cada comando sale una sola vez. Falta: Claude Code y Codex.
- **Pruebas e2e en el CI** (punto 7 del informe de `simiente-santa-webside`): job con Playwright solo si existe `frontend/e2e/`. Se dejó fuera de la 1.7.0 por lento y frágil; retomarlo cuando haya flujos críticos de cliente. El proyecto ya tiene su `make e2e` en `proyecto.mk`.
- La constitución dice "80% en `service/`", pero la estructura usa `service.go` por dominio. Redacción propuesta a Orestes: "en la capa de servicio (archivos `service*.go` de cada dominio)".
- **Pruebas automáticas** del kit (etapa 0 de `HOJA-DE-RUTA.md`): hechas las dos entregas (1.9.0 y 1.10.0). `kit.yml` quedó en verde en GitHub el 2026-10-04 (1.10.1). Sin pruebas todavía: `make doctor`, `make estado`, `make actualizar-modelos`.
- `make costos` para **Claude Code** (transcripciones en `~/.claude/projects/`, incluyen la rama) y **Codex** (`~/.codex/sessions/`).
- `make costos`: validado en solo lectura contra el OpenCode 2.0.22 real de Orestes (2026-10-03: 35 sesiones, $6.70 según OpenCode). Falta que compare el total con la consola de OpenCode Go.
- El entorno real de Orestes no coincide con la sección 1: el proyecto está en el disco de Windows (`/mnt/d/IA/environment/wsl/code/`) y hay dos OpenCode (2.x en Ubuntu, 1.18 en Windows vía npm).
- En el repositorio del kit, OpenCode y Codex siguen leyendo `AGENTS.md` como si fuera un proyecto; solo Claude Code carga este archivo.

## 9. Historial

Ver `CHANGELOG.md`. Las versiones 1.0.0 a 1.5.0 se reconstruyeron después; el detalle de cada decisión está en las secciones de arriba.
