# El perfil del proyecto

- [Introducción](#introducción)
- [Para qué sirve](#para-qué-sirve)
- [Qué contiene](#qué-contiene)
- [Los verbos](#los-verbos)
- [Crear el perfil](#crear-el-perfil)
- [Ver y validar el perfil](#ver-y-validar-el-perfil)
- [Qué cambia cuando hay perfil](#qué-cambia-cuando-hay-perfil)
- [Aprobar un cambio en el perfil](#aprobar-un-cambio-en-el-perfil)
- [Cuando algo falla](#cuando-algo-falla)
- [Límites](#límites)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

El perfil es un archivo, `equipo/perfil.json`, en el que el proyecto se describe a sí mismo: qué partes tiene, en qué carpeta está cada una, con qué tecnología está hecha y qué comando hay que ejecutar para probarla, revisarla o formatearla.

Es del proyecto, no del kit: el kit no lo instala ni lo reemplaza al actualizarse. Lo redacta un agente mirando el código y lo aprueba una persona.

> [!NOTE]
> El perfil es opcional por ahora. Un proyecto sin perfil funciona como siempre: el kit supone Go en `backend/` y React en `frontend/`. En la versión 2.0 del kit, el perfil pasará a ser la única forma (ver la [hoja de ruta](../HOJA-DE-RUTA.md)).

## Para qué sirve

Sin perfil, el kit trae escrito cómo es tu proyecto. `make test`, por ejemplo, ejecuta `go test` dentro de `backend/`. Eso sirve si el proyecto es exactamente así, y no sirve si la carpeta se llama distinto, si está en PHP o si todavía no tiene pruebas.

Con perfil, el kit deja de suponer. Cuando alguien escribe `make test`, busca en el perfil qué significa "probar" en cada parte del proyecto y ejecuta eso. El mismo kit funciona entonces en un proyecto de Go, en uno de PHP o en uno con tres servicios distintos.

## Qué contiene

Una lista de **partes**. Una parte es algo que se construye, se prueba o se despliega por separado: una API, un panel web, una aplicación móvil. Un proyecto pequeño puede tener una sola.

```json
{
  "partes": [
    {
      "nombre": "api",
      "carpeta": "servidor",
      "descripcion": "API del inventario",
      "rol": "dev-backend",
      "skills": ["go-backend", "postgres-db"],
      "terceros": ["vendor"],
      "inmutables": ["migrations/*.sql"],
      "verbos": {
        "formato": "test -z \"$(gofmt -l .)\"",
        "revisar": "go vet ./...",
        "probar": "go test ./...",
        "cobertura": null,
        "auditar": "govulncheck ./...",
        "generar": null
      }
    },
    {
      "nombre": "panel",
      "carpeta": "web/panel",
      "rol": "dev-frontend",
      "verbos": {
        "revisar": "find . -name '*.php' -not -path './libraries/*' -print0 | xargs -0 -n1 php -l > /dev/null"
      }
    }
  ]
}
```

| Campo | Qué es | Obligatorio |
|---|---|---|
| `nombre` | Cómo se llama la parte. Minúsculas, números y guiones; no se repite | Sí |
| `carpeta` | Dónde está, relativa a la raíz del proyecto. `"."` si el proyecto entero es una sola parte | Sí |
| `descripcion` | Una línea para quien lo lea | No |
| `rol` | El agente de `equipo/agentes/` que trabaja esa parte | No |
| `skills` | Las [skills](skills.md) con las convenciones de su tecnología | No |
| `terceros` | Carpetas con código ajeno copiado dentro de la parte. No se les revisa el formato | No |
| `inmutables` | Archivos que no se modifican una vez guardados en git, como las migraciones. Son patrones relativos a la parte | No |
| `verbos` | El comando de cada verbo | No |

## Los verbos

Un verbo es una acción que el kit necesita pedir en cualquier proyecto. Son seis, y siempre los mismos. Lo que cambia de un proyecto a otro es el comando que los ejecuta.

| Verbo | Qué debe hacer su comando | Quién lo usa |
|---|---|---|
| `formato` | Comprobar que el código esté formateado, sin cambiar archivos. Tiene que ser rápido | Cada commit que toca la parte, y `make lint` |
| `revisar` | Análisis del código sin ejecutarlo: linters, tipos, sintaxis | `make lint` |
| `probar` | Ejecutar las pruebas | `make test` |
| `cobertura` | Medir cuánto código cubren las pruebas y fallar bajo el mínimo del proyecto | `make cobertura` |
| `auditar` | Buscar vulnerabilidades conocidas en las dependencias | `make security` |
| `generar` | Regenerar el código que sale de otra fuente | `make generar`, `make verificar-generados` |

Tres reglas:

- El comando se ejecuta con `bash`, **dentro de la carpeta de la parte**.
- Termina con código 0 si todo está bien y con otro si no.
- **Un verbo puede quedar sin definir**, con `null` o no escribiéndolo. Significa "este proyecto todavía no tiene eso". El kit avisa y sigue; no falla.

> [!WARNING]
> No rellenes un verbo con un comando que siempre pasa (`"probar": "true"`) para quitar el aviso. El aviso es información: dice que esa parte no tiene pruebas. Un comando falso lo esconde.

## Crear el perfil

En el chat de tu herramienta:

```text
/bowser-profile
```

(En Codex, `$bowser-profile`.) El agente hace esto:

1. Ejecuta `make profile DETECTAR=1`, que mira el proyecto y lista lo que encuentra: carpetas con código y en qué lenguaje, archivos que delatan una tecnología (`go.mod`, `composer.json`, `package.json`), archivos de SQL con su motor probable, y carpetas que parecen de terceros. Si uno de esos archivos está dentro de una carpeta dudosa (por ejemplo `libraries/PHPMailer/composer.json`), lo marca con `dentro_de_carpeta_a_confirmar`: suele ser de una biblioteca copiada, no la tecnología del proyecto. Solo lee.
2. Le pasa esos hechos al `arquitecto`, que redacta el perfil.
3. Te pregunta lo que no puede saber mirando el código: cómo se prueba, qué versión se usa, si una carpeta dudosa es de terceros.
4. Te muestra la propuesta en lenguaje simple y espera tu aprobación.
5. Con tu "sí", escribe `equipo/perfil.json` y lo valida.

En un proyecto recién creado, sin código todavía, el paso 1 no encuentra nada y el perfil sale de la conversación sobre qué se va a construir.

Si prefieres escribirlo a mano, es un archivo de texto: créalo con el formato de arriba y valídalo con `make profile`.

## Ver y validar el perfil

```bash
make profile
```

```text
Perfil del proyecto (equipo/perfil.json): 2 partes

  api  ·  carpeta servidor  ·  dev-backend  ·  skills: go-backend, postgres-db
    API del inventario
    formato    test -z "$(gofmt -l .)"
    revisar    go vet ./...
    probar     go test ./...
    cobertura  — sin definir
    auditar    govulncheck ./...
    generar    — sin definir
    terceros:   vendor
    inmutables: migrations/*.sql

  panel  ·  carpeta web/panel  ·  dev-frontend
    formato    — sin definir
    revisar    find . -name '*.php' -not -path './libraries/*' -print0 | xargs -0 -n1 php -l > /dev/null
    probar     — sin definir
    cobertura  — sin definir
    auditar    — sin definir
    generar    — sin definir

OK: perfil válido (2 partes).
```

Dentro del chat, `/bowser-profile ver` hace lo mismo y lo explica.

Para ejecutar un verbo en una sola parte:

```bash
make test PARTE=api
```

## Qué cambia cuando hay perfil

| Comando o control | Sin perfil | Con perfil |
|---|---|---|
| `make test` | `go test` en `backend/` y `npm test` en `frontend/` | El verbo `probar` de cada parte |
| `make lint` | `gofmt`, `go vet`, `golangci-lint`; lint y tipos del frontend | Los verbos `formato` y `revisar` |
| `make cobertura` | Cobertura de la capa de servicio de Go, mínimo 80 % | El verbo `cobertura` |
| `make security` | `govulncheck` y `npm audit` | El verbo `auditar` |
| `make generar`, `make verificar-generados` | sqlc y los tipos de la API | El verbo `generar` |
| Commit: formato | `gofmt` y `prettier` | El verbo `formato`, solo en las partes que el commit toca |
| Commit: archivos que no se modifican | `backend/migrations/*.sql` | Los `inmutables` de cada parte |

Lo demás no cambia: estado, costos, instalación del kit, secretos, mensajes de commit y aprobaciones no dependen de la tecnología.

`make test-backend` y `make test-frontend` siguen existiendo, pero son los comandos de siempre: no leen el perfil.

## Aprobar un cambio en el perfil

Los comandos del perfil se ejecutan en la máquina de cada persona del equipo y en la integración continua. Por eso un commit que crea, cambia o elimina `equipo/perfil.json` necesita que una persona lo confirme:

```bash
APROBADO_PERFIL=1 git commit -m "chore: perfil del proyecto"
```

Antes de confirmarlo, lee los comandos con `make profile`. Un agente nunca usa esa variable por su cuenta: te deja el cambio listo y te dice que lo confirmes.

## Cuando algo falla

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| `El perfil del proyecto (equipo/perfil.json) cambió` | El commit toca el perfil y nadie lo confirmó | Revísalo con `make profile` y repite el commit con `APROBADO_PERFIL=1` |
| `equipo/perfil.json no es un JSON válido` | Falta una coma, una comilla o una llave | Corrige el archivo; el mensaje indica la línea |
| `la carpeta «x» no existe` | La parte apunta a una carpeta que no está, o se renombró | Corrige `carpeta` |
| `verbo desconocido «x»` | Solo existen los seis verbos de la tabla | Usa uno de ellos. Un comando propio del proyecto va en `proyecto.mk` |
| `el rol «x» no existe en equipo/agentes/` | El nombre del rol está mal escrito | Mira los disponibles en `equipo/agentes/` |
| `la skill «x» no está en .agents/skills/` | Es un aviso: el agente trabajará sin esa skill | Quítala del perfil o agrega la skill al proyecto |
| `La parte «x» no define el verbo «y»: se omite` | Es un aviso: esa parte todavía no tiene eso | Nada, si es cierto. Si ya lo tiene, agrega el comando al perfil |
| `Ninguna parte define «y»` | Es un aviso: el comando no ejecutó nada | Lo mismo |
| `y falló en la parte «x» (código N)` | El comando del verbo terminó con error | El error real está justo encima: es la salida del comando |
| `Estos archivos de la parte «x» no se modifican una vez versionados` | El commit cambia, renombra o borra un archivo `inmutable` | Deja el archivo como estaba y crea uno nuevo |
| `La parte «x» no pasa la revisión de formato` | El verbo `formato` falló en una parte que el commit toca | Formatea el código de esa parte y repite el commit |

Con un perfil inválido el kit no ejecuta ningún verbo y bloquea los commits hasta que se corrija.

## Límites

- **La integración continua todavía no lee el perfil.** El `ci.yml` que trae el kit sigue buscando `backend/go.mod` y `frontend/package.json`. Un proyecto con otra forma necesita por ahora su propio workflow. Se resuelve en una entrega posterior.
- **Los roles y `make doctor` todavía hablan de Go, React y PostgreSQL.** El campo `skills` del perfil se valida y se muestra, pero los roles siguen llevando las suyas escritas. También es de una entrega posterior.
- **El hook de Claude Code sigue protegiendo `backend/migrations/`**, no los `inmutables` del perfil. El control del commit sí usa el perfil, y es el que vale para las tres herramientas.
- **`make verificar-generados` revisa toda la carpeta de la parte.** Si tienes otros cambios sin commit en ella, los toma por código generado desactualizado.
- **La detección describe, no decide.** Reconoce las tecnologías más comunes por sus archivos; una que no conozca aparece solo como carpetas con archivos. Y no sabe cómo se prueba ni cómo se levanta el proyecto: eso se pregunta.
- **La confirmación con `APROBADO_PERFIL=1` depende de que el agente respete la instrucción de no usarla.** Es la misma garantía que tiene la constitución.

## Siguientes pasos

- [Comandos](comandos.md): la lista completa, con sus opciones.
- [Hooks de git](hooks-de-git.md): los controles de cada commit.
- [Personalizar un proyecto](personalizar.md): comandos, roles y skills propios.
