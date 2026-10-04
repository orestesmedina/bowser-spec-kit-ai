# Cobertura y código generado

- [Introducción](#introducción)
- [Cobertura de pruebas](#cobertura-de-pruebas)
    - [Qué mide el kit](#qué-mide-el-kit)
    - [Medirla](#medirla)
    - [Cuando no alcanza el mínimo](#cuando-no-alcanza-el-mínimo)
    - [Lo que la cobertura no garantiza](#lo-que-la-cobertura-no-garantiza)
- [Código generado](#código-generado)
    - [Qué se genera](#qué-se-genera)
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

## Cobertura de pruebas

La cobertura es el porcentaje del código que se ejecuta cuando corren las pruebas. Si una función tiene diez instrucciones y las pruebas pasan por ocho, su cobertura es del 80 %. Las dos restantes son código que nadie comprobó que funcione.

### Qué mide el kit

La constitución exige un mínimo de **80 % en la capa de servicio** del backend. El kit lo mide así:

- Toma los archivos `service*.go` dentro de `backend/internal/` (por ejemplo `internal/users/service.go`), sin contar los de pruebas.
- Suma todos los dominios y calcula un único porcentaje.
- Falla si ese porcentaje queda por debajo de 80.

Se mide esa capa, y no todo el backend, porque ahí viven las reglas del negocio: cuánto se cobra, quién puede hacer qué, qué pasa cuando algo falla. Es donde un error cuesta más y donde las pruebas son más baratas de escribir, porque no dependen de la base de datos ni de HTTP.

El mínimo es fijo. No se configura por proyecto, porque lo define la constitución.

### Medirla

```bash
make cobertura
```

Ejecuta las pruebas del backend y muestra el resultado por archivo:

```
COBERTURA DE LA CAPA DE SERVICIO · mínimo 80 %
  status/service.go                                     8/8     100.0 %
  Total                                                 8/8     100.0 %

✓ Cumple el mínimo.
```

Los dos números son instrucciones cubiertas sobre instrucciones totales. Lo que cuenta para aprobar es la fila **Total**, no cada archivo por separado.

Si el proyecto todavía no tiene ningún archivo de servicio, el comando lo indica y pasa.

### Cuando no alcanza el mínimo

```
✗ Cobertura de servicio 50.0 % por debajo del mínimo 80 % (constitución, III). Agrega pruebas a la capa de servicio.
```

La tabla muestra qué archivo tiene el porcentaje más bajo: ahí faltan las pruebas. Pídele al agente que las agregue, indicando el archivo:

> La cobertura de `internal/pedidos/service.go` está en 40 %. Agrega pruebas para los casos que faltan, incluidos los de error.

> [!WARNING]
> No aceptes como solución que el agente saque código de la capa de servicio, cambie el nombre del archivo para que deje de contarse o escriba pruebas que ejecutan el código sin comprobar nada. Las tres suben el número sin probar nada.

### Lo que la cobertura no garantiza

Un 100 % no significa que el código esté bien. La cobertura dice que las pruebas *pasaron por* una línea, no que comprobaron lo correcto. Sirve para detectar lo que nadie probó; la calidad de las pruebas la revisan el agente de QA y quien aprueba el Pull Request.

## Código generado

Parte del código de un proyecto no lo escribe nadie: lo produce una herramienta a partir de otro archivo, que es la verdadera fuente. Si la fuente cambia y el código generado no se actualiza, los dos quedan contando historias distintas.

### Qué se genera

| Qué | Fuente | Resultado | Herramienta |
|---|---|---|---|
| Consultas a la base de datos | Los archivos `.sql` de `backend/internal/db/queries/` y las migraciones | Código Go en `backend/internal/db/` | [sqlc](https://sqlc.dev) |
| Tipos de la API para el frontend | El contrato `backend/api/openapi.yaml` | Tipos TypeScript en `frontend/src/api/` | [openapi-typescript](https://openapi-ts.dev), mediante el script `api:gen` |

El caso típico: se agrega un campo a una respuesta de la API y se actualiza el contrato, pero no se regeneran los tipos. El frontend sigue creyendo que el campo no existe. Todo compila y la pantalla no muestra el dato.

El código generado **se sube a git**, igual que el resto. Así cualquiera puede leer el proyecto y compilarlo sin tener instaladas las herramientas de generación.

Para que el kit pueda regenerar, el proyecto debe seguir estas convenciones:

- La configuración de sqlc está en `backend/sqlc.yaml`.
- El archivo `frontend/package.json` tiene un script llamado `api:gen`, y su salida queda dentro de `frontend/src/api/`.

### Regenerarlo

```bash
make generar
```

Ejecuta las dos generaciones. Úsalo **después de cambiar una fuente**:

- Agregaste o cambiaste una consulta SQL.
- Creaste una migración que afecta a una tabla que ya tiene consultas.
- Cambiaste el contrato de la API.

Después, incluye en el mismo commit tanto la fuente como el código generado.

> [!NOTE]
> Cada parte se omite si el proyecto todavía no la tiene: sin `sqlc.yaml`, sin ninguna consulta o sin el script `api:gen`. Un proyecto recién creado puede ejecutar `make generar` sin que falle.

### Verificar que está al día

```bash
make verificar-generados
```

Regenera todo y falla si quedó algún cambio sin subir a git. Es la misma comprobación que hace la integración continua, así que conviene ejecutarla antes de abrir un Pull Request.

### Cuando la verificación falla

```
✗ El código generado no está al día (o tiene cambios sin commit):
 M frontend/src/api/schema.d.ts
  Ejecuta 'make generar' y agrega el resultado al commit.
```

Significa que alguien cambió una fuente y no regeneró. La solución es la que indica el mensaje: `make generar` y un commit con el resultado.

Si el error es `Falta sqlc` o `Faltan las dependencias del frontend`, no es un problema del código sino de tu máquina: instala lo que falta según la página de [Instalación](instalacion.md).

> [!WARNING]
> Nunca edites a mano un archivo generado para que "coincida". La próxima generación borra el cambio. Si el resultado no es el que quieres, lo que hay que cambiar es la fuente.

## En la integración continua

En cada Pull Request, GitHub ejecuta estas comprobaciones por su cuenta:

| Dónde | Qué comprueba |
|---|---|
| Backend | Que el código de sqlc esté al día, y que la cobertura de la capa de servicio llegue al 80 % |
| Frontend | Que los tipos de la API estén al día |

Si alguna falla, el Pull Request queda en rojo y no se puede integrar hasta corregirlo.

Para repetir en tu máquina todo lo que hace la integración continua, incluidos estos dos controles:

```bash
make ci
```

## Siguientes pasos

- [Hooks de git](hooks-de-git.md): los controles que se ejecutan en cada commit, antes de llegar a GitHub.
- [Capas de control](capas-de-control.md): cómo se complementan todas las protecciones.
- [Integración continua](integracion-continua.md): el resto de lo que GitHub comprueba.
- [Instalación](instalacion.md#herramientas-de-go): cómo instalar `sqlc` y el resto de las herramientas.
