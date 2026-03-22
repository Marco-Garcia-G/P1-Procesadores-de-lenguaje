# Guia extensa para la memoria de P2

Este documento esta pensado como base para redactar la memoria de la practica 2 del lenguaje Lava. No sustituye a la memoria final en PDF, pero contiene la estructura, la logica y el contenido tecnico necesario para que puedas convertirlo en una memoria completa, coherente y defendible.

La idea correcta no es copiar esto sin pensar, sino usarlo como plantilla y adaptarlo a vuestro tono, decisiones y estilo. Aun asi, el contenido esta alineado con la implementacion actual de:

- `P2_MARCO_GARCIA_PABLO_ROIG/lexer.py`
- `P2_MARCO_GARCIA_PABLO_ROIG/parser.py`
- `P2_MARCO_GARCIA_PABLO_ROIG/main.py`
- `P2_MARCO_GARCIA_PABLO_ROIG/tests/`

## Como usar esta guia

1. Crea la memoria final en un procesador de texto o en LaTeX.
2. Copia la estructura propuesta.
3. Reescribe con vuestra voz lo que aqui aparece.
4. Manteneos fieles al codigo real.
5. Añadid capturas o fragmentos pequenos de codigo solo cuando ayuden.
6. Exportad a PDF con el nombre que vayais a entregar.

Conviene que la memoria final tenga entre 6 y 12 paginas utiles, dependiendo del formato. Menos puede quedarse corta; mucho mas puede hacerla pesada si repite cosas obvias.

## Propuesta de estructura final de la memoria

1. Portada
2. Introduccion y objetivos
3. Estructura general de la solucion
4. Analizador lexico
5. Analizador sintactico
6. Precedencia y asociatividad
7. Validaciones adicionales orientadas a P2
8. Punto de entrada y modo de ejecucion
9. Bateria de pruebas
10. Decisiones de diseño y problemas encontrados
11. Conclusiones

## Portada

En la portada deberiais poner:

- Nombre de la asignatura
- Curso academico
- Practica 2
- Titulo del trabajo
- Nombres completos de los integrantes
- Grupo o pareja
- Fecha de entrega

Un titulo razonable seria:

`Practica 2 - Analizador sintactico del lenguaje Lava con PLY`

## 1. Introduccion y objetivos

### Que deberia contar esta seccion

Aqui debe quedar claro:

- Que problema resuelve la practica
- Que papel tiene el parser dentro del compilador
- Que relacion hay entre P1, P2 y futuras ampliaciones
- Que se ha implementado exactamente en esta entrega

### Texto base sugerido

La segunda entrega de la practica tiene como objetivo la implementacion del analizador sintactico del lenguaje Lava utilizando la libreria PLY, concretamente el modulo `ply.yacc`. Esta fase parte del analizador lexico desarrollado en la primera entrega y construye sobre el la gramatica necesaria para reconocer programas validos del lenguaje descrito en el enunciado.

El parser desarrollado acepta programas formados por declaraciones, expresiones, estructuras de control, funciones y registros. Ademas de reconocer la sintaxis general del lenguaje, la solucion incorpora una capa adicional de validacion estructural orientada a P2 para rechazar ciertos casos que, aunque podrian parecer parseables con una gramatica demasiado permisiva, no deben considerarse programas validos segun la especificacion.

En esta entrega no se realiza todavia un analisis semantico completo de tipos, tablas de simbolos o conversiones automaticas propias de P3. Sin embargo, si se comprueban ciertas restricciones estructurales esenciales, como la validez del lado izquierdo de una asignacion, el contexto de uso de `break`, la validez de `return` y la obligatoriedad de inicializacion en declaraciones de variables de tipo registro.

## 2. Estructura general de la solucion

### Que deberia contar esta seccion

Esta parte debe orientar al corrector rapido. Tiene que entender como estan repartidas las responsabilidades entre los ficheros.

### Texto base sugerido

La implementacion se ha dividido en tres ficheros principales:

