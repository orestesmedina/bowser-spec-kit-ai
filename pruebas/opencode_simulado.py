#!/usr/bin/env python3
"""OpenCode simulado para probar make costos sin gastar ni depender de una sesión real.

Las pruebas lo copian a una carpeta del PATH con el nombre `opencode`. Imita lo que el kit usa de OpenCode
(formatos verificados el 2026-10-03, ver MANTENER-KIT.md):
  1.x: --version · session list --format json · export <id>
  2.x: --version · session list --format json [--standalone] · session export <id>

Hay una sesión raíz "ses_raiz" (orquestador, dos respuestas) con un subagente "ses_hija" (seguridad, una).
El consumo es el mismo en los dos formatos: los totales deben coincidir.

Variables: FALSO_VERSION=1|2 · FALSO_AHORA=<milisegundos> (fijo entre llamadas, como en el OpenCode real) ·
FALSO_SIN_SESIONES=1 (no devuelve ninguna sesión).
"""
import json
import os
import sys

v = os.environ.get("FALSO_VERSION", "1")
a = sys.argv[1:]
ahora = int(os.environ["FALSO_AHORA"])


def tok(entrada, salida, razonamiento, cache):
    return {"input": entrada, "output": salida, "reasoning": razonamiento, "cache": {"read": cache, "write": 0}}


RAIZ = [("orquestador", "deepseek-v4.1-flash", tok(1000, 500, 100, 20000), 0.01),
        ("orquestador", "deepseek-v4.1-flash", tok(2000, 300, 0, 50000), 0.02)]
HIJA = [("seguridad", "glm-5.3", tok(4000, 1000, 200, 10000), 0.05)]
RELLENO = "x" * 400000   # export grande: en 2.x una tubería lo cortaría


def exportar(sid):
    datos, hija = (RAIZ, "ses_hija") if sid == "ses_raiz" else (HIJA, None)
    if v == "1":
        ms = [{"info": {"role": "user", "time": {"created": ahora - 5000}}, "parts": [{"type": "text", "text": RELLENO}]}]
        for n, (agente, modelo, tokens, costo) in enumerate(datos):
            ms.append({"info": {"role": "assistant", "agent": agente, "providerID": "opencode-go", "modelID": modelo,
                                "time": {"created": ahora - 4000 + n}, "cost": costo, "tokens": tokens}, "parts": []})
        if hija:
            ms[-1]["parts"].append({"type": "tool", "tool": "task", "state": {"metadata": {"sessionId": hija}}})
    else:
        ms = [{"type": "user", "time": {"created": ahora - 5000}, "text": RELLENO, "files": [], "agents": []}]
        for n, (agente, modelo, tokens, costo) in enumerate(datos):
            ms.append({"type": "assistant", "agent": agente, "model": {"id": modelo, "providerID": "opencode-go", "variant": "default"},
                       "time": {"created": ahora - 4000 + n}, "cost": costo, "tokens": tokens, "content": []})
        if hija:
            ms[-1]["content"].append({"type": "tool", "name": "subagent", "state": {"metadata": {"sessionID": hija}}})
            ms.append({"type": "synthetic", "metadata": {"source": "subagent", "childID": hija}, "time": {"created": ahora}})
    return {"info": {"id": sid, "title": "prueba"}, "messages": ms}


if a == ["--version"]:
    print("1.18.33" if v == "1" else "opencode v2.0.22")
elif a[:2] == ["session", "list"]:
    lista = [{"id": "ses_raiz", "title": "prueba", "updated": ahora, "created": ahora - 6000, "projectId": "p", "directory": os.getcwd()}]
    if os.environ.get("FALSO_SIN_SESIONES") or (v == "2" and "--standalone" not in a):
        lista = []          # el servicio en segundo plano de 2.x devuelve vacío aunque haya sesiones
    print(json.dumps(lista) if (lista or v == "2") else "", end="")
elif (v == "1" and a[:1] == ["export"]) or (v == "2" and a[:2] == ["session", "export"]):
    if v == "1":
        print("Exporting session...", file=sys.stderr)
    print(json.dumps(exportar(a[-1])))
else:
    print("ERROR Unexpected positional argument", file=sys.stderr)
    sys.exit(1)
