"""Roles sin tecnología: cada rol describe un oficio y recibe del perfil sus partes, skills y comandos."""
import json
import re

from apoyo import afirmar, contiene, correr, prueba

PERFIL = "equipo/perfil.json"
APROBADO = {"APROBADO_PERFIL": "1"}
# Lo que un rol no puede nombrar: va en las skills del catálogo y en el perfil de cada proyecto.
TECNOLOGIAS = re.compile(
    r"\b(Go|Golang|gofmt|golangci|govulncheck|sqlc|pgx|React|TypeScript|Vite|Vitest|Playwright|Tailwind|npm|Node|"
    r"PostgreSQL|Postgres|MySQL|PHP|Laravel|Docker|Dockerfile|OpenAPI|openapi)\b|backend/|frontend/")


def perfil_de_tres_partes() -> dict:
    return {"partes": [
        {"nombre": "api", "carpeta": "servidor", "descripcion": "API del producto",
         "roles": [{"rol": "dev-backend", "skills": ["go-backend"]}], "terceros": ["ajeno"],
         "verbos": {"revisar": "true", "probar": "true"}},
        {"nombre": "datos", "carpeta": "bd", "roles": ["dev-dba"], "skills": ["postgres-db"],
         "inmutables": ["cambios/*.sql"], "verbos": {"formato": "true"}},
        {"nombre": "panel", "carpeta": "web/panel",
         "roles": ["dev-backend", {"rol": "dev-frontend", "skills": ["react-frontend"]}]},
    ]}


