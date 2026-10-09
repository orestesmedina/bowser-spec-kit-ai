"""Catálogo de skills: las de tecnología viven en el kit y cada proyecto recibe solo las que nombra su perfil."""
import json

from apoyo import SUBMODULO, afirmar, contiene, correr, prueba

PERFIL = "equipo/perfil.json"
APROBADO = {"APROBADO_PERFIL": "1"}
DE_SIEMPRE = ("go-backend", "postgres-db", "react-frontend")


def skill(nombre: str, madurez: str | None = "redactada") -> str:
    metadatos = f"metadata:\n  madurez: {madurez}\n" if madurez else ""
    return f"---\nname: {nombre}\ndescription: Convenciones de {nombre}. Usar al tocar {nombre}.\n{metadatos}---\n# {nombre}\n"


def perfil_con(p, skills: list, roles: list | None = None) -> None:
    parte = {"nombre": "api", "carpeta": "servidor", "skills": skills}
    if roles is not None:
        parte["roles"] = roles
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir(PERFIL, json.dumps({"partes": [parte]}, ensure_ascii=False, indent=2) + "\n")


def instaladas(p) -> list[str]:
    return sorted(x.name for x in p.archivo(".agents/skills").iterdir()
                  if not x.name.startswith(("bowser-", "equipo-", "perfil-")))


@prueba("el catálogo del kit está bien escrito, y una skill sin madurez o con otro nombre se rechaza")
def catalogo_valido(e):
    kit = e.kit()
    contiene(correr(["python3", "scripts/catalogo.py", "--verificar"], kit, e.entorno).salida, "skills en el catálogo")
    for nombre in DE_SIEMPRE:
        afirmar((kit / "catalogo/skills" / nombre / "SKILL.md").is_file(), f"falta {nombre} en el catálogo")
        afirmar(not (kit / ".agents/skills" / nombre).exists(), f"{nombre} sigue en .agents/skills/ del kit")
    r = correr(["make", "--no-print-directory", "skills"], kit, e.entorno)
    contiene(r.salida, "go-backend      probada")

    for carpeta, texto, mensaje in (
        ("sin-madurez", skill("sin-madurez", None), "falta la madurez en los metadatos"),
        ("madurez-rara", skill("madurez-rara", "excelente"), "falta la madurez en los metadatos"),
        ("otro-nombre", skill("php"), "«name» debe ser igual al nombre de la carpeta (otro-nombre)"),
        ("Con Mayusculas", skill("Con Mayusculas"), "solo admite minúsculas, números y guiones"),
        ("sin-cabecera", "# solo texto\n", "falta el bloque de metadatos"),
    ):
        destino = kit / "catalogo/skills" / carpeta / "SKILL.md"
        destino.parent.mkdir()
        destino.write_text(texto, encoding="utf-8")
        contiene(correr(["python3", "scripts/catalogo.py", "--verificar"], kit, e.entorno, espera=1).salida, mensaje)
        destino.unlink()
        destino.parent.rmdir()
    (kit / "catalogo/skills/vacia").mkdir()
    contiene(correr(["python3", "scripts/catalogo.py", "--verificar"], kit, e.entorno, espera=1).salida, "falta SKILL.md")