- `lexer.py`: define el conjunto de tokens del lenguaje, las expresiones regulares asociadas y la construccion del analizador lexico.
- `parser.py`: define la gramatica del lenguaje mediante reglas de produccion de PLY, establece la precedencia de operadores y realiza validaciones estructurales adicionales sobre el resultado del parseo.
- `main.py`: actua como punto de entrada del programa. Gestiona la lectura del fichero, el modo de ejecucion normal y el modo opcional `--token`.

Adicionalmente, se ha creado una bateria de pruebas en la carpeta `tests` con casos validos e invalidos para verificar el comportamiento del analizador.

### Idea importante para defender oralmente

No conviene presentar el proyecto como tres archivos aislados. La vision correcta es esta:

- El lexer convierte el texto en tokens.
- El parser consume esos tokens y construye una representacion estructurada del programa.
- Sobre esa representacion se realiza una validacion minima adicional de restricciones propias de P2.
- `main.py` orquesta el proceso y decide si se exportan tokens o si se valida sintacticamente el programa.

## 3. Analizador lexico

### Objetivo del lexer

El objetivo del analizador lexico es transformar la secuencia de caracteres de entrada en una secuencia de tokens. Cada token representa una categoria lexica del lenguaje: identificadores, literales, operadores, delimitadores o palabras reservadas.

### Palabras reservadas

El lexer mantiene un diccionario `reserved` que asocia cada palabra reservada del lenguaje con su nombre de token correspondiente. Esta tecnica permite reconocer primero un lexema mediante la regla general de identificadores y, a continuacion, decidir si ese lexema debe tratarse como `ID` o como palabra reservada.

La lista de palabras reservadas implementada es:

- `true`, `false`
- `int`, `float`, `char`, `boolean`, `void`
- `return`
- `if`, `else`, `do`, `while`, `break`
- `print`
- `new`, `record`

### Tokens del lenguaje

Los tokens definidos en la implementacion cubren:

- Identificadores: `ID`
- Literales: `INT_VALUE`, `FLOAT_VALUE`, `CHAR_VALUE`
- Operadores de asignacion y comparacion: `ASSIGN`, `EQ`, `GT`, `GE`, `LT`, `LE`
- Operadores aritmeticos y logicos: `PLUS`, `MINUS`, `TIMES`, `DIVIDE`, `AND`, `OR`, `NOT`
- Operadores de estructura: `DOT`
- Separadores y delimitadores: `COMMA`, `SEMICOLON`, `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`
- Todos los tokens asociados a palabras reservadas

### Espacios y saltos de linea

Se ignoran espacios, tabuladores y retornos de carro mediante:

`t_ignore = " \t\r"`

Los saltos de linea no se ignoran sin mas; se procesan mediante una regla especifica para actualizar correctamente el contador de lineas del lexer. Esto es importante porque tanto el lexer como el parser informan errores con numero de linea.

### Comentarios

Se soportan dos tipos de comentarios:

- Comentarios de una linea: comienzan por `//` y terminan al final de la linea.
- Comentarios multilínea: delimitados por `/* ... */`.

En el caso de los comentarios multilínea, ademas de ignorar el contenido, se incrementa el numero de linea segun el numero de saltos de linea contenidos en el comentario. Esta decision evita desajustes entre la posicion real del error y la posicion informada al usuario.

### Literales enteros

La expresion regular de enteros acepta:

- Decimal sin ceros a la izquierda, salvo el caso especial `0`
- Binario con prefijo `0b`
- Octal con prefijo `0`
- Hexadecimal con prefijo `0x` y digitos hexadecimales en mayusculas

Esta decision sigue la especificacion del enunciado y evita aceptar formatos ambiguos o no permitidos.

### Literales reales

La expresion regular de reales acepta:

- Notacion con punto decimal: por ejemplo `10.5`
- Notacion cientifica con base decimal o entera: por ejemplo `9.87e-2` o `5e5`

La notacion exponencial se integra en el token `FLOAT_VALUE`, lo que simplifica la posterior expresion gramatical de los literales.

### Literales caracter

Los caracteres se reconocen entre comillas simples. La regla permite:

- Un caracter simple distinto de salto de linea, comilla simple y barra invertida
- Secuencias escapadas mediante `\\.` si fuera necesario

### Identificadores

La regla de identificadores sigue el patron clasico:

