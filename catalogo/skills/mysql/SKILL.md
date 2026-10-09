---
name: mysql
description: Convenciones para diseñar tablas, índices, consultas, cambios de esquema y procedimientos almacenados en MySQL, según las recomendaciones del manual de referencia de MySQL. Usar al crear o modificar tablas, índices, consultas SQL o procedimientos almacenados.
metadata:
  madurez: redactada
---
# MySQL — convenciones

Fuente: el manual de referencia de MySQL 8.4 (dev.mysql.com/doc/refman/8.4/en/), sobre todo sus capítulos de InnoDB, optimización, tipos de datos, programas almacenados y seguridad. Revisado el 2026-10-09. Ante una duda que esta página no resuelva, se consulta ahí. Donde el manual no fija una convención (el formato de los archivos de cambio), esta página lo dice.

## Versión
- Con soporte al 2026-10-09 (endoflife.date/mysql): las LTS 8.4 y 9.7. La 8.0 dejó de recibir correcciones el 2026-04-30.
- Un proyecto usa una versión LTS con soporte. Si corre en una sin soporte, dilo en la entrega como riesgo.
- No escribas sintaxis que la versión del proyecto no entiende: el manual dice desde cuál existe cada cosa.

## Nombres
- Bases de datos y tablas **en minúsculas**: es lo que el manual recomienda, porque en Linux esos nombres distinguen mayúsculas y en Windows y macOS no, y un esquema con mayúsculas se rompe al cambiar de sistema.
- `snake_case`, en inglés, tablas en plural (`order_items`). La clave primaria se llama `id` y una clave foránea, `<tabla en singular>_id` (`order_id`).
- Sin palabras reservadas como nombre (`order`, `key`, `date`, `group`): el manual tiene la lista. Máximo 64 caracteres.

## Tablas
- Motor `InnoDB` (el predeterminado): es el que tiene transacciones y claves foráneas.
- **Clave primaria en toda tabla** (manual, buenas prácticas de InnoDB): la columna más consultada o, si no hay una evidente, un entero autoincremental (`BIGINT UNSIGNED AUTO_INCREMENT`).
- **Claves foráneas declaradas** en toda columna que une tablas, con el mismo tipo de dato en los dos lados y el `ON DELETE` decidido a conciencia.
- Juego de caracteres `utf8mb4` (el predeterminado desde la 8.0). No `utf8`: es un alias de `utf8mb3`, que no guarda todos los caracteres y está en retirada. La misma colación en las columnas que se comparan o se unen entre sí.
- El tipo más pequeño que alcance, y `NOT NULL` siempre que se pueda: el manual lo recomienda porque ocupa menos y permite usar mejor los índices.
- Dinero y todo valor exacto en `DECIMAL`. Nunca `FLOAT` ni `DOUBLE`, que son aproximados.
- Fechas: `DATETIME` guarda lo que se le da; `TIMESTAMP` convierte a UTC según la zona horaria de la conexión y solo llega hasta enero de 2038. Se guarda siempre UTC. Creación y modificación las pone la base de datos (`DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP`).
- Sin ancho en los enteros (`INT`, no `INT(11)`): está en retirada y no cambia lo que se guarda.
- Las reglas de los datos se declaran en la tabla: `UNIQUE`, `NOT NULL`, `CHECK`, claves foráneas.
- El servidor trabaja en modo estricto (`STRICT_TRANS_TABLES` y `ONLY_FULL_GROUP_BY`, activos por defecto): no se desactivan para que algo "funcione".

## Índices
- Índice en las columnas que se usan en `WHERE`, `JOIN` y `ORDER BY`. InnoDB crea solo el de cada clave foránea.
- En un índice de varias columnas el orden importa: sirve para las consultas que usan sus columnas de izquierda a derecha. Primero las que se comparan por igualdad.
- Cada índice cuesta en cada escritura: no se crea uno que ninguna consulta usa, ni dos que empiezan por las mismas columnas.
- Toda consulta nueva de listado o reporte se revisa con `EXPLAIN`: que use el índice esperado y no recorra la tabla entera (`type: ALL`).

## Consultas y transacciones
- Siempre con parámetros desde la aplicación; nunca uniendo texto.
- Se listan las columnas que se necesitan; nada de `SELECT *`.
- Las operaciones relacionadas van juntas en una transacción (`START TRANSACTION` … `COMMIT`), ni una por sentencia ni una enorme que dure minutos (manual, buenas prácticas de InnoDB).
- Para reservar filas antes de modificarlas, `SELECT … FOR UPDATE`. No `LOCK TABLES`.
- Listados grandes: paginación por la clave (`WHERE id > ? ORDER BY id LIMIT ?`), no con un `OFFSET` alto.
- Toda columna del `SELECT` que no es un agregado está en el `GROUP BY`.

