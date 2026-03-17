# Preparacion de memoria P2

Este documento no es la memoria final. Es un registro corto de decisiones de diseño tomadas durante la implementacion de la P2 para poder redactar despues una buena memoria a mano, con criterio y sin olvidar por que se eligio cada solucion.

## Objetivo de la P2

- Implementar un parser con `ply.yacc`.
- Reutilizar el lexer de P1 con los cambios minimos necesarios para informar errores lexicos.
- Hacer un analizador sintactico claro, corto y facil de extender en P3.
- Mantener la implementacion simple: reconocimiento y errores, sin AST completo.

## Decisiones generales

- Se ha implementado un parser de reconocimiento, no un AST completo.
  Motivo: el enunciado de P2 pide validar sintaxis y reportar errores; meter AST entero ahora aumenta complejidad sin aportar valor directo.

- Se ha dejado `ASSIGN` fuera de `expression`.
  Motivo: asi se prohiben sintacticamente asignaciones dentro de expresiones como `A + B = 3`.

- `record` se ha limitado al nivel superior del programa.
  Motivo: el enunciado y los ejemplos lo usan como declaracion de tipo global; asi la gramatica queda mas simple y con menos ambiguedad.

- `function_decl` se ha limitado al nivel superior del programa.
  Motivo: es la estructura natural del lenguaje descrito y evita mezclar declaraciones de funcion dentro de bloques.

- Se han aceptado tanto `return;` como `return expr;`.
  Motivo: el enunciado textual sugiere restricciones sobre `void`, pero los ejemplos reales incluyen `return;` en funciones `void`. Se ha preferido una sintaxis permisiva y dejar la validacion fina a P3.

- `print(expr)` se ha tratado como sentencia propia, no como llamada ordinaria.
  Motivo: `print` es palabra reservada y aparece en los ejemplos como instruccion del lenguaje.

- Se ha implementado `do { ... } while (...)`.
  Motivo: aparece en el enunciado y debe estar cubierto aunque no salga en todos los casos de prueba.

## Uso de recursion por zonas de la gramatica

### Programa y bloques

- `program_items_opt` y `block_items_opt`: recursion izquierda + produccion vacia.
  Motivo: permite consumir secuencias largas de items/sentencias de forma natural en Yacc y mantener la posibilidad de fichero o bloque vacio.

- `program_item` y `block_item`: sin recursion propia.
  Motivo: son unidades de secuencia; la repeticion real vive en el no terminal contenedor.

### Delimitadores `;`

- `semicolons`: recursion izquierda.
  Motivo: el lenguaje admite uno o varios `;` entre sentencias; con recursion izquierda se modela de forma directa y clara en PLY.

### Comas

- `field_list`, `param_list`, `arg_list`, `id_list`: recursion izquierda.
  Motivo: son listas separadas por comas, exactamente el caso tipico donde Yacc trabaja bien con recursion izquierda. Ademas deja listas en orden natural para una futura semantica.

- `field_list_opt`, `param_list_opt`, `arg_list_opt`: recursion derecha por epsilon en la alternativa vacia.
  Motivo: son opcionales. Aqui no interesa forzar una lista ficticia; la opcion vacia deja la gramatica mas limpia.

### Expresiones

- Operadores binarios: recursion izquierda en `expression`.
  Motivo: los operadores aritmeticos y booleanos usados son naturalmente asociativos por la izquierda, y PLY resuelve la precedencia con menos ruido mediante `precedence`.

- Operadores unarios: sin recursion izquierda ni derecha de lista; se usan reglas directas sobre `expression`.
  Motivo: el operador unario se expresa mejor con una regla simple y precedencia explicita.

- Agrupacion con parentesis: regla directa.
  Motivo: no es un caso de lista ni de secuencia.

### Llamadas y acceso con `.`

- `postfix_expr`: recursion izquierda.
  Motivo: las cadenas tipo `a.b.c`, `f(x)(y)` o `obj.metodo().campo` se extienden naturalmente por la izquierda en una gramatica LALR.

- `lvalue`: recursion izquierda.
  Motivo: permite modelar `a.b.c = x` de forma directa y separar claramente el lado izquierdo asignable de una expresion cualquiera.

### Opcionales

- `empty` se usa en las zonas donde el lenguaje permite ausencia real de elementos.
  Motivo: en PLY es la forma mas simple y legible de modelar opcionalidad.

## Decisiones de sintaxis dudosas y razonamiento

### Puntos `.`

- El operador `.` se ha tratado como parte de `postfix_expr` y `lvalue`, no solo como precedencia.
  Motivo: no es un operador binario cualquiera; representa acceso estructural y encaja mejor como extension de un primario/postfijo.

### Comas `,`

- Las comas solo separan listas de identificadores, parametros, campos y argumentos.
  Motivo: es coherente con lenguajes tipo Java/C y con la propia especificacion de Lava.

### Parentesis

- Se usan tanto para agrupacion como para listas de parametros/argumentos.
  Motivo: es la convencion habitual en lenguajes similares y evita inventar otra sintaxis no descrita.

### Comparadores

- `==`, `>`, `>=`, `<`, `<=` se resuelven con `precedence` como operadores no asociativos.
  Motivo: evita aceptar de forma natural cadenas dudosas como `a < b < c` y simplifica la gramatica.

### Tipos de registro

- `type_spec` admite `ID`.
  Motivo: los tipos definidos por `record` se usan luego como nombres de tipo normales, por ejemplo `Vector v`.

- Se acepta el posible solapamiento entre `ID` como tipo y `ID` como expresion.
  Motivo: la forma concreta de la sentencia desambigua el caso en la practica (`ID ID` para declaracion, `ID(` para llamada, `ID =` para asignacion, `ID.` para acceso).

## Precedencia elegida

```python
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'NOT', 'UPLUS', 'UMINUS'),
)
```

Motivo:

- Mantiene la gramatica de expresiones corta.
- Sigue una jerarquia razonable y familiar para lenguajes tipo Java/C.
- Evita multiplicar no terminales solo para codificar prioridad.

## Cambios introducidos en el lexer respecto a P1

- Se mantienen los tokens y expresiones regulares de P1.
- Se añade acumulacion de errores lexicos en `lexer.errors`.

Motivo:

- En P1 saltar caracteres ilegales podia ser suficiente para exportar tokens.
- En P2 un fichero con caracteres ilegales no debe pasar como programa valido.

## Riesgos o puntos que conviene mencionar en la memoria final

- La mayor fuente de ambiguedad potencial es `type_spec : ID`.
- Los accesos con `.` y las llamadas encadenadas son mas faciles de manejar como postfijos que como operadores binarios normales.
- Algunas restricciones de contexto, como `break` fuera de bucle o reglas exactas de `return` segun el tipo de la funcion, se dejan para el analisis semantico de P3.