- Primera posicion: letra o guion bajo
- Posiciones siguientes: letras, digitos o guion bajo

Tras reconocer un `ID`, se consulta el diccionario de palabras reservadas para decidir el tipo final del token.

### Gestion de errores lexicos

Cuando aparece un caracter ilegal, no se interrumpe inmediatamente todo el proceso sin informacion. En su lugar:

- Se registra un mensaje de error con el caracter y la linea
- Se avanza un caracter con `lexer.skip(1)`

Esto permite informar del problema de manera mas precisa y mantener un comportamiento coherente durante el analisis.

### Posible texto de cierre de la seccion

En conjunto, el analizador lexico implementa todos los elementos necesarios para servir de base al parser. Ademas, realiza un seguimiento cuidadoso de lineas y soporta el modo opcional de exportacion de tokens heredado de P1, lo que permite reutilizar y validar la fase lexico-sintactica de forma independiente.

## 4. Analizador sintactico

### Vision general

El parser se implementa con `ply.yacc` siguiendo una gramatica de estilo LALR. Su objetivo es reconocer la estructura global de un programa Lava y detectar secuencias de tokens no compatibles con la sintaxis definida.

La gramatica no se limita a expresiones sueltas, sino que cubre:

- Programas vacios o formados solo por delimitadores
- Declaraciones simples y multiples
- Declaraciones de registros
- Funciones con y sin parametros
- Expresiones aritmeticas, booleanas y comparativas
- Llamadas a funciones
- Acceso por punto
- Construccion de registros con `new`
- Estructuras `if`, `if-else`, `while` y `do-while`
- Sentencias `break`, `return` y `print`

### Simbolo inicial

El simbolo inicial del parser es `program`. A partir de el se construye una secuencia opcional de elementos del programa.

Esto permite aceptar de forma natural varios casos que el enunciado declara validos:

- Fichero vacio
- Fichero con solo saltos de linea
- Fichero con solo `;`
- Secuencias con varios delimitadores entre sentencias

### Estructura global del programa

La gramatica separa el programa en `program_item`. Un elemento del programa puede ser:

- Un `;` aislado
- Una declaracion de registro
- Una funcion
- Una declaracion o inicializacion de variable
- Una estructura de control
- Una sentencia simple terminada en `;`

Esto hace que la estructura general del lenguaje sea flexible pero controlada.

### Eleccion importante: construccion de nodos intermedios

Aunque el objetivo de P2 no exige un AST completo de compilador, en esta implementacion se construyen nodos internos mediante una funcion auxiliar `node(...)`. La razon es doble:

- Facilitar una validacion estructural posterior sin complicar en exceso la gramatica
- Separar el reconocimiento sintactico del control de ciertas restricciones de contexto

Los nodos no pretenden ser todavia una representacion semantica completa de P3, pero si una estructura suficiente para razonar sobre asignaciones, bloques, bucles y funciones.

Esto es un punto importante de defensa oral: no se ha construido un AST “por gusto”, sino porque permite expresar de forma clara restricciones que una CFG pura no modela comodamente sin introducir ambigüedades o complejidad innecesaria.

## 5. Diseño de la gramatica

### Declaraciones de tipos primitivos y tipos registro

Una de las decisiones mas importantes de la implementacion es no tratar todos los tipos con una unica regla demasiado general. En lugar de eso, se distinguen:

- `primitive_type`: `int`, `float`, `char`, `boolean`
- `custom_type`: `ID`, pensado para tipos de registro ya definidos

Esta separacion permite modelar correctamente una restriccion importante del enunciado:

- Los tipos primitivos admiten declaracion simple, declaracion multiple e inicializacion.
- Los tipos registro deben declararse con inicializacion.

Por eso se aceptan ejemplos como:

- `int a, b;`
- `float x = 3.2;`
- `Point p = new Point(1, 2);`
- `Point p = makePoint();`

Y se rechazan:

- `Point p;`
- `Point a, b;`

### Justificacion tecnica de esa decision

Si se hubiera dejado una regla generica del estilo `type_spec : INT | FLOAT | CHAR | BOOLEAN | ID`, entonces la gramatica habria aceptado demasiados casos no permitidos por el enunciado, especialmente declaraciones vacias de registros o multideclaraciones de tipos complejos.

