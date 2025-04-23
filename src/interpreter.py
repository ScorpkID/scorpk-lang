import re
import threading
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        self.intents: Dict[str, Dict[str, list]] = {}  # Almacena intenciones y sus estados

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

    def set_intent(self, name: str, estados: Dict[str, list]):
        self.intents[name] = estados

    def get_intent(self, name: str) -> Dict[str, list]:
        if name not in self.intents:
            raise ValueError(f"Intención {name} no definida")
        return self.intents[name]

# Intérprete de Scorpk
class ScorpkInterpreter:
    def __init__(self):
        self.context = ScorpkContext()

    def execute(self, code: str):
        lines = code.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line or line.startswith("//"):
                i += 1
                continue
            i = self.parse_line(line, lines, i)

    def eval_expr(self, expr: str) -> Any:
        # Evalúa expresiones como "variable + número" o "variable * número"
        if match := re.match(r"(\w+) \+ (\d+)", expr):
            var_name, num = match.groups()
            try:
                var_value = self.context.get_var(var_name)
                if isinstance(var_value, int):
                    return var_value + int(num)
                raise ValueError(f"Operación no soportada para {var_name}")
            except ValueError as e:
                print(f"Error: {e}")
                return None
        elif match := re.match(r"(\w+) - (\d+)", expr):
            var_name, num = match.groups()
            try:
                var_value = self.context.get_var(var_name)
                if isinstance(var_value, int):
                    return var_value - int(num)
                raise ValueError(f"Operación no soportada para {var_name}")
            except ValueError as e:
                print(f"Error: {e}")
                return None
        elif match := re.match(r"(\w+) \* (\d+)", expr):
            var_name, num = match.groups()
            try:
                var_value = self.context.get_var(var_name)
                if isinstance(var_value, int):
                    return var_value * int(num)
                raise ValueError(f"Operación no soportada para {var_name}")
            except ValueError as e:
                print(f"Error: {e}")
                return None
        return None

    def parse_line(self, line: str, lines: list, index: int) -> int:
        line = line.strip()
        # Declaración de variable: let nombre = valor;
        if match := re.match(r"let (\w+) = (.+);", line):
            name, value = match.groups()
            value = value.strip('"') if value.startswith('"') else int(value) if value.isdigit() else value
            if name in self.context.variables and self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
            else:
                self.context.set_var(name, value)
            return index + 1

        # Asignación con expresión: nombre = expr;
        if match := re.match(r"(\w+) = (.+);", line):
            name, expr = match.groups()
            if name in self.context.variables and self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
            else:
                value = self.eval_expr(expr)
                if value is not None:
                    self.context.set_var(name, value)
                else:
                    print(f"Error: Expresión no válida: {expr}")
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
            while i < len(lines) and lines[i].rstrip() != "}":
                body.append(lines[i])
                i += 1
            def func():
                for body_line in body:
                    self.parse_line(body_line, lines, i)
            self.context.set_func(func_name, func)
            return i + 1

        # Intención: intent nombre { ... }
        if match := re.match(r"intent (\w+) \{", line):
            intent_name = match.group(1)
            estados = {}
            i = index + 1
            current_estado = None
            while i < len(lines) and lines[i].rstrip() != "}":
                line = lines[i].strip()
                if match := re.match(r"estado (\w+):", line):
                    current_estado = match.group(1)
                    estados[current_estado] = []
                elif current_estado and line:
                    estados[current_estado].append(line)
                i += 1
            self.context.set_intent(intent_name, estados)
            for estado, actions in estados.items():
                print(f"Ejecutando estado {estado} en intención {intent_name}")
                for action in actions:
                    self.parse_line(action, lines, i)
            return i + 1

        # Activar intención: activar nombre estado;
        if match := re.match(r"activar (\w+) (\w+);", line):
            intent_name, estado = match.groups()
            try:
                estados = self.context.get_intent(intent_name)
                if estado in estados:
                    print(f"Ejecutando estado {estado} en intención {intent_name}")
                    for action in estados[estado]:
                        self.parse_line(action, lines, index)
                else:
                    print(f"Error: Estado {estado} no definido en intención {intent_name}")
            except ValueError as e:
                print(f"Error: {e}")
            return index + 1

        # Concurrencia: paralelo { ... }
        if line == "paralelo {":
            tasks = []
            i = index + 1
            while i < len(lines) and lines[i].rstrip() != "}":
                task = lines[i].strip()
                if task:
                    tasks.append(task)
                i += 1
            threads = []
            for task in tasks:
                if match := re.match(r"(\w+)\(\);", task):
                    func_name = match.group(1)
                    try:
                        func = self.context.get_func(func_name)
                        thread = threading.Thread(target=func)
                        threads.append(thread)
                    except ValueError as e:
                        print(f"Error: {e}")
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

        # Impresión: print("texto"); o print(nombre);
        if match := re.match(r"print\((.+)\);", line):
            arg = match.group(1).strip('"')
            try:
                value = self.context.get_var(arg) if arg in self.context.variables else arg
                print(value)
            except ValueError as e:
                print(f"Error: {e}")
            return index + 1

        print(f"Error: Línea no reconocida: {line}")
        return index + 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python src/interpreter.py <archivo.scpk>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as file:
        code = file.read()
    interpreter = ScorpkInterpreter()
    interpreter.execute(code)