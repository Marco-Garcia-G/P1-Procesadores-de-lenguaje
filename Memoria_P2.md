# PROCESADORES DEL LENGUAJE
## GRADO EN INGENIERÍA INFORMÁTICA

---

## MEMORIA DE LA PRÁCTICA
### Práctica 2 — Generación del analizador sintáctico o parser
### Curso 2025/2026

---

**DATOS DE LOS AUTORES**

| | |
|---|---|
| **Nombre** | Marco García |
| **Correo electrónico** | [correo]@alumnos.uc3m.es |
| **Grupo de clase** | [Grupo] |
| **Titulación cursada** | Grado en Ingeniería Informática |

| | |
|---|---|
| **Nombre** | Pablo Roig |
| **Correo electrónico** | [correo]@alumnos.uc3m.es |
| **Grupo de clase** | [Grupo] |
| **Titulación cursada** | Grado en Ingeniería Informática |

---

## ÍNDICE

1. Introducción y objetivos
2. Estructura general de la solución
3. Analizador léxico
4. Analizador sintáctico
5. Definición formal de la gramática
6. Precedencia y asociatividad
7. Validaciones adicionales orientadas a P2
8. Punto de entrada y modos de ejecución
9. Batería de pruebas
10. Decisiones de diseño y problemas encontrados
11. Conclusiones

---

## 1. Introducción y objetivos

Esta memoria documenta el diseño e implementación del analizador sintáctico correspondiente a la segunda entrega de la práctica de Procesadores del Lenguaje. El objetivo de esta fase es construir, sobre el analizador léxico entregado en P1, un parser capaz de determinar si una secuencia de tokens pertenece al lenguaje Lava tal y como queda definido en el enunciado.

Para su implementación se ha empleado la librería `ply.yacc`, que genera tablas LALR(1) a partir de las reglas de producción definidas en Python. La gramática resultante es capaz de reconocer el lenguaje completo: tipos básicos, registros, expresiones aritméticas y lógicas con precedencia correcta, control de flujo (if-else, while, do-while), funciones con y sin parámetros, y todos los casos límite descritos en la especificación.

Además de reconocer la sintaxis general del lenguaje, la solución incorpora una capa adicional de validación estructural orientada a P2 para rechazar ciertos programas que, aunque podrían resultar gramaticalmente válidos con una gramática demasiado permisiva, el enunciado declara expresamente inválidos. En concreto se comprueban: la validez del lado izquierdo de una asignación, el contexto de uso de `break`, el contexto de uso de `return` y la presencia obligatoria de retorno en funciones no void.

En esta entrega no se realiza análisis semántico completo de tipos, tablas de símbolos ni conversiones automáticas; esas tareas quedan reservadas para P3.

---

## 2. Estructura general de la solución

La implementación se ha dividido en tres ficheros principales:

- **`lexer.py`**: define el conjunto de tokens del lenguaje, las expresiones regulares asociadas y la función `build_lexer()` que construye y devuelve el analizador léxico.
- **`parser.py`**: define la gramática del lenguaje mediante reglas de producción de PLY, establece la tabla de precedencia de operadores, construye una representación estructural intermedia (nodos) y realiza validaciones adicionales sobre el resultado del parseo.
- **`main.py`**: actúa como punto de entrada del programa. Gestiona la lectura del fichero de entrada, el modo de ejecución normal (parser completo) y el modo opcional `--token` (solo lexer).

Adicionalmente, el subdirectorio `tests/` contiene una batería de 22 casos de prueba organizados en válidos e inválidos, junto con un script `run_tests.py` que automatiza su ejecución.

La visión de conjunto es la siguiente: el lexer convierte el texto fuente en una secuencia de tokens; el parser consume esos tokens, construye una representación estructural del programa y aplica validaciones de contexto; finalmente, `main.py` orquesta el proceso e informa al usuario del resultado.

---

## 3. Analizador léxico

El analizador léxico implementado en P1 se reutiliza sin modificaciones funcionales en esta entrega. Su objetivo es transformar la secuencia de caracteres de entrada en una secuencia de tokens que el parser puede consumir.