Separar ambos mundos permite aproximarse mucho mejor a la especificacion real del lenguaje.

### Declaracion de registros

Los registros se reconocen con la forma:

`record Nombre(tipo campo1, tipo campo2, ...) ;`

Cada campo puede ser de tipo primitivo o de otro tipo de registro. Esta decision coincide con el enunciado, que permite registros anidados.

### Parametros de funciones

Los parametros se describen como una lista opcional de pares `tipo identificador`. Se reutiliza la idea de `any_type`, que puede ser un tipo primitivo o un tipo de registro.

Esto permite funciones como:

- `int sum(int a, int b) { ... }`
- `Point make(int x, int y) { ... }`
- `void move(Planet p) { ... }`

### Bloques

Los bloques se representan mediante llaves y una lista opcional de elementos internos. Dentro de un bloque se permiten:

- Delimitadores vacios
- Estructuras de control
- Declaraciones
- Sentencias simples terminadas en `;`

### Expresiones

La gramatica de expresiones soporta:

- Literales
- Identificadores
- Expresiones parentizadas
- Construccion con `new`
- Llamadas a funciones
- Acceso a campos con `.`
- Operadores unarios `+`, `-`, `!`
- Operadores binarios aritmeticos, comparativos y booleanos

La estrategia empleada consiste en usar:

- `primary_expr` para literales, identificadores, parentizacion y `new`
- `postfix_expr` para llamadas y acceso por punto
- `expression` para operaciones unarias y binarias

Esta organizacion permite modelar de forma limpia el hecho de que llamadas a funciones y accesos a campos tienen una precedencia alta y se encadenan de manera natural.

### Asignaciones

La regla de asignacion se expresa como:

`assignment : postfix_expr ASSIGN expression`

Esta formulacion es deliberada. La alternativa intuitiva seria introducir desde la gramatica un no terminal `lvalue` muy restrictivo. Sin embargo, la solucion elegida aprovecha la expresividad de `postfix_expr` para el parseo y desplaza la comprobacion de “si realmente es una ubicacion asignable” a una validacion estructural posterior.

Esta decision tiene una justificacion tecnica importante:

- Simplifica la construccion de la gramatica
- Evita forzar artificialmente reglas mas complicadas
- Permite mantener el soporte a accesos encadenados como `a.b.c = x`

Despues, la funcion `is_lvalue` acepta solo:

- Identificadores simples
- Accesos por punto cuyo valor base tambien sea asignable

De este modo se rechazan ejemplos como:

- `f() = 3;`
- `new Circle(1) = 2;`
- `(a + b) = 4;`

## 6. Precedencia y asociatividad

### Por que se usa `precedence`

El enunciado recomienda usar la herramienta de precedencia de PLY en lugar de codificar la precedencia enteramente con niveles de no terminales. Esta implementacion sigue esa recomendacion.

El bloque `precedence` define:

1. `OR`
2. `AND`
3. Comparativos `EQ`, `GT`, `GE`, `LT`, `LE`
4. Suma y resta
5. Multiplicacion y division
6. Operadores unarios `NOT`, `UPLUS`, `UMINUS`

### Interpretacion

Esto significa, por ejemplo, que:

- `*` y `/` se evaluan antes que `+` y `-`
- Los comparativos se aplican despues de operaciones aritmeticas
- `&&` tiene mayor precedencia que `||`
- Los operadores unarios se aplican sobre su operando antes que los binarios

Ademas, las expresiones entre parentesis se gestionan en `primary_expr`, lo que fuerza su evaluacion como subexpresion prioritaria.

### Justificacion para la memoria

Una forma buena de explicarlo es esta:

Se ha preferido una solucion basada en la declaracion explicita de precedencia y asociatividad porque reduce la complejidad de la gramatica, hace mas legible el parser y encaja mejor con la manera habitual de modelar expresiones en PLY. Esta estrategia permite resolver de forma limpia combinaciones de operadores sin introducir conflictos innecesarios en la construccion de las tablas LALR.

