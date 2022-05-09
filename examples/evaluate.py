
from typing import List, Optional
from hcl2_ast.api import parse_string
from hcl2_ast.eval import Configurable, ConfigurationError, Evaluator, Interpreter, ValueType


class HelloStanza(Configurable):

    def __init__(self) -> None:
        self.name: Optional[str] = None

    def set_attribute(self, attr: str, value: ValueType) -> None:
        if attr == 'name':
            if not isinstance(value, str):
                raise ConfigurationError(self, 'attribute "name" must be a str')
            self.name = value
        else:
            super().set_attribute(attr, value)

    def validate(self) -> None:
        if self.name is None:
            raise ConfigurationError(self, 'attribute "name" must be set')

    def say_hello(self) -> None:
        assert self.name is not None
        print(f"Hello, {self.name}!")


class RootStanza(Configurable):

    def start_block(self, name: str, args: List[ValueType]) -> "Configurable":
        if name == 'hello':
            if args:
                raise ConfigurationError(self, "block {name!r} takes not arguments")
            return HelloStanza()
        super().start_block(name, args)

    def end_block(self, name: str, args: List[ValueType], block: "Configurable") -> None:
        assert isinstance(block, HelloStanza)
        block.say_hello()


module = parse_string("""
    hello {
        name = "World"
    }
""")

Interpreter(Evaluator()).execute(module, RootStanza())
