# Retomar el trabajo

- [Introducción](#introducción)
- [Dónde vive el estado](#dónde-vive-el-estado)
- [Ver por dónde va el proyecto](#ver-por-dónde-va-el-proyecto)
- [Retomar una funcionalidad](#retomar-una-funcionalidad)
- [Dejar el trabajo](#dejar-el-trabajo)
- [Qué contiene estado.md](#qué-contiene-estadomd)
- [Cuando el estado no coincide con la realidad](#cuando-el-estado-no-coincide-con-la-realidad)
- [Funcionalidades sin estado.md](#funcionalidades-sin-estadomd)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Un agente de IA no recuerda la conversación de ayer. Si el trabajo dependiera de la memoria de una sesión, cada día habría que volver a explicar todo, y nadie más podría continuar lo que empezaste.

El kit lo resuelve guardando el estado del trabajo en **archivos dentro de git**. Cualquier sesión, cualquier día y cualquier persona puede saber en segundos dónde quedó todo.

## Dónde vive el estado

| Archivo | Qué dice | Quién lo mantiene |
|---|---|---|
| `docs/producto/roadmap.md` | El estado de cada funcionalidad del producto | El orquestador |
| `specs/<rama>/estado.md` | La fase, las aprobaciones, los hallazgos abiertos, las decisiones y el próximo paso de una funcionalidad | El orquestador |
| `specs/<rama>/tasks.md` | Qué tareas están hechas (`[X]`) y cuáles faltan | Los desarrolladores |
| `specs/<rama>/revision-*.md` | Lo que encontró la última validación | Los revisores |
| git | Qué se cambió, cuándo, y si quedó algo sin guardar | — |

## Ver por dónde va el proyecto

```bash
make estado
```

Muestra el roadmap, la funcionalidad de la rama actual con su fase y sus aprobaciones, las tareas hechas sobre el total, los hallazgos abiertos, el costo de IA acumulado y el próximo paso. No modifica nada.

Con `make estado TODO=1` incluye también las funcionalidades ya terminadas.

Desde la rama principal, además lista el **trabajo en otras ramas**: el roadmap de la rama principal solo se actualiza cuando una funcionalidad se integra, así que es la forma de ver lo que está en curso.

## Retomar una funcionalidad

1. Cámbiate a la rama de la funcionalidad y mira el estado:
   ```bash
   git checkout 003-registro-usuarios
   make estado
   ```
2. Abre el agente. El orquestador te dice dónde quedaron y pregunta si sigue. También puedes pedírselo:
   > ¿Por dónde quedamos?
3. **Confirma que el resumen es correcto** antes de que continúe.

El resumen tiene esta forma:

```
Quedamos en: 003-registro-usuarios · Fase 6/9 (implementar) · 7/12 tareas
Aprobados: spec y plan · Hallazgos abiertos: 0
Próximo paso: T008 [frontend] formulario de registro → dev-frontend. ¿Sigo?
```

Cuando confirmas, el orquestador continúa **desde esa fase**, sin repetir las ya cerradas.

> [!NOTE]
> Si al retomar falta una aprobación registrada, el orquestador te la va a pedir. Léela antes de darla: que el archivo exista no significa que alguien lo haya aprobado.

## Dejar el trabajo

Antes de cerrar, dile al orquestador:

> Lo dejamos por hoy.

Hace tres cosas: registra el costo de IA de la sesión, anota en `estado.md` el próximo paso concreto con una línea en la bitácora, y guarda ambos en un commit.

Si quedan cambios de código sin guardar, **te avisa** en lugar de guardarlos por su cuenta: un commit de trabajo a medias puede dejar la rama rota para quien la retome.

## Qué contiene estado.md

| Sección | Contenido |
|---|---|
| **Resumen** | Rama, flujo, fase actual (por ejemplo `6/9 · Implementar`), ciclo de corrección, próximo paso, si está bloqueado y por qué |
| **Aprobaciones** | Cada puerta con su estado y, si se aprobó, quién, cuándo y con qué frase |
| **Hallazgos abiertos** | Los bloqueantes de la última validación que aún no se corrigen |
| **Decisiones y aclaraciones** | Lo que se decidió en el chat y no está en la especificación ni en el plan |
| **Bitácora** | Una línea por sesión o hito, la más reciente arriba |

Lo escribe **solo el orquestador**; los demás agentes no lo tocan. Tú puedes corregirlo si ves algo mal.

La sección de decisiones es la que más se agradece semanas después: evita la pregunta "¿por qué hicimos esto así?".

## Cuando el estado no coincide con la realidad

Puede pasar que `estado.md` diga una cosa y los archivos otra. Por ejemplo, dice "fase 4" pero todas las tareas están marcadas como hechas, porque una sesión se cortó antes de actualizarlo.

La regla: **mandan los archivos y git**. El orquestador compara el estado con la evidencia (qué documentos existen, qué tareas están hechas, qué dice el historial de commits) y, si no coinciden, corrige `estado.md` y te explica qué ajustó.

Hay una excepción importante: **las aprobaciones nunca se deducen**. Que exista `plan.md` prueba que alguien lo escribió, no que alguien lo aprobó. Si una aprobación no consta, el orquestador pregunta.

`make estado` avisa de estas situaciones:

| Aviso | Qué significa |
|---|---|
| Un documento cambió después de `estado.md` | El estado probablemente quedó viejo |
| Aprobación no registrada | El trabajo avanzó a una fase que requería una aprobación que no consta |
| Cambios sin commit | Quedó trabajo sin guardar |

Y el [hook de git](hooks-de-git.md) avisa, sin bloquear, cuando un commit cambia la especificación, el plan o las tareas sin tocar `estado.md`.

Si quedaron cambios sin guardar de una sesión anterior, el orquestador no los descarta ni los guarda por su cuenta: te los muestra y pregunta qué hacer.

## Funcionalidades sin estado.md

Si una funcionalidad se empezó antes de usar este flujo, o el proyecto adoptó el kit con trabajo en curso, dile al orquestador:

> Retomemos.

Reconstruye el `estado.md` a partir de los archivos y de git, marca como `pendiente de confirmar` las aprobaciones que no consten y te pide confirmarlas una por una.

## Siguientes pasos

- [Construir una funcionalidad](funcionalidad.md): las fases a las que se refiere el estado.
- [Costos de IA](costos.md): el otro archivo que el orquestador mantiene en cada funcionalidad.
- [Comandos](comandos.md): `make estado` y el resto.