## 7. Validaciones adicionales orientadas a P2

Esta es una de las secciones mas importantes de vuestra memoria, porque aqui esta el valor diferencial de la implementacion actual.

### Idea general

El parser no se limita a aceptar o rechazar segun la CFG basica, sino que realiza una validacion estructural adicional sobre los nodos construidos. Estas comprobaciones no son aun analisis semantico completo de P3, pero si restricciones necesarias para que el comportamiento encaje con P2.

### 7.1 Validez del lado izquierdo de una asignacion

Tras parsear una asignacion, se comprueba si el objetivo es realmente asignable. Solo se consideran validos:

- `ID`
- `ID.campo`
- `ID.campo.subcampo`

Con esta comprobacion se evita aceptar como asignables expresiones que producen valor pero no representan una posicion modificable.

### 7.2 Uso correcto de `break`

`break` solo es valido dentro de un bucle. La validacion recorre los bloques manteniendo la informacion de contexto `in_loop`.

Asi:

- `while (...) { break; }` es valido
- `if (...) { break; }` fuera de bucle es invalido
- `break;` en el nivel global es invalido

### 7.3 Uso correcto de `return`

`return` solo es valido dentro de una funcion. La validacion mantiene la informacion `in_function` y el tipo de retorno de la funcion actual.

Se rechazan los siguientes casos:

- `return` fuera de una funcion
- `return` dentro de una funcion `void`
- `return` sin expresion dentro de una funcion no `void`

### 7.4 Presencia obligatoria de `return` en funciones no `void`

Segun el enunciado, una funcion no `void` debe contener al menos una sentencia de retorno. La validacion comprueba este requisito recorriendo el cuerpo de cada funcion.

Importante para la memoria: esta comprobacion no intenta demostrar caminos de ejecucion exhaustivos, ni hacer control de flujo avanzado. Lo que comprueba es la presencia estructural de al menos un `return` con expresion dentro del cuerpo de la funcion. Para P2 esta aproximacion es razonable, simple y defendible.

### 7.5 Inicializacion obligatoria en variables de tipo registro

Como ya se ha explicado, la gramatica diferencia entre tipos primitivos y tipos de registro para impedir declaraciones vacias o multideclaraciones de estos ultimos.

Aqui conviene explicar un matiz importante:

La implementacion no obliga a que la expresion de inicializacion de un registro sea literalmente `new`. Se permite cualquier expresion, por ejemplo una llamada a funcion que devuelva un registro.

Esto esta justificado porque el propio enunciado incluye casos equivalentes a:

`Line l = lineFromCoordinates(...);`

Por tanto, la restriccion real no es “el lado derecho debe ser `new`”, sino “una variable de tipo registro no puede declararse sin quedar inicializada”.

## 8. Gestion de errores

### Errores lexicos

Los errores lexicos se registran en `lexer.errors` con informacion de linea. El analizador continua avanzando caracter a caracter tras cada caracter ilegal.

### Errores sintacticos

La funcion `p_error` genera dos clases principales de error:

- `Fin de archivo inesperado`
- `Token 'X' inesperado en la linea N`

En cuanto se detecta un error sintactico, se lanza `SyntaxError` y `parse_text` devuelve la lista acumulada de errores.

### Acumulacion de errores

La salida final del analisis combina:

- Errores lexicos recogidos por el lexer
- Errores de parseo
- Errores de validacion estructural

Esta unificacion permite que `main.py` tenga una logica sencilla: si la lista de errores esta vacia, el programa es aceptado; en caso contrario, se imprimen los errores y se devuelve codigo de salida 1.

## 9. Punto de entrada del programa

### Funcion principal

El fichero `main.py` contiene un unico `main`, encargado de:

- Comprobar los argumentos de linea de comandos
- Leer el fichero de entrada
- Ejecutar el analizador sintactico en modo normal
- Ejecutar el lexer en modo `--token`

### Modo normal

Con:

`python3 main.py fichero.lava`

el programa:

- Lee el fichero
- Ejecuta `parse_text`
- No muestra salida si el programa es valido
- Muestra errores y devuelve codigo 1 si es invalido

### Modo `--token`

Con:

