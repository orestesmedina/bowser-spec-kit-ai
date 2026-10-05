# Cómo contribuir

- [Introducción](#introducción)
- [Cómo está organizado el kit](#cómo-está-organizado-el-kit)
- [Qué cambiar según lo que quieras lograr](#qué-cambiar-según-lo-que-quieras-lograr)
- [Reglas para cada cambio](#reglas-para-cada-cambio)
- [Probar un cambio](#probar-un-cambio)
- [Publicar una versión](#publicar-una-versión)
- [Usar tu propia copia del kit](#usar-tu-propia-copia-del-kit)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página es para quien quiere **cambiar el kit**: corregir un error, agregar un control, ajustar un rol o adaptarlo a otro equipo. Los cambios se hacen en el repositorio del kit, nunca dentro de un proyecto, y llegan a los proyectos cuando estos actualizan.

## Cómo está organizado el kit

El repositorio tiene dos clases de archivos:

| Clase | Archivos | Regla |
|---|---|---|
| **Fuentes** | `AGENTS.md`, `equipo/orquestador.md`, `equipo/agentes/`, `equipo/config.json`, `.agents/skills/`, `.specify/memory/constitution.md`, `scripts/`, `.githooks/`, `.github/`, `Makefile`, `docs/` | Se editan a mano |
| **Solo del kit** | `pruebas/`, `kit.mk`, `.github/workflows/kit.yml` | Se editan a mano. No llegan a los proyectos |
| **Generados** | `CLAUDE.md`, `.claude/`, `.codex/`, `.opencode/`, `opencode.json` | Nunca se editan. Se regeneran con `make sincronizar` |

Qué llega a los proyectos lo decide `scripts/instalar_kit.py`, en dos listas: los archivos **gestionados** (se reemplazan en cada actualización) y las **semillas** (se copian una sola vez). Un archivo nuevo que deba llegar a los proyectos tiene que estar en una de las dos. La explicación completa está en [El kit como submódulo](submodulo.md).

## Qué cambiar según lo que quieras lograr

| Quieres… | Cambia |
|---|---|
| Que los agentes dejen de repetir un error de código | La skill del stack correspondiente, en `.agents/skills/` |
| Cambiar cómo se ejecuta un flujo (funcionalidad, bug, revisión) | La skill `equipo-*` correspondiente |
| Cambiar qué hace o qué puede tocar un rol | `equipo/agentes/<rol>.md` |
| Agregar un rol | Un archivo nuevo en `equipo/agentes/` |
| Cambiar cómo coordina el orquestador | `equipo/orquestador.md` y `AGENTS.md` |
| Que algo no pueda pasar nunca | `.githooks/pre-commit` **y** `.github/workflows/ci.yml` |
| Cambiar una regla del código | La constitución. Es la decisión más pesada: afecta a todos los proyectos |
| Soportar otro agente de código | Una función `generar_<herramienta>` en `scripts/sincronizar.py` |
| Agregar un comando | El `Makefile` y, si hace falta, un script en `scripts/` |
| Agregar un comando que solo sirve para mantener el kit | `kit.mk`, que no se copia a los proyectos |

## Reglas para cada cambio

1. **Registro de cambios y versión, siempre.** Cada cambio agrega una entrada en `CHANGELOG.md` (Agregado, Cambiado o Corregido) y sube el número en `VERSION`. Si un proyecto debe hacer algo a mano, va en una sección **Al actualizar**.
2. **Documentación al día.** Si cambia cómo se usa algo, cambia su página en `docs/`.
3. **Regenerar.** Después de tocar una fuente: `make sincronizar`. El comando `python3 scripts/sincronizar.py --verificar` debe dar OK.
4. **Solo biblioteca estándar.** Los scripts usan Python 3.9 o superior sin instalar nada, y bash portable. Tienen que correr en cualquier máquina del equipo.
5. **Compatibilidad con la versión anterior.** `make actualizar-kit` se ejecuta con el `Makefile` viejo del proyecto; el nuevo recién queda instalado al terminar. Todo comando nuevo debe funcionar bien en ese primer paso.
6. **Las semillas no se sobrescriben.** Si el kit cambia algo de una semilla, se ofrece un comando explícito que muestre las diferencias y pida confirmación, como `make actualizar-modelos`.
7. **Documentos y mensajes en español; nombres de comandos en inglés.** Los comandos actuales de `make` siguen en español hasta la versión 2.0; todo comando nuevo nace en inglés.
8. **Scripts ejecutables.** Un hook o un `.sh` nuevo debe guardarse en git con permiso de ejecución; sin él, git lo ignora sin avisar.

## Probar un cambio

El kit tiene pruebas automáticas. En Linux o WSL, desde la raíz del repositorio del kit:

```bash
make test-kit
```

Instalan el kit en proyectos temporales, lo actualizan desde la versión anterior publicada y comprueban que los controles sigan bloqueando lo que deben bloquear. Prueban la carpeta de trabajo tal como está: no hace falta hacer commit antes. Tardan cerca de un minuto.

```text
Pruebas del kit 1.10.0 · actualización desde v1.9.0

nucleo/repositorio
  ✓ los archivos generados del kit (CLAUDE.md, .claude/, .codex/, .opencode/) están al día  (0.2 s)
  ✓ VERSION tiene su entrada en el CHANGELOG y es la más reciente  (0.0 s)
  …
nucleo/costos
  ✓ make costos con OpenCode 1.x y 2.x: mismos totales, subagente enlazado y sin duplicar al repetir  (2.4 s)
  …
go/cobertura
  ✓ make cobertura con Go real: falla con pruebas insuficientes y pasa al completarlas  (12.7 s)

Resultado: 32 pasaron, 0 fallaron, 0 omitidas · 58 s
✓ Todo pasó.
```

Cuando una prueba falla, muestra qué esperaba y qué obtuvo:

```text
  ✗ el mensaje de commit debe seguir Conventional Commits
      «git commit -m mensaje malo» debía fallar y terminó bien:
      [main 5b98bf6] mensaje malo
```

Para repetir solo esa prueba, `make test-kit SOLO=Conventional`. Con `CONSERVAR=1` la carpeta temporal no se borra y se puede entrar a mirar el proyecto.

Si tu cambio agrega o cambia un comportamiento, agrega su prueba. Las opciones, la lista de lo que se comprueba y cómo escribir una prueba están en [`pruebas/README.md`](../pruebas/README.md).

Las pruebas de código generado y de cobertura necesitan `go`, `sqlc`, `node` y `npm`. Si falta alguno, esas pruebas se omiten y el resultado lo dice:

```text
  – make cobertura con Go real: falla con pruebas insuficientes y pasa al completarlas
      omitida: falta go en esta máquina
```

En GitHub las mismas pruebas corren solas en cada Pull Request y en cada push a `main` (workflow `kit.yml`), con todo instalado y sin permitir pruebas omitidas.

> [!WARNING]
> Las pruebas no lo cubren todo. `make doctor`, `make estado` y `make actualizar-modelos` todavía se prueban a mano, y `make costos` se prueba contra un OpenCode simulado.

> [!NOTE]
> Lo que cambia en `.github/workflows/ci.yml` solo se prueba de verdad en GitHub. Valida el cambio en un proyecto real antes de darlo por bueno.

## Publicar una versión

```bash
git commit -m "feat: descripción del cambio"
git tag v1.8.0
git push origin main --tags
```

> [!WARNING]
> `git push --follow-tags` no sirve aquí: solo sube los tags anotados (`git tag -a`), y `git tag v1.8.0` crea uno simple. Sin los tags en GitHub, las pruebas del kit fallan ahí, porque la prueba de actualización parte del último tag publicado. Para comprobar que subieron: `git ls-remote --tags origin`.

Los proyectos reciben la versión cuando ejecutan `make actualizar-kit`, y ven en ese momento las novedades y los pasos manuales.

## Usar tu propia copia del kit

El kit se publica con licencia MIT: puedes copiarlo, modificarlo y usarlo en tus proyectos. Si tu equipo necesita reglas, modelos o un stack distintos, lo natural es mantener una copia propia:

1. Crea un fork del repositorio.
2. Ajusta la constitución, las skills del stack, `equipo/config.json` y `.github/CODEOWNERS`.
3. En tus proyectos, agrega tu copia como submódulo en lugar del original.

Lo que distingue al kit de la forma en que lo usa cada equipo:

| Es del kit | Es de cada equipo |
|---|---|
| El proceso por fases y las puertas de aprobación | La constitución: qué reglas son no negociables |
| Los roles y qué puede tocar cada uno | Qué modelo usa cada rol |
| La instalación, el estado del trabajo y los costos | El stack y sus convenciones |
| Los controles y cómo se aplican | Quién aprueba los cambios a las reglas |

## Siguientes pasos

- [Manual de mantenimiento](../MANTENER-KIT.md): el contexto, las decisiones de diseño y los hechos verificados que usa quien mantiene el kit.
- [Novedades de cada versión](../CHANGELOG.md).
- [Hoja de ruta](../HOJA-DE-RUTA.md): hacia dónde va el kit y qué etapa sigue.
- [Una fuente, varias herramientas](una-fuente-varias-herramientas.md): cómo funciona el generador.
