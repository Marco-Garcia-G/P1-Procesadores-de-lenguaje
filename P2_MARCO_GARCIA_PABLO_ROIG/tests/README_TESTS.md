# Bateria de pruebas P2

Estructura:
- `valid/`: programas que deben aceptarse sin salida
- `invalid/`: programas que deben rechazarse
- `expected_invalid/`: salida esperada exacta para cada caso invalido
- `run_tests.py`: ejecuta toda la bateria

Ejecucion:

```bash
cd P2_MARCO_GARCIA_PABLO_ROIG/tests
python3 run_tests.py
```

Exito:
- Todos los casos deben mostrar `OK`
- Resumen final: `Summary: 22/22 passed`

Cobertura:
- Ficheros con solo saltos de linea y con solo `;`
- Declaraciones primitivas, asignaciones y `print`
- Registros, `new`, acceso por punto y campos anidados
- `if/else`, `while`, `do while` y `break`
- Funciones, parametros, retorno y llamadas
- Restricciones de P2 sobre asignacion, `break`, `return` y registros