`python3 main.py --token fichero.lava`

el programa ejecuta solo el lexer y exporta un fichero `.token` siguiendo el formato heredado de P1:

`TIPO, VALOR, LINEA, COLUMNA_INICIO, COLUMNA_FIN`

### Por que mantener este modo en P2

Aunque es opcional, mantener `--token` es util por tres razones:

- Facilita la comprobacion de que el lexer sigue funcionando correctamente
- Permite depurar errores separando la fase lexico-sintactica
- Reutiliza el trabajo de P1 y muestra continuidad entre entregas

## 10. Gramatica formal

El enunciado menciona la conveniencia de incluir una descripcion formal de la gramatica como 4-tupla:

`G = (Vn, Vt, P, S)`

### Texto sugerido

La gramatica implementada puede describirse formalmente como `G = (Vn, Vt, P, S)`, donde:

- `Vn` es el conjunto de simbolos no terminales. Entre los mas relevantes se encuentran `program`, `program_item`, `record_decl`, `param_list`, `block`, `control_statement`, `plain_simple_statement`, `expression`, `postfix_expr`, `primary_expr`, `literal` y `arg_list`.
- `Vt` es el conjunto de simbolos terminales, esto es, los tokens generados por el analizador lexico: `ID`, `INT_VALUE`, `FLOAT_VALUE`, `CHAR_VALUE`, operadores, delimitadores y palabras reservadas del lenguaje.
- `P` es el conjunto de reglas de produccion definidas en `parser.py`.
- `S` es el simbolo inicial, que en esta implementacion es `program`.

### Consejo practico

No hace falta listar absolutamente todas las reglas en forma matematica si eso hace la memoria ilegible. Lo razonable es:

- Dar la 4-tupla
- Enumerar las familias de no terminales importantes
- Incluir una seleccion de producciones representativas

Por ejemplo, puedes poner algo como:

```text
program -> program_items_opt
program_item -> record_decl SEMICOLON
program_item -> primitive_type ID ASSIGN expression SEMICOLON
program_item -> primitive_type ID primitive_id_list_tail SEMICOLON
program_item -> VOID ID LPAREN param_list_opt RPAREN block
program_item -> primitive_type ID LPAREN param_list_opt RPAREN block
control_statement -> IF LPAREN expression RPAREN block
control_statement -> IF LPAREN expression RPAREN block ELSE block
control_statement -> WHILE LPAREN expression RPAREN block
control_statement -> DO block WHILE LPAREN expression RPAREN
expression -> expression PLUS expression
expression -> expression TIMES expression
expression -> NOT expression
postfix_expr -> postfix_expr LPAREN arg_list_opt RPAREN
postfix_expr -> postfix_expr DOT ID
primary_expr -> ID
primary_expr -> literal
primary_expr -> LPAREN expression RPAREN
primary_expr -> NEW ID LPAREN arg_list_opt RPAREN
```

## 11. Bateria de pruebas

### Que habeis añadido

La carpeta `P2_MARCO_GARCIA_PABLO_ROIG/tests` contiene:

- Casos validos
- Casos invalidos
- Salidas esperadas para los invalidos
- Un script `run_tests.py` que ejecuta todo automaticamente

### Que cubre la bateria

La bateria cubre al menos:

- Ficheros vacios de facto o con solo separadores
- Declaraciones primitivas y multideclaraciones
- Inicializaciones
- Registros y acceso por punto
- Registros anidados
- `if`, `if-else`, `while`, `do-while`
- `break`
- Funciones y llamadas
- Retornos de funciones
- Precedencia de operadores
- Casos invalidos clave de P2

### Casos invalidos especialmente relevantes

Conviene nombrar algunos en la memoria porque demuestran que habeis pensado en la logica del lenguaje y no solo en parsear ejemplos felices:

- Asignaciones invalidas: `f() = 3;`, `(a+b)=3;`
- Declaraciones invalidas de registros: `Circle c;`
- `break` fuera de bucle
- `return` fuera de funcion
- `return` en funcion `void`
- Funcion no `void` sin retorno
- Multideclaracion con inicializacion, prohibida por el enunciado
- Fin de archivo inesperado

