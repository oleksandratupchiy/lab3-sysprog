import json
from pathlib import Path
import subprocess
import sys
import pytest
from compiler.parser import Parser
from compiler.code_generator import generate
from compiler.interpreter import Interpreter
from compiler.ast_serializer import serialize

ROOT = Path(__file__).resolve().parents[1]


def generated_result(source, tmp_path, step_limit=100_000):
    program = Parser().parse(source)
    generated = generate(program, step_limit)
    compile(generated, '<generated>', 'exec')
    path = tmp_path / 'program.py'
    path.write_text(generated, encoding='utf-8')
    harness = '''import contextlib,io,json,runpy,sys
module = runpy.run_path(sys.argv[1])
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    value = module['main']()
print(json.dumps([buffer.getvalue(),value]))
'''
    process = subprocess.run([sys.executable, '-I', '-c', harness, str(path)],
                             capture_output=True, text=True, timeout=5)
    return program, process, path


@pytest.mark.parametrize('filename', ['arithmetic.c', 'conditions.c', 'loops.c', 'complex.c'])
def test_example_differential(filename, tmp_path):
    source = (ROOT / 'examples' / filename).read_text(encoding='utf-8')
    tree, process, path = generated_result(source, tmp_path)
    expected = Interpreter().run(tree)
    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout) == [expected.stdout, expected.return_value]
    direct = subprocess.run([sys.executable, '-I', str(path)], capture_output=True,
                            text=True, timeout=5)
    assert direct.returncode == 0 and direct.stdout == expected.stdout


def test_edge_cases_differential(tmp_path):
    bodies = [
        'int x; x=2; {int x=8; printf("%d",x);} return x;',
        'return (0 && 1/0) || (3 || 1/0);',
        'if(1) if(0) return 1; else return 2; return 3;',
        'while(1) {return -7%-3;} return 0;',
        'int i=0; while(i<2){int j=0;while(j<2){printf("%d",j);j=j+1;}i=i+1;}',
        'return (-7/3 == -2) + (7/-3 == -2) + (-7%-3 == -1) + (7%-3 == 1);',
        'return -100000000000000000000000000000000000001 / 3;',
        'int main_value=1; int _rt=2; int print=3; return main_value+_rt+print;',
        'int x; if(0){printf("%d",x);} return !0 + +2 * -3;',
        'int i=0; while(i<2){int x; x=i; printf("%d",x);i=i+1;} return 0;',
    ]
    for body in bodies:
        tree, process, _ = generated_result('int main(){'+body+'}', tmp_path)
        expected = Interpreter().run(tree)
        assert process.returncode == 0, process.stderr
        assert json.loads(process.stdout) == [expected.stdout, expected.return_value]


def test_generated_runtime_errors(tmp_path):
    for body, message in [('return 1/0;', 'division by zero'),
                          ('return 1%0;', 'division by zero'),
                          ('int x;return x;', 'uninitialized'),
                          ('int x=1; {int x=x;}', 'uninitialized'),
                          ('int i=0;while(i<2){int x;if(i==0)x=1;printf("%d",x);i=i+1;}', 'uninitialized'),
                          ('while(1);', 'step limit')]:
        _, process, _ = generated_result('int main(){'+body+'}', tmp_path, 30)
        assert process.returncode != 0
        assert message in process.stderr


def test_ast_json_stable_roles_and_unique_ids():
    tree = Parser().parse((ROOT/'examples/complex.c').read_text(encoding='utf-8'))
    exported = serialize(tree)
    assert exported == serialize(tree)
    document = json.loads(exported)
    seen = set()

    def visit(node):
        assert node['id'] not in seen
        seen.add(node['id'])
        assert node['label'] and node['type'] and node['role']
        assert node['line'] > 0 and node['column'] > 0
        for child in node['children']:
            visit(child)
    visit(document)
    assert document['type'] == 'Program' and len(seen) > 40