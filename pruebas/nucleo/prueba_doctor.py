"""make doctor: las herramientas que el kit necesita siempre y las que el perfil del proyecto declara en «requisitos»."""
import json
import os
import re

from apoyo import afirmar, contiene, prueba

PERFIL = "equipo/perfil.json"


def con_perfil(e, requisitos=None):
    """Proyecto con el kit instalado y un perfil de una parte (sin commit: make doctor solo lee)."""
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    escribir_perfil(p, requisitos)
    return p


def escribir_perfil(p, requisitos=None) -> None:
    perfil = {"partes": [{"nombre": "api", "carpeta": "servidor", "roles": ["dev-backend"]}]}
    if requisitos is not None:
        perfil["requisitos"] = requisitos
    p.escribir(PERFIL, json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")


def programa(p, nombre: str, cuerpo: str) -> None:
    """Un programa falso en una carpeta que doctor() pone al inicio del PATH."""
    p.escribir(f"falsos/{nombre}", "#!/bin/sh\n" + cuerpo + "\n")
    p.archivo(f"falsos/{nombre}").chmod(0o755)


def doctor(p):
    """Su código de salida depende de la máquina (Spec Kit, hooks, .env…): se comprueban las líneas."""
    return p.make("doctor", espera=None, extra={"PATH": f"{p.ruta}/falsos:{os.environ['PATH']}"})


def linea(salida: str, texto: str) -> str:
    for l in salida.splitlines():
        if texto in l:
            return l
    contiene(salida, texto, "la salida de make doctor")
    return ""


def problemas(salida: str) -> int:
    m = re.search(r"Resultado: \d+ correctos, \d+ avisos, (\d+) problemas", salida)
    afirmar(m, f"make doctor no terminó con su resumen:\n{salida}")
    return int(m.group(1))


@prueba("make doctor: sin perfil revisa Go y Node; con perfil, solo lo que declara en «requisitos»; Docker, solo si hace falta")
def doctor_segun_el_perfil(e):
    p = e.proyecto()
    s = doctor(p).salida
    contiene(s, "Herramientas del proyecto (sin perfil: Go y Node)")
    contiene(s, "golangci-lint")
    # Un proyecto sin entorno local no necesita Docker.
    afirmar("Docker" not in s, f"make doctor revisa Docker en un proyecto sin archivo de Docker Compose:\n{s}")
    p.escribir("compose.yaml", "services: {}\n")
    s = doctor(p).salida
    contiene(s, "Docker")
    contiene(s, "corriendo")

    # Con perfil, lo de Go y Node deja de revisarse. Sin requisitos, se avisa.
    p = con_perfil(e)
    s = doctor(p).salida
    contiene(s, "Herramientas del proyecto (según su perfil)")
    afirmar("!" in linea(s, "El perfil no declara requisitos"), "la falta de requisitos no es un aviso")
    for sobra in ("golangci-lint", "Node.js", "sqlc", "Docker"):
        afirmar(sobra not in s, f"con perfil, make doctor sigue revisando {sobra}:\n{s}")
    afirmar("✓" in linea(s, "Git "), "con perfil no se revisan las herramientas base")

    programa(p, "mitool", 'echo "mitool 2.5.1"')
    programa(p, "viejo", '[ "$1" = version ] && echo "viejo 2.9"')
    escribir_perfil(p, ["mitool"])
    antes = problemas(doctor(p).salida)
    escribir_perfil(p, [
        "mitool",
        {"comando": "viejo", "nombre": "Viejo", "minima": "3.0", "version": "viejo version"},
        {"comando": "no-existe-uno", "nombre": "Falta", "instalar": "apt install falta"},
        {"comando": "no-existe-dos", "opcional": True},
    ])
    r = doctor(p)
    s = r.salida
    afirmar("no declara requisitos" not in s, "avisa de que no hay requisitos cuando sí los hay")
    afirmar("✓" in linea(s, "mitool 2.5.1"), "un requisito instalado no sale como correcto")
    afirmar("✗" in linea(s, "Viejo 2.9 (se requiere 3.0 o superior)"), "una versión menor que la mínima no es un problema")
    afirmar("✗" in linea(s, "Falta no está instalado. Se instala con: apt install falta"), "un requisito que falta no es un problema")
    afirmar("!" in linea(s, "no-existe-dos no está instalado (recomendado)"), "un requisito opcional que falta no es un aviso")
    afirmar(problemas(s) == antes + 2, f"los dos requisitos que fallan no se cuentan como problemas:\n{s}")
    afirmar(r.codigo != 0, "make doctor terminó bien aunque falta un requisito")
    contiene(p.make("profile").salida,
             "Requisitos de la máquina (los revisa make doctor): mitool  ·  Viejo 3.0 o superior  ·  Falta  ·  no-existe-dos (recomendado)")

    # Docker pedido por el perfil se revisa aunque no haya archivo de Docker Compose.
    afirmar("corriendo" not in s, "revisa si Docker corre sin que el proyecto lo use")
    escribir_perfil(p, ["mitool", {"comando": "docker", "nombre": "Docker"}])
    contiene(doctor(p).salida, "corriendo")


@prueba("requisitos mal escritos se rechazan con un mensaje que dice qué corregir, y make doctor lo marca")
def requisitos_invalidos(e):
    p = con_perfil(e)
    malos = [
        ("go", "\"requisitos\" debe ser una lista de programas"),
        ([{"comando": "go test"}], "\"comando\" debe ser el nombre de un programa"),
        ([{"nombre": "Go"}], "\"comando\" debe ser el nombre de un programa"),
        (["go", {"comando": "go"}], "el requisito «go» está dos veces"),
        ([{"comando": "go", "minima": 1.26}], "\"minima\" debe ser una versión entre comillas"),
        ([{"comando": "go", "version": "go version\nrm -rf"}], "\"version\" debe ser un texto de una sola línea"),
        ([{"comando": "go", "opcional": "sí"}], "\"opcional\" debe ser true o false"),
        ([{"comando": "go", "url": "https://go.dev"}], "campo desconocido «url»"),
    ]
    for requisitos, mensaje in malos:
        escribir_perfil(p, requisitos)
        contiene(p.make("profile", espera=1).salida, mensaje)
        s = doctor(p).salida
        afirmar("✗" in linea(s, "El perfil tiene errores"), "make doctor no marca un perfil inválido")