### 3.1. Palabras reservadas

El lexer mantiene un diccionario `reserved` que asocia cada palabra reservada del lenguaje con su nombre de token. La regla de identificadores consulta este diccionario para decidir si el lexema reconocido debe tratarse como `ID` o como una palabra reservada. Las palabras reservadas implementadas son:

| Token | Lexema |
|---|---|
| `TRUE` / `FALSE` | `true` / `false` |
| `INT` / `FLOAT` / `CHAR` / `BOOLEAN` | `int` / `float` / `char` / `boolean` |
| `VOID` | `void` |
| `RETURN` | `return` |
| `IF` / `ELSE` | `if` / `else` |
| `DO` / `WHILE` | `do` / `while` |
| `BREAK` | `break` |
| `PRINT` | `print` |
| `NEW` / `RECORD` | `new` / `record` |

### 3.2. Tokens del lenguaje

Los tokens definidos cubren:

| Categoría | Tokens |
|---|---|
| Identificadores | `ID` |
| Literales | `INT_VALUE`, `FLOAT_VALUE`, `CHAR_VALUE` |
| Asignación y comparación | `ASSIGN` (`=`), `EQ` (`==`), `GT` (`>`), `GE` (`>=`), `LT` (`<`), `LE` (`<=`) |
| Aritméticos y lógicos | `PLUS` (`+`), `MINUS` (`-`), `TIMES` (`*`), `DIVIDE` (`/`), `AND` (`&&`), `OR` (`\|\|`), `NOT` (`!`) |
| Acceso a campo | `DOT` (`.`) |
| Separadores y delimitadores | `COMMA` (`,`), `SEMICOLON` (`;`), `LPAREN` (`(`), `RPAREN` (`)`), `LBRACE` (`{`), `RBRACE` (`}`) |

### 3.3. Literales

Los literales enteros aceptan notación decimal (sin ceros a la izquierda), binaria (`0b`), octal (`0`) y hexadecimal (`0x` con dígitos en mayúsculas). Los literales reales admiten notación con punto decimal y notación científica con exponente (`e±`). Los literales de carácter se reconocen entre comillas simples y soportan secuencias de escape.

### 3.4. Comentarios y saltos de línea

Se soportan dos tipos de comentarios: de línea (`//` hasta fin de línea) y de bloque (`/* ... */`). Ambos se ignoran, pero el de bloque actualiza el contador de líneas según los saltos de línea que contenga, evitando desajustes en los mensajes de error. Los saltos de línea se procesan mediante una regla específica para actualizar `lineno`.

### 3.5. Gestión de errores léxicos

Cuando el lexer encuentra un carácter ilegal, registra un mensaje de error con el carácter y la línea en `lexer.errors` y avanza una posición con `lexer.skip(1)`, permitiendo continuar el análisis.

---

## 4. Analizador sintáctico

### 4.1. Visión general

El parser se implementa con `ply.yacc` siguiendo una gramática de estilo LALR(1). Su objetivo es reconocer la estructura global de un programa Lava. La gramática cubre:

- Programas vacíos o formados solo por delimitadores (`;`)
- Declaraciones de tipos primitivos, simples y múltiples
- Declaraciones de variables de tipo registro con inicialización obligatoria
- Declaraciones de registros (`record`)
- Funciones con tipo de retorno primitivo, tipo registro o `void`
- Expresiones aritméticas, lógicas y comparativas con precedencia correcta
- Llamadas a funciones y acceso por punto a campos de registro
- Construcción de registros con `new`
- Estructuras `if`, `if-else`, `while` y `do-while`
- Sentencias `break`, `return` y `print`

### 4.2. Representación estructural intermedia

Durante el parseo se construyen nodos mediante la función auxiliar `node(kind, line, **data)`. Cada nodo es un diccionario que contiene el tipo de construcción (`kind`), la línea de origen y los datos específicos de cada producción. Esta representación no es un AST completo de compilador, pero sí una estructura suficiente para realizar la validación adicional de restricciones de contexto que el enunciado exige y que una gramática libre de contexto pura no puede expresar cómodamente.

