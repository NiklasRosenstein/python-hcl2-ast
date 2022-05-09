import dataclasses
import textwrap
import typing as t

from termcolor import colored

LiteralValue = t.Union[None, bool, int, float, str]


def pformat(value: t.Union[LiteralValue, "Node"]) -> str:
    if isinstance(value, Node):
        return value.pformat()
    if isinstance(value, str):
        return colored(repr(value), "yellow")
    else:
        return colored(repr(value), "cyan")


def pformat_list(values: t.List["Expression"]) -> str:
    result = ""
    if values:
        for value in values:
            result += "\n" + textwrap.indent(pformat(value), "  ") + ","
        result += "\n"
    return result


def indent_but_first_line(text: str, indent: str) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    return lines[0] + "\n" + textwrap.indent("\n".join(lines[1:]), indent)


class Node:
    """Base class for HCL2 AST nodes."""

    def pformat_field(self, field_name: str) -> str:
        value = getattr(self, field_name)
        if isinstance(value, Expression):
            formatted = value.pformat()
        elif isinstance(value, list):
            formatted = f"[{pformat_list(value)}]"
        else:
            formatted = pformat(value)
        return formatted

    def pformat(self) -> str:
        args = []
        fields = dataclasses.fields(self)
        for field in fields:
            args.append(colored(field.name, "cyan") + "=" + self.pformat_field(field.name))
        if any("\n" in arg for arg in args) and len(args) > 1:
            sep = ",\n"
            args_string = f'(\n{sep.join(textwrap.indent(arg, "  ") for arg in args)}\n)'
        else:
            args_string = f'({", ".join(args)})'
        return f"{colored(type(self).__name__, 'blue')}{args_string}"


class Expression(Node):
    """Base class for nodes that represent expressions in HCL2."""


@dataclasses.dataclass
class Literal(Expression):
    value: LiteralValue

    def __post_init__(self) -> None:
        assert isinstance(self.value, (type(None), bool, int, float, str)), self.value
        if "Identifier" in str(self.value):
            import pdb

            pdb.set_trace()


@dataclasses.dataclass
class Array(Expression):
    values: t.List[Expression]


@dataclasses.dataclass
class Object(Expression):
    fields: t.Dict[str, Expression]

    def pformat_field(self, field_name: str) -> str:
        if field_name == "fields":
            if not self.fields:
                return "{}"
            result = "{"
            for key, value in self.fields.items():
                result += f'\n  {pformat(key)}: {indent_but_first_line(value.pformat(), "  ")}'
            return result + "}"
        return super().pformat_field(field_name)


@dataclasses.dataclass
class FunctionCall(Expression):
    name: str
    args: t.List[Expression]

    def __post_init__(self) -> None:
        assert all(isinstance(arg, Expression) for arg in self.args), self.args


@dataclasses.dataclass
class Identifier(Expression):
    name: str


@dataclasses.dataclass
class GetAttr(Expression):
    on: t.Optional["Expression"]
    name: str


@dataclasses.dataclass
class UnaryOp(Expression):
    op: t.Literal["-", "!"]
    expr: Expression


@dataclasses.dataclass
class BinaryOp(Expression):
    op: t.Literal["==", "!=", "<", ">", "<=", ">=", "-", "*", "/", "%", "&&", "||", "+"]
    left: Expression
    right: Expression


class Stmt(Node):
    """Base class for nodes that represent statements in HCL2."""


@dataclasses.dataclass
class Attribute(Stmt):
    key: str
    value: Expression


@dataclasses.dataclass
class Block(Stmt):
    name: str
    args: t.List[Expression]
    body: t.List[Stmt]


@dataclasses.dataclass
class Module(Node):
    body: t.List[Stmt]
