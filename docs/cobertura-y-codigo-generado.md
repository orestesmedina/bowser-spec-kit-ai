# Cobertura y código generado

- [Introducción](#introducción)
- [Cobertura de pruebas](#cobertura-de-pruebas)
    - [Quién decide el mínimo](#quién-decide-el-mínimo)
    - [Medirla](#medirla)
    - [Cuando no alcanza el mínimo](#cuando-no-alcanza-el-mínimo)
    - [Lo que la cobertura no garantiza](#lo-que-la-cobertura-no-garantiza)
- [Código generado](#código-generado)
    - [Regenerarlo](#regenerarlo)
    - [Verificar que está al día](#verificar-que-está-al-día)
    - [Cuando la verificación falla](#cuando-la-verificación-falla)
- [En la integración continua](#en-la-integración-continua)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página describe dos controles que protegen contra errores que **no se notan a simple vista**: el código compila, las pruebas que existen pasan y, sin embargo, algo quedó mal.

- **Cobertura:** que la lógica de negocio tenga pruebas suficientes.
- **Código generado:** que el código que produce una herramienta coincida con la fuente de la que sale.

Los dos son el tipo de descuido que un agente de IA puede cometer sin avisar: entregar menos pruebas de las pedidas u olvidar un paso mecánico. Por eso no dependen de que alguien se acuerde de revisarlos: los comprueba la integración continua en cada Pull Request.

Cómo se mide la cobertura y cómo se regenera el código depende de la tecnología. El kit no lo sabe: lo declara cada proyecto en su [perfil](perfil-del-proyecto.md), con los verbos `cobertura` y `generar`.

## Cobertura de pruebas

La cobertura es el porcentaje del código que se ejecuta cuando corren las pruebas. Si una función tiene diez instrucciones y las pruebas pasan por ocho, su cobertura es del 80 %. Las dos restantes son código que nadie comprobó que funcione.

### Quién decide el mínimo

Los principios de la [constitución](la-constitucion.md) dicen que el mínimo lo fijan las reglas del proyecto (`equipo/reglas.md`). Una regla típica:

```markdown
## Pruebas
- La cobertura mínima de las reglas de negocio DEBE ser 80 %.
```

Conviene medir la capa donde viven las reglas del negocio (cuánto se cobra, quién puede hacer qué, qué pasa cuando algo falla) y no todo el código: ahí un error cuesta más, y las pruebas son más baratas de escribir porque no dependen de la base de datos ni de la red.

El verbo `cobertura` del perfil es el que hace cumplir esa regla: ejecuta las pruebas, mide y **falla** si el resultado queda bajo el mínimo. Un ejemplo en una parte escrita en Go:

```json
"cobertura": "go test -coverprofile=coverage.out ./... && bash $PERFIL_RAIZ/tools/cobertura-minima.sh coverage.out 80"
```

Ahí, `tools/cobertura-minima.sh` es un script del propio proyecto: si la herramienta de la tecnología no sabe fallar bajo un mínimo, el proyecto agrega el suyo en `tools/` (la carpeta `scripts/` es del kit).

> [!NOTE]
> Hasta la versión 1.22.0, el kit traía `scripts/cobertura.py`, que medía los archivos `service*.go` con un mínimo fijo de 80 %. Si el perfil o un workflow del proyecto todavía lo usa, la actualización no lo borra: queda como archivo del proyecto. Conviene moverlo a `tools/`.

### Medirla

```bash
make coverage
```

Ejecuta el verbo `cobertura` en cada parte que lo define. Una parte que no lo define se omite con un aviso:

```text
⚠ La parte «panel» no define el verbo «cobertura»: se omite.
```

Si ninguna parte lo define, el proyecto todavía no mide la cobertura: `make ci` lo marca como «sin definir» en su [resumen](perfil-del-proyecto.md#el-resumen-de-make-ci).

### Cuando no alcanza el mínimo

`make coverage` termina con error y dice en qué parte:

```text
✗ cobertura falló en la parte «api» (código 1).
```

Arriba de ese mensaje está lo que imprimió la herramienta de la parte, normalmente el porcentaje por archivo: el más bajo es donde faltan las pruebas. Pídele al agente que las agregue, indicando el archivo:

> La cobertura de `pedidos/servicio` está en 40 %. Agrega pruebas para los casos que faltan, incluidos los de error.

> [!WARNING]
> No aceptes como solución que el agente saque código de la capa que se mide, cambie el nombre de un archivo para que deje de contarse, baje el mínimo o escriba pruebas que ejecutan el código sin comprobar nada. Todas suben el número sin probar nada. Bajar el mínimo es cambiar las reglas del proyecto: lo decide una persona.

### Lo que la cobertura no garantiza

Un 100 % no significa que el código esté bien. La cobertura dice que las pruebas *pasaron por* una línea, no que comprobaron lo correcto. Sirve para detectar lo que nadie probó; la calidad de las pruebas la revisan el agente de QA y quien aprueba el Pull Request.

## Código generado

Parte del código de un proyecto no lo escribe nadie: lo produce una herramienta a partir de otro archivo, que es la verdadera fuente. Por ejemplo, el código que consulta la base de datos a partir de archivos `.sql`, o los tipos de la API a partir de su contrato. Si la fuente cambia y el código generado no se actualiza, los dos quedan contando historias distintas.

El caso típico: se agrega un campo a una respuesta de la API y se actualiza el contrato, pero no se regeneran los tipos. La interfaz sigue creyendo que el campo no existe. Todo compila y la pantalla no muestra el dato.

El código generado **se sube a git**, igual que el resto. Así cualquiera puede leer el proyecto y compilarlo sin tener instaladas las herramientas de generación.

Qué se genera y con qué herramienta lo dice el verbo `generar` de cada parte del perfil:

```json
"generar": "sqlc generate"
```

### Regenerarlo

```bash
make generate
```

Ejecuta el verbo `generar` en cada parte que lo define. Úsalo **después de cambiar una fuente** (una consulta, el contrato de la API, lo que el proyecto genere) e incluye en el mismo commit la fuente y el código generado.

### Verificar que está al día

```bash
make check-generated
```

Regenera y falla si la parte quedó con algún cambio sin subir a git. Es la misma comprobación que hace la integración continua, así que conviene ejecutarla antes de abrir un Pull Request.

### Cuando la verificación falla

```text
✗ El código generado de la parte «api» no estaba al día (o hay cambios sin commit):
   M servidor/db/consultas.go
  Ejecuta 'make generate' y agrega el resultado al commit.
```

Significa que alguien cambió una fuente y no regeneró. La solución es la que indica el mensaje: `make generate` y un commit con el resultado.

La comprobación mira toda la carpeta de la parte: un archivo cualquiera de esa parte que todavía no tenga commit también la hace fallar. Haz el commit de tu trabajo antes de verificar.

Si el error es que falta un programa, no es un problema del código sino de tu máquina: `make doctor` dice qué falta, según los [requisitos](perfil-del-proyecto.md#los-requisitos-de-la-máquina) del perfil.

> [!WARNING]
> Nunca edites a mano un archivo generado para que "coincida". La próxima generación borra el cambio. Si el resultado no es el que quieres, lo que hay que cambiar es la fuente.

## En la integración continua

En cada Pull Request, GitHub ejecuta estas comprobaciones por su cuenta si el workflow del proyecto las incluye: `make ci` ejecuta los verbos `generar` (verificando) y `cobertura` junto a los demás. Ver [Integración continua](integracion-continua.md#el-workflow-del-proyecto).

Si alguna falla, el Pull Request queda en rojo y no se puede integrar hasta corregirlo.

Para repetir en tu máquina todo lo que hace la integración continua, incluidos estos dos controles:

```bash
make ci
```

## Siguientes pasos

- [El perfil del proyecto](perfil-del-proyecto.md): cómo se declaran los verbos `cobertura` y `generar`.
- [Hooks de git](hooks-de-git.md): los controles que se ejecutan en cada commit, antes de llegar a GitHub.
- [Capas de control](capas-de-control.md): cómo se complementan todas las protecciones.
- [Integración continua](integracion-continua.md): el resto de lo que GitHub comprueba.
