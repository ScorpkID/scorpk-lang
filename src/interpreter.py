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
    type: str
    locked: bool = False

# Contexto de ejecución
class ScorpkContext:
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.functions: Dict[str, Callable] = {}
        self.intents: Dict[str, Dict[str, list]] = {}

    def set_var(self, name: str, value: Any, type: str, locked: bool = False):
        self.variables[name] = Variable(name, value, type, locked)

    def get_var(self, name: str) -> Any:
        if name not in self.variables:
            raise ValueError(f"Variable {name} no definida")
        return self.variables[name].value

    def get_var_type(self, name: str) -> str:
        if name not in self.variables:
            raise ValueError(f"Variable {name} no definida")
        return self.variables[name].type

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
        # Declaración de variable: let nombre: tipo = valor;
        if match := re.match(r"let (\w+): (\w+) = (.+);", line):
            name, type, value = match.groups()
            if type not in ["int", "string"]:
                print(f"Error: Tipo {type} no soportado")
                return index + 1
            if type == "int" and not value.isdigit():
                print(f"Error: Valor {value} no es un entero para tipo int")
                return index + 1
            if type == "string" and not (value.startswith('"') and value.endswith('"')):
                print(f"Error: Valor {value} no es un string para tipo string")
                return index + 1
            value = int(value) if type == "int" else value.strip('"')
            if name in self.context.variables and self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
            else:
                self.context.set_var(name, value, type)
            return index + 1

        # Declaración de variable sin tipo: let nombre = valor;
        if match := re.match(r"let (\w+) = (.+);", line):
            name, value = match.groups()
            type = "int" if value.isdigit() else "string" if value.startswith('"') else None
            if type is None:
                print(f"Error: Valor {value} no soportado sin tipo explícito")
                return index + 1
            value = int(value) if type == "int" else value.strip('"')
            if name in self.context.variables and self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
            else:
                self.context.set_var(name, value, type)
            return index + 1

        # Cambio de tipo: nombre -> tipo;
        if match := re.match(r"(\w+) -> (\w+);", line):
            name, new_type = match.groups()
            if new_type not in ["int", "string"]:
                print(f"Error: Tipo {new_type} no soportado")
                return index + 1
            if name not in self.context.variables:
                print(f"Error: Variable {name} no definida")
                return index + 1
            if self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
                return index + 1
            current_value = self.context.get_var(name)
            if new_type == "int" and not isinstance(current_value, int):
                print(f"Error: Valor {current_value} no convertible a int")
                return index + 1
            if new_type == "string" and not isinstance(current_value, str):
                print(f"Error: Valor {current_value} no convertible a string")
                return index + 1
            self.context.variables[name].type = new_type
            return index + 1

        # Asignación con expresión: nombre = expr;
        if match := re.match(r"(\w+) = (.+);", line):
            name, expr = match.groups()
            if name in self.context.variables and self.context.variables[name].locked:
                print(f"Error: No se puede modificar {name}, está bloqueada")
            else:
                value = self.eval_expr(expr)
                if value is not None:
                    var_type = self.context.get_var_type(name)
                    if var_type == "int" and not isinstance(value, int):
                        print(f"Error: Valor {value} no es un entero para {name}")
                    else:
                        self.context.set_var(name, value, var_type)
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

        # Condicional simple: if variable (>|<|==) número acción;
        if match := re.match(r"if (\w+) (>|<|==) (\d+) (.+);", line):
            var_name, op, num, action = match.groups()
            try:
                var_value = self.context.get_var(var_name)
                var_type = self.context.get_var_type(var_name)
                if var_type != "int":
                    print(f"Error: Variable {var_name} debe ser int para comparación")
                    return index + 1
                num = int(num)
                condition_met = False
                if op == ">" and isinstance(var_value, int):
                    condition_met = var_value > num
                elif op == "<" and isinstance(var_value, int):
                    condition_met = var_value < num
                elif op == "==" and isinstance(var_value, int):
                    condition_met = var_value == num
                if condition_met:
                    # Manejar activar
                    if match_action := re.match(r"activar (\w+) (\w+)", action):
                        intent_name, estado = match_action.groups()
                        try:
                            estados = self.context.get_intent(intent_name)
                            if estado in estados:
                                print(f"Ejecutando estado {estado} en intención {intent_name}")
                                for sub_action in estados[estado]:
                                    self.parse_line(sub_action, lines, index)
                            else:
                                print(f"Error: Estado {estado} no definido en intención {intent_name}")
                        except ValueError as e:
                            print(f"Error: {e}")
                    # Manejar llamada a función
                    elif match_action := re.match(r"(\w+)\(\)", action):
                        func_name = match_action.group(1)
                        try:
                            self.context.get_func(func_name)()
                        except ValueError as e:
                            print(f"Error: {e}")
                    # Otras acciones
                    else:
                        self.parse_line(action, lines, index)
            except ValueError as e:
                print(f"Error: {e}")
            return index + 1

        # Condicional con bloque: if variable (>|<|==) número { ... } [else { ... }]
        if match := re.match(r"if (\w+) (>|<|==) (\d+) \{", line):
            var_name, op, num = match.groups()
            if_body = []
            else_body = []
            i = index + 1
            # Recolectar cuerpo del if
            while i < len(lines) and lines[i].rstrip() != "}":
                if_body.append(lines[i])
                i += 1
            if i >= len(lines):
                print(f"Error: Bloque if incompleto, falta '}}'")
                return i
            i += 1  # Saltar el "}"
            # Verificar si hay else
            has_else = i < len(lines) and lines[i].strip() == "else {"
            if has_else:
                i += 1
                while i < len(lines) and lines[i].rstrip() != "}":
                    else_body.append(lines[i])
                    i += 1
                if i >= len(lines):
                    print(f"Error: Bloque else incompleto, falta '}}'")
                    return i
                i += 1  # Saltar el "}"
            try:
                var_value = self.context.get_var(var_name)
                var_type = self.context.get_var_type(var_name)
                if var_type != "int":
                    print(f"Error: Variable {var_name} debe ser int para comparación")
                    return i
                num = int(num)
                condition_met = False
                if op == ">" and isinstance(var_value, int):
                    condition_met = var_value > num
                elif op == "<" and isinstance(var_value, int):
                    condition_met = var_value < num
                elif op == "==" and isinstance(var_value, int):
                    condition_met = var_value == num
                if condition_met:
                    for body_line in if_body:
                        self.parse_line(body_line, lines, index)
                else:
                    for body_line in else_body:
                        self.parse_line(body_line, lines, index)
            except ValueError as e:
                print(f"Error: {e}")
            return i

        # Bucle while: while variable (>|<|==) número { ... }
        if match := re.match(r"while (\w+) (>|<|==) (\d+) \{", line):
            var_name, op, num = match.groups()
            body = []
            i = index + 1
            while i < len(lines) and lines[i].rstrip() != "}":
                body.append(lines[i])
                i += 1
            if i >= len(lines):
                print(f"Error: Bloque while incompleto, falta '}}'")
                return i
            i += 1  # Saltar el "}"
            try:
                while True:
                    var_value = self.context.get_var(var_name)
                    var_type = self.context.get_var_type(var_name)
                    if var_type != "int":
                        print(f"Error: Variable {var_name} debe ser int para comparación")
                        break
                    num = int(num)
                    condition_met = False
                    if op == ">" and isinstance(var_value, int):
                        condition_met = var_value > num
                    elif op == "<" and isinstance(var_value, int):
                        condition_met = var_value < num
                    elif op == "==" and isinstance(var_value, int):
                        condition_met = var_value == num
                    if not condition_met:
                        break
                    for body_line in body:
                        self.parse_line(body_line, lines, index)
            except ValueError as e:
                print(f"Error: {e}")
            return i

        # Bucle for: for variable in inicio..fin { ... }
        if match := re.match(r"for (\w+) in (\d+)\.\.(\d+) \{", line):
            var_name, start, end = match.groups()
            body = []
            i = index + 1
            while i < len(lines) and lines[i].rstrip() != "}":
                body.append(lines[i])
                i += 1
            if i >= len(lines):
                print(f"Error: Bloque for incompleto, falta '}}'")
                return i
            i += 1  # Saltar el "}"
            try:
                start, end = int(start), int(end)
                if var_name in self.context.variables:
                    var_type = self.context.get_var_type(var_name)
                    if var_type != "int":
                        print(f"Error: Variable {var_name} debe ser int para bucle for")
                        return i
                    if self.context.variables[var_name].locked:
                        print(f"Error: Variable {var_name} está bloqueada")
                        return i
                for value in range(start, end + 1):
                    self.context.set_var(var_name, value, "int")
                    for body_line in body:
                        self.parse_line(body_line, lines, index)
            except ValueError as e:
                print(f"Error: {e}")
            return i

        # Concurrencia: paralelo { ... }
        if line == "paralelo {":
            tasks = []
            i = index + 1
            while i < len(lines) and lines[i].rstrip() != "}":
                task = lines[i].strip()
                if task:
                    tasks.append(task)
                i += 1
            if i >= len(lines):
                print(f"Error: Bloque paralelo incompleto, falta '}}'")
                return i
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