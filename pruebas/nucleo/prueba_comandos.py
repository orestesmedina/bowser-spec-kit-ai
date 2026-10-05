"""Comandos dentro de la herramienta: equipo/comandos/ genera el formato de Claude Code, Codex y OpenCode."""
import json

from apoyo import afirmar, contiene, correr, prueba

PREFIJO = "bowser-"


def nombres(p) -> list[str]:
    cortos = sorted(a.stem for a in p.archivo("equipo/comandos").glob("*.md"))
    afirmar(len(cortos) >= 6, f"se esperaban al menos seis comandos en equipo/comandos/, hay {len(cortos)}")
    return [PREFIJO + c for c in cortos]


@prueba("cada comando de equipo/comandos/ queda generado para Claude Code, Codex y OpenCode")
def generados_en_las_tres(e):
    p = e.proyecto(commit=False)
    for n in nombres(p):
        claude = p.leer(f".claude/skills/{n}/SKILL.md")
        contiene(claude, f"name: {n}\n", f"el comando {n} de Claude Code")
        contiene(claude, "disable-model-invocation: true", f"el comando {n} de Claude Code")
        contiene(p.leer(f".agents/skills/{n}/SKILL.md"), f"name: {n}\n", f"el comando {n} de Codex")
        contiene(p.leer(f".agents/skills/{n}/agents/openai.yaml"), "allow_implicit_invocation: false",
                 f"la política del comando {n} de Codex")
        opencode = p.leer(f".opencode/commands/{n}.md")
        afirmar(opencode.startswith("---\ndescription: "), f"el comando {n} de OpenCode no empieza con su descripción")
        for texto, donde in ((claude, "Claude Code"), (opencode, "OpenCode")):
            contiene(texto, "GENERADO por scripts/sincronizar.py", f"el comando {n} de {donde}")

    # Los argumentos solo llegan como marcador donde la herramienta lo sustituye.
    contiene(p.leer(f".claude/skills/{PREFIJO}status/SKILL.md"), "$ARGUMENTS", "el comando de estado de Claude Code")
    contiene(p.leer(f".opencode/commands/{PREFIJO}status.md"), "$ARGUMENTS", "el comando de estado de OpenCode")
    afirmar("$ARGUMENTS" not in p.leer(f".agents/skills/{PREFIJO}status/SKILL.md"),
            "Codex no sustituye $ARGUMENTS: su comando no debe llevarlo")
    afirmar("$ARGUMENTS" not in p.leer(f".claude/skills/{PREFIJO}doctor/SKILL.md"),
            "un comando sin argumentos no debe llevar $ARGUMENTS")

    # Lo generado para Codex dentro de .agents/skills/ no es un archivo del kit ni se duplica en Claude Code.
    manifiesto = json.loads(p.leer(".kit-manifest.json"))["archivos"]
    colados = [r for r in manifiesto if r.startswith(f".agents/skills/{PREFIJO}")]
    afirmar(not colados, f"el instalador copió comandos generados como si fueran archivos del kit: {colados}")
    afirmar("equipo/comandos/status.md" in manifiesto, "equipo/comandos/ no llegó al proyecto como archivo del kit")
    afirmar(not p.existe(f".claude/skills/{PREFIJO}status/agents"), "Claude Code recibió la copia del comando de Codex")
    p.verificar_kit()
    p.commit("chore: instala kit")
    afirmar(not p.pendientes(), f"quedaron archivos sin commit: {p.pendientes()}")


@prueba("al desactivar una herramienta, sus comandos se retiran y el kit sigue verificado")
def sin_codex(e):
    p = e.proyecto()
    config = json.loads(p.leer("equipo/config.json"))
    config["herramientas"] = ["claude"]
    p.escribir("equipo/config.json", json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    p.make("sincronizar")
    afirmar(not list(p.archivo(".agents/skills").glob(f"{PREFIJO}*")), "quedaron comandos de Codex con Codex desactivado")
    afirmar(not p.existe(".opencode/commands"), "quedaron comandos de OpenCode con OpenCode desactivado")
    afirmar(p.existe(f".claude/skills/{PREFIJO}status/SKILL.md"), "se perdió el comando de Claude Code")
    afirmar(p.existe(".agents/skills/equipo-retomar/SKILL.md"), "sincronizar borró una skill escrita a mano")
    p.verificar_kit()
    p.correr("python3", "scripts/sincronizar.py", "--verificar")
    p.commit("chore: solo Claude Code")


@prueba("un comando propio del proyecto se genera igual, y uno mal escrito detiene make sincronizar")
def comando_propio(e):
    p = e.proyecto()
    p.escribir("equipo/comandos/deploy-demo.md",
               "---\nnombre: deploy-demo\ndescripcion: Publica la demo.\n---\nEjecuta `make demo`.\n")
    p.make("sincronizar")
    contiene(p.leer(f".opencode/commands/{PREFIJO}deploy-demo.md"), "Ejecuta `make demo`.", "el comando propio en OpenCode")
    afirmar(p.existe(f".claude/skills/{PREFIJO}deploy-demo/SKILL.md"), "falta el comando propio en Claude Code")
    afirmar(p.existe(f".agents/skills/{PREFIJO}deploy-demo/SKILL.md"), "falta el comando propio en Codex")
    p.verificar_kit()
    p.commit("feat: comando propio")

    malos = {
        "otro.md": ("---\nnombre: distinto\ndescripcion: x\n---\nHaz algo.\n", "debe coincidir con el nombre del archivo"),
        "Mayus.md": ("---\nnombre: Mayus\ndescripcion: x\n---\nHaz algo.\n", "solo admite minúsculas"),
        "vacio.md": ("---\nnombre: vacio\ndescripcion: x\n---\n", "no tiene instrucciones"),
        "sin-desc.md": ("---\nnombre: sin-desc\n---\nHaz algo.\n", "falta el campo 'descripcion'"),
        "marcador.md": ("---\nnombre: marcador\ndescripcion: x\n---\nUsa $ARGUMENTS.\n", "no escribas $ARGUMENTS"),
    }
    for archivo, (texto, mensaje) in malos.items():
        p.escribir(f"equipo/comandos/{archivo}", texto)
        r = correr(["python3", "scripts/sincronizar.py"], p.ruta, p.entorno, espera=1)
        contiene(r.salida, mensaje, f"el error de {archivo}")
        p.archivo(f"equipo/comandos/{archivo}").unlink()
    p.correr("python3", "scripts/sincronizar.py", "--verificar")


@prueba("un proyecto en la versión anterior recibe los comandos al actualizar, con su Makefile viejo")
def llegan_al_actualizar(e):
    e.version_anterior()
    kit = e.kit("anterior")
    p = e.proyecto(kit)
    e.pasar_kit_a(kit, "actual")
    p.make("actualizar-kit")
    for n in nombres(p):
        afirmar(p.existe(f".opencode/commands/{n}.md"), f"falta {n} en OpenCode después de actualizar")
        afirmar(p.existe(f".claude/skills/{n}/SKILL.md"), f"falta {n} en Claude Code después de actualizar")
        afirmar(p.existe(f".agents/skills/{n}/SKILL.md"), f"falta {n} en Codex después de actualizar")
    p.verificar_kit()
    p.commit("chore: actualiza kit")
    afirmar(not p.pendientes(), f"quedaron archivos sin commit después de actualizar: {p.pendientes()}")
