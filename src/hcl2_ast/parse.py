import typing as t

from hcl2.lark_parser import Lark_StandAlone  # type: ignore

from hcl2_ast.ast import Module
from hcl2_ast.transformer import ToAstTransformer


def parse_file(file: t.TextIO) -> Module:
    return parse_string(file.read())


def parse_string(text: str) -> Module:
    return Module(Lark_StandAlone(transformer=ToAstTransformer()).parse(text + "\n"))