### Texto base sugerido

Se ha desarrollado una bateria de pruebas propia para validar tanto el reconocimiento de programas correctos como la deteccion de errores en casos borde. Esta bateria automatiza la ejecucion del analizador sobre un conjunto de ejemplos representativos y permite comprobar que la salida coincide con la esperada. Con ello se busca reducir errores regresivos y aportar evidencia objetiva de que el parser implementado cubre no solo los ejemplos positivos, sino tambien restricciones sintacticas relevantes del enunciado.

## 12. Decisiones de diseño importantes

Esta seccion puede ser determinante para la nota, porque es donde se ve si entendeis lo que habeis hecho.

### Decision 1: reutilizar el lexer de P1 con cambios minimos

Ventaja:

- Se mantiene continuidad entre entregas
- Se evita duplicar trabajo
- Se conserva el modo `--token`

### Decision 2: usar `precedence` en lugar de una gramatica de expresiones con muchos niveles

Ventaja:

- Parser mas legible
- Menos reglas auxiliares
- Menos probabilidad de conflictos si se define correctamente

### Decision 3: construir nodos estructurales aunque P2 no pida aun P3

Ventaja:

- Facilita validaciones de contexto
- Prepara el terreno para una futura ampliacion semantica
- Evita mezclar parseo y validaciones no puramente sintacticas

### Decision 4: separar tipos primitivos de tipos de registro

Ventaja:

- Ajuste mas fiel a la especificacion del lenguaje
- Permite restringir correctamente la declaracion de registros

### Decision 5: validar el lado izquierdo de las asignaciones fuera de la regla base

Ventaja:

- Gramaticamente se soportan accesos encadenados con facilidad
- Se conserva claridad en la definicion del parser
- Se evita aceptar cualquier expresion como destino final de una asignacion

## 13. Problemas encontrados y como se resolvieron

Esta seccion es muy recomendable. Un corrector suele valorar mas una memoria que explica dificultades reales que una que solo enumera cosas obvias.

### Problema 1: exceso de permisividad con los tipos definidos por el usuario

Una primera aproximacion usando una regla general de tipo hacia que el parser aceptara declaraciones no permitidas de registros. Se soluciono separando explicitamente los tipos primitivos y los tipos complejos definidos por identificador, y restringiendo para estos ultimos la declaracion a la forma con inicializacion.

### Problema 2: control del lado izquierdo de la asignacion

Si la gramatica se hace demasiado abierta, es facil aceptar expresiones que no son realmente asignables. La solucion adoptada consistio en parsear la asignacion de forma flexible y, posteriormente, validar que el destino fuese un identificador o una cadena de accesos por punto.

### Problema 3: restricciones de contexto de `break` y `return`

Estas restricciones no encajan de forma natural en una CFG simple sin introducir una explosion de reglas segun contexto. Por ello se resolvieron mediante una fase posterior de validacion estructural que recorre los bloques con informacion de contexto.

### Problema 4: mantener coherencia con el enunciado y con ejemplos reales

Un caso delicado fue la inicializacion de registros: el enunciado enfatiza el uso de `new`, pero tambien muestra ejemplos donde una variable de tipo registro se inicializa con una llamada a funcion que devuelve un registro. La solucion fue imponer la inicializacion obligatoria, pero no limitar la expresion de inicializacion a `new`.

## 14. Limitaciones actuales

Es muy sano incluir una seccion breve de limitaciones. Muestra madurez tecnica.

### Texto sugerido

Aunque el parser implementado cubre las construcciones exigidas en P2 y añade validaciones estructurales importantes, no realiza aun comprobaciones semanticas completas. En particular, no se comprueba en esta fase:

- La existencia previa de identificadores o tipos
- La compatibilidad de tipos en expresiones y asignaciones
- La validez semantica de llamadas a funciones
- La coherencia entre el tipo declarado y el valor devuelto en cada `return`
- El flujo de control completo en funciones no `void`

Estas tareas se consideran propias de una futura ampliacion semantica en P3.

## 15. Conclusiones

### Texto base sugerido

