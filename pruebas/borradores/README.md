# Borradores de pruebas

Scripts usados **a mano** para validar versiones anteriores del kit y que todavía no se convirtieron en pruebas automáticas. Los demás borradores ya son parte de [las pruebas del kit](../README.md) (versión 1.9.0).

| Script | Qué comprueba | Qué falta |
|---|---|---|
| `generados-y-cobertura.sh` | `make generar`, `make verificar-generados` (con `sqlc` real) y `make cobertura` (con Go real), en los casos que deben pasar y los que deben fallar | Pasarlo a un grupo de pruebas de Go, separado del núcleo. Es la segunda entrega de la etapa 0 de la [hoja de ruta](../../HOJA-DE-RUTA.md) |

Se ejecuta en Linux o WSL, desde la raíz del repositorio del kit. Necesita `go`, `sqlc` y `node` instalados, y no lo comprueba antes. No da un resultado único: hay que leer la salida.