Los tipos de nodo construidos son: `function`, `record_decl`, `decl`, `assign`, `break`, `return`, `print`, `expr`, `if`, `while`, `do_while`, `call`, `field`, `id`, `literal`, `unary`, `binary` y `new`.

### 4.3. Símbolo inicial y estructura global del programa

El símbolo inicial es `program`, que deriva en una lista opcional de elementos de programa `program_items_opt`. Esto permite aceptar de forma natural ficheros vacíos, ficheros con solo saltos de línea y ficheros con solo `;`, tal como especifica el enunciado.

Un elemento de programa (`program_item`) puede ser:

- Un `;` aislado (ignorado)
- Una declaración de registro: `record_decl SEMICOLON`
- Una función con retorno void, primitivo o de tipo registro
- Una declaración de variable con o sin inicialización
- Una estructura de control
- Una sentencia simple terminada en `;`

Las declaraciones de funciones y de registros **solo se permiten a nivel global** (`program_item`), no dentro de bloques (`block_item`). Esta restricción se impone directamente en la gramática.

### 4.4. Separación entre tipos primitivos y tipos de registro

Una de las decisiones de diseño más relevantes es distinguir en la gramática entre `primitive_type` (`INT | FLOAT | CHAR | BOOLEAN`) y `custom_type` (`ID`).

Esta separación permite modelar correctamente una restricción central del enunciado: **las variables de tipo registro deben declararse siempre con inicialización**. Para `primitive_type` se admite tanto la declaración simple, como la multideclaración y la inicialización. Para `custom_type` solo se permite la forma con inicialización. De este modo:

- `int a, b;` → válido (multideclaración primitiva)
- `float x = 3.14;` → válido (inicialización primitiva)
- `Point p = new Point(1, 2);` → válido (inicialización de registro)
- `Point p;` → **error sintáctico** (declaración de registro sin inicialización)
- `Point a, b;` → **error sintáctico** (multideclaración de registro)

Esta restricción se impone a nivel gramatical, sin necesidad de comprobación semántica posterior.

### 4.5. Jerarquía de expresiones

La gramática de expresiones se organiza en tres niveles de no terminales:

1. **`primary_expr`**: elementos atómicos — literales, identificadores (`ID`), expresiones parentizadas y construcción con `new`.
2. **`postfix_expr`**: expresiones primarias más llamadas a función (`postfix_expr LPAREN arg_list_opt RPAREN`) y acceso a campo (`postfix_expr DOT ID`). La recursión por la izquierda permite encadenar accesos y llamadas de forma natural.
3. **`expression`**: operaciones unarias (`PLUS`, `MINUS` unarios, `NOT`) y binarias aritméticas, lógicas y comparativas.

Esta jerarquía garantiza que las llamadas a función y los accesos a campo tienen mayor precedencia que cualquier operador, sin necesidad de incluir `DOT` en la tabla de precedencia. El resultado es que expresiones como `p.x * 2` o `f(a).campo` se parsean correctamente.

### 4.6. Asignaciones y validación del lvalue

La regla de asignación es:

```
assignment : postfix_expr ASSIGN expression
```

El lado izquierdo se parsea como `postfix_expr` para soportar accesos encadenados como `p.velocity.x = 3.0`. Sin embargo, no toda `postfix_expr` es un destino de asignación válido: una llamada `f()` o una expresión `new Point(...)` no lo son.

La validación se realiza después del parseo mediante la función `is_lvalue(expr)`, que acepta únicamente:

- Nodos de tipo `id` (identificador simple)
- Nodos de tipo `field` cuyo valor base también sea un lvalue

Con esto se rechazan en la fase de validación:

- `f() = 3;` → destino inválido (llamada a función)
- `(a + b) = 4;` → destino inválido (expresión aritmética)
- `new Circle(1) = 2;` → destino inválido (instanciación)

### 4.7. Control de flujo

Los bloques son obligatorios en todas las estructuras de control (`if`, `while`, `do-while`). Esta decisión elimina por completo el problema del *dangling else*, ya que nunca hay ambigüedad sobre a qué `if` pertenece un `else` cuando el cuerpo siempre está delimitado por llaves.