@prueba("sin perfil llegan las tres skills de siempre; con perfil, solo las que nombra, y las demás se retiran")
def solo_las_del_perfil(e):
    p = e.proyecto()
    afirmar(instaladas(p) == list(DE_SIEMPRE), f"sin perfil deben llegar las tres de siempre: {instaladas(p)}")
    manifiesto = json.loads(p.leer(".kit-manifest.json"))["archivos"]
    for nombre in DE_SIEMPRE:
        afirmar(f".agents/skills/{nombre}/SKILL.md" in manifiesto, f"{nombre} no quedó registrada como archivo del kit")
        afirmar(p.existe(f".claude/skills/{nombre}/SKILL.md"), f"{nombre} no llegó a Claude Code")
    afirmar(not p.existe("catalogo"), "el catálogo se copió a la raíz del proyecto")
    contiene(p.leer(".claude/agents/dev-backend.md"), "skills: go-backend, postgres-db\n", "el rol dev-backend sin perfil")
    r = p.make("skills")
    contiene(r.salida, "go-backend      probada    en el proyecto")
    contiene(r.salida, "sin perfil, las de siempre")

    # El proyecto tiene además una skill propia, que el perfil también nombra.
    p.escribir(".agents/skills/pagos/SKILL.md", skill("pagos", None))
    perfil_con(p, ["go-backend", "pagos"], roles=["dev-backend"])
    r = p.make("instalar-kit")
    afirmar(instaladas(p) == ["go-backend", "pagos"], f"con perfil deben quedar solo las que nombra: {instaladas(p)}")
    contiene(r.salida, ".agents/skills/react-frontend/SKILL.md")
    afirmar("«pagos»" not in r.salida, "avisó de una skill propia del proyecto, que sí existe")
    for nombre in ("postgres-db", "react-frontend"):
        afirmar(not p.existe(f".claude/skills/{nombre}"), f"{nombre} sigue en Claude Code después de retirarla")
    afirmar(p.existe(".claude/skills/pagos/SKILL.md"), "la skill propia no llegó a Claude Code")
    # Cada rol recibe las skills de su parte, y ninguno conserva una que el proyecto ya no tiene.
    contiene(p.leer(".claude/agents/dev-backend.md"), "skills: go-backend, pagos\n", "el rol dev-backend")
    afirmar("\nskills:" not in p.leer(".claude/agents/dev-frontend.md"), "dev-frontend declara una skill que se retiró")
    afirmar("react-frontend` (en" not in p.leer(".opencode/agents/dev-frontend.md"), "dev-frontend de OpenCode nombra la skill retirada")
    p.verificar_kit()
    p.correr("python3", "scripts/sincronizar.py", "--verificar")
    p.commit("chore: perfil del proyecto", extra=APROBADO)
    afirmar(not p.pendientes(), f"quedaron archivos sin commit: {p.pendientes()}")
    contiene(p.make("instalar-kit").salida, "Sin cambios: el proyecto ya estaba al día.")
    contiene(p.make("skills").salida, "react-frontend  probada    —")

    # Skills en un rol, y un perfil sin ninguna skill.
    perfil_con(p, [], roles=[{"rol": "dev-frontend", "skills": ["react-frontend"]}])
    p.make("instalar-kit")
    afirmar(instaladas(p) == ["pagos", "react-frontend"], f"no tomó la skill nombrada en un rol: {instaladas(p)}")
    perfil_con(p, [])
    p.make("instalar-kit")
    afirmar(instaladas(p) == ["pagos"], f"un perfil sin skills debe dejar solo las propias: {instaladas(p)}")


@prueba("cambiar las skills del perfil sin instalar se detecta: make profile lo avisa y el commit se rechaza")
def perfil_cambia_las_skills(e):
    p = e.proyecto()
    perfil_con(p, ["go-backend"])
    # Sobran dos: el proyecto todavía tiene las tres de siempre.
    r = p.verificar_kit(espera=1)
    contiene(r.salida, f"Las skills instaladas no son las que pide el perfil ({PERFIL}). Ejecuta: make instalar-kit")
    contiene(r.salida, "react-frontend: sobra")
    afirmar("go-backend:" not in r.salida, "marcó como pendiente una skill que está y se pide")
    contiene(p.commit("chore: perfil", espera=1, extra=APROBADO).salida, "Los archivos del kit no coinciden")
    p.make("instalar-kit")
    p.commit("chore: perfil", extra=APROBADO)

    # Falta una: el perfil la nombra y está en el catálogo.
    perfil_con(p, ["go-backend", "postgres-db"])
    contiene(p.make("profile").salida, "la skill «postgres-db» está en el catálogo del kit pero todavía no en el proyecto")
    contiene(p.verificar_kit(espera=1).salida, "postgres-db: falta")
    p.commit("chore: suma postgres", espera=1, extra=APROBADO)
    p.make("instalar-kit")
    afirmar("«postgres-db»" not in p.make("profile").salida, "sigue avisando de una skill ya instalada")
    p.commit("chore: suma postgres", extra=APROBADO)

    # Una skill del kit editada en el proyecto y que el perfil deja de nombrar: se conserva y se avisa.
    p.agregar(".agents/skills/postgres-db/SKILL.md", "\nRegla propia.\n")
    perfil_con(p, ["go-backend"])
    contiene(p.make("instalar-kit").salida, "tienen cambios locales; se conservaron")
    afirmar(p.existe(".agents/skills/postgres-db/SKILL.md"), "se borró una skill con cambios locales")


