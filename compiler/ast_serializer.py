"""Стабільні адреси вузлів визначаються шляхом, а не адресою об'єкта Python."""
from dataclasses import fields
import json
from .ast_nodes import Node


def to_dict(node: Node, path='0', role='program') -> dict:
    result = {'id': path, 'type': type(node).__name__, 'role': role,
              'label': type(node).__name__, 'line': node.line,
              'column': node.column, 'children': []}
    for field in fields(node):
        if field.name in ('line', 'column'):
            continue
        value = getattr(node, field.name)
        if isinstance(value, Node):
            result['children'].append(to_dict(value, f'{path}.{field.name}', field.name))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                result['children'].append(to_dict(child, f'{path}.{field.name}.{index}',
                                                  f'{field.name}[{index}]'))
        elif value is not None:
            result[field.name] = value
            result['label'] += f' {value!r}'
    return result


def serialize(node: Node) -> str:
    return json.dumps(to_dict(node), ensure_ascii=False, indent=2) + '\n'