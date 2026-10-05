"""make cobertura: cobertura de la capa de servicio del backend, con el mínimo de la constitución."""
from apoyo import afirmar, contiene, prueba

MODULO = "ejemplo/backend/internal"
BAJO = "por debajo del mínimo 80 %"
CUMPLE = "✓ Cumple el mínimo."

SERVICIO = """\
package users

func Suma(a, b int) int { return a + b }

func Signo(n int) string {
	if n < 0 {
		return "negativo"
	}
	if n == 0 {
		return "cero"
	}
	return "positivo"
}
"""
PRUEBA_SUMA = """\
package users

import "testing"

func TestSuma(t *testing.T) {
	if Suma(1, 2) != 3 {
		t.Fatal("suma")
	}
}
"""
PRUEBA_SIGNO = """
func TestSigno(t *testing.T) {
	for n, quiere := range map[int]string{-1: "negativo", 0: "cero", 1: "positivo"} {
		if Signo(n) != quiere {
			t.Fatalf("signo %d", n)
		}
	}
}
"""


def medir(p, bloques: list[str], espera: int = 0):
    """Ejecuta cobertura.py sobre un perfil de Go escrito a mano (archivo:rango sentencias veces)."""
    p.escribir("perfil.out", "mode: set\n" + "".join(b + "\n" for b in bloques))
    return p.correr("python3", "scripts/cobertura.py", "perfil.out", espera=espera)


@prueba("cobertura.py: mide solo los archivos de servicio y falla por debajo del 80 %")
def perfil_a_mano(e):
    p = e.proyecto()
    servicio = [f"{MODULO}/users/service.go:3.1,4.2 4 1", f"{MODULO}/users/service.go:6.1,7.2 1 0"]

    r = medir(p, servicio)
    contiene(r.salida, "4/5")
    contiene(r.salida, "80.0 %")
    contiene(r.salida, CUMPLE)

    # Lo que no es de la capa de servicio no cuenta, aunque no tenga ninguna prueba.
    otros = [f"{MODULO}/users/handler.go:3.1,9.2 50 0", f"{MODULO}/users/service_test.go:3.1,9.2 50 0",
             "ejemplo/backend/cmd/service.go:3.1,9.2 50 0"]
    r = medir(p, servicio + otros)
    contiene(r.salida, CUMPLE)
    afirmar("handler.go" not in r.salida and "cmd/" not in r.salida, f"midió archivos que no son de servicio:\n{r.salida}")

    # Varios dominios se suman: 4 de 7 sentencias.
    r = medir(p, servicio + [f"{MODULO}/orders/service_pagos.go:3.1,4.2 2 0"], espera=1)
    contiene(r.salida, "orders/service_pagos.go")
    contiene(r.salida, "57.1 %")
    contiene(r.salida, BAJO)

    # Un bloque repetido (perfiles unidos) cuenta una sola vez, y basta que una de las veces esté cubierto.
    r = medir(p, servicio + [f"{MODULO}/users/service.go:6.1,7.2 1 1"])
    contiene(r.salida, "5/5")

    contiene(medir(p, otros[:1]).salida, "nada que medir")
    contiene(p.correr("python3", "scripts/cobertura.py", "no-existe.out", espera=1).salida, "No se pudo leer no-existe.out")


@prueba("make cobertura con Go real: falla con pruebas insuficientes y pasa al completarlas", requiere=("go",))
def cobertura_real(e):
    p = e.proyecto()
    p.escribir("backend/go.mod", "module ejemplo/backend\n\ngo 1.26\n")
    p.escribir("backend/internal/users/service.go", SERVICIO)
    p.escribir("backend/internal/users/service_test.go", PRUEBA_SUMA)
    p.commit("feat: servicio de usuarios")

    r = p.make("cobertura", espera=1)
    contiene(r.salida, "users/service.go")
    contiene(r.salida, "1/6")
    contiene(r.salida, BAJO)

    p.agregar("backend/internal/users/service_test.go", PRUEBA_SIGNO)
    r = p.make("cobertura")
    contiene(r.salida, "6/6")
    contiene(r.salida, CUMPLE)

    p.commit("test: completa las pruebas del servicio")
    afirmar(not p.pendientes(), f"backend/coverage.out debería estar ignorado por git: {p.pendientes()}")