La sentencia `do-while` sigue la forma `DO block WHILE LPAREN expression RPAREN` sin punto y coma final, tal como muestra la especificación.

### 4.8. Funciones y tipo de retorno void

El tipo de retorno `void` se trata de forma separada en la gramática para evitar que se pueda declarar una variable de tipo `void`. Las funciones con tipo de retorno `void` se reconocen mediante:

```
program_item : VOID ID LPAREN param_list_opt RPAREN block
```

Si `void` se hubiera incluido dentro de `primitive_type`, la gramática habría aceptado declaraciones como `void x;`, lo que no tiene sentido.

La verificación de que una función `void` no contiene `return` con valor, y de que una función no `void` contiene al menos un `return` con expresión, se delega a la fase de validación estructural.

### 4.9. Registros

La declaración de un tipo registro sigue la forma:

```
record ID ( field_list_opt ) ;
```

Cada campo es un par `tipo nombre`, donde el tipo puede ser `any_type` (primitivo o de registro). Los campos se reutilizan en la misma estructura que los parámetros de función.

La instanciación con `new` se modela como una expresión primaria:

```
primary_expr : NEW ID LPAREN arg_list_opt RPAREN
```

Al ser una `primary_expr`, puede aparecer en cualquier lugar donde se espere un valor.

---

## 5. Definición formal de la gramática

Formalmente, la gramática implementada es una 4-tupla `G = (Vn, Vt, P, S)`:

**S** = `program`

**Vn** (no terminales principales):

```
program                  program_items_opt
program_item             record_decl
field_list_opt           field_list           field_decl
param_list_opt           param_list           param_decl
block                    block_items_opt      block_item
plain_simple_statement   control_statement
primitive_id_list_tail   comma_id_list
assignment
primitive_type           custom_type          any_type
expression               postfix_expr         primary_expr
literal
arg_list_opt             arg_list
empty
```

**Vt**: todos los tokens definidos en el lexer (ver sección 3).

**P** (producciones principales):

```
program → program_items_opt

program_items_opt → empty
                  | program_items_opt program_item

program_item → SEMICOLON
             | record_decl SEMICOLON
             | VOID ID LPAREN param_list_opt RPAREN block
             | primitive_type ID LPAREN param_list_opt RPAREN block
             | custom_type   ID LPAREN param_list_opt RPAREN block
             | primitive_type ID ASSIGN expression SEMICOLON
             | primitive_type ID primitive_id_list_tail SEMICOLON
             | custom_type   ID ASSIGN expression SEMICOLON
             | control_statement
             | plain_simple_statement SEMICOLON

record_decl → RECORD ID LPAREN field_list_opt RPAREN

field_list_opt → empty | field_list
field_list     → field_decl | field_list COMMA field_decl
field_decl     → any_type ID

param_list_opt → empty | param_list
param_list     → param_decl | param_list COMMA param_decl
param_decl     → any_type ID

block            → LBRACE block_items_opt RBRACE
block_items_opt  → empty | block_items_opt block_item
block_item       → SEMICOLON
                 | control_statement
                 | primitive_type ID ASSIGN expression SEMICOLON
                 | primitive_type ID primitive_id_list_tail SEMICOLON
                 | custom_type   ID ASSIGN expression SEMICOLON
                 | plain_simple_statement SEMICOLON

plain_simple_statement → assignment
                       | BREAK
                       | RETURN
                       | RETURN expression
                       | PRINT LPAREN expression RPAREN
                       | expression

control_statement → IF LPAREN expression RPAREN block
                  | IF LPAREN expression RPAREN block ELSE block
                  | WHILE LPAREN expression RPAREN block
                  | DO block WHILE LPAREN expression RPAREN

primitive_id_list_tail → empty | comma_id_list
comma_id_list          → COMMA ID
                       | comma_id_list COMMA ID

assignment → postfix_expr ASSIGN expression

primitive_type → INT | FLOAT | CHAR | BOOLEAN
custom_type    → ID
any_type       → primitive_type | custom_type

expression → postfix_expr
           | PLUS  expression  %prec UPLUS
           | MINUS expression  %prec UMINUS
           | NOT   expression
           | expression TIMES  expression
           | expression DIVIDE expression
           | expression PLUS   expression
           | expression MINUS  expression
           | expression GT  expression
           | expression GE  expression
           | expression LT  expression
           | expression LE  expression
           | expression EQ  expression
           | expression AND expression
           | expression OR  expression

postfix_expr → primary_expr
             | postfix_expr LPAREN arg_list_opt RPAREN
             | postfix_expr DOT ID

primary_expr → literal
             | ID
             | LPAREN expression RPAREN
             | NEW ID LPAREN arg_list_opt RPAREN

literal → INT_VALUE | FLOAT_VALUE | CHAR_VALUE | TRUE | FALSE

arg_list_opt → empty | arg_list
arg_list     → expression | arg_list COMMA expression

empty → ε
```

