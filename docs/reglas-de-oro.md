# Reglas de oro

- [Introducción](#introducción)
- [Las nueve reglas](#las-nueve-reglas)
- [Por qué cada una](#por-qué-cada-una)
- [Señales de alerta](#señales-de-alerta)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Nueve reglas para quien trabaja con el equipo de agentes. Son pocas a propósito: son las que, cuando se rompen, causan los problemas caros.

Varias están respaldadas por un control automático. Las demás dependen de ti, y por eso están aquí.

## Las nueve reglas

1. **Nunca apruebes lo que no leíste.** Tu aprobación es tu firma.
2. **Nunca uses `git commit --no-verify`,** ni permitas que el agente lo haga.
3. **Nunca pegues secretos** (contraseñas, claves, datos de clientes) en el chat del agente ni en archivos del repositorio.
4. **Nunca edites archivos generados** (`CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`). Cambia la fuente y ejecuta `make sincronizar`.
5. **Nunca modifiques una migración ya aplicada.** Se crea una nueva.
6. **No aceptes pruebas desactivadas o debilitadas** para que "pase el CI".
7. **Ante la duda, pregunta:** al cliente si es de negocio, a alguien con más experiencia si es técnica.
8. **Si el agente se atasca o da vueltas, detenlo.** Una instrucción más precisa vale más que diez intentos.
9. **Reporta lo que se repite.** Si un error de los agentes aparece varias veces, es una mejora pendiente en una skill o en la constitución.

## Por qué cada una

| Regla | Qué pasa si se rompe | ¿Hay un control? |
|---|---|---|
| 1. No aprobar sin leer | Todo el proceso descansa en que las aprobaciones significan algo. Una aprobación sin leer convierte las suposiciones del agente en decisiones tuyas | No. Depende de ti |
| 2. No usar `--no-verify` | Se saltan los controles locales, y el problema reaparece en GitHub, más tarde y a la vista de todos | La integración continua repite las comprobaciones |
| 3. No pegar secretos | Lo que se escribe en un chat puede quedar en registros; lo que entra a git queda en el historial para siempre | Los hooks y la búsqueda de secretos detectan los archivos. **El chat no lo vigila nadie** |
| 4. No editar generados | El siguiente `make sincronizar` borra el cambio, y mientras tanto los agentes trabajan con instrucciones inconsistentes | El hook de git y la integración continua |
| 5. No modificar migraciones | Las bases de datos donde ya se aplicó quedan distintas al código, sin forma automática de arreglarlo | Los hooks del agente, el hook de git y la integración continua |
| 6. No debilitar pruebas | La prueba detectaba un problema real. Desactivarla esconde el problema, no lo resuelve | No del todo. El revisor lo busca, pero la decisión final es tuya al aprobar |
| 7. Preguntar ante la duda | Una duda de negocio sin resolver se convierte en una regla inventada. Una duda técnica, en un plan aprobado sin entenderlo | No |
| 8. Detener al agente que se atasca | Cada intento fallido consume presupuesto y suele dejar el código peor que antes | El orquestador se detiene solo tras tres ciclos de corrección |
| 9. Reportar lo que se repite | El mismo error se corrige a mano una y otra vez, en lugar de una sola vez en la skill | No |

## Señales de alerta

Frases de un agente que justifican detenerlo y mirar qué está haciendo:

| Si el agente dice… | Lo que suele estar pasando |
|---|---|
| "Voy a desactivar esta prueba temporalmente" | No encontró la causa del fallo |
| "Lo arreglo con `--no-verify` y después lo corrijo" | Después no llega |
| "Voy a ajustar la prueba para que refleje el comportamiento actual" | Puede ser legítimo, o puede estar adaptando la prueba al error. Pregunta cuál de los dos tiene razón: la prueba o el código |
| "Para simplificar, voy a asumir que…" | Está inventando una regla de negocio |
| "Ya que estoy, voy a mejorar también…" | Se está saliendo del alcance |
| "Intento otra vez con otro enfoque", por tercera vez | Le falta información. Detenlo y dásela |
| "Edito este archivo directamente para que coincida" | Si es un archivo generado o del kit, está esquivando un control |

Y una tuya: si te descubres aprobando porque "seguro está bien", o porque revisar bien llevaría demasiado, la funcionalidad es más grande de lo que debería. Pide dividirla.

## Siguientes pasos

- [Aprobaciones](aprobaciones.md): qué leer antes de firmar.
- [Capas de control](capas-de-control.md): las reglas que sí tienen un control automático.
- [El orquestador](el-orquestador.md#lo-que-nunca-hace): las reglas que cumple el propio agente.
