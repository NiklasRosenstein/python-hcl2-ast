""" Uses python-hcl2 to parse a Kraken configuration file, but outputs it in a different format that instead
retains the order of assignments and blocks. """

import typing as t

from hcl2.transformer import DictTransformer  # type: ignore[import]

from hcl2_ast.ast import Array, Attribute, Block, Expression, FunctionCall, Literal, Object


class ToAstTransformer(DictTransformer):  # type: ignore[misc]
    def to_expression(self, value: t.Any) -> Expression:
        return value if isinstance(value, Expression) else Literal(value)

    def float_lit(self, args: t.List[t.Any]) -> Literal:
        return Literal(super().float_lit(args))

    def int_lit(self, args: t.List[t.Any]) -> Literal:
        return Literal(super().int_lit(args))

    def expr_term(self, args: t.List[t.Any]) -> t.Union[Literal, t.Any]:
        if args[0] == "true":
            return Literal(True)
        elif args[0] == "false":
            return Literal(False)
        elif args[0] == "null":
            return Literal(None)
        return super().expr_term(args)

    def attribute(self, args: t.List[t.Any]) -> Attribute:
        attr = super().attribute(args)
        return Attribute(attr.key, self.to_expression(attr.value))

    def function_call(self, args: t.List[t.Any]) -> FunctionCall:
        args = self.strip_new_line_tokens(args)
        assert len(args) in (1, 2), args
        if len(args) == 1:
            args.append([])
        args[1] = [self.to_expression(self.strip_quotes(arg)) for arg in args[1]]
        return FunctionCall(args[0], args[1])

    def body(self, args: t.List[t.Any]) -> t.List[t.Any]:
        return args

    def block(self, args: t.List[t.Any]) -> Block:
        args = self.strip_new_line_tokens(args)

        # if the last token is a string instead of an object then the block is empty
        # such as 'foo "bar" "baz" {}'
        # in that case append an empty object
        if isinstance(args[-1], str):
            args.append({})

        args = [self.strip_quotes(arg) for arg in args]

        return Block(args[0], args[1:-1], args[-1])

    def object(self, args: t.List[t.Any]) -> Object:
        args = self.strip_new_line_tokens(args)
        result: t.Dict[str, t.Any] = {}
        for arg in args:
            result.update(arg)
        return Object(result)

    def tuple(self, args: t.List[t.Any]) -> Array:
        return Array(super().tuple(args))