---

## 6. Precedencia y asociatividad

### 6.1. Por qué se usa `precedence`

El enunciado recomienda usar la herramienta de precedencia de PLY en lugar de estratificar la gramática en múltiples niveles de no terminales para operadores binarios. Esta implementación sigue esa recomendación para los operadores binarios.

### 6.2. Tabla de precedencia

La tabla declarada en el parser, ordenada de menor a mayor prioridad:

| Nivel | Token(s) | Asociatividad | Justificación |
|---|---|---|---|
| 1 (menor) | `OR` | left | Disyunción lógica, menor precedencia booleana |
| 2 | `AND` | left | Conjunción lógica |
| 3 | `EQ`, `GT`, `GE`, `LT`, `LE` | nonassoc | Comparativos; nonassoc evita `a == b == c` |
| 4 | `PLUS`, `MINUS` | left | Suma y resta binarias |
| 5 | `TIMES`, `DIVIDE` | left | Multiplicación y división |
| 6 (mayor) | `NOT`, `UPLUS`, `UMINUS` | right | Operadores unarios; right por corrección |

Esta tabla sigue el estándar de precedencia de Java, tal como sugiere el enunciado. La elección `nonassoc` para los comparativos impide expresiones como `a == b == c`, que no tienen un significado claro en Lava.

### 6.3. Operadores unarios UMINUS y UPLUS

El token `MINUS` aparece tanto como operador binario de sustracción como operador unario de negación. Para resolver la ambigüedad, se declaran dos pseudo-tokens ficticioss `UMINUS` y `UPLUS` con mayor precedencia, y se anotan las reglas de los operadores unarios con `%prec`:

```python
"expression : MINUS expression %prec UMINUS"
"expression : PLUS  expression %prec UPLUS"
```

Con esto, `-a + b` se interpreta como `(-a) + b` (lo correcto), no como `-(a + b)`.

### 6.4. Acceso a campo y llamadas: precedencia estructural

El acceso a campo (`.`) y las llamadas a función no se incluyen en la tabla de precedencia. Su precedencia máxima se garantiza estructuralmente mediante la jerarquía `primary_expr` → `postfix_expr` → `expression`: las operaciones postfijas siempre se reducen antes que cualquier operador binario o unario. Esto elimina la necesidad de incluir `DOT` en la tabla y simplifica el parser.

### 6.5. Ausencia del conflicto dangling else

En esta implementación no existe el conflicto shift/reduce del *dangling else*. La razón es que todas las ramas de control de flujo (`if`, `while`, `do-while`) exigen un bloque delimitado por llaves, no una sentencia desnuda. Por tanto, no hay ambigüedad posible sobre a qué `if` pertenece un `else`. No fue necesario el truco del token ficticio `IFX`.

---

## 7. Validaciones adicionales orientadas a P2

Esta es la sección más diferencial de la implementación. El parser no se limita a aceptar o rechazar según la gramática libre de contexto, sino que realiza una validación estructural sobre los nodos construidos durante el parseo. Esta validación recorre el árbol de nodos y comprueba restricciones de contexto que una CFG no puede expresar sin complicar enormemente la gramática.

