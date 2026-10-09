---
name: php
description: Convenciones para escribir PHP sin framework según los estándares de PHP-FIG (PSR-1, PSR-4, PER Coding Style) y las recomendaciones del manual de PHP (tipos, errores, base de datos, seguridad, pruebas). Usar siempre que se cree o modifique un archivo .php.
metadata:
  madurez: redactada
---
# PHP — convenciones

Fuentes: el manual de PHP (php.net/manual) y los estándares de PHP-FIG (php-fig.org): PSR-1, PSR-4 y PER Coding Style 3.1, que reemplaza a PSR-12. Revisado el 2026-10-09. Ante una duda que esta página no resuelva, se consulta ahí, no en la costumbre.

## Versión
- Con soporte al 2026-10-09 (php.net/supported-versions): 8.4 y 8.5 con soporte activo; 8.3 solo recibe correcciones de seguridad (hasta 2027-12-31) y 8.2 las deja de recibir el 2026-12-31. Todo lo anterior ya no recibe correcciones.
- Un proyecto usa una versión con soporte activo y la declara en `composer.json` (`"require": {"php": "^8.4"}`).
- No escribas sintaxis que la versión declarada no entiende: el manual dice desde cuál existe cada cosa. Si el proyecto corre en una versión sin soporte, dilo en la entrega como riesgo.

## Estructura (PSR-4 y Composer)
```
composer.json        # dependencias y carga de clases; composer.lock también va en git
public/index.php     # único punto de entrada web; lo único que el servidor web expone
src/                 # el código, con el espacio de nombres del proyecto
tests/               # las pruebas, con la misma estructura que src/
vendor/              # lo instala Composer; nunca en git, nunca se edita
```
- Carga de clases por PSR-4, declarada en `composer.json`: el espacio de nombres corresponde a la carpeta y cada clase va en un archivo con su mismo nombre (`App\Pedidos\Pedido` → `src/Pedidos/Pedido.php`). Nada de `require` para cargar clases.
- Un archivo declara cosas (clases, funciones, constantes) **o** ejecuta algo (imprime, cambia la configuración, abre conexiones), nunca las dos (PSR-1).
- Solo `public/` queda al alcance del servidor web. Configuración, `src/`, `vendor/` y registros quedan fuera.
- Se separan tres responsabilidades: entrada y salida (leer la petición, validar, responder), reglas de negocio, y acceso a datos. Una clase recibe lo que necesita por el constructor; no lo busca en variables globales ni en instancias estáticas.
- La configuración que cambia entre entornos (credenciales, direcciones) viene de variables de entorno. Nunca en el código ni en git.

## Estilo (PER Coding Style) y nombres (PSR-1)
- Archivos en UTF-8 sin BOM, fin de línea LF, solo `<?php` (o `<?=` en plantillas) y sin `?>` final en los archivos que son solo PHP.
- Sangría de 4 espacios, sin tabuladores. Líneas de hasta 120 caracteres; mejor 80.
- Palabras reservadas y tipos en minúsculas y en su forma corta (`bool`, `int`).
- Clases en `PascalCase`, métodos en `camelCase`, constantes en `MAYUSCULAS_CON_GUION_BAJO`. Sin guion bajo inicial para marcar lo privado.
- La llave de apertura de clases y métodos va en su propia línea; la de `if`, `for`, `foreach`, `while` y `switch`, en la misma. Las estructuras de control llevan siempre llaves. `elseif`, no `else if`.
- Visibilidad escrita en toda propiedad, método y constante. Nunca `var`. Una propiedad por declaración.
- En listas de varias líneas (argumentos, arreglos), coma también después del último elemento.
- Orden de la cabecera: `<?php`, `declare(strict_types=1);`, `namespace`, y los `use` (clases, luego funciones, luego constantes).
- No se formatea a mano: lo aplica y lo comprueba `php-cs-fixer` con la regla `@PER-CS`.

## Tipos
- `declare(strict_types=1);` en todos los archivos.
- Tipo declarado en cada parámetro, valor de retorno y propiedad. `?Tipo` o `Tipo|null` cuando puede no haber valor; `void` cuando no devuelve nada. `mixed` solo cuando de verdad puede ser cualquier cosa.
- Lo que no cambia después de crearse, `readonly`. Un conjunto fijo de valores, un `enum`, no constantes sueltas ni textos.
- Comparaciones con `===` y `!==`.

