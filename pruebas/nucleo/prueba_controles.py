"""Los controles que no dependen de que el agente obedezca: hooks de git y hook de Claude Code."""
import json
import os
import shutil
import subprocess

from apoyo import afirmar, contiene, prueba

CONSTITUCION = ".specify/memory/constitution.md"


@prueba("el mensaje de commit debe seguir Conventional Commits")
def mensaje_de_commit(e):
    p = e.proyecto()
    p.escribir("nota.txt", "x\n")
    for malo in ("mensaje malo", "Feat: con mayúscula", "feat: x", "arreglo: tipo inventado"):
        contiene(p.commit(malo, espera=1).salida, "Mensaje de commit inválido")
    afirmar(p.commits() == 1, "un commit con mensaje inválido entró al historial")
    p.commit("feat(notas): agrega una nota")
    p.escribir("nota.txt", "y\n")
    p.commit("fix!: cambio incompatible en la nota")
    afirmar(p.commits() == 3, "un commit con mensaje válido fue rechazado")


@prueba("no se pueden subir archivos que suelen tener secretos, aunque se fuerce el git add")
def secretos(e):
    p = e.proyecto()
    for rel in (".env", "backend/.env.local", "certificado.pem", "llave.key", "secrets/token.txt"):
        p.escribir(rel, "contenido de prueba\n")
        afirmar(rel not in p.git("status", "--short", "--untracked-files=all").salida, f"{rel} no está ignorado por git")
        p.git("add", "-f", rel)
        r = p.git("commit", "-m", "chore: agrega configuración", espera=1)
        contiene(r.salida, f"No se permite commitear '{rel}'")
        p.git("rm", "-q", "--cached", rel)
    p.agregar(".env.example", "\n# variable nueva, sin valor\nNUEVA=\n")
    p.commit("docs: documenta una variable de entorno")


