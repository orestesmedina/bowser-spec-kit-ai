# Integración continua

- [Introducción](#introducción)
- [Para qué sirve en este kit](#para-qué-sirve-en-este-kit)
- [Dos workflows: el del kit y el del proyecto](#dos-workflows-el-del-kit-y-el-del-proyecto)
- [Cuándo se ejecuta](#cuándo-se-ejecuta)
- [Qué comprueba el workflow del kit](#qué-comprueba-el-workflow-del-kit)
- [El workflow del proyecto](#el-workflow-del-proyecto)
    - [Crearlo con `/bowser-ci`](#crearlo-con-bowser-ci)
    - [Qué forma tiene](#qué-forma-tiene)
    - [Comprobar que no falta nada](#comprobar-que-no-falta-nada)
- [Ejecutar lo mismo en tu máquina](#ejecutar-lo-mismo-en-tu-máquina)
- [Cuando falla](#cuando-falla)
- [Si vienes de una versión anterior](#si-vienes-de-una-versión-anterior)
- [Lo que no hace](#lo-que-no-hace)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

La integración continua (CI) es un conjunto de comprobaciones que **GitHub ejecuta por su cuenta** cada vez que alguien propone un cambio. Si alguna falla, el Pull Request queda marcado en rojo y no se puede integrar.

## Para qué sirve en este kit

Es la única capa de control que **no se puede saltar**. Los [hooks de git](hooks-de-git.md) corren en la máquina de quien hace el cambio, y esa persona (o ese agente) puede no tenerlos activos, o evitarlos con `--no-verify`. La integración continua corre en GitHub, fuera de su alcance.

Por eso repite lo que ya revisaron los hooks, y agrega lo que los hooks no hacen por ser lento: ejecutar todas las pruebas, medir la cobertura y buscar vulnerabilidades.

Para que tenga efecto, la rama principal debe estar protegida en GitHub, de modo que nada entre sin pasar por ella. Ver [Configuración](configuracion.md#configuración-en-github).

## Dos workflows: el del kit y el del proyecto

Instalar un lenguaje, levantar una base de datos o correr un linter depende de la tecnología de cada proyecto, y el kit no la dicta. Por eso la integración continua está en dos archivos:

| Archivo | De quién es | Qué trae |
|---|---|---|
| `.github/workflows/bowser.yml` | Del kit. Se reemplaza en cada actualización y no se edita | Los controles que valen para cualquier proyecto: archivos del kit, agentes y perfil al día, archivos inmutables, constitución y secretos |
| `.github/workflows/ci.yml` | Del proyecto. Se edita ahí | Lo que depende de la tecnología: instalar las herramientas de cada parte, levantar sus servicios y ejecutar sus [verbos](perfil-del-proyecto.md#los-verbos) |

El kit no instala ningún `ci.yml`. Lo redacta un agente a partir del [perfil del proyecto](perfil-del-proyecto.md), con el comando `/bowser-ci`, y lo aprueba una persona.

> [!NOTE]
> El nombre `ci.yml` es una costumbre, no una obligación. Cualquier archivo de `.github/workflows/` que no sea `bowser.yml` es del proyecto.

## Cuándo se ejecuta

- En cada **Pull Request**, y cada vez que se le agregan commits.
- En cada cambio que llega a la **rama principal**.

Si llega un commit nuevo mientras una ejecución anterior de la misma rama sigue en curso, la anterior se cancela.

## Qué comprueba el workflow del kit

`bowser.yml` tiene tres grupos, que corren en paralelo.

**Kit, agentes y perfil al día**

| Comprobación | Qué detecta |
|---|---|
| Los archivos del kit coinciden con su submódulo | Que alguien editó en el proyecto un archivo que viene del kit |
| La configuración de agentes está al día | Que cambió un rol, una skill o el perfil y no se ejecutó `make sincronizar` |
| El perfil del proyecto es válido | Un `equipo/perfil.json` mal escrito. Solo si el proyecto tiene perfil |
| La integración continua del proyecto ejecuta los verbos | Que una parte tiene verbos que ningún workflow ejecuta. **Avisa**, no falla |

**Archivos inmutables y constitución**

Solo en Pull Requests, porque compara contra la rama de destino.

| Comprobación | Qué detecta |
|---|---|
| Los archivos inmutables no se modifican | Que se editó, renombró o borró un archivo que el perfil declara en `inmutables` (por ejemplo, un cambio de esquema ya versionado). **Falla**. Sin perfil, cuida `backend/migrations/` |
| Aviso si cambia la constitución | Que el Pull Request toca los principios o las reglas del proyecto (`equipo/principios.md`, `equipo/reglas.md`). **Avisa**, y la aprobación la exige `CODEOWNERS` |

**Búsqueda de secretos**

Revisa todo el historial del cambio con `gitleaks`, en busca de claves, tokens o contraseñas.

## El workflow del proyecto

### Crearlo con `/bowser-ci`

En el chat de tu herramienta, con el perfil ya creado:

```text
/bowser-ci
```

El agente (el rol `devops`, con la skill `ci-proyecto`) lee el perfil, mira qué necesita cada verbo para correr y propone el archivo. Te explica qué se revisa en cada parte, qué se instala y en qué versión, qué servicios se levantan y qué secretos hay que crear en GitHub. Con tu "sí", lo escribe.

`/bowser-ci ver` no cambia nada: solo muestra qué verbos ejecuta hoy la integración continua.

Vuelve a ejecutarlo cuando el proyecto sume una parte, un verbo o un servicio. Si ya hay un `ci.yml`, lo actualiza sin perder los pasos propios.

> [!WARNING]
> Un workflow solo se prueba de verdad en GitHub. El primer Pull Request después de crearlo dirá si funciona: revísalo.

### Qué forma tiene

La idea central es que el workflow **no repite los comandos de los verbos: los ejecuta**. Cada parte se revisa con una línea, la misma que usa el equipo en su máquina:

```yaml
- run: make ci PARTE=api
```

Todo lo demás del archivo existe para que esa línea pueda correr. Un job típico, para una parte que necesita una base de datos:

```yaml
jobs:
  api:
    runs-on: ubuntu-latest
    services:
      # la base de datos que usan las pruebas, en la versión mayor del entorno local
    steps:
      - uses: actions/checkout@v7
      # instalar el lenguaje, en la versión que declara el proyecto
      # instalar las dependencias y las herramientas que los verbos llaman, en versiones fijas
      # preparar la base de datos
      - run: make ci PARTE=api
```

Así, cambiar el comando de un verbo en el perfil cambia lo que revisa GitHub sin tocar el workflow, y lo que pasa en tu máquina es lo mismo que pasa allá.

Una parte sin verbos no lleva job: no hay nada que ejecutar. Queda sin revisar, y el agente lo dice al entregar.

### Comprobar que no falta nada

```bash
make ci-check
```

```text
.github/workflows/ci.yml
  api: formato, revisar, probar, auditar
⚠ Ningún workflow del proyecto ejecuta estos verbos del perfil (panel: revisar). Lo que no corre en la integración continua nadie lo revisa en un Pull Request. Para redactarla desde el perfil, escribe en el chat: /bowser-ci
```

Lee los workflows del proyecto y busca dónde se ejecutan los verbos, con `make ci`, `make lint`, `make test`, `make cobertura`, `make security` o `make verificar-generados` (con `PARTE=nombre` cuenta solo esa parte), o con `scripts/verbos.py`. El mismo aviso aparece en cada Pull Request, dentro de `bowser.yml`.

Es un aviso y no un bloqueo porque un proyecto recién instalado todavía no tiene su workflow. Quien quiera exigirlo puede agregar a su `ci.yml` el paso `python3 scripts/ci.py --verificar`, que sí falla.

## Ejecutar lo mismo en tu máquina

```bash
make ci
```

Ejecuta los seis verbos en todas las partes y termina con un resumen de lo que se comprobó y lo que no. Conviene correrlo antes de abrir un Pull Request: es más rápido enterarse en tu máquina que esperar a GitHub.

Cada verbo también se puede ejecutar por separado. Ver [Comandos](comandos.md#calidad-y-pruebas).

> [!NOTE]
> `make ci` necesita las mismas herramientas que la integración continua, en las mismas versiones. Con otras, algo puede pasar en tu máquina y fallar en GitHub.

## Cuando falla

1. **Abre la ejecución en GitHub** (pestaña "Checks" del Pull Request) y mira qué paso falló. El nombre del paso ya dice mucho.
2. **Reprodúcelo en tu máquina** con el comando correspondiente.
3. **Corrige la causa.** Si el cambio lo hizo un agente, pásale el error completo.

| El paso que falló | Comando para reproducirlo | Solución habitual |
|---|---|---|
| Archivos del kit | `make verificar-kit` | Revertir el cambio al archivo del kit, o `make instalar-kit` |
| Configuración de agentes | `make verificar-agentes` | `make sincronizar` |
| Perfil del proyecto | `make profile` | Corregir lo que indique, o `/bowser-profile` |
| Archivos inmutables | `python3 scripts/verbos.py --inmutables origin/main` | Deshacer el cambio al archivo y crear uno nuevo |
| Un verbo de una parte | `make ci PARTE=nombre` | Corregir el código. Nunca la prueba, salvo que la prueba esté mal |
| Secretos | `gitleaks detect -v` | Quitar el secreto **y cambiarlo**: ya quedó expuesto |
| No puede descargar el submódulo | — | La copia del kit es privada: configura `KIT_TOKEN` |
| Falta un programa en GitHub que en tu máquina sí está | — | El workflow del proyecto no lo instala: `/bowser-ci` |

> [!WARNING]
> Un secreto que llegó a GitHub está comprometido aunque después se borre del código, porque sigue en el historial. Borrarlo no alcanza: hay que cambiar la contraseña o la clave.

## Si vienes de una versión anterior

Hasta la versión 1.17, el kit traía un `ci.yml` propio, pensado para Go, React y PostgreSQL, y lo reemplazaba en cada actualización. Al actualizar:

- **Tu `ci.yml` no se borra.** Queda tal como estaba y pasa a ser del proyecto: `make instalar-kit` lo dice al terminar. Ya lo puedes editar.
- Llega `bowser.yml`, que repite tres grupos de tu `ci.yml`: `agentes`, `controles` y `secretos`. Bórralos de `ci.yml` para que no corran dos veces.
- Las versiones de las herramientas, que antes se cambiaban con variables del repositorio (`GOLANGCI_LINT_VERSION` y las demás), ahora se editan en el archivo.
- Cuando el proyecto tenga perfil, `/bowser-ci` reescribe los grupos `backend` y `frontend` para que ejecuten los verbos.

## Lo que no hace

- **No despliega.** La integración continua solo comprueba. El despliegue es otro workflow del proyecto, y siempre lo aprueba una persona.
- **No revisa que el cambio sea lo que el cliente pidió.** Eso lo hacen los agentes revisores y, al final, quien aprueba el Pull Request.
- **No garantiza que el workflow del proyecto sea bueno.** `make ci-check` ve si los verbos se ejecutan, no si el entorno donde corren se parece al real. Eso lo revisa una persona.
- **Solo GitHub Actions.** Un proyecto en otra plataforma escribe su propia integración continua, que ejecute `make ci`.

## Siguientes pasos

- [El perfil del proyecto](perfil-del-proyecto.md): de dónde salen los verbos.
- [Capas de control](capas-de-control.md): cómo encaja la integración continua con las demás protecciones.
- [Personalizar un proyecto](personalizar.md#workflows-propios): agregar workflows propios.