La practica desarrollada implementa un analizador sintactico funcional y robusto para el lenguaje Lava utilizando PLY. La solucion no solo reconoce la estructura general del lenguaje, sino que incorpora decisiones de diseño orientadas a ajustarse mejor al enunciado y evitar aceptaciones indebidas de programas incorrectos.

Entre los aspectos mas relevantes del trabajo destacan la separacion entre tipos primitivos y tipos registro, el uso de precedencia declarativa para las expresiones, la construccion de una representacion estructural intermedia y la validacion adicional de restricciones como el uso de `break`, `return` y la forma correcta de las asignaciones. Ademas, la bateria de pruebas desarrollada permite verificar de forma sistematica tanto casos validos como invalidos, reforzando la fiabilidad de la implementacion.

En conjunto, la practica deja una base adecuada para la futura incorporacion del analisis semantico en la siguiente fase del proyecto.

## 16. Preguntas tipicas que os pueden hacer en una defensa oral

Preparad respuestas cortas para esto:

### Por que no habeis hecho todo solo con la gramatica?

Porque ciertas restricciones, como `break` fuera de bucle o `return` segun tipo de funcion, son mucho mas limpias y mantenibles si se validan estructuralmente tras el parseo. Intentar expresar todo eso unicamente con CFG complica mucho la gramatica y no aporta valor real en P2.

### Por que permitis inicializar un registro con una llamada a funcion y no solo con `new`?

Porque el enunciado muestra ejemplos donde una funcion devuelve un registro y ese valor se asigna a una variable de tipo registro. La restriccion importante es la inicializacion obligatoria, no que el lado derecho tenga que ser literalmente una expresion `new`.

### Por que usais `precedence`?

Porque es la herramienta natural de PLY para resolver la precedencia de operadores sin duplicar reglas ni degradar la legibilidad de la gramatica.

### Habeis hecho ya el analisis semantico?

No. Solo se han añadido validaciones estructurales minimas necesarias para que el comportamiento del parser encaje con P2. El analisis semantico completo queda fuera del alcance de esta entrega.

## 17. Checklist final antes de exportar la memoria a PDF

- Revisar faltas de ortografia
- Unificar tiempos verbales
- No prometer funcionalidad que no esta implementada
- Asegurarse de que la memoria explica decisiones, no solo enumera reglas
- Mencionar la bateria de pruebas
- Incluir el modo `--token` como funcionalidad opcional mantenida
- Confirmar que la estructura del proyecto descrita coincide con el contenido real de la entrega
- Añadir capturas o fragmentos pequenos solo si aclaran algo
- Exportar a PDF con el nombre adecuado

## 18. Mini estructura final recomendada para copiar directamente

Si quieres una version muy operativa, esta es una estructura compacta y muy razonable:

### 1. Introduccion

- Objetivo de P2
- Relacion con P1 y P3

### 2. Arquitectura de la solucion

- `lexer.py`
- `parser.py`
- `main.py`
- `tests/`

### 3. Analizador lexico

- Tokens
- Palabras reservadas
- Expresiones regulares
- Comentarios
- Conteo de lineas
- Errores lexicos

### 4. Analizador sintactico

- Simbolo inicial
- Estructura global del programa
- Declaraciones
- Funciones
- Registros
- Expresiones
- Control de flujo

### 5. Precedencia y asociatividad

- Tabla de precedencia
- Justificacion

### 6. Validaciones adicionales de P2

- Lado izquierdo de asignacion
- `break`
- `return`
- Registros con inicializacion obligatoria

### 7. Main y ejecucion

- Modo normal
- Modo `--token`

### 8. Pruebas

- Tipos de casos
- Automatizacion
- Resumen de cobertura

### 9. Conclusiones

- Logros
- Limitaciones
- Trabajo futuro

## 19. Recomendacion final

La mejor memoria no es la que mas jerga tecnica mete, sino la que demuestra tres cosas:

1. Que entendeis el lenguaje que os pedian implementar.
2. Que entendeis por que vuestra gramatica acepta lo correcto y rechaza lo incorrecto.
3. Que las decisiones de diseño del codigo tienen una razon tecnica clara.

Si la memoria refleja eso, estara al nivel de una entrega seria y defendible.
