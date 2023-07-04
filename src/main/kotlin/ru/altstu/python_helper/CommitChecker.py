from git import Commit
from pycparser import c_parser, c_ast
from typing import Tuple, Type

def addition_in_commit(commit: Commit):
    raw_commit = commit.parents[0].diff(commit, create_patch=True)[0].diff.decode("utf-8")
    rows = raw_commit.splitlines()[1:]
    rows = filter(lambda a: a.startswith('+'), rows)
    rows = map(lambda a: a[1:], rows)
    additions = "\n".join(rows)
    return additions


def get_ast(code :str):
    code = "int main(){" + code + "}"
    parser = c_parser.CParser()
    ast = parser.parse(code)
    return ast

def find_object(ast: c_ast.Node, object_types : Tuple[Type, ...]):
    counter = 0
    if isinstance(ast, object_types):
        counter += 1
    for _, child in ast.children():
        counter += find_object(child, object_types)
    return counter