def escribir_perfil(p, perfil) -> None:
    for parte in perfil["partes"]:
        p.escribir(f"{parte['carpeta']}/LEEME.txt", "código\n")
    p.escribir(PERFIL, json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")


def seccion(p, rol: str, herramienta: str = "claude") -> str:
    ruta = {"claude": f".claude/agents/{rol}.md", "codex": f".codex/agents/{rol}.toml",
            "opencode": f".opencode/agents/{rol}.md"}[herramienta]
    texto = p.leer(ruta)
    return texto[texto.index("## Este proyecto"):] if "## Este proyecto" in texto else ""


@prueba("ningún rol del kit nombra una tecnología, existe el rol de base de datos y un rol mal declarado se rechaza")
def roles_sin_tecnologia(e):
    kit = e.kit()
    roles = sorted((kit / "equipo/agentes").glob("*.md"))
    afirmar(len(roles) >= 11, f"faltan roles: {[r.stem for r in roles]}")
    for ruta in roles:
        texto = ruta.read_text(encoding="utf-8")
        nombradas = sorted({m.group(0) for m in TECNOLOGIAS.finditer(texto)})
        afirmar(not nombradas, f"equipo/agentes/{ruta.name} nombra tecnologías o carpetas fijas: {nombradas}")
        afirmar("\nskills:" not in texto.split("---\n", 2)[1], f"{ruta.name} trae skills escritas: las asigna el perfil")
    dba = (kit / "equipo/agentes/dev-dba.md").read_text(encoding="utf-8")
    contiene(dba, "\nproyecto: partes\n", "el rol dev-dba")

    (kit / "equipo/agentes/dev-dba.md").write_text(dba.replace("proyecto: partes", "proyecto: todo"), encoding="utf-8")
    r = correr(["python3", "scripts/sincronizar.py", "--verificar"], kit, e.entorno, espera=1)
    contiene(r.salida, "equipo/agentes/dev-dba.md: proyecto debe ser 'partes'")


@prueba("sin perfil, los roles reciben la estructura de siempre: backend y frontend, con sus skills y comandos")
def roles_sin_perfil(e):
    p = e.proyecto()
    for herramienta in ("claude", "codex", "opencode"):
        s = seccion(p, "dev-backend", herramienta)
        contiene(s, "El proyecto no tiene perfil", f"dev-backend en {herramienta}")
        contiene(s, "- **backend**, en `backend`")
        contiene(s, "Skills que debes aplicar: `go-backend`, `postgres-db` (en `.agents/skills/`).")
        contiene(s, "go test ./...")
        contiene(s, "`backend/migrations/*.sql`")
        contiene(s, "Las demás partes no son tuyas: `frontend` (`frontend`, de `dev-frontend`).")
        afirmar("react-frontend" not in s, "dev-backend recibió la skill del frontend")
    contiene(p.leer(".claude/agents/dev-backend.md"), "\nskills: go-backend, postgres-db\n", "la cabecera de dev-backend")
    contiene(p.leer(".claude/agents/dev-frontend.md"), "\nskills: react-frontend\n", "la cabecera de dev-frontend")
    contiene(seccion(p, "dev-dba"), "Hoy no te asigna ninguna parte", "dev-dba sin perfil")
    afirmar("\nskills:" not in p.leer(".claude/agents/dev-dba.md"), "dev-dba sin partes no debe traer skills")

    # Un rol que ve todo el proyecto recibe las dos partes; el analista, que no habla de tecnología, ninguna.
    mapa = seccion(p, "revisor-codigo")
    contiene(mapa, "- **backend**, en `backend`")
    contiene(mapa, "- **frontend**, en `frontend`")
    contiene(mapa, "La trabajan: `dev-frontend`.")
    contiene(mapa, "Sus convenciones están en las skills `react-frontend`")
    afirmar("\nskills:" not in p.leer(".claude/agents/revisor-codigo.md"), "un rol que solo ve el mapa no carga las skills")
    afirmar(not seccion(p, "analista-producto"), "el analista de producto no debe recibir datos de tecnología")


@prueba("con perfil, cada rol recibe sus partes con carpeta, skills, comandos y límites; los demás roles ven el mapa completo")
def roles_con_perfil(e):
    p = e.proyecto()
    escribir_perfil(p, perfil_de_tres_partes())
    p.make("instalar-kit")
    p.commit("chore: perfil del proyecto", extra=APROBADO)

    dba = seccion(p, "dev-dba")
    contiene(dba, f"Sale del perfil del proyecto (`{PERFIL}`), que no editas tú. Tus partes:")
    contiene(dba, "- **datos**, en `bd`.")
    contiene(dba, "Skills que debes aplicar: `postgres-db` (en `.agents/skills/`).")
    contiene(dba, "Comandos: `make lint PARTE=datos`.")
    contiene(dba, "El proyecto todavía no tiene cómo: revisar, probar, cobertura, generar, auditar.")
    contiene(dba, "No se modifican una vez versionados (se crea un archivo nuevo): `bd/cambios/*.sql`.")
    contiene(dba, "Las demás partes no son tuyas: `api` (`servidor`, de `dev-backend`), "
                  "`panel` (`web/panel`, de `dev-backend`, `dev-frontend`).")
    contiene(p.leer(".claude/agents/dev-dba.md"), "\nskills: postgres-db\n", "la cabecera de dev-dba")
    contiene(seccion(p, "dev-dba", "codex"), "- **datos**, en `bd`.", "dev-dba en Codex")
    contiene(seccion(p, "dev-dba", "opencode"), "- **datos**, en `bd`.", "dev-dba en OpenCode")

    # Un rol en dos partes: cada una con sus skills, y nada de lo que el kit suponía sin perfil.
    backend = seccion(p, "dev-backend")
    contiene(backend, "- **api**, en `servidor`: API del producto")
    contiene(backend, "Skills que debes aplicar: `go-backend`")
    contiene(backend, "Comandos: `make lint PARTE=api`, `make test PARTE=api`.")
    contiene(backend, "El proyecto todavía no tiene cómo: formato, cobertura, generar, auditar.")
    contiene(backend, "Código de terceros, que no se toca: `servidor/ajeno`.")
    contiene(backend, "- **panel**, en `web/panel`.")
    contiene(backend, "También la trabajan: `dev-frontend`.")
    contiene(backend, "Las demás partes no son tuyas: `datos` (`bd`, de `dev-dba`).")
    afirmar("go test" not in backend and "postgres-db" not in backend, "dev-backend conserva lo que se suponía sin perfil")
    contiene(p.leer(".claude/agents/dev-backend.md"), "\nskills: go-backend\n", "la cabecera de dev-backend")
    contiene(seccion(p, "dev-frontend"), "Skills que debes aplicar: `react-frontend`")

    mapa = seccion(p, "arquitecto")
    for esperado in ("- **api**, en `servidor`", "- **datos**, en `bd`.", "- **panel**, en `web/panel`.",
                     "La trabajan: `dev-backend`, `dev-frontend`.", "Sus convenciones están en las skills `postgres-db`",
                     "Comandos: `make lint PARTE=api`, `make test PARTE=api`."):
        contiene(mapa, esperado, "el mapa del arquitecto")

    # Un rol que suele ver el mapa también puede trabajar una parte, y un rol sin parte lo sabe.
    perfil = perfil_de_tres_partes()
    perfil["partes"][2]["roles"] = [{"rol": "devops", "skills": ["react-frontend"]}]
    escribir_perfil(p, perfil)
    contiene(p.correr("python3", "scripts/sincronizar.py", "--verificar", espera=1).salida, "Desactualizados: .claude/agents/devops.md")
    contiene(p.commit("chore: el panel pasa a devops", espera=1, extra=APROBADO).salida, "make sincronizar")
    p.make("sincronizar")
    contiene(seccion(p, "devops"), "- **panel**, en `web/panel` (la trabajas tú).")
    contiene(p.leer(".claude/agents/devops.md"), "\nskills: react-frontend\n", "la cabecera de devops")
    contiene(seccion(p, "dev-frontend"), "Hoy no te asigna ninguna parte")
    afirmar("\nskills:" not in p.leer(".claude/agents/dev-frontend.md"), "dev-frontend conserva una skill sin tener parte")

    # Las convenciones del proyecto van después del estándar, las nombre donde las nombre el perfil.
    p.escribir(".agents/skills/convenciones-de-panel/SKILL.md", "---\nname: convenciones-de-panel\ndescription: Del proyecto.\n---\n")
    perfil["partes"][2]["skills"] = ["convenciones-de-panel"]
    escribir_perfil(p, perfil)
    p.make("sincronizar")
    contiene(seccion(p, "devops"), "Skills que debes aplicar: `react-frontend`, `convenciones-de-panel` (en")
    contiene(seccion(p, "arquitecto"), "Sus convenciones están en las skills `react-frontend`, `convenciones-de-panel` (en")
    contiene(p.make("profile").salida, "devops (react-frontend, convenciones-de-panel)")
    p.commit("chore: el panel pasa a devops", extra=APROBADO)

    # Con un perfil mal escrito no se supone nada: se avisa y los roles lo dicen.
    p.escribir(PERFIL, "{ esto no es json")
    r = p.make("sincronizar")
    contiene(r.salida, "los roles se generan sin los datos del proyecto")
    contiene(seccion(p, "dev-backend"), "tiene errores y no se pudo leer")
    afirmar("servidor" not in seccion(p, "dev-backend"), "con un perfil ilegible se siguieron mostrando las partes")