La función central es `validate_program(items)`, que itera sobre los elementos del programa y despacha la validación de cada función a `validate_function()` y de cada sentencia a `validate_item()`.

### 7.1. Validez del lado izquierdo de una asignación

La función `is_lvalue(expr)` comprueba si un nodo es un destino de asignación válido. Solo acepta:

- Nodo `id`: identificador simple (`x`)
- Nodo `field` cuyo base también sea un lvalue: acceso a campo (`p.x`, `p.velocity.x`)

Cualquier otra expresión (llamada a función, `new`, operación aritmética, literal) es rechazada con el mensaje `[ERROR] Lado izquierdo de asignación inválido en la línea N`.

### 7.2. Uso correcto de `break`

La función `validate_block()` propaga el flag `in_loop` al descender en bucles (`while`, `do-while`), pero no al descender en bloques `if`. Cuando se encuentra un nodo `break` y `in_loop` es falso, se genera el error `[ERROR] 'break' fuera de bucle en la línea N`. Así:

- `while (...) { break; }` → válido
- `if (...) { break; }` fuera de bucle → **inválido**
- `break;` a nivel global → **inválido**

### 7.3. Uso correcto de `return`

Cuando se valida un nodo `return`, se comprueban tres condiciones:

1. **`return` fuera de función**: si `in_function` es falso → `[ERROR] 'return' fuera de función en la línea N`.
2. **`return` en función `void`**: si `function_type == "void"` → `[ERROR] 'return' no permitido en función void en la línea N`.
3. **`return` sin expresión en función no void**: si el nodo tiene `value=None` → `[ERROR] 'return' sin expresión en función no void en la línea N`.

### 7.4. Presencia obligatoria de `return` en funciones no void

La función `validate_function()` mantiene un estado `has_value_return` que se activa cuando se encuentra un `return` con expresión dentro del cuerpo de la función. Si al finalizar el recorrido del cuerpo este flag sigue en falso para una función no void, se genera el error `[ERROR] La función 'nombre' debe contener al menos un return con expresión en la línea N`.

Esta comprobación no intenta análisis de flujo exhaustivo (no verifica que todos los caminos de ejecución lleguen a un `return`), sino que comprueba la presencia estructural de al menos un `return` con valor. Para P2 esta aproximación es razonable y defendible.

### 7.5. Acumulación y reporte de errores

La función `parse_text(text)` combina en una sola lista los errores léxicos registrados en `lexer.errors`, los errores de parseo en `_parse_errors` y los errores de validación devueltos por `validate_program()`. Si la lista está vacía, el programa es aceptado; en caso contrario, cada error se imprime en stdout y se devuelve código de salida 1.

---

## 8. Punto de entrada y modos de ejecución

El fichero `main.py` es el único punto de entrada del programa. Gestiona dos modos de operación:

### 8.1. Modo normal

```bash
python3 main.py fichero.lava
```

Lee el fichero, llama a `parse_text()` y:
- Si el programa es sintácticamente válido: no produce salida y termina con código 0.
- Si hay errores: imprime cada mensaje de error y termina con código 1.

### 8.2. Modo `--token`

```bash
python3 main.py --token fichero.lava
```

Ejecuta únicamente el analizador léxico y genera un fichero `.token` con el mismo nombre base que el fichero de entrada, siguiendo el formato heredado de P1:

```
TIPO, VALOR, LINEA, COLUMNA_INICIO, COLUMNA_FIN
```

El cálculo de columnas se realiza buscando el último salto de línea antes de la posición `lexpos` del token. Mantener este modo en P2 permite seguir validando el lexer de forma independiente y muestra continuidad entre entregas.

### 8.3. Integración léxico-parser

PLY requiere que el parser tenga acceso al lexer durante el proceso de análisis. En lugar de precargar todos los tokens, el objeto lexer se pasa directamente al método `parse()`:

```python
_parser.parse(text, lexer=lexer)
```

Esto hace que el parser llame internamente al lexer token a token, bajo demanda, a medida que necesita el siguiente símbolo de lookahead. El flujo es completamente on-the-fly.

---

## 9. Batería de pruebas

Se ha desarrollado una batería de 22 casos de prueba organizada en:

