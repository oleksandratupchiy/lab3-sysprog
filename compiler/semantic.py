"""Лексичне зв'язування і перевірки до виконання; ініціалізація — динамічна."""
from . import ast_nodes as a
from .errors import SemanticError


class SemanticAnalyzer:
    def analyze(self, program):
        self.scopes = []
        self.bindings = {}
        self.counter = 0
        self.visit(program.body)
        return self.bindings

    def lookup(self, node):
        for scope in reversed(self.scopes):
            if node.name in scope:
                self.bindings[id(node)] = scope[node.name]
                return
        raise SemanticError(f'Невідома змінна {node.name!r}', node)

    def visit(self, node):
        if isinstance(node, a.Block):
            self.scopes.append({})
            for statement in node.statements:
                self.visit(statement)
            self.scopes.pop()
        elif isinstance(node, a.Declaration):
            if node.name in self.scopes[-1]:
                raise SemanticError(f'Повторне оголошення {node.name!r}', node)
            self.counter += 1
            symbol = f'v_{self.counter}_{node.name}'
            self.scopes[-1][node.name] = symbol
            self.bindings[id(node)] = symbol
            if node.initializer is not None:
                self.visit(node.initializer)
        elif isinstance(node, a.Variable):
            self.lookup(node)
        elif isinstance(node, a.Assignment):
            self.lookup(node)
            self.visit(node.expression)
        elif isinstance(node, a.BinaryOp):
            self.visit(node.left)
            self.visit(node.right)
        elif isinstance(node, a.UnaryOp):
            self.visit(node.operand)
        elif isinstance(node, a.If):
            self.visit(node.condition)
            self.visit(node.then_branch)
            if node.else_branch is not None:
                self.visit(node.else_branch)
        elif isinstance(node, a.While):
            self.visit(node.condition)
            self.visit(node.body)
        elif isinstance(node, (a.Return, a.Print)):
            if isinstance(node, a.Print) and node.format not in ('%d', '%d\n'):
                raise SemanticError('printf підтримує лише "%d" та "%d\\n"', node)
            self.visit(node.expression)