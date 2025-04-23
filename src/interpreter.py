import re
import threading
from dataclasses import dataclass
from typing import Dict, Any, Callable

# Representa una variable en Scorpk
@dataclass
class Variable:
    name: str
    value: Any
    locked: bool = False

# Contexto de ejecución
class ScorpkContext:
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.functions: Dict[str, Callable] = {}

    def set_var(self, name: str, value: Any, locked: bool = False):
        self.variables[name] = Variable(name, value, locked)

    def get_var(self, name: str) -> Any:
        if name not in self.variables:
            raise ValueError(f"Variable {name} no definida")
        return self.variables[name].value

    def set_func(self, name: str, func: Callable):
        self.functions[name] = func

    def get_func(self, name: str) -> Callable:
        if name not in self.functions:
            raise ValueError(f"Función {name} no definida")
        return self.functions[name]

# Intérprete de Scorpk
class ScorpkInterpreter:
    def __init__(self):
        self.context = ScorpkContext()
        self.current_indent = 0

    def execute(self, code: str):
        lines = code.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("//"):
                i += 1
                continue
            i = self.parse_line(line, lines, i)

    def parse_line(self, line: str, lines: list, index: int) -> int:
        # Declaración de variable: let nombre = valor;
        if match := re.match(r"let (\w+) = (.+);", line):
            name, value = match.groups()
            value = value.strip('"') if value.startswith('"') else int(value) if value.isdigit() else value
            if name in self.context.variables and self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
            else:
                self.context.set_var(name, value)
            return index + 1

        # Bloqueo de variable: lock(nombre);
        if match := re.match(r"lock\((\w+)\);", line):
            name = match.group(1)
            if name in self.context.variables:
                self.context.variables[name].locked = True
            else:
                print(f"Error: Variable {name} no definida")
            return index + 1

        # Declaración de función: fn nombre() { ... }
        if match := re.match(r"fn (\w+)\(\) \{", line):
            func_name = match.group(1)
            body = []
            i = index + 1
            while i < len(lines) and not lines[i].strip() == "}":
                body.append(lines[i])
                i += 1
            def func():
                for body_line in body:
                    self.parse_line(body_line.strip(), lines, i)
            self.context.set_func(func_name, func)
            return i + 1

        # Intención: intent nombre { ... }
        if match := re.match(r"intent (\w+) \{", line):
            intent_name = match.group(1)
            i = index + 1
            while i < len(lines) and not lines[i].strip() == "}":
                if match := re.match(r"\s*estado (\w+):", lines[i]):
                    estado = match.group(1)
                    print(f"Ejecutando estado {estado} en intención {intent_name}")
                i += 1
            return i + 1

        # Concurrencia: paralelo { ... }
        if line == "paralelo {":
            tasks = []
            i = index + 1
            while i < len(lines) and not lines[i].strip() == "}":
                tasks.append(lines[i].strip())
                i += 1
            threads = []
            for task in tasks:
                if match := re.match(r"(\w+)\(\);", task):
                    func_name = match.group(1)
                    thread = threading.Thread(target=lambda: self.context.get_func(func_name)())
                    threads.append(thread)
                elif match := re.match(r"print\((.+)\);", task):
                    msg = match.group(1).strip('"')
                    thread = threading.Thread(target=lambda: print(msg))
                    threads.append(thread)
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            return i + 1

        # Llamada a función: nombre();
        if match := re.match(r"(\w+)\(\);", line):
            func_name = match.group(1)
            try:
                self.context.get_func(func_name)()
            except ValueError as e:
                print(f"Error: {e}")
            return index + 1

        # Impresión: print("texto");
        if match := re.match(r"print\((.+)\);", line):
            msg = match.group(1).strip('"')
            print(msg)
            return index + 1

        print(f"Error: Línea no reconocida: {line}")
        return index + 1

# Programa de prueba
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python3 interpreter.py <archivo.scpk>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        code = file.read()
    interpreter = ScorpkInterpreter()
    interpreter.execute(code)