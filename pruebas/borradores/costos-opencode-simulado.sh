#!/usr/bin/env bash
# make costos con un OpenCode simulado, en formato 1.x y 2.x. Mismo consumo en ambos: los totales deben coincidir.
set -euo pipefail
ORIGEN=${ORIGEN:-$(git rev-parse --show-toplevel)}
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=protocol.file.allow GIT_CONFIG_VALUE_0=always \
       GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1='*'
export GIT_AUTHOR_NAME=prueba GIT_AUTHOR_EMAIL=prueba@example.com GIT_COMMITTER_NAME=prueba GIT_COMMITTER_EMAIL=prueba@example.com
T=$(mktemp -d)
mkdir "$T/kit" "$T/bin"
cp "$ORIGEN/.git/index" "$T/indice"
ARBOL=$(cd "$ORIGEN" && GIT_INDEX_FILE="$T/indice" git add -A 2>/dev/null && GIT_INDEX_FILE="$T/indice" git write-tree)
git -C "$ORIGEN" archive "$ARBOL" | tar -x -C "$T/kit"
(cd "$T/kit" && git init -q && git add -A && git commit -qm kit --no-verify)

cat > "$T/precios.json" <<'EOF'
{"opencode-go": {"models": {
  "deepseek-v4.1-flash": {"cost": {"input": 0.15, "output": 0.60, "cache_read": 0.003}},
  "glm-5.3": {"cost": {"input": 1.0, "output": 3.0, "cache_read": 0.1}}}}}
EOF

# OpenCode simulado. FALSO_VERSION=1|2. Sesión raíz "ses_raiz" (orquestador) con un subagente "ses_hija" (seguridad).
cat > "$T/bin/opencode" <<'EOF'
#!/usr/bin/env python3
import json, os, sys, time
v = os.environ.get("FALSO_VERSION", "1"); a = sys.argv[1:]; cwd = os.getcwd()
ahora = int(os.environ["FALSO_AHORA"])   # fijo: como en el OpenCode real, las horas no cambian entre llamadas
tok = lambda i, o, r, cr: {"input": i, "output": o, "reasoning": r, "cache": {"read": cr, "write": 0}}
RAIZ = [("orquestador", "deepseek-v4.1-flash", tok(1000, 500, 100, 20000), 0.01), ("orquestador", "deepseek-v4.1-flash", tok(2000, 300, 0, 50000), 0.02)]
HIJA = [("seguridad", "glm-5.3", tok(4000, 1000, 200, 10000), 0.05)]
relleno = "x" * 400000   # export grande: en 2.x una tubería lo cortaría
def exportar(sid):
    datos, hija = (RAIZ, "ses_hija") if sid == "ses_raiz" else (HIJA, None)
    if v == "1":
        ms = [{"info": {"role": "user", "time": {"created": ahora - 5000}}, "parts": [{"type": "text", "text": relleno}]}]
        for n, (ag, mo, t, c) in enumerate(datos):
            ms.append({"info": {"role": "assistant", "agent": ag, "providerID": "opencode-go", "modelID": mo, "time": {"created": ahora - 4000 + n}, "cost": c, "tokens": t}, "parts": []})
        if hija: ms[-1]["parts"].append({"type": "tool", "tool": "task", "state": {"metadata": {"sessionId": hija}}})
    else:
        ms = [{"type": "user", "time": {"created": ahora - 5000}, "text": relleno, "files": [], "agents": []}]
        for n, (ag, mo, t, c) in enumerate(datos):
            ms.append({"type": "assistant", "agent": ag, "model": {"id": mo, "providerID": "opencode-go", "variant": "default"}, "time": {"created": ahora - 4000 + n}, "cost": c, "tokens": t, "content": []})
        if hija:
            ms[-1]["content"].append({"type": "tool", "name": "subagent", "state": {"metadata": {"sessionID": hija}}})
            ms.append({"type": "synthetic", "metadata": {"source": "subagent", "childID": hija}, "time": {"created": ahora}})
    return {"info": {"id": sid, "title": "prueba"}, "messages": ms}
if a == ["--version"]:
    print("1.18.33" if v == "1" else "opencode v2.0.22")
elif a[:2] == ["session", "list"]:
    lista = [{"id": "ses_raiz", "title": "prueba", "updated": ahora, "created": ahora - 6000, "projectId": "p", "directory": cwd}]
    if v == "2" and "--standalone" not in a: lista = []          # el servicio de 2.x devuelve vacío
    print(json.dumps(lista) if (lista or v == "2") else "", end="")
elif (v == "1" and a[:1] == ["export"]) or (v == "2" and a[:2] == ["session", "export"]):
    if v == "1": print("Exporting session...", file=sys.stderr)
    print(json.dumps(exportar(a[-1])))
else:
    print('ERROR Unexpected positional argument', file=sys.stderr); sys.exit(1)
EOF
chmod +x "$T/bin/opencode"
export PATH="$T/bin:$PATH" COSTOS_FUENTE_PRECIOS="$T/precios.json"

for V in 1 2; do
  echo "================ OpenCode simulado $V.x"
  P="$T/proy$V"; mkdir "$P" && cd "$P" && git init -q
  git submodule add -q "$T/kit" .bowser-spec-kit-ai
  make -f .bowser-spec-kit-ai/Makefile instalar-kit >/dev/null
  git add -A && git commit -qm "chore: instala kit"
  git checkout -q -b 001-prueba && mkdir -p specs/001-prueba && echo "# spec" > specs/001-prueba/spec.md
  export FALSO_VERSION=$V XDG_DATA_HOME="$T/datos$V" FALSO_AHORA=$(($(date +%s) * 1000))
  make costos
  echo "--- segunda vez (no debe duplicar)"; make costos | sed -n '1,3p;/Total/p;/⚠\|✓/p'
  python3 - <<'EOF'
import json
c = json.load(open("specs/001-prueba/costos.json")); t = c["totales"]
print("VERIFICACIÓN: sesiones", len(c["sesiones"]), "| tokens", t["tokens"], "| costo", t["costo"], "| según OpenCode", t["costo_opencode"],
      "| padres", sorted(str(s["padre"]) for s in c["sesiones"]))
assert len(c["sesiones"]) == 2 and t["tokens"] == 89100 and abs(t["costo_opencode"] - 0.08) < 1e-9, "totales inesperados"
EOF
done
echo "================ sin sesiones (2.x con otra carpeta): debe avisar"
cd "$T" && mkdir vacio && cd vacio && cp -r "$T/proy2/." . && XDG_DATA_HOME="$T/datos3" FALSO_VERSION=2 FALSO_AHORA=$(($(date +%s) * 1000)) PATH="$T/bin:$PATH" bash -c 'sed -i "s/lista = \[{/lista = [] if True else [{/" "'"$T"'/bin/opencode"; rm -f specs/001-prueba/costos.json; make costos'
rm -rf "$T"; echo "== FIN"
