P2 - Analizador sintactico Lava

Contenido:
- lexer.py
- parser.py
- main.py
- tests/

Ejecucion:
- Analisis sintactico:
  python3 main.py <fichero.lava>
- Modo lexer opcional:
  python3 main.py --token <fichero.lava>

Comportamiento esperado:
- Si el programa es valido, no muestra salida y termina con codigo 0
- Si el programa es invalido, muestra los errores detectados y termina con codigo 1

Bateria de pruebas:
- Ejecutar desde tests/:
  python3 run_tests.py
- Resultado esperado:
  Summary: 25/25 passed