- `tests/valid/`: 9 programas que deben aceptarse sin salida.
- `tests/invalid/`: 13 programas que deben rechazarse.
- `tests/expected_invalid/`: salida esperada exacta para cada caso inválido.
- `tests/run_tests.py`: script de automatización.

Para ejecutar:

```bash
cd P2_MARCO_GARCIA_PABLO_ROIG/tests
python3 run_tests.py
```

Resultado esperado: `Summary: 22/22 passed`.

### 9.1. Casos válidos

| Caso | Descripción |
|---|---|
| `01_newlines_only.lava` | Fichero con solo saltos de línea |
| `02_semicolons_only.lava` | Fichero con solo `;` |
| `03_primitive_decls.lava` | Declaraciones simples y múltiples de tipos primitivos, asignaciones, `print` |
| `04_records_access.lava` | Registro, instanciación con `new` y acceso por punto |
| `05_control_flow.lava` | `do-while`, `while`, `if` anidado con `break` |
| `06_functions_calls.lava` | Función con parámetros, llamada, uso del valor de retorno |
| `07_record_function_return.lava` | Función que devuelve un registro, instanciación e `new` como retorno |
| `08_nested_fields.lava` | Registros anidados y acceso encadenado por punto |
| `09_precedence_parentheses.lava` | Expresiones con precedencia de operadores y paréntesis |

### 9.2. Casos inválidos

| Caso | Error esperado |
|---|---|
| `01_invalid_assignment_call.lava` | `f() = 3;` — lvalue inválido (llamada a función) |
| `02_invalid_assignment_expr.lava` | `(a+b) = 3;` — lvalue inválido (expresión) |
| `03_invalid_record_without_init.lava` | `Point p;` — declaración de registro sin inicialización |
| `04_invalid_record_multidecl.lava` | `Point a, b;` — multideclaración de tipo registro |
| `05_invalid_break_top.lava` | `break;` a nivel global |
| `06_invalid_break_in_if.lava` | `break;` dentro de `if` sin bucle exterior |
| `07_invalid_return_top.lava` | `return 1;` a nivel global |
| `08_invalid_void_return.lava` | `return expr;` en función void |
| `09_invalid_nonvoid_missing_return.lava` | Función no void sin ningún `return` |
| `10_invalid_nonvoid_empty_return.lava` | `return;` sin expresión en función no void |
| `11_invalid_multidecl_with_assign.lava` | `float d, e = 0;` — multideclaración con asignación |
| `12_invalid_unexpected_eof.lava` | Fin de archivo inesperado |
| `13_invalid_chained_assignment.lava` | Asignación encadenada inválida |

La batería incluye especialmente los casos límite que el enunciado especifica como errores, verificando que el parser los detecta y reporta con el formato correcto.

---

## 10. Decisiones de diseño y problemas encontrados

### 10.1. Separación entre `primitive_type` y `custom_type`

Esta es la decisión de diseño más importante de la implementación. Una alternativa más simple habría sido definir un único no terminal `type` que englobara tanto los tipos primitivos como los identificadores de tipo registro. Sin embargo, eso habría obligado a tratar la restricción de inicialización obligatoria de registros en la fase semántica.

Al separar explícitamente `primitive_type` y `custom_type` en la gramática, la restricción se impone directamente en las producciones de `program_item` y `block_item`: para `custom_type` solo existe la alternativa con `ASSIGN`, nunca la de declaración sin inicialización ni la multideclaración. Esto simplifica enormemente el análisis posterior.

### 10.2. Jerarquía `primary_expr` → `postfix_expr` → `expression`

En lugar de utilizar una única regla `expr` plana con la tabla de precedencia para todos los operadores, se optó por organizar las expresiones en tres niveles. Esto es más natural para modelar el hecho de que las llamadas a función y los accesos a campo se comportan como operadores de altísima precedencia que se encadenan de derecha a izquierda sobre su base.

Esta estructura también simplifica la validación de lvalues: los nodos `field` siempre tienen una estructura predecible (base + nombre de campo) que `is_lvalue()` puede recorrer recursivamente.

