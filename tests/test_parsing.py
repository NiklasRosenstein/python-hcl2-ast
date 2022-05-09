from hcl2_ast.api import parse_string
from hcl2_ast.ast import Attribute, Block, Literal, Module


def test_can_parse_attribute_string() -> None:
    assert parse_string('foo-bar = "Hello World!"') == Module([Attribute("foo-bar", Literal("Hello World!"))])


def test_can_parse_attribute_float() -> None:
    assert parse_string("foo-bar = 42.0") == Module([Attribute("foo-bar", Literal(42.0))])


def test_can_parse_attribute_null() -> None:
    assert parse_string("foo-bar = null") == Module([Attribute("foo-bar", Literal(None))])


def test_can_parse_empty_block() -> None:
    assert parse_string("myblock {}") == Module([Block("myblock", [], [])])


def test_can_parse_block_with_args() -> None:
    assert parse_string('myblock "argument1" "argument2" {}') == Module(
        [Block("myblock", ["argument1", "argument2"], [])]
    )


def test_can_parse_block_with_args_as_identifiers() -> None:
    assert parse_string("myblock argument1 argument2 {}") == Module([Block("myblock", ["argument1", "argument2"], [])])