## Cambios de esquema
- Todo cambio va en un **archivo nuevo**, numerado en orden, con su pareja que lo revierte. MySQL no trae una herramienta para esto: se usa la del proyecto, con su formato y su carpeta. Si no tiene ninguna, carpeta `migrations/` en la parte de la base de datos, con `0007_add_orders.up.sql` y `0007_add_orders.down.sql`.
- Un archivo de cambio ya versionado no se edita nunca: se corrige con otro.
- **En MySQL un cambio de estructura no se deshace con `ROLLBACK`**: `CREATE`, `ALTER` y `DROP` confirman la transacción en curso. Por eso va un solo cambio de estructura por archivo: si falla, se sabe hasta dónde llegó.
- En una tabla con datos, pide en el `ALTER` el modo que necesitas (`ALGORITHM=INSTANT` o `ALGORITHM=INPLACE, LOCK=NONE`): si esa operación no lo admite, falla en vez de bloquear la tabla. Qué admite cada operación está en el capítulo "Online DDL" del manual.
- Cambios que rompen (columna obligatoria nueva, renombrar, cambiar un tipo) se hacen en pasos: agregar aceptando nulos, rellenar, y recién entonces restringir.
- Un `down` que borra una columna o una tabla pierde datos: dilo antes de escribirlo.
- Nada de datos reales, usuarios ni contraseñas en un archivo de cambio.

## Procedimientos almacenados
- Solo si el plan los justifica. Nombres en minúsculas y `snake_case`, como las tablas.
- Parámetros y variables con prefijo (`p_` y `v_`): el manual advierte que una variable no debe llamarse igual que una columna, porque dentro del procedimiento el nombre se toma como la variable.
- `SQL SECURITY INVOKER` siempre que se pueda, y sin `DEFINER` de una cuenta con privilegios altos: es la recomendación del manual para que el procedimiento no pueda más que quien lo llama.
- **Nada de SQL dinámico armado con texto recibido.** Si hace falta `PREPARE`, los valores van con `?` y `EXECUTE … USING`.
- Los errores se señalan con `SIGNAL`. Un procedimiento que modifica varias tablas abre su transacción y declara un `HANDLER` para `SQLEXCEPTION` que hace `ROLLBACK` y vuelve a lanzar el error con `RESIGNAL`.
- Cambiar un procedimiento es reemplazarlo entero: el archivo `up` trae `DROP PROCEDURE IF EXISTS` y la definición nueva; el `down`, la anterior completa.
- En un archivo `.sql`, el cuerpo va entre `DELIMITER //` y `DELIMITER ;`. `DELIMITER` es una orden del cliente `mysql`, no SQL: el archivo se aplica con ese cliente.
- Cambiar los parámetros o las columnas que devuelve cambia el contrato con el código que lo llama: va en la entrega, con el antes y el después.

## Seguridad
- La aplicación se conecta con una cuenta propia que tiene solo los permisos que usa, sobre su base de datos. Nunca `root`, y nunca `GRANT ALL` (manual, guías de seguridad).
- Las contraseñas de las personas no se guardan en claro ni cifradas de forma reversible: las resume la aplicación antes de guardarlas.
- Ninguna credencial en los archivos del repositorio.

## Cómo probar un cambio
- Siempre contra una base de datos local o de pruebas, en la misma versión que producción (por ejemplo, un contenedor). Nunca contra una con datos reales.
- La secuencia completa: aplicar el `up`, comprobar el resultado, aplicar el `down`, comprobar que quedó como estaba, y aplicar el `up` otra vez.
- Un procedimiento se prueba llamándolo con `CALL` para cada caso de la tarea, incluidos los que deben fallar.
- Si el proyecto tiene pruebas de base de datos, las nuevas van en su misma carpeta; si no, las llamadas y su resultado esperado van en la entrega, para que QA las repita.

## Si el proyecto tiene sus propias convenciones
- Esta página es el estándar. Si el proyecto tiene una skill de convenciones propias, **en nombres, estructura, patrones y herramientas manda esa**, para que lo nuevo se parezca a lo que ya hay. Lo que ella no diga se hace como dice esta página.
- Las reglas de **Seguridad**, los parámetros en las consultas y el archivo de cambio con su reverso no admiten excepción. Si cumplirlas exige cambiar algo que tu tarea no cubre, detente y avisa.
- No renombres ni reorganices lo que tu tarea no toca. Lo que encuentres fuera del estándar va en la entrega, como deuda.
