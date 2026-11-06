from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def cli(*arguments):
    return subprocess.run([sys.executable, str(ROOT/'main.py'), *map(str, arguments)],
                          cwd=ROOT, capture_output=True, encoding='utf-8',
                          env={**os.environ, 'PYTHONUTF8': '1'}, timeout=10)


def test_cli_help_run_and_exports(tmp_path):
    assert '--emit-python' in cli('--help').stdout
    legacy = subprocess.run([sys.executable, str(ROOT/'main.py'), '--help'],
                            capture_output=True, encoding='cp1251', timeout=10,
                            env={**os.environ, 'PYTHONIOENCODING': 'cp1251'})
    assert legacy.returncode == 0 and '--emit-python' in legacy.stdout
    output = tmp_path/'nested'
    result = cli(ROOT/'examples/complex.c', '--run', '--emit-python', output/'program.py',
                 '--emit-ast', output/'ast.json')
    assert result.returncode == 0, result.stderr
    assert result.stdout == '-2\n35\n'
    assert '35' in result.stderr
    assert json.loads((output/'ast.json').read_text(encoding='utf-8'))['type'] == 'Program'
    assert (output/'program.py').exists()


def test_cli_errors(tmp_path):
    source = tmp_path/'bad.c'
    for text in ['int main(){return 0}', 'int main(){return missing;}', 'int main(){return 1/0;}']:
        source.write_text(text, encoding='utf-8')
        result = cli(source, '--run')
        assert result.returncode == 1 and '1:' in result.stderr
    source.write_text('int main(){while(1);}', encoding='utf-8')
    assert cli(source, '--run', '--step-limit', 10).returncode == 1
    assert cli(source, '--run', '--step-limit', 0).returncode == 2


def test_parser_report_has_no_unresolved_conflicts(tmp_path):
    from compiler.parser import Parser
    path = tmp_path/'parser.out'
    Parser(path).parse('int main(){if(1) if(0); else; return 0;}')
    report = path.read_text(encoding='utf-8')
    assert 'Parsing method: LALR' in report
    assert 'conflict' not in report.lower()
    assert '!' in report  # Альтернативи, відхилені заданим пріоритетом.