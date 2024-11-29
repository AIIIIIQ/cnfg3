import sys
import argparse
import json
import re

class ConfigParser:
    def __init__(self):
        self.constants = {}
        self.tokens = []
        self.pos = 0

    def tokenize(self, text):
        # Удаление комментариев
        text = re.sub(r'%.*', '', text)
        text = re.sub(r'--\[\[.*?\]\]-*', '', text, flags=re.DOTALL)
        # Правила токенизации
        token_specification = [
            ('NUMBER',   r'\d+(\.\d*)?'),       # Числа
            ('NAME',     r'[A-Z]+'),            # Имена (заглавные буквы)
            ('VAR',      r'var'),               # Ключевое слово var
            ('ASSIGN',   r':='),                # Оператор присваивания
            ('EVAL',     r'\|'),                # Оператор вычисления
            ('LPAREN',   r'\('),                # Левая скобка
            ('RPAREN',   r'\)'),                # Правая скобка
            ('LBRACE',   r'\{'),                # Левая фигурная скобка
            ('RBRACE',   r'\}'),                # Правая фигурная скобка
            ('COMMA',    r','),                 # Запятая
            ('EQUAL',    r'='),                 # Знак равно
            ('SEMICOLON',r';'),                 # Точка с запятой
            ('SKIP',     r'[ \t\r\n]+'),        # Пробелы и переносы строк
            ('MISMATCH', r'.'),                 # Любой другой символ
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        for mo in re.finditer(tok_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Unexpected character {value}')
            self.tokens.append((kind, value))

    def parse(self):
        results = []
        while self.pos < len(self.tokens):
            result = self.parse_value()
            if result is not None:
                results.append(result)
        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            return results
        else:
            return None

    def parse_value(self):
        if self.pos >= len(self.tokens):
            raise SyntaxError('Expected a value, but reached end of input')
        if self.match('VAR'):
            self.parse_var()
            return None
        elif self.match('EVAL'):
            return self.parse_eval()
        elif self.match('NAME'):
            return self.parse_assignment()
        elif self.match('NUMBER'):
            return self.consume('NUMBER')[1]
        elif self.match('LPAREN'):
            return self.parse_array()
        elif self.match('LBRACE'):
            return self.parse_dict()
        else:
            raise SyntaxError('Expected a value')

    def parse_assignment(self):
        name = self.consume('NAME')[1]
        self.consume('EQUAL')
        value = self.parse_value()
        return {name: value}

    def parse_array(self):
        self.consume('LPAREN')
        array = []
        while True:
            if self.match('RPAREN'):
                break
            array.append(self.parse_value())
            if self.match('COMMA'):
                self.consume('COMMA')
            elif self.match('RPAREN'):
                break
            else:
                raise SyntaxError('Expected comma or right parenthesis')
        self.consume('RPAREN')
        return array

    def parse_dict(self):
        self.consume('LBRACE')
        obj = {}
        while not self.match('RBRACE'):
            if self.pos >= len(self.tokens):
                raise SyntaxError('Expected a name or closing brace')
            if not self.match('NAME'):
                raise SyntaxError('Expected a name')
            key = self.consume('NAME')[1]
            self.consume('EQUAL')
            value = self.parse_value()
            obj[key] = value
        self.consume('RBRACE')
        return obj

    def parse_var(self):
        self.consume('VAR')
        if not self.match('NAME'):
            raise SyntaxError('Expected a name after var')
        name = self.consume('NAME')[1]
        self.consume('ASSIGN')
        value = self.parse_value()
        self.consume('SEMICOLON')
        self.constants[name] = value

    def parse_eval(self):
        self.consume('EVAL')
        if not self.match('NAME'):
            raise SyntaxError('Expected a name after |')
        name = self.consume('NAME')[1]
        if name not in self.constants:
            raise SyntaxError(f'Undefined constant {name}')
        self.consume('EVAL')
        return self.constants[name]

    def match(self, kind):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] == kind

    def consume(self, kind):
        if self.match(kind):
            tok = self.tokens[self.pos]
            self.pos += 1
            return tok
        else:
            raise SyntaxError(f'Expected {kind}')

def main():
    parser = argparse.ArgumentParser(description='Config Parser')
    parser.add_argument('-i', '--input', required=True, help='Input configuration file')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        config_parser = ConfigParser()
        config_parser.tokenize(text)
        result = config_parser.parse()
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print('Parsing completed successfully.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()