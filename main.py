"""CLI навчального компілятора підмножини C."""
import argparse
from pathlib import Path
import sys
from compiler.errors import CompilerError
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.interpreter import Interpreter


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('Потрібне додатне число')
    return number


def main(argv=None):
    cli = argparse.ArgumentParser(description='Mini C: PLY LALR -> AST -> виконання / Python / JSON')
    cli.add_argument('source', type=Path, help='Файл програми C (UTF-8)')
    cli.add_argument('--tokens', action='store_true', help='Показати токени')
    cli.add_argument('--ast', action='store_true', help='Показати AST у JSON')
    cli.add_argument('--run', action='store_true', help='Виконати програму')
    cli.add_argument('--emit-python', type=Path, help='Записати автономний Python-файл')
    cli.add_argument('--emit-ast', type=Path, help='Записати JSON для d3.js')
    cli.add_argument('--parser-report', type=Path, help='Записати діагностику PLY parser.out')
    cli.add_argument('--step-limit', type=positive, default=100_000, help='Ліміт кроків (100000)')
    args = cli.parse_args(argv)
    try:
        source = args.source.read_text(encoding='utf-8-sig')
        if args.tokens:
            for token in Lexer().tokenize(source):
                print(f'{token.lineno}:{token.column} {token.type} {token.value!r}')
        program = Parser(args.parser_report).parse(source)
        SemanticAnalyzer().analyze(program)
        if args.ast or args.emit_ast:
            from compiler.ast_serializer import serialize
            document = serialize(program)
            if args.ast:
                print(document)
            if args.emit_ast:
                write(args.emit_ast, document)
        if args.emit_python:
            from compiler.code_generator import generate
            write(args.emit_python, generate(program, args.step_limit))
        if args.run:
            result = Interpreter(args.step_limit).run(program)
            print(result.stdout, end='')
            print(f'[main повернув {result.return_value}; кроків: {result.steps}]', file=sys.stderr)
        elif not any((args.tokens, args.ast, args.emit_ast, args.emit_python, args.parser_report)):
            print('Синтаксичний і семантичний аналіз успішний.')
        return 0
    except (CompilerError, OSError, UnicodeError, RecursionError, ValueError) as error:
        print(f'Помилка: {error}', file=sys.stderr)
        return 1


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    sys.exit(main())