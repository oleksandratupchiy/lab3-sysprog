import ply.lex as lex
from .errors import LexError


class Lexer:
    reserved = {word: word.upper() for word in
                ('int', 'main', 'if', 'else', 'while', 'return', 'printf')}
    tokens = tuple(reserved.values()) + (
        'ID', 'NUMBER', 'STRING', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'AND', 'OR', 'NOT', 'ASSIGN',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMI', 'COMMA')
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_EQ = r'=='
    t_NE = r'!='
    t_LE = r'<='
    t_GE = r'>='
    t_LT = r'<'
    t_GT = r'>'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_ASSIGN = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMI = r';'
    t_COMMA = r','
    t_ignore = ' \t\r'

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def input(self, source):
        self.source = source
        self.lexer.lineno = 1
        self.lexer.input(source)

    @property
    def lineno(self):
        return getattr(getattr(self, 'lexer', None), 'lineno', 1)

    @property
    def lexpos(self):
        return getattr(getattr(self, 'lexer', None), 'lexpos', 0)

    def token(self):
        token = self.lexer.token()
        if token:
            token.column = self.column(token.lexpos)
        return token

    def column(self, position):
        return position - self.source.rfind('\n', 0, position)

    def t_COMMENT(self, t):
        r'//[^\n]*|/\*(?:[^*]|\*(?!/))*\*/'
        t.lexer.lineno += t.value.count('\n')

    def t_UNCLOSED_COMMENT(self, t):
        r'/\*(?:[^*]|\*(?!/))*$'
        raise LexError('Незавершений блоковий коментар', line=t.lineno,
                       column=self.column(t.lexpos))

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_STRING(self, t):
        r'"(?:[^"\\\n]|\\[^\n])*"'
        # Інші формати відхиляє семантичний аналізатор.
        t.value = t.value[1:-1].replace('\\n', '\n')
        return t

    def t_NUMBER(self, t):
        r'[0-9]+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_error(self, t):
        raise LexError(f'Неприпустимий символ {t.value[0]!r}', line=t.lineno,
                       column=self.column(t.lexpos))

    def tokenize(self, source):
        self.input(source)
        return list(iter(self.token, None))
