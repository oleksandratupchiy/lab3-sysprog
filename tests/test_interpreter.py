import pytest
from compiler.parser import Parser
from compiler.interpreter import Interpreter, trunc_div
from compiler.errors import SemanticError, ExecutionError
from compiler.semantic import SemanticAnalyzer


def run(body, limit=100_000):
    return Interpreter(limit).run(Parser().parse('int main(){' + body + '}'))


def test_arithmetic_precedence_boolean_short_circuit():
    result = run('return (2+3*4==14) && ((2+3)*4==20) && !0 && +2 && (0 && 1/0 || 5);')
    assert result.return_value == 1
    assert run('return 1 || 1/0;').return_value == 1
    assert run('return 1 < 2 == 1 && 0 || 3 >= 3;').return_value == 1


def test_negative_division_remainder_and_big_integers():
    for left, right, quotient, remainder in [(-7, 3, -2, -1), (7, -3, -2, 1),
                                            (-7, -3, 2, -1), (7, 3, 2, 1)]:
        assert run(f'return {left}/{right};').return_value == quotient
        assert run(f'return {left}%{right};').return_value == remainder
    assert trunc_div(10**100 + 2, -3) == -((10**100 + 2)//3)


def test_scopes_assignment_initialization():
    result = run('int x; x=3; {int x=8; printf("%d",x);} {x=x+1;} return x;')
    assert (result.stdout, result.return_value) == ('8', 4)


def test_dangling_else_and_early_return():
    assert run('if(1) if(0) return 1; else return 2; return 3;').return_value == 2
    assert run('while(1){return 7;} return 8;').return_value == 7


def test_nested_loops_print_and_empty():
    result = run('int i=0; int n=0; ; while(i<3){int j=0; while(j<2){n=n+1;j=j+1;} i=i+1;} printf("%d\\n",n);')
    assert (result.stdout, result.return_value) == ('6\n', 0)


@pytest.mark.parametrize('body', ['return x;', 'int x; int x;', '{int x=0;} return x;',
                                 'printf("%x",1);', 'if(0) return missing;'])
def test_static_errors(body):
    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(Parser().parse('int main(){'+body+'}'))
    assert error.value.line == 1


def test_runtime_errors_and_loop_guard():
    for body in ['return 1/0;', 'return 1%0;', 'int x; return x;',
                 'int x=1; {int x=x;}', 'int x; if(0)x=1; return x;',
                 'int i=0; while(i<2){int x; if(i==0)x=1; printf("%d",x); i=i+1;}']:
        with pytest.raises(ExecutionError):
            run(body)
    with pytest.raises(ExecutionError, match='ліміт'):
        run('while(1);', limit=20)