"""Bounded arithmetic for spectral channels; never eval/exec user expressions."""
import ast
import re
import numpy as np


def parse(expression):
    if not isinstance(expression, str) or len(expression) > 256:
        raise ValueError('Composite expression exceeds 256 characters')
    try:
        tree = ast.parse(expression.strip(), mode='eval')
    except (SyntaxError, RecursionError) as exc:
        raise ValueError('Composite expression is not valid arithmetic') from exc
    nodes = list(ast.walk(tree))
    if len(nodes) > 64:
        raise ValueError('Composite expression exceeds 64 syntax nodes')
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div,
               ast.UAdd, ast.USub, ast.Name, ast.Load, ast.Constant)
    for node in nodes:
        if not isinstance(node, allowed):
            raise ValueError('Composite expression permits only bands, constants, + - * / and parentheses')
        if isinstance(node, ast.Name) and not re.fullmatch(r'B(?:[1-9]|1[0-2]|3N|8A)', node.id):
            raise ValueError('Composite expression requires exact scientific band IDs, e.g. B8 or B8A')
        if isinstance(node, ast.Constant) and (type(node.value) not in (int,float) or not np.isfinite(node.value) or abs(node.value)>1e6):
            raise ValueError('Composite expression constant is invalid')
    bands = {n.id for n in nodes if isinstance(n, ast.Name)}
    if not bands:
        raise ValueError('Composite expression must reference at least one band')
    return tree.body, bands


def calculate(expression, bands, epsilon=1e-8):
    tree, required = parse(expression)
    if not required <= bands.keys():
        raise ValueError('Composite missing scientific bands: ' + ', '.join(sorted(required-bands.keys())))
    def visit(node):
        if isinstance(node, ast.Name): return bands[node.id]
        if isinstance(node, ast.Constant): return float(node.value)
        if isinstance(node, ast.UnaryOp): return -visit(node.operand) if isinstance(node.op, ast.USub) else visit(node.operand)
        left, right = visit(node.left), visit(node.right)
        if isinstance(node.op, ast.Add): return left + right
        if isinstance(node.op, ast.Sub): return left - right
        if isinstance(node.op, ast.Mult): return left * right
        return np.where(np.abs(right) > epsilon, left / right, np.nan)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        result = np.asarray(visit(tree), dtype='float32')
    return np.where(np.isfinite(result), result, np.nan).astype('float32')
