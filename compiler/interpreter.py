from dataclasses import dataclass
from . import ast_nodes as a
from .semantic import SemanticAnalyzer
from .errors import ExecutionError


def trunc_div(left: int, right: int) -> int:
    """Ділення до нуля без перетворення на float."""
    quotient = abs(left) // abs(right)
    return -quotient if (left < 0) != (right < 0) else quotient


@dataclass
class Result:
    stdout: str
    return_value: int
    steps: int


class _Return(Exception):
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self, step_limit=100_000):
        if step_limit <= 0:
            raise ValueError('Ліміт кроків має бути додатним')
        self.step_limit = step_limit

    def run(self, program):
        self.bindings = SemanticAnalyzer().analyze(program)
        self.values = {}
        self.output = []
        self.steps = 0
        value = 0
        try:
            self.statement(program.body)
        except _Return as returned:
            value = returned.value
        return Result(''.join(self.output), value, self.steps)

    def tick(self, node):
        self.steps += 1
        if self.steps > self.step_limit:
            raise ExecutionError('Перевищено ліміт кроків', node)

    def expression(self, node):
        if isinstance(node, a.IntegerLiteral):
            return node.value
        if isinstance(node, a.Variable):
            value = self.values[self.bindings[id(node)]]
            if value is None:
                raise ExecutionError(f'Змінна {node.name!r} не ініціалізована', node)
            return value
        if isinstance(node, a.UnaryOp):
            value = self.expression(node.operand)
            return {'+': lambda: value, '-': lambda: -value,
                    '!': lambda: int(not value)}[node.operator]()
        left = self.expression(node.left)
        op = node.operator
        if op == '&&':
            return int(bool(left) and bool(self.expression(node.right)))
        if op == '||':
            return int(bool(left) or bool(self.expression(node.right)))
        right = self.expression(node.right)
        if op in ('/', '%'):
            if right == 0:
                raise ExecutionError('Ділення на нуль', node)
            quotient = trunc_div(left, right)
            return quotient if op == '/' else left - quotient * right
        return {'+': lambda: left + right, '-': lambda: left - right,
                '*': lambda: left * right, '==': lambda: int(left == right),
                '!=': lambda: int(left != right), '<': lambda: int(left < right),
                '<=': lambda: int(left <= right), '>': lambda: int(left > right),
                '>=': lambda: int(left >= right)}[op]()

    def statement(self, node):
        self.tick(node)
        if isinstance(node, a.Block):
            for statement in node.statements:
                self.statement(statement)
        elif isinstance(node, a.Declaration):
            symbol = self.bindings[id(node)]
            self.values[symbol] = None
            if node.initializer is not None:
                self.values[symbol] = self.expression(node.initializer)
        elif isinstance(node, a.Assignment):
            self.values[self.bindings[id(node)]] = self.expression(node.expression)
        elif isinstance(node, a.Print):
            self.output.append(node.format % self.expression(node.expression))
        elif isinstance(node, a.Return):
            raise _Return(self.expression(node.expression))
        elif isinstance(node, a.If):
            branch = node.then_branch if self.expression(node.condition) else node.else_branch
            if branch is not None:
                self.statement(branch)
        elif isinstance(node, a.While):
            while True:
                self.tick(node.condition)
                if not self.expression(node.condition):
                    break
                self.statement(node.body)