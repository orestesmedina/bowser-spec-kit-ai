# Skills

- [Introducción](#introducción)
- [Skill, rol y constitución](#skill-rol-y-constitución)
- [Cómo se activa una skill](#cómo-se-activa-una-skill)
- [El catálogo de skills de tecnología](#el-catálogo-de-skills-de-tecnología)
    - [Qué skills llegan a tu proyecto](#qué-skills-llegan-a-tu-proyecto)
    - [La madurez de una skill](#la-madurez-de-una-skill)
    - [Cuando algo falla](#cuando-algo-falla)
- [Las skills del stack](#las-skills-del-stack)
    - [go-backend](#go-backend)
    - [react-frontend](#react-frontend)
    - [postgres-db](#postgres-db)
    - [php](#php)
    - [mysql](#mysql)
    - [web-sin-framework](#web-sin-framework)
    - [De dónde sale cada skill](#de-dónde-sale-cada-skill)
- [Las skills de flujo](#las-skills-de-flujo)
- [El formato de una skill](#el-formato-de-una-skill)
- [Cuándo cambiar una skill](#cuándo-cambiar-una-skill)
- [Agregar una skill propia](#agregar-una-skill-propia)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Una skill es un conjunto de instrucciones reutilizables que un agente carga **cuando la tarea lo requiere**. El kit trae dos grupos:

- **Las que usa todo proyecto:** cuatro con el paso a paso de cada flujo de trabajo, una para redactar el perfil del proyecto y una para redactar sus convenciones.
- **Las de tecnología:** el estándar de cada una, según su documentación oficial: Go, React, PostgreSQL, PHP, MySQL. Están en un [catálogo](#el-catálogo-de-skills-de-tecnología) dentro del kit, y a cada proyecto llegan solo las que usa.

En el proyecto, todas viven en `.agents/skills/`, una carpeta por skill, cada una con un archivo `SKILL.md`.

## Skill, rol y constitución

Los tres son instrucciones para los agentes, pero responden preguntas distintas:

| | Responde | Ejemplo |
|---|---|---|
| **[Rol](roles.md)** | ¿Quién soy y qué me toca hacer? | "Eres el desarrollador backend. No tocas las partes que no son tuyas" |
| **Skill** | ¿Cómo se hace esto aquí? | "Envuelve los errores con contexto. Las pruebas van en tabla de casos" |
| **[Constitución](la-constitucion.md)** | ¿Qué no se negocia? | "El backend sigue la arquitectura por capas" |

La ventaja de separar el "cómo" en skills es que varios roles comparten el mismo conocimiento: `dev-backend` escribe según `go-backend`, y `revisor-codigo` puede cargar la misma skill para revisar contra ella.

## Cómo se activa una skill

De tres maneras:

- **Por su descripción.** Cada skill dice cuándo usarse. Cuando la tarea coincide, el agente la carga solo. Es lo normal.
- **Porque el perfil se la asigna al rol.** Si el [perfil](perfil-del-proyecto.md) dice que a la parte `api` la trabaja `dev-backend` con `go-backend`, ese rol la lleva escrita en sus instrucciones y siempre la aplica. Los demás roles (revisor, QA, seguridad…) ven en qué skill están las convenciones de cada parte y la cargan cuando revisan esa parte. Ver [Lo que cada rol recibe del proyecto](roles.md#lo-que-cada-rol-recibe-del-proyecto).
- **Nombrándola.** Puedes pedirla: "Usa la skill equipo-revision". En Claude Code también se invocan como `/equipo-feature`.

## El catálogo de skills de tecnología

Un proyecto en PHP no necesita las convenciones de Go, y si las tuviera, sus agentes las verían en la lista y podrían aplicarlas donde no toca. Por eso las skills de tecnología no se copian todas: viven en el kit, en `catalogo/skills/`, y cada proyecto recibe las suyas.

Para ver el catálogo:

```bash
make skills
```

```text
Catálogo de skills del kit (.bowser-spec-kit-ai/catalogo/skills/): 6

  go-backend         redactada  en el proyecto
                     Convenciones para escribir servicios en Go según la documentación oficial (Effective Go, Go Code Review Comments, la guía de organización de módulos y las buenas prácticas de seguridad de go.dev). Usar siempre que se cree o modifique un archivo .go.
  mysql              redactada  —
                     Convenciones para diseñar tablas, índices, consultas, cambios de esquema y procedimientos almacenados en MySQL, según las recomendaciones del manual de referencia de MySQL. Usar al crear o modificar tablas, índices, consultas SQL o procedimientos almacenados.
  php                redactada  —
                     Convenciones para escribir PHP sin framework según los estándares de PHP-FIG (PSR-1, PSR-4, PER Coding Style) y las recomendaciones del manual de PHP (tipos, errores, base de datos, seguridad, pruebas). Usar siempre que se cree o modifique un archivo .php.
  postgres-db        redactada  en el proyecto
                     Convenciones para diseñar tablas, índices, consultas, cambios de esquema y funciones en PostgreSQL, según el manual oficial y la lista "Don't Do This" de la wiki de PostgreSQL. Usar al crear o modificar tablas, índices, consultas SQL o funciones.
  react-frontend     redactada  —
                     Convenciones para escribir interfaces en React con TypeScript según la documentación oficial (react.dev: las Reglas de React, cómo estructurar el estado y cuándo usar efectos). Usar siempre que se cree o modifique un componente, un hook o cualquier archivo .tsx o .jsx.
  web-sin-framework  redactada  —
                     Convenciones para interfaces web con HTML, CSS y JavaScript estándar, sin framework ni paso de compilación, según el estándar HTML, las pautas de accesibilidad WCAG y las guías de MDN y OWASP. Usar al crear o modificar páginas, plantillas, hojas de estilo o archivos JavaScript de una interfaz así.

  probada: usada en un proyecto real
  redactada: solo redactada: todavía no se usó en un proyecto real

Al proyecto llegan con `make instalar-kit`: las que nombra equipo/perfil.json.
```

### Qué skills llegan a tu proyecto

Lo decide el [perfil del proyecto](perfil-del-proyecto.md), y lo aplica `make instalar-kit` (también `make actualizar-kit`, que lo ejecuta al final):

| Tu proyecto | Qué recibe del catálogo |
|---|---|
| No tiene perfil | Las tres de siempre: `go-backend`, `postgres-db` y `react-frontend` |
| Tiene perfil | Las que nombra en `skills`, de las partes y de los roles. Ninguna más |

Cuando cambias las skills del perfil, ejecuta `make instalar-kit`: copia las que agregaste y retira las que quitaste. `/bowser-profile` lo hace por ti. Hasta que lo ejecutes, el commit se rechaza, para que lo que dice el perfil y lo que tienen los agentes no se separen.

Una skill que llega del catálogo es un archivo del kit, igual que un rol: no se edita en el proyecto, y las actualizaciones la reemplazan. Si el proyecto necesita su propia versión, se excluye. Ver [Personalizar un proyecto](personalizar.md).

El perfil también puede nombrar skills propias del proyecto, las que no están en el catálogo y viven solo en su `.agents/skills/`. Esas el kit no las toca. Ver [Agregar una skill propia](#agregar-una-skill-propia).

### La madurez de una skill

Cada skill del catálogo lleva una etiqueta:

| Etiqueta | Qué significa | Qué hacer |
|---|---|---|
| `probada` | Se usó en un proyecto real y se corrigió con lo que salió ahí | Nada especial |
| `redactada` | Se escribió a partir de la documentación oficial, pero todavía no se hizo ningún cambio real con ella | Revisa con más cuidado lo que los agentes hagan con ella, y corrígela cuando contradiga lo que el proyecto necesita |

`make instalar-kit` avisa la primera vez que trae una skill `redactada`. Hoy las seis son `redactada`: `php`, `mysql` y `web-sin-framework` son nuevas, y `go-backend`, `react-frontend` y `postgres-db` se reescribieron en la versión 1.16.0 a partir de la documentación oficial, así que el texto actual tampoco se ha usado todavía en un proyecto.

### Cuando algo falla

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| `Las skills instaladas no son las que pide el perfil` | Cambiaste las `skills` del perfil (o creaste o quitaste el perfil) y no instalaste. Debajo dice cuál `falta` y cuál `sobra` | `make instalar-kit` y agrega los cambios al commit |
| `la skill «x» está en el catálogo del kit pero todavía no en el proyecto` | Aviso de `make profile`: es el mismo caso | `make instalar-kit` |
| `El perfil pide la skill «x», que no está en el catálogo del kit ni en .agents/skills/` | Aviso: el nombre está mal escrito, o esa tecnología todavía no tiene skill | Corrige el nombre (`make skills` lista las que hay), o escribe una skill propia. Mientras tanto los agentes trabajan sin ella |
| `La skill «x» está solo redactada` | Aviso al traerla por primera vez | Ver [La madurez de una skill](#la-madurez-de-una-skill) |
| `equipo/perfil.json no se puede leer: las skills del catálogo se dejan como estaban` | El perfil tiene un error de escritura y el kit no sabe qué pide el proyecto | Corrígelo con `make profile` y repite `make instalar-kit` |
| `El kit eliminó estos archivos, pero tienen cambios locales; se conservaron` | Quitaste del perfil una skill que alguien había editado en el proyecto | Si ya no la necesitas, bórrala a mano |

## Las skills del stack

Son las del catálogo. Cada una recoge **el estándar de su tecnología**: lo que recomienda su documentación oficial sobre cómo escribir código, qué patrones seguir y qué no hacer. No dicen qué bibliotecas usar ni cómo nombrar las cosas en tu proyecto: eso son las [convenciones del proyecto](convenciones-del-proyecto.md).

### go-backend

Se usa siempre que se crea o modifica un archivo `.go`. Fuentes: Effective Go, Go Code Review Comments y las guías de go.dev.

| Tema | Lo que establece |
|---|---|
| Estructura | La que go.dev recomienda para un servidor: `cmd/` para los ejecutables e `internal/` para la lógica |
| Formato y nombres | `gofmt`, `MixedCaps`, siglas en mayúsculas, paquetes cortos, receptores de una o dos letras |
| Errores | Se revisan todos, se envuelven con `%w`, el camino normal va sin sangría, `panic` no es manejo de errores |
| Interfaces | Pequeñas, declaradas por quien las usa |
| Concurrencia | `context.Context` como primer parámetro, goroutines con final claro, pruebas con `-race` |
| Base de datos | Valores siempre como parámetros, filas cerradas, transacción con `defer tx.Rollback()` |
| Seguridad | `govulncheck`, `crypto/rand`, `html/template`, tiempos límite en el servidor |
| Pruebas | Paquete `testing`, tabla de casos, junto al código |

### react-frontend

Se usa siempre que se crea o modifica un componente o un hook. Fuente: react.dev.

| Tema | Lo que establece |
|---|---|
| Componentes | Funciones puras, declaradas en el nivel superior, con props tipadas y `key` estable en las listas |
| Reglas de React | Pureza, props y estado sin modificar, hooks solo en el nivel superior. Las comprueba el complemento oficial de ESLint |
| Estado | El mínimo, sin duplicar; lo que se puede calcular no es estado |
| Efectos | Solo para sincronizar con algo de fuera de React, siempre con su limpieza |
| Interfaz | Los estados cargando, vacío, error y éxito; HTML por lo que significa; accesibilidad |
| Seguridad | Sin `dangerouslySetInnerHTML` con datos, ningún secreto en el navegador |
| Pruebas | Junto al componente, probando lo que la persona ve y hace |

Qué herramienta de compilación, de rutas, de datos o de estilos se usa no lo dice esta skill: es del proyecto.

### postgres-db

Se usa al crear o modificar tablas, índices, consultas o funciones. Fuentes: el manual de PostgreSQL y la lista "Don't Do This" de su wiki.

| Tema | Lo que establece |
|---|---|
| Nombres | En minúsculas y con guion bajo, sin comillas ni palabras reservadas |
| Tipos | `text`, `timestamptz`, `numeric` para dinero, columnas de identidad en vez de `serial`, `jsonb` |
| Tablas | Clave primaria, claves foráneas con su índice, `NOT NULL` por defecto, reglas declaradas en la tabla |
| Consultas | Con parámetros, `NOT EXISTS` en vez de `NOT IN`, rangos de fechas con `>=` y `<` |
| Cambios de esquema | Un archivo nuevo por cambio, con el que lo revierte, dentro de una transacción. En tablas con datos: `lock_timeout`, `NOT VALID`, índices con `CONCURRENTLY` |
| Funciones | Sin SQL dinámico armado con texto recibido; `SECURITY DEFINER` solo con `search_path` fijo |
| Seguridad | Rol de la aplicación sin `SUPERUSER`, contraseñas con `scram-sha-256` |

### php

Se usa siempre que se crea o modifica un archivo `.php` en un proyecto sin framework. Solo redactada. Fuentes: el manual de PHP y los estándares de PHP-FIG.

| Tema | Lo que establece |
|---|---|
| Versión | Una con soporte activo, declarada en `composer.json` |
| Estructura | Composer y carga de clases PSR-4: `public/` como único punto de entrada, `src/`, `tests/` |
| Estilo y nombres | PER Coding Style (el sucesor de PSR-12) y PSR-1, aplicados con `php-cs-fixer` |
| Tipos | `declare(strict_types=1)` y tipos declarados en parámetros, retornos y propiedades |
| Errores | Excepciones, un único manejador, y la configuración de errores que recomienda el manual para desarrollo y producción |
| Base de datos | Sentencias preparadas siempre, con PDO o `mysqli`; usuario con permisos mínimos |
| Seguridad | Escapar la salida, `password_hash`, sesiones estrictas, token contra CSRF, sin `eval` ni `unserialize` sobre datos recibidos |
| Pruebas | PHPUnit en `tests/`, con la misma estructura que `src/`; PHPStan para el análisis estático |

### mysql

Se usa al crear o modificar tablas, índices, consultas o procedimientos almacenados. Solo redactada. Fuente: el manual de referencia de MySQL.

| Tema | Lo que establece |
|---|---|
| Nombres | Bases de datos y tablas en minúsculas, como recomienda el manual; `snake_case`, sin palabras reservadas |
| Tablas | `InnoDB`, clave primaria en toda tabla, claves foráneas declaradas, `utf8mb4`, `NOT NULL` siempre que se pueda, dinero en `DECIMAL` |
| Índices | Según las consultas, con el orden de las columnas pensado, y revisados con `EXPLAIN` |
| Transacciones | Las operaciones relacionadas, juntas. `SELECT … FOR UPDATE` en vez de `LOCK TABLES` |
| Cambios de esquema | Un archivo nuevo por cambio, con el que lo revierte. Un solo cambio de estructura por archivo, porque MySQL no los deshace con `ROLLBACK` |
| Procedimientos | Prefijos en parámetros y variables, `SQL SECURITY INVOKER`, sin SQL dinámico armado con texto recibido |
| Seguridad | Cuenta de la aplicación con permisos mínimos; nunca `root` |

### web-sin-framework

Se usa al crear o modificar páginas, plantillas, hojas de estilo o JavaScript de una interfaz que no tiene framework ni paso de compilación. Solo redactada. Fuentes: el estándar HTML, MDN, WCAG 2.2 y OWASP.

| Tema | Lo que establece |
|---|---|
| Estructura | Contenido en el HTML, apariencia en `css/`, comportamiento en `js/` como módulos. El código de terceros no se edita |
| HTML | Documento válido, elementos por lo que significan, `label` en cada campo |
| Accesibilidad | WCAG 2.2 nivel AA: teclado, foco visible, contraste, mensajes anunciados |
| CSS | Clases, propiedades personalizadas, diseño que parte de la pantalla angosta |
| JavaScript | Estándar y disponible en los navegadores vigentes. `fetch` comprobando `response.ok`, y los cuatro estados de toda llamada: cargando, vacío, error y éxito |
| Seguridad | Todo dato se escapa al ponerlo en la página; nunca `innerHTML` con datos; ningún secreto en lo que llega al navegador |
| Pruebas | En `tests/`, con la herramienta que defina el plan |

### De dónde sale cada skill

Una skill del catálogo no describe cómo está hecho un proyecto en particular ni las preferencias de un equipo: recoge lo que recomienda quien mantiene la tecnología. Cada una nombra sus fuentes al inicio, con la fecha en que se revisaron, y a ellas se va cuando la skill no resuelve una duda. Donde la fuente oficial no fija nada (por ejemplo, el formato de los archivos de cambio de una base de datos), la skill lo dice.

Cada una dice también qué no va en git (`node_modules/`, `vendor/`, binarios, volcados con datos reales). El kit no trae esas reglas en su bloque de `.gitignore`: las escribe `/bowser-profile` en el del proyecto, con la carpeta de cada parte.

Así una skill sirve igual para cualquier proyecto que use esa tecnología.

Lo propio de cada proyecto (cómo nombra variables, tablas y columnas, qué patrones de diseño sigue, qué bibliotecas eligió) va aparte, en una skill del proyecto que redacta `/bowser-conventions`. Ver [Convenciones del proyecto](convenciones-del-proyecto.md). Cuando las dos dicen cosas distintas:

1. En seguridad, siempre el estándar.
2. En nombres, estructura, patrones y bibliotecas, el proyecto.
3. En lo que el proyecto no define, el estándar.

Un perfil que combina las dos, para un proyecto con una API, su base de datos y un panel web hecho con PHP que genera HTML:

```json
{
  "partes": [
    { "nombre": "api", "carpeta": "api", "roles": ["dev-backend"], "skills": ["php", "convenciones-de-api"] },
    { "nombre": "base-de-datos", "carpeta": "api/database", "roles": ["dev-dba"], "skills": ["mysql", "convenciones-de-base-de-datos"] },
    { "nombre": "panel", "carpeta": "panel", "roles": ["dev-frontend"], "skills": ["php", "web-sin-framework", "convenciones-de-panel"] }
  ]
}
```

El panel lleva las dos del catálogo: `php` para la parte de la página que se arma en el servidor y `web-sin-framework` para lo que llega al navegador.

## Las skills de flujo

Describen el paso a paso de cada tipo de trabajo. Las ejecuta el orquestador.

| Skill | Cuándo se usa | Qué hace | Página |
|---|---|---|---|
| `equipo-feature` | Se pide construir, agregar o cambiar una funcionalidad | El flujo completo en siete fases, desde la especificación hasta el Pull Request, con las puertas de aprobación | [Construir una funcionalidad](funcionalidad.md) |
| `equipo-bug` | Se reporta un error | Diagnóstico, prueba que lo reproduce, arreglo mínimo, validación y registro | [Corregir un bug](bugs.md) |
| `equipo-revision` | Antes de abrir o aprobar un Pull Request, o al pedir una revisión | Lanza QA, revisión y seguridad en paralelo y consolida un veredicto | [El equipo de agentes](equipo-de-agentes.md#quién-escribe-no-aprueba) |
| `equipo-retomar` | Al iniciar cada sesión, o al preguntar por dónde iban | Reconstruye el estado a partir de los archivos y de git. Solo lee | [Retomar el trabajo](retomar.md) |

Estas skills son las que hacen que el proceso sea el mismo cada vez. El orquestador no improvisa el orden de las fases: lo lee.

Hay dos skills más, que no son de una tecnología ni de un flujo. `perfil-proyecto` explica el formato del [perfil del proyecto](perfil-del-proyecto.md) y cómo redactarlo; la usa el `arquitecto` cuando alguien escribe `/bowser-profile`. `convenciones-proyecto` explica cómo redactar las [convenciones propias del proyecto](convenciones-del-proyecto.md) leyendo su código; la usa con `/bowser-conventions`.

## El formato de una skill

Una skill sigue el estándar abierto `SKILL.md`, que entienden las tres herramientas:

```markdown
---
name: go-backend
description: Convenciones para escribir backend en Go (estructura, capas, errores, HTTP, pruebas). Usar siempre que se cree o modifique código en backend/.
metadata:
  madurez: probada
---
# Backend en Go — convenciones

## Estructura
…
```

| Campo | Qué define |
|---|---|
| `name` | El nombre de la skill, igual al de su carpeta |
| `description` | Qué contiene y **cuándo usarla**. El agente decide si la carga leyendo esta frase |
| `metadata: madurez` | Solo en las skills del catálogo, y obligatoria ahí: `probada` o `redactada`. Una skill propia del proyecto no la necesita |

El cuerpo es texto libre. Funciona mejor cuando es concreto: reglas cortas, la estructura de carpetas dibujada y un ejemplo de código.

Codex y OpenCode leen `.agents/skills/` directamente. Claude Code lee una copia en `.claude/skills/`, que produce `make sincronizar`.

## Cuándo cambiar una skill

La señal más clara: **un mismo error aparece en varias funcionalidades**. Si el revisor rechaza tres veces lo mismo, el problema no es el desarrollador sino que la convención no está escrita.

| Situación | Qué hacer |
|---|---|
| Los agentes repiten un error de código | Si es una costumbre del proyecto, agrégala a sus [convenciones](convenciones-del-proyecto.md). Si es algo que la documentación oficial de la tecnología recomienda y la skill no dice, va en la skill del catálogo |
| El proyecto adopta una librería nueva | Agrégala a las convenciones del proyecto, con su forma de uso. No a la skill del catálogo: esa elección es del proyecto |
| Un flujo siempre se atasca en el mismo paso | Ajusta la skill de flujo correspondiente |
| La regla debe cumplirse sin excepción | Va en la constitución, no en una skill |

Las skills vienen del kit: el cambio se hace en el repositorio del kit (las de tecnología, en `catalogo/skills/`; las demás, en `.agents/skills/`), o el proyecto excluye la skill para tener su versión. Ver [Personalizar un proyecto](personalizar.md).

## Agregar una skill propia

Crea una carpeta nueva en `.agents/skills/` con su `SKILL.md`:

```bash
mkdir -p .agents/skills/pagos-stripe
# escribe .agents/skills/pagos-stripe/SKILL.md
make sincronizar
```

Una skill que no viene del kit es del proyecto: las actualizaciones nunca la tocan. Si es de una tecnología, nómbrala en las `skills` del [perfil](perfil-del-proyecto.md) para la parte que la usa.

> [!WARNING]
> No le pongas el nombre de una skill del catálogo (`make skills` los lista). Si el perfil la nombra, `make instalar-kit` la reemplaza por la del kit y deja la tuya en `.kit-respaldo/`.

Buenos candidatos para una skill propia: las convenciones de una integración externa, las reglas de un dominio de negocio particular, o un procedimiento que el equipo repite.

> [!TIP]
> Escribe la descripción pensando en el agente que la va a leer para decidir si la carga. "Usar al crear o modificar cualquier código que cobre, reembolse o consulte pagos" funciona mucho mejor que "Skill de pagos".

## Siguientes pasos

- [Convenciones del proyecto](convenciones-del-proyecto.md): lo propio de cada proyecto, junto al estándar.
- [Roles](roles.md): quién usa cada skill.
- [La constitución](la-constitucion.md): las reglas que están por encima de las skills.
- [Personalizar un proyecto](personalizar.md): skills y roles propios.
