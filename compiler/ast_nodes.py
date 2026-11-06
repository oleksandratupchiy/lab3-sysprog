from dataclasses import dataclass


@dataclass(kw_only=True)
class Node:
    line: int = 1
    column: int = 1


@dataclass
class Program(Node):
    body: 'Block'


@dataclass
class Block(Node):
    statements: list[Node]


@dataclass
class Declaration(Node):
    name: str
    initializer: Node | None = None


@dataclass
class Assignment(Node):
    name: str
    expression: Node


@dataclass
class Variable(Node):
    name: str


@dataclass
class IntegerLiteral(Node):
    value: int


@dataclass
class BinaryOp(Node):
    operator: str
    left: Node
    right: Node


@dataclass
class UnaryOp(Node):
    operator: str
    operand: Node


@dataclass
class If(Node):
    condition: Node
    then_branch: Node
    else_branch: Node | None = None


@dataclass
class While(Node):
    condition: Node
    body: Node


@dataclass
class Print(Node):
    format: str
    expression: Node


@dataclass
class Return(Node):
    expression: Node


@dataclass
class Empty(Node):
    pass
