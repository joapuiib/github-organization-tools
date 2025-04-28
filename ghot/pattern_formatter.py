import ast
import re
import unicodedata
from string import Formatter

def words(s, index, delimiter=' '):
    """
    Splits a string into words and returns the word at the specified index.
    """
    words_list = s.split(delimiter)
    if index < 0 or index >= len(words_list):
        return ''
    return words_list[index]


def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )


class PatternFormatter:
    ALLOWED_FUNCS = {
        'lower': str.lower,
        'upper': str.upper,
        'title': str.title,
        'strip': str.strip,
        'words': words,
        'replace': str.replace,
        'remove_accents': remove_accents,
    }

    def __init__(self, schema=None):
        self.schema = schema or {}

    def resolve_field(self, name, row):
        match = re.match(r'^f(\d+)$', name)
        if match:
            index = int(match.group(1))
            if index < 0 or index >= len(row):
                raise ValueError(f"Index {index} out of range for row with length {len(row)}")
            return row[index]
        elif name in self.schema:
            index = self.schema.get(name)
            return row[index]
        else:
            raise ValueError(f"Field '{name}' not found in schema")

    def apply_expr(self, expr, row):
        tree = ast.parse(expr, mode='eval')

        class Visitor(ast.NodeVisitor):
            def __init__(self, outer):
                self.outer = outer

            def visit_Expression(self, node):
                return self.visit(node.body)

            def visit_Name(self, node):
                return self.outer.resolve_field(node.id, row)

            def visit_Constant(self, node):
                return node.value

            def visit_Str(self, node):
                return node.s

            def visit_Call(self, node):
                func = self.visit(node.func)
                args = [self.visit(arg) for arg in node.args]
                return func(*args)

            def visit_Attribute(self, node):
                value = self.visit(node.value)
                attr = node.attr
                if attr not in self.outer.ALLOWED_FUNCS:
                    raise ValueError(f"Unsupported method '{attr}' on expression: {expr}")
                return lambda *args: self.outer.ALLOWED_FUNCS[attr](value, *args)

        return Visitor(self).visit(tree)

    def format(self, pattern, row):
        result = ''
        for literal, field, _, _ in Formatter().parse(pattern):
            result += literal
            if field:
                # Handle optional/default with "?" operator
                if '?' in field:
                    exprs = field.split('?', 1)
                    for expr in exprs:
                        try:
                            value = self.apply_expr(expr, row)
                            result += str(value)
                            break
                        except Exception:
                            continue
                else:
                    value = self.apply_expr(field, row)
                    result += str(value)
        return result

