""" Provides the #Configurable base class that allows for evaluating HCL2 configuration code. """

import typing as t

from hcl2_ast.ast import Attribute, Block, Expression, Identifier, Literal, Module, Stmt

PlainType = t.Union[None, bool, int, str, float]
ValueType = t.Union[t.List[PlainType], t.Dict[str, PlainType]]


class ConfigurationError(Exception):
    def __init__(self, context: "Configurable", message: str) -> None:
        self.context = context
        self.message = message

    def __str__(self) -> str:
        return f"in context of object {self.context!r}: {self.message}"


class Function(t.Protocol):
    def __call__(self, args: t.List[ValueType]) -> None:
        ...


class Configurable:
    """A configurable object responds to configuration requests when attributes are set or
    blocks are defined in its context in a HCL2 configuration file."""

    def set_attribute(self, attr: str, value: ValueType) -> None:
        raise ConfigurationError(self, f"attribute {attr!r} does not exist")

    def get_attribute(self, attr: str) -> ValueType:
        raise ConfigurationError(self, f"attribute {attr!r} does not exist")

    def start_block(self, name: str, args: t.List[ValueType]) -> "Configurable":
        raise ConfigurationError(self, "block {name!r} does not exist")

    def end_block(self, name: str, args: t.List[ValueType], block: "Configurable") -> None:
        pass

    def get_function(self, name: str) -> Function:
        raise ConfigurationError(self, f"function {name!r} does not exist")

    def validate(self) -> None:
        pass


class Evaluator:
    def evaluate(self, expr: Expression, context: Configurable) -> ValueType:
        method = "_eval_" + type(expr).__name__
        return t.cast(ValueType, getattr(self, method)(expr, context))

    def _eval_Literal(self, literal: Literal, context: Configurable) -> PlainType:
        return literal.value

    def _eval_Identifier(self, identifier: Identifier, context: Configurable) -> ValueType:
        return context.get_attribute(identifier.name)


class Interpreter:
    def __init__(self, evaluator: Evaluator) -> None:
        self.evaluator = evaluator

    def execute(self, stmt: t.Union[Stmt, Module], context: Configurable) -> None:
        if isinstance(stmt, Module):
            for node in stmt.body:
                self.execute(node, context)
        else:
            method = "_handle_" + type(stmt).__name__
            getattr(self, method)(stmt, context)

    def _handle_Attribute(self, attr: Attribute, context: Configurable) -> None:
        context.set_attribute(attr.key, self.evaluator.evaluate(attr.value, context))

    def _handle_Block(self, block: Block, context: Configurable) -> None:
        args = [self.evaluator.evaluate(arg, context) for arg in block.args]
        new_context = context.start_block(block.name, args)
        for stmt in block.body:
            self.execute(stmt, new_context)
        context.end_block(block.name, args, new_context)
