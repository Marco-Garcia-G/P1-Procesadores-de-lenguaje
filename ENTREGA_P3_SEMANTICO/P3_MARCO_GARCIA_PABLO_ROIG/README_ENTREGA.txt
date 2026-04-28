P3 - Analizador semantico Lava

Contenido:
- lexer.py
- parser.py
- semantic.py
- main.py
- tests/

Ejecucion:
- Analisis lexico, sintactico y semantico:
  python3 main.py <fichero.lava>
- Modo lexer opcional heredado de P1:
  python3 main.py --token <fichero.lava>

Comportamiento esperado:
- Si el programa es valido, no muestra salida y termina con codigo 0.
- Si el programa es invalido, muestra los errores detectados y termina con codigo 1.

Controles semanticos implementados:
- Tabla de registros con campos tipados.
- Tabla de funciones con sobrecarga por firma de parametros.
- Tabla de simbolos con ambitos para variables globales, parametros y bloques.
- Comprobacion de variables declaradas antes de usarse.
- Deteccion de redeclaraciones en el mismo ambito.
- Comprobacion de tipos en inicializaciones y asignaciones.
- Comprobacion de operadores aritmeticos, logicos y comparativos.
- Conversion automatica segura de int a float.
- Validacion de constructores new: registro existente, aridad y tipos.
- Validacion de acceso a campos de registros.
- Validacion de llamadas a funciones y resolucion de sobrecarga.
- Condiciones de if, while y do-while obligatoriamente booleanas.
- Control de break solo dentro de bucles.
- Control de return segun el tipo de la funcion.
- Rechazo de return en funciones void, como indica el enunciado.

Bateria de pruebas:
- Ejecutar desde tests/:
  python3 run_tests.py
- Resultado esperado:
  Summary: 68/68 passed

Decision de tipos:
- int puede promocionar automaticamente a float.
- float no se convierte automaticamente a int.
- char y boolean solo son compatibles consigo mismos.
- Los registros son nominales: dos registros son compatibles solo si tienen el mismo nombre de tipo.
- Los registros completos no se comparan con ==; se comparan sus campos.
- Los nombres globales de registros, funciones y variables no pueden reutilizarse entre categorias.
