import argparse
import yaml
import re
from typing import Any, Dict, Union


class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text: str) -> Dict[str, Any]:
        self.constants = {}
        lines = text.splitlines()
        result = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('*>'):
                i += 1
                continue
            if '<-' in line:
                self._parse_constant(line)
                i += 1
            elif line.startswith('struct') or '=' in line:
                struct_name, struct_value, skip_lines = self._parse_struct(lines, i)
                result[struct_name] = struct_value
                i += skip_lines
            else:
                i += 1
        return result

    def _parse_constant(self, line: str):
        match = re.match(r"([a-z]+)\s*<-\s*(.+);", line)
        if not match:
            raise SyntaxError(f"Invalid constant declaration: {line}")
        name, value = match.groups()
        self.constants[name] = self._evaluate_expression(value)

    def _evaluate_expression(self, expr: str) -> Union[int, str]:
        if expr.startswith('$') and expr.endswith('$'):
            expr = expr[1:-1].strip()
            tokens = expr.split()
            stack = []
            for token in tokens:
                if token.isdigit():
                    stack.append(int(token))
                elif token in self.constants:
                    stack.append(self.constants[token])
                elif token == '+':
                    b, a = stack.pop(), stack.pop()
                    stack.append(a + b)
                elif token == '-':
                    b, a = stack.pop(), stack.pop()
                    stack.append(a - b)
                elif token == 'min':
                    b, a = stack.pop(), stack.pop()
                    stack.append(min(a, b))
                elif token == 'mod':
                    b, a = stack.pop(), stack.pop()
                    stack.append(a % b)
                else:
                    raise ValueError(f"Unknown token in expression: {token}")
            if len(stack) != 1:
                raise ValueError(f"Invalid expression: {expr}")
            return stack[0]
        elif expr.isdigit():
            return int(expr)
        elif expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]
        else:
            raise ValueError(f"Invalid constant value: {expr}")

    def _parse_struct(self, lines, start_index: int) -> (str, Dict[str, Any], int):
        struct_declaration = lines[start_index].strip()
        match = re.match(r"([a-zA-Z0-9_]+)\s*=\s*struct\s*\{", struct_declaration)
        if match:
            struct_name = match.group(1)
            struct = {}
            i = start_index + 1
            open_braces = 1

            while i < len(lines):
                line = lines[i].strip()
                if line == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        return struct_name, struct, i - start_index + 1
                elif line == '{':
                    open_braces += 1
                elif 'struct' in line:
                    nested_name, nested_value, nested_lines = self._parse_struct(lines, i)
                    struct[nested_name] = nested_value
                    i += nested_lines - 1
                elif '=' in line:
                    key_value_match = re.match(r"([A-z0-9_]+)\s*=\s*(.*?),", line)
                    if key_value_match:
                        key, value = key_value_match.groups()
                        struct[key] = self._evaluate_expression(value)
                    else:
                        raise SyntaxError(f"Invalid key-value pair: {line}")
                i += 1

            raise SyntaxError(f"Struct {struct_name} is not properly closed with '}}'")

        # Handle the case where the structure is defined on its own (e.g., struct Foo { ... })
        match = re.match(r"struct\s+([A-z]+)\s*\{", struct_declaration)
        if match:
            struct_name = match.group(1)
            struct = {}
            i = start_index + 1
            open_braces = 1

            while i < len(lines):
                line = lines[i].strip()
                if line == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        return struct_name, struct, i - start_index + 1
                elif line == '{':
                    open_braces += 1
                elif line.startswith("struct") or '=' in line:
                    # Handle nested structure
                    nested_name, nested_value, nested_lines = self._parse_struct(lines, i)
                    struct[nested_name] = nested_value
                    i += nested_lines - 1
                elif '=' in line:
                    key_value_match = re.match(r"([A-z0-9_]+)\s*=\s*(.*?),", line)
                    if key_value_match:
                        key, value = key_value_match.groups()
                        struct[key] = self._evaluate_expression(value)
                    else:
                        raise SyntaxError(f"Invalid key-value pair: {line}")
                i += 1

            raise SyntaxError(f"Struct {struct_name} is not properly closed with '}}'")

        raise SyntaxError(f"Invalid struct declaration: {struct_declaration}")

def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык преобразователь в YAML.")
    parser.add_argument("--input", required=True,
                        help="Путь к файлу с входным текстом на учебном конфигурационном языке.")
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print(f"Файл {args.input} не найден.")
        return

    try:
        config_parser = ConfigParser()
        parsed_data = config_parser.parse(text)
        print(yaml.dump(parsed_data, allow_unicode=True, default_flow_style=False))
    except (SyntaxError, ValueError) as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