@prueba("la constitución no cambia sin aprobación; la que llega con una actualización del kit sí pasa")
def constitucion(e):
    kit = e.kit()
    p = e.proyecto(kit)

    p.agregar(CONSTITUCION, "\n- regla agregada a mano\n")
    contiene(p.commit("docs: cambia la constitución", espera=1).salida, "La constitución cambió")
    p.git("checkout", "-q", "HEAD", "--", CONSTITUCION)

    # El proyecto la declara suya (kit.excluir): desde entonces cada cambio necesita la aprobación.
    config = json.loads(p.leer("equipo/config.json"))
    config.setdefault("kit", {})["excluir"] = [CONSTITUCION]
    p.escribir("equipo/config.json", json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    p.make("instalar-kit")
    p.commit("chore: constitución propia del proyecto")
    p.agregar(CONSTITUCION, "\n- regla propia del proyecto\n")
    contiene(p.commit("docs: ajusta la constitución", espera=1).salida, "La constitución cambió")
    p.commit("docs: ajusta la constitución", extra={"APROBADO_CONSTITUCION": "1"})

    # Otro proyecto, sin exclusión: la constitución cambia en el kit y llega con la actualización.
    q = e.proyecto(kit)
    with open(kit / CONSTITUCION, "a", encoding="utf-8") as f:
        f.write("\n- regla nueva aprobada en el kit\n")
    e.commit_kit(kit, "cambia la constitución")
    q.make("actualizar-kit")
    contiene(q.leer(CONSTITUCION), "regla nueva aprobada en el kit", "la constitución del proyecto")
    q.commit("chore: actualiza kit")


@prueba("una migración ya versionada no se modifica; una nueva sí se puede agregar")
def migraciones(e):
    p = e.proyecto()
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.commit("feat(db): primera migración")
    p.agregar("backend/migrations/000001_inicio.up.sql", "ALTER TABLE a ADD b int;\n")
    contiene(p.commit("fix(db): cambia la migración", espera=1).salida, "No modifiques migraciones existentes")
    p.git("checkout", "-q", "HEAD", "--", "backend/migrations/000001_inicio.up.sql")
    # Eliminarla también es modificarla, aunque el commit no traiga nada más.
    p.git("rm", "-q", "backend/migrations/000001_inicio.up.sql")
    contiene(p.git("commit", "-m", "chore(db): elimina la migración", espera=1).salida, "No modifiques migraciones existentes")
    p.git("reset", "-q", "HEAD", "--", "backend/migrations/000001_inicio.up.sql")
    p.git("checkout", "-q", "HEAD", "--", "backend/migrations/000001_inicio.up.sql")
    p.escribir("backend/migrations/000002_columna.up.sql", "ALTER TABLE a ADD b int;\n")
    p.commit("feat(db): agrega una columna")


@prueba("sin python3, el commit se bloquea y el mensaje explica cómo resolverlo")
def sin_python(e):
    p = e.proyecto()
    limitado = e.tmp / f"sin-python-{p.ruta.name}"
    limitado.mkdir()
    for programa in ("git", "bash", "sh", "env", "grep", "sed", "awk", "cat", "head", "dirname", "basename", "sort", "xargs", "tr", "cut"):
        real = shutil.which(programa)
        if real:
            os.symlink(real, limitado / programa)
    p.escribir("nota.txt", "x\n")
    p.git("add", "-A")
    r = p.git("commit", "-m", "docs: nota", espera=1, extra={"PATH": str(limitado)})
    contiene(r.salida, "No se encontró python3")
    contiene(r.salida, "docs/windows-wsl.md")
    afirmar(p.commits() == 1, "el commit entró sin que corrieran los controles")


def intento_de_editar(e, p, rel: str) -> subprocess.CompletedProcess:
    """Lo que Claude Code le pasa al hook antes de editar un archivo."""
    return subprocess.run(["bash", "equipo/adaptadores/claude/hooks/proteger-archivos.sh"], cwd=p.ruta,
                          input=json.dumps({"tool_input": {"file_path": str(p.ruta / rel)}}).encode(),
                          env=dict(e.entorno, CLAUDE_PROJECT_DIR=str(p.ruta)), capture_output=True)


def se_bloquea(e, p, rel: str) -> str:
    r = intento_de_editar(e, p, rel)
    afirmar(r.returncode == 2, f"editar {rel} debía bloquearse (código 2) y dio {r.returncode}")
    motivo = r.stderr.decode("utf-8", "replace")
    contiene(motivo, "Bloqueado", f"el motivo al bloquear {rel}")
    return motivo


def se_permite(e, p, rel: str) -> None:
    r = intento_de_editar(e, p, rel)
    afirmar(r.returncode == 0, f"editar {rel} debía permitirse y se bloqueó: {r.stderr.decode('utf-8', 'replace')}")


@prueba("Claude Code: el hook bloquea secretos, constitución, archivos del kit y costos, y deja pasar el resto",
        requiere=("jq",))
def hook_de_claude(e):
    p = e.proyecto()
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.commit("feat(db): primera migración")

    # Sin perfil, los inmutables son los de la estructura supuesta: las migraciones de backend/.
    for rel in (".env", "secrets/clave.txt", "certificado.pem", CONSTITUCION, "AGENTS.md", "equipo/orquestador.md",
                ".bowser-spec-kit-ai/README.md", "backend/migrations/000001_inicio.up.sql", "specs/001-x/costos.json"):
        se_bloquea(e, p, rel)
    for rel in (".env.example", "src/app.go", "equipo/config.json", "backend/migrations/000002_nueva.up.sql", "specs/001-x/spec.md"):
        se_permite(e, p, rel)


@prueba("Claude Code: con perfil, el hook protege los inmutables que el perfil declara, y solo los ya versionados",
        requiere=("jq",))
def hook_de_claude_con_perfil(e):
    p = e.proyecto()
    perfil = {"partes": [
        {"nombre": "datos", "carpeta": "base", "roles": ["dev-dba"], "inmutables": ["cambios/*.sql"]},
        {"nombre": "api", "carpeta": "backend", "roles": ["dev-backend"]},
    ]}
    p.escribir("equipo/perfil.json", json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")
    p.escribir("base/cambios/001_inicio.sql", "CREATE TABLE a (id int);\n")
    p.escribir("base/consultas/listar.sql", "SELECT 1;\n")
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.make("instalar-kit")
    p.commit("feat(db): primer cambio de esquema", extra={"APROBADO_PERFIL": "1"})

    motivo = se_bloquea(e, p, "base/cambios/001_inicio.sql")
    contiene(motivo, "«datos»", "el motivo del bloqueo")
    contiene(motivo, "crea uno nuevo", "el motivo del bloqueo")
    # Uno nuevo se puede escribir y corregir mientras no esté en git, aunque ya exista en el disco.
    se_permite(e, p, "base/cambios/002_columna.sql")
    p.escribir("base/cambios/002_columna.sql", "ALTER TABLE a ADD b int;\n")
    se_permite(e, p, "base/cambios/002_columna.sql")
    # Lo que el perfil no declara no se protege: ni otros archivos de la parte ni la carpeta de la estructura original.
    se_permite(e, p, "base/consultas/listar.sql")
    se_permite(e, p, "backend/migrations/000001_inicio.up.sql")

    # Con un perfil mal escrito no se bloquea nada (el commit lo rechaza): si no, no se podría ni corregir.
    p.escribir("equipo/perfil.json", "{ esto no es JSON\n")
    se_permite(e, p, "base/cambios/001_inicio.sql")
    se_bloquea(e, p, ".env")


@prueba("Claude Code: los permisos y los hooks que el kit instala no nombran ninguna tecnología ni formatean al editar")
def ajustes_de_claude(e):
    p = e.proyecto(commit=False)
    for rel in ("equipo/adaptadores/claude/settings.json", ".claude/settings.json"):
        ajustes = json.loads(p.leer(rel))
        afirmar("PostToolUse" not in ajustes.get("hooks", {}), f"{rel} ejecuta un hook después de cada edición")
        permisos = [regla for grupo in ajustes["permissions"].values() for regla in grupo]
        for palabra in ("go ", "gofmt", "golangci", "govulncheck", "npm", "npx", "playwright", "php", "composer"):
            malos = [regla for regla in permisos if palabra in regla.lower()]
            afirmar(not malos, f"{rel} nombra una tecnología en sus permisos: {malos}")
        for regla in ("Bash(make:*)", "Read(./.env)", "Bash(git push:*)"):
            afirmar(regla in permisos, f"{rel} perdió el permiso {regla}")
    afirmar(not p.existe("equipo/adaptadores/claude/hooks/formatear.sh"), "el hook de formateo sigue llegando a los proyectos")
    hook = p.leer("equipo/adaptadores/claude/hooks/proteger-archivos.sh")
    for palabra in ("backend", "migrations", "gofmt", "prettier"):
        afirmar(palabra not in hook, f"el hook de Claude Code nombra «{palabra}»")
