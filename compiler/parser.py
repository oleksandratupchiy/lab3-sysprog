from pathlib import Path
import ply.yacc as yacc
from . import ast_nodes as a
from .lexer import Lexer
from .errors import ParseError


class Parser:
    tokens = Lexer.tokens
    precedence = (
        ('nonassoc', 'IF_WITHOUT_ELSE'), ('nonassoc', 'ELSE'),
        ('left', 'OR'), ('left', 'AND'), ('left', 'EQ', 'NE'),
        ('left', 'LT', 'LE', 'GT', 'GE'), ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('right', 'UPLUS', 'UMINUS', 'NOT'))

    def __init__(self, diagnostics=None):
        self.lexer = Lexer()
        options = {}
        if diagnostics:
            path = Path(diagnostics)
            path.parent.mkdir(parents=True, exist_ok=True)
            options['debugfile'] = str(path.resolve())
        self.parser = yacc.yacc(module=self, start='program', method='LALR',
                                write_tables=False, debug=bool(diagnostics), **options)

    def parse(self, source):
        self.lexer.input(source)
        return self.parser.parse(lexer=self.lexer, tracking=True)

    def loc(self, p, i=1):
        return dict(line=p.lineno(i), column=self.lexer.column(p.lexpos(i)))

    def p_program(self, p):
        'program : INT MAIN LPAREN RPAREN block'
        p[0] = a.Program(p[5], **self.loc(p))

    def p_block(self, p):
        'block : LBRACE statements RBRACE'
        p[0] = a.Block(p[2], **self.loc(p))

    def p_statements(self, p):
        '''statements : statements statement
                      | statements declaration
                      |'''
        p[0] = p[1] + [p[2]] if len(p) == 3 else []

    def p_declaration(self, p):
        '''declaration : INT ID SEMI
                       | INT ID ASSIGN expression SEMI'''
        p[0] = a.Declaration(p[2], p[4] if len(p) == 6 else None, **self.loc(p))

    def p_statement_block(self, p):
        'statement : block'
        p[0] = p[1]

    def p_assignment(self, p):
        'statement : ID ASSIGN expression SEMI'
        p[0] = a.Assignment(p[1], p[3], **self.loc(p))

    def p_if(self, p):
        '''statement : IF LPAREN expression RPAREN statement %prec IF_WITHOUT_ELSE
                     | IF LPAREN expression RPAREN statement ELSE statement'''
        p[0] = a.If(p[3], p[5], p[7] if len(p) == 8 else None, **self.loc(p))

    def p_while(self, p):
        'statement : WHILE LPAREN expression RPAREN statement'
        p[0] = a.While(p[3], p[5], **self.loc(p))

    def p_print(self, p):
        'statement : PRINTF LPAREN STRING COMMA expression RPAREN SEMI'
        p[0] = a.Print(p[3], p[5], **self.loc(p))

    def p_return(self, p):
        'statement : RETURN expression SEMI'
        p[0] = a.Return(p[2], **self.loc(p))

    def p_empty(self, p):
        'statement : SEMI'
        p[0] = a.Empty(**self.loc(p))

    def p_binary(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression MOD expression
                      | expression EQ expression
                      | expression NE expression
                      | expression LT expression
                      | expression LE expression
                      | expression GT expression
                      | expression GE expression
                      | expression AND expression
                      | expression OR expression'''
        p[0] = a.BinaryOp(p[2], p[1], p[3], **self.loc(p, 2))

    def p_unary(self, p):
        '''expression : MINUS expression %prec UMINUS
                      | PLUS expression %prec UPLUS
                      | NOT expression'''
        p[0] = a.UnaryOp(p[1], p[2], **self.loc(p))

    def p_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_literal(self, p):
        'expression : NUMBER'
        p[0] = a.IntegerLiteral(p[1], **self.loc(p))

    def p_variable(self, p):
        'expression : ID'
        p[0] = a.Variable(p[1], **self.loc(p))

    def p_error(self, token):
        if token:
            raise ParseError(f'Неочікуваний токен {token.value!r}',
                             line=token.lineno, column=token.column)
        source = self.lexer.source
        raise ParseError('Неочікуваний кінець файлу', line=source.count('\n') + 1,
                         column=self.lexer.column(len(source)))
