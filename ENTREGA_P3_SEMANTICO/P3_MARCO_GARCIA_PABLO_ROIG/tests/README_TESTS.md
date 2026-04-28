# Bateria de pruebas P3

Estructura:
- `valid/`: programas que deben aceptarse sin salida.
- `invalid/`: programas que deben rechazarse con al menos un mensaje `[ERROR]`.
- `run_tests.py`: ejecuta toda la bateria.

Ejecucion:

```bash
cd P3_MARCO_GARCIA_PABLO_ROIG/tests
python3 run_tests.py
```

Exito:
- Todos los casos deben mostrar `OK`.
- Resumen final: `Summary: 68/68 passed`.

Cobertura:
- Casos sintacticos heredados de P2.
- Declaraciones, asignaciones y uso de variables.
- Registros, `new`, acceso por punto y campos anidados.
- Tipos numericos con promocion `int -> float`.
- Operadores aritmeticos, logicos y comparativos.
- `if/else`, `while`, `do while`, `break` y condiciones booleanas.
- Funciones, parametros, retorno, llamadas y sobrecarga.
- Errores semanticos: variables no declaradas, redeclaraciones, incompatibilidad de tipos, campos inexistentes, constructores incorrectos y firmas duplicadas.
- Rechazo de comparacion directa entre registros completos y de nombres globales duplicados entre categorias.
