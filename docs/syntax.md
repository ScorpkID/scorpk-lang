# Sintaxis Básica de Scorpk (Versión Prototipo 0.2)

Scorpk es un lenguaje minimalista y potente. Este documento define la sintaxis del prototipo actual.

## Variables
- Declaración con `let`:
  ```scorpk
  let nombre = 42;        // Entero
  let texto = "Hola";     // String
  ```
- Bloqueo con `lock`:
  ```scorpk
  lock(nombre);           // Evita cambios
  ```

## Expresiones
- Asignaciones con operaciones aritméticas:
  ```scorpk
  nombre = nombre + 5;    // Suma
  nombre = nombre - 3;    // Resta
  nombre = nombre * 2;    // Multiplicación
  ```

## Funciones
- Declaración con `fn`:
  ```scorpk
  fn saludar() {
      print(texto);       // Accede a variables del entorno
  }
  ```

## Intenciones
- Bloques `intent` para flujos basados en estados:
  ```scorpk
  intent combate {
      estado ataque:
          print("Atacando!");
          fuerza = fuerza + 10;
      estado defensa:
          print("Defendiendo!");
  }
  ```
- Activar un estado específico:
  ```scorpk
  activar combate ataque; // Ejecuta solo el estado ataque
  ```

## Concurrencia
- Ejecución paralela con `paralelo`:
  ```scorpk
  paralelo {
      saludar();
      print("Ejecutando en paralelo");
  }
  ```

## Impresión
- Mostrar valores o variables:
  ```scorpk
  print("Hola");         // Imprime un texto
  print(fuerza);         // Imprime el valor de una variable
  ```

Esta sintaxis se expandirá en futuras versiones para incluir tipado híbrido, interoperabilidad y más.