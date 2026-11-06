import pytest
from compiler.parser import Parser
from compiler.lexer import Lexer
from compiler.errors import LexError, ParseError
from compiler.ast_nodes import BinaryOp


def test_minimal_and_precedence():
    tree = Parser().parse('int main(){return 2 + 3 * 4 == 14;}')
    expr = tree.body.statements[0].expression
    assert isinstance(expr, BinaryOp) and expr.operator == '=='
    assert expr.left.right.operator == '*'


def test_lexer_keywords_operators_comments_locations():
    tokens = Lexer().tokenize('// comment\n/* a\nb */ int main(){return a<=2 && a!=0 || !a;}')
    assert tokens[0].type == 'INT'
    assert (tokens[0].lineno, tokens[0].column) == (3, 6)
    assert {'LE', 'AND', 'NE', 'OR', 'NOT'} <= {t.type for t in tokens}


@pytest.mark.parametrize('source', ['int main(){return 0}', 'int main(){return 2+;}',
                                    'int main( { }', 'int main(){'])
def test_invalid_syntax(source):
    with pytest.raises(ParseError):
        Parser().parse(source)


@pytest.mark.parametrize('source', ['@', '/* never closed', '"unterminated'])
def test_invalid_lexeme(source):
    with pytest.raises(LexError):
        Lexer().tokenize(source)
