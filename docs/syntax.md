# Sintaxis Básica de Scorpk (Versión Prototipo 0.4)

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

## Condicionales
- Ejecución condicional con `if`:
  ```scorpk
  if poder > 50 print("Fuerte"); // Imprime si variable > número
  if energia < 30 activar combate atacar; // Activa si variable < número
  if recursos == 40 mostrar_analisis(); // Ejecuta si variable == número
  ```
- Bloques `if` para múltiples acciones:
  ```scorpk
  if amenaza == 30 {
      activar respuesta evacuar;
      print("Amenaza crítica");
  }
  ```
- Condicionales con `else`:
  ```scorpk
  if amenaza > 20 {
      activar tactica atacar;
      print("Amenaza alta");
  } else {
      activar tactica replegarse;
      print("Amenaza baja");
  }
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