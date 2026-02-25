# Bateria de pruebas P1

Estructura:
- `cases/`: ficheros de entrada `.lava`
- `expected/`: salidas esperadas `.token`
- `run_tests.py`: ejecuta todos los casos y compara resultado real vs esperado

Ejecucion:

```bash
cd P1_MARCO_GARCIA_PABLO_ROIG/tests
python3 run_tests.py
```

Criterio de exito:
- Todos los casos deben mostrar `OK`
- Resumen final: `Summary: 13/13 passed`

Cobertura de la bateria:
- Tipos basicos (`int`, `float`, `char`, `boolean`)
- Palabras reservadas vs identificadores
- Enteros decimal/binario/octal/hexadecimal
- Reales con punto y notacion cientifica
- Operadores aritmeticos, logicos y comparativos
- Separadores y puntuacion
- Comentarios de una y varias lineas
- Registros, `new` y acceso con `.`
- Estructuras `if/else`, `while`, `break`, `return`, `print`
- Espacios/tabulaciones
- Caracteres invalidos (comprobacion de recuperacion lexica)
