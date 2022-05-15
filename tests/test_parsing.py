from hcl2_ast.api import parse_string
from hcl2_ast.ast import Attribute, BinaryOp, Block, FunctionCall, GetAttr, Identifier, Literal, Module, UnaryOp


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
        [Block("myblock", [Literal("argument1"), Literal("argument2")], [])]
    )


def test_can_parse_block_with_args_as_identifiers() -> None:
    assert parse_string("myblock argument1 argument2 {}") == Module(
        [Block("myblock", [Identifier("argument1"), Identifier("argument2")], [])]
    )


def test_can_parse_read_from_attributes() -> None:
    assert parse_string("value = foo") == Module([Attribute("value", Identifier("foo"))])
    assert parse_string("value = foo.bar") == Module([Attribute("value", GetAttr(Identifier("foo"), "bar"))])
    assert parse_string("value = foo.bar.baz") == Module(
        [Attribute("value", GetAttr(GetAttr(Identifier("foo"), "bar"), "baz"))]
    )
    assert parse_string('value = "42".bar') == Module([Attribute("value", GetAttr(Literal("42"), "bar"))])


def test_can_parse_binary_operator() -> None:
    assert parse_string("value = 1 + (addend * 2) - 1 ") == Module(
        [
            Attribute(
                "value",
                BinaryOp(
                    "+",
                    Literal(value=1),
                    BinaryOp(
                        "-",
                        BinaryOp(
                            "*",
                            Identifier(name="addend"),
                            Literal(value=2),
                        ),
                        Literal(value=1),
                    ),
                ),
            )
        ]
    )

    # TODO (@NiklasRosenstein): Missing operator precedence.
    assert parse_string("value = 1 + addend * 2 - 1 ") == Module(
        [
            Attribute(
                "value",
                BinaryOp(
                    "+",
                    Literal(value=1),
                    BinaryOp("*", Identifier(name="addend"), BinaryOp("-", Literal(value=2), Literal(value=1))),
                ),
            )
        ]
    )


def test_can_parse_unary_operator() -> None:
    assert parse_string("value = !addend") == Module([Attribute("value", UnaryOp("!", Identifier("addend")))])


def test_can_parse_function_call() -> None:
    assert parse_string("value = foo()") == Module([Attribute("value", FunctionCall("foo", []))])