## Errores
- Los errores se comunican con excepciones, de una clase propia por tipo de problema, y se atrapan donde se puede hacer algo con ellos. Nunca un `catch` vacío.
- Las excepciones no atrapadas llegan a un único manejador, que registra el detalle y responde con un mensaje genérico. A quien llama nunca le llega el mensaje interno, la consulta ni la traza.
- Configuración que recomienda el manual: en desarrollo, `error_reporting = E_ALL` y `display_errors = On`; en producción, `display_errors = Off` y `log_errors = On`.
- No se usa `@` para callar errores.
- Los registros no contienen contraseñas, tokens ni datos personales completos.

## Base de datos
- **Sentencias preparadas siempre**, con PDO o `mysqli`: es lo que el manual llama la forma más fácil y segura de pasar datos a una consulta. Ningún valor se une al texto del SQL.
- Lo que no puede ser un parámetro (nombre de tabla o de columna, `ASC`/`DESC`) se elige de una lista fija escrita en el código.
- PDO: `PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION`, `PDO::ATTR_EMULATE_PREPARES => false`, y el juego de caracteres en la cadena de conexión.
- La aplicación se conecta con un usuario de base de datos propio, con los permisos mínimos; nunca como administrador.
- Lo que modifica varias tablas va en una transacción (`beginTransaction`, `commit`, y `rollBack` en el `catch`).
- El SQL vive solo en la capa de datos.

## Seguridad
- **Salida:** todo dato que se imprime en HTML pasa por `htmlspecialchars($valor, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` en el momento de imprimirlo, venga de la persona o de la base de datos.
- **Entrada:** se valida al llegar (tipo, rango, longitud, formato), con `filter_var()` y sus filtros donde alcancen. Validar no reemplaza a escapar la salida ni a las sentencias preparadas.
- **Contraseñas:** `password_hash($clave, PASSWORD_DEFAULT)`, `password_verify()` y `password_needs_rehash()` al iniciar sesión. Nunca MD5, SHA-1 ni un cifrado reversible.
- **Sesiones:** `session.use_strict_mode = 1`; cookie con `HttpOnly`, `Secure` y `SameSite`; `session_regenerate_id(true)` al iniciar sesión y al cambiar de permisos. Después de `header('Location: …')` va siempre `exit;`.
- **CSRF:** todo formulario o petición que cambia datos lleva un token creado con `random_bytes()` y comprobado con `hash_equals()`.
- **Aleatorios:** `random_bytes()` y `random_int()`. Nunca `rand()`, `mt_rand()` ni `uniqid()` para algo que deba ser secreto.
- **Nunca** `eval()`, `unserialize()` sobre datos recibidos (para intercambiar datos, `json_decode()`), ni `include` o `require` con una ruta armada con datos recibidos.
- **Archivos subidos:** se mueven con `move_uploaded_file()`, no se confía en el nombre ni en el tipo que manda el navegador, se guardan con un nombre generado y fuera de `public/`.
- **Llamadas a otros servicios:** la verificación del certificado queda encendida y toda llamada lleva tiempo límite.
- **Dependencias:** `composer audit` sin vulnerabilidades conocidas.

## Pruebas
- PHPUnit, configurado en `phpunit.xml`. Las pruebas van en `tests/`, repitiendo la estructura de `src/`: la clase `src/Pedidos/Pedido.php` se prueba en `tests/Pedidos/PedidoTest.php`.
- Las reglas de negocio se prueban solas, reemplazando el acceso a datos por un doble. El acceso a datos se prueba contra una base de datos de pruebas, nunca la real.
- Análisis estático con PHPStan.

## Comandos
| Para | Comando |
|---|---|
| Comprobar el formato | `vendor/bin/php-cs-fixer fix --dry-run --diff` |
| Análisis estático | `vendor/bin/phpstan analyse` |
| Pruebas | `vendor/bin/phpunit` |
| Vulnerabilidades en dependencias | `composer audit` |
| Sintaxis de un archivo | `php -l archivo.php` |

Los que el proyecto tiene de verdad están en su perfil; no instales una herramienta que el plan no pidió.

## Si el proyecto tiene sus propias convenciones
- Esta página es el estándar. Si el proyecto tiene una skill de convenciones propias, **en nombres, estructura, patrones y bibliotecas manda esa**, para que el código nuevo se parezca al que ya hay. Lo que ella no diga se hace como dice esta página.
- Las reglas de **Seguridad** y las sentencias preparadas de **Base de datos** no admiten excepción. Si cumplirlas exige cambiar algo que tu tarea no cubre, detente y avisa.
- No reformatees ni reorganices lo que tu tarea no toca. Lo que encuentres fuera del estándar va en la entrega, como deuda.
