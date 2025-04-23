# Scorpk: Un Lenguaje de Programación Minimalista y Potente

Scorpk es un lenguaje de programación en desarrollo, diseñado para ser rápido, seguro y adaptable. Inspirado en la precisión de un escorpión, Scorpk combina una sintaxis limpia con funcionalidades modernas como concurrencia, intenciones y tipado híbrido.

**Estado**: Prototipo (Versión 0.1). Este es un proyecto en sus primeras etapas, ¡y buscamos colaboradores!

## Instalación

1. **Requisitos**:
   - Python 3.8 o superior.
   - Git.

2. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/TuUsuario/scorpk-lang.git
   cd scorpk-lang
   ```

3. **Probar el intérprete**:
   ```bash
   python3 src/interpreter.py examples/test.scpk
   ```

## Uso

Escribe programas en Scorpk (archivos con extensión `.scpk`) y ejécutalos con el intérprete:

```bash
python3 src/interpreter.py <archivo.scpk>
```

Consulta la [sintaxis básica](docs/syntax.md) para ver las funcionalidades soportadas.

## Ejemplo

```scorpk
let fuerza = 10;
fn mostrar_fuerza() {
    print(fuerza);
}
paralelo {
    mostrar_fuerza();
    print("En paralelo");
}
```

## Contribuir

¡Scorpk es de código abierto! Si quieres contribuir:
- Abre un issue o pull request en [GitHub](https://github.com/TuUsuario/scorpk-lang).
- Contacta al equipo en [inserta un canal de comunicación, ej. Discord o X].

## Licencia

MIT License (o la licencia que elijas).