@prueba("una skill que no existe se avisa, una solo redactada se advierte al llegar, y un perfil ilegible no retira nada")
def avisos_del_catalogo(e):
    kit = e.kit()
    (kit / "catalogo/skills/php").mkdir()
    (kit / "catalogo/skills/php/SKILL.md").write_text(skill("php"), encoding="utf-8")
    (kit / "catalogo/skills/php/referencias").mkdir()
    (kit / "catalogo/skills/php/referencias/errores.md").write_text("# Errores\n", encoding="utf-8")
    e.commit_kit(kit, "skill php, solo redactada")
    p = e.proyecto(kit)
    afirmar(not p.existe(".agents/skills/php"), "llegó una skill del catálogo que nadie pidió")

    perfil_con(p, ["php", "cobol"])
    d = json.loads(p.make("profile", "DETECTAR=1").salida)
    afirmar({"php", "go-backend"} <= set(d["skills_disponibles"]), f"la detección no ofrece el catálogo: {d['skills_disponibles']}")
    afirmar(d["madurez_de_las_skills_del_catalogo"].get("php") == "redactada", "la detección no informa la madurez")
    contiene(p.make("profile").salida, "la skill «cobol» no está en .agents/skills/ ni en el catálogo del kit")
    r = p.make("instalar-kit")
    contiene(r.salida, "El perfil pide la skill «cobol», que no está en el catálogo del kit")
    contiene(r.salida, "La skill «php» está solo redactada")
    afirmar("«go-backend» está" not in r.salida and "«php», que no está" not in r.salida, "avisos de más")
    afirmar(p.existe(".agents/skills/php/referencias/errores.md"), "no llegaron los archivos de apoyo de la skill")
    afirmar(instaladas(p) == ["php"], f"skills inesperadas: {instaladas(p)}")
    contiene(p.make("skills").salida, "php             redactada  en el proyecto")
    contiene(p.make("skills").salida, "el perfil pide la skill «cobol»")
    r = p.make("instalar-kit")
    afirmar("solo redactada" not in r.salida, "repite la advertencia de madurez en cada instalación")
    contiene(r.salida, "«cobol»")
    p.commit("chore: perfil con php", extra=APROBADO)

    # Con un perfil que no se puede leer no se sabe qué pide el proyecto: todo queda como estaba.
    p.escribir(PERFIL, "{ esto no es json")
    r = p.make("instalar-kit")
    contiene(r.salida, f"{PERFIL} no se puede leer: las skills del catálogo se dejan como estaban")
    afirmar(instaladas(p) == ["php"], f"un perfil ilegible cambió las skills: {instaladas(p)}")

    # El proyecto se queda con su versión de una skill del catálogo.
    perfil_con(p, ["php"])
    config = json.loads(p.leer("equipo/config.json"))
    config.setdefault("kit", {})["excluir"] = [".agents/skills/php/"]
    p.escribir("equipo/config.json", json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    p.agregar(".agents/skills/php/SKILL.md", "\nRegla propia del proyecto.\n")
    p.make("instalar-kit")
    p.verificar_kit()
    contiene(p.leer(".agents/skills/php/SKILL.md"), "Regla propia del proyecto.", "la skill excluida")
    afirmar(p.existe(f"{SUBMODULO}/catalogo/skills/php/SKILL.md"), "el catálogo debe leerse desde el submódulo")
    afirmar(".agents/skills/php/SKILL.md" not in json.loads(p.leer(".kit-manifest.json"))["archivos"],
            "la skill excluida sigue registrada como del kit")
