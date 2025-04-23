# Sintaxis Básica de Scorpk (Versión Prototipo 0.1)

Scorpk es un lenguaje minimalista y potente. Este documento define la sintaxis inicial para el prototipo.

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

## Funciones
- Declaración con `fn`:
  ```scorpk
  fn saludar() {
      return texto;       // Retorna variable del entorno
  }
  ```

## Intenciones
- Bloques `intent` para flujos basados en estados:
  ```scorpk
  intent combate {
      estado ataque:
          print("Atacando!");
      estado defensa:
          print("Defendiendo!");
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

Esta sintaxis se expandirá en futuras versiones para incluir tipado híbrido, interoperabilidad y más.