### 10.3. Ausencia de conflictos shift/reduce

Gracias a las decisiones de diseño adoptadas, el parser genera las tablas LALR sin ningún warning ni conflicto:

- **No dangling else**: los bloques son obligatorios, eliminando la ambigüedad.
- **UMINUS/UPLUS**: resuelven el doble papel de `PLUS` y `MINUS`.
- **Estructura de expresiones**: la jerarquía elimina la necesidad de incluir `DOT` en la tabla de precedencia.
- **Separación `primitive_type`/`custom_type`**: elimina ambigüedades en las declaraciones.

### 10.4. Validación estructural post-parseo en lugar de gramática más compleja

Las restricciones de contexto (`break` en bucle, `return` en función, tipo de retorno) podrían intentarse expresar puramente en la gramática libre de contexto, pero el coste sería inaceptable: habría que duplicar todos los no terminales de bloques y sentencias en versiones "dentro de bucle", "dentro de función void", etc. Esto viola el principio de simplicidad y hace el parser innecesariamente difícil de mantener.

La alternativa adoptada —parsear libremente y validar estructuralmente después— es mucho más limpia y produce mensajes de error informativos con número de línea.

### 10.5. Problema: multideclaración con asignación

El enunciado establece que `float d, e = 0xFF;` debe ser un error sintáctico. La gramática lo rechaza de forma natural porque la producción `primitive_type ID primitive_id_list_tail SEMICOLON` construye una lista de solo identificadores (sin expresiones de inicialización), y la producción `primitive_type ID ASSIGN expression SEMICOLON` solo acepta un único identificador. No existe ninguna producción que combine la lista de identificadores con un valor inicial, por lo que el parser rechaza directamente ese caso sin necesitar ningún control adicional.

---

## 11. Uso de inteligencia artificial generativa

De acuerdo con la normativa de la asignatura, queremos declarar el uso de herramientas de IA generativa (Claude y Gemini) durante el desarrollo de la práctica.

Hemos utilizado la IA principalmente como apoyo para:

- **Investigar patrones de diseño** en construcción de parsers con PLY cuando encontramos enfoques que producían conflictos o estructuras demasiado repetitivas.
- **Depurar conflictos de la gramática**, especialmente al explorar por qué ciertas formulaciones generaban warnings en las tablas LALR y qué alternativas podían resolverlos sin introducir complejidad innecesaria.
- **Estructurar la memoria** y ayudarnos a describir con mayor precisión las decisiones de diseño que ya habíamos tomado e implementado.

Todo el código resultante ha sido analizado, adaptado a nuestra estructura y comprendido en su totalidad. Las decisiones de diseño reflejadas tanto en el código como en esta memoria son nuestras.

---

## 12. Conclusiones

El desarrollo del analizador sintáctico ha sido la fase más exigente del proyecto hasta el momento, especialmente en lo que respecta al diseño de la gramática y a la elección de qué restricciones imponer a nivel gramatical frente a cuáles delegar a una validación posterior.

La gramática resultante cubre la totalidad de las construcciones del lenguaje Lava descritas en el enunciado y genera las tablas LALR sin ningún conflicto ni warning. La separación entre tipos primitivos y tipos de registro, la jerarquía de expresiones en tres niveles y la validación estructural post-parseo son los tres pilares que permiten que el analizador rechace correctamente todos los casos inválidos sin necesitar un análisis semántico completo.

Además, la batería de pruebas desarrollada verifica de forma automática tanto los casos válidos como los casos límite inválidos, aportando evidencia objetiva del correcto funcionamiento del parser.

El mayor aprendizaje de esta entrega ha sido entender que una gramática no es solo una descripción formal de un lenguaje, sino también un mecanismo de control: diseñar bien las producciones permite rechazar código incorrecto sin necesitar análisis semántico, simplificando las fases posteriores del compilador.

La implementación deja una base sólida para la siguiente entrega, donde habrá que añadir acciones semánticas —tabla de símbolos, comprobación de tipos, resolución de sobrecarga— sobre la estructura ya establecida, sin necesidad de reestructurar la gramática.
