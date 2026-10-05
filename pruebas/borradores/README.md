# Borradores de pruebas

Scripts usados **a mano** para validar las versiones 1.6.2 a 1.8.0 del kit. No son la suite de pruebas: son su materia prima. Convertirlos en un comando único es la etapa 0 de la [hoja de ruta](../../HOJA-DE-RUTA.md).

Se ejecutan en Linux o WSL, desde la raíz del repositorio del kit. Cada uno instala el kit en una carpeta temporal y la borra al terminar.

| Script | Qué comprueba |
|---|---|
| `actualizacion-y-hooks.sh` | Instalar la versión de `HEAD`, actualizar al árbol de trabajo con el `Makefile` viejo, permisos de los hooks y rechazo de un commit con mensaje inválido |
| `costos-opencode-simulado.sh` | `make costos` con un OpenCode simulado en formato 1.x y 2.x: mismos totales, sin duplicar al repetir, aviso si no hay sesiones |
| `generados-y-cobertura.sh` | `make generar`, `make verificar-generados` (con `sqlc` real) y `make cobertura` (con Go real), en los casos que deben pasar y los que deben fallar |
| `documentacion-y-constitucion.sh` | Actualización que retira archivos del proyecto, mensajes de `make doctor` y del pre-commit, y protección de la constitución |
| `proyecto-existente.sh` | Instalar el kit sobre un proyecto que ya tiene `Makefile`, `AGENTS.md` y `ci.yml` propios: qué se reemplaza y qué se respeta |
| `enlaces.py` | Enlaces internos de la documentación con las reglas de GitHub. Con `--externos`, también los enlaces a otros sitios |

Limitaciones conocidas, a resolver en la etapa 0:

- Comparan `HEAD` contra el árbol de trabajo, así que solo sirven mientras hay cambios sin commit.
- Algunos necesitan `go`, `sqlc`, `node` o `PyYAML` instalados, y no lo comprueban antes.
- No tienen un resultado único: hay que leer la salida.
- `PROYECTO_REAL=<ruta>` activa una comprobación opcional contra un clon limpio de un proyecto real.
