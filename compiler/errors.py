class CompilerError(Exception):
    """Помилка вхідної програми з координатами."""

    def __init__(self, message, node=None, *, line=None, column=None):
        self.line = line if line is not None else getattr(node, 'line', None)
        self.column = column if column is not None else getattr(node, 'column', None)
        location = f'{self.line}:{self.column}: ' if self.line else ''
        super().__init__(location + message)


class LexError(CompilerError):
    pass


class ParseError(CompilerError):
    pass


class SemanticError(CompilerError):
    pass


class ExecutionError(CompilerError):
    pass
