# hcl2-ast

A [HCL2][] parser and evaluator based on [python-hcl2][] that produces an Abstract Syntax Tree.

  [HCL2]: https://github.com/hashicorp/hcl/blob/main/README.md
  [python-hcl2]: https://pypi.org/project/python-hcl2/
  [hcl2-eval]: https://pypi.org/project/hcl2-eval/

> __Note__: This project is in an early stage. It does not currently cover all HCL2 syntax features
> and does not have good test coverage.

## Usage

```py
from hcl2_ast import parse_string

module = parse_string("""
  hello {
    name = "World"
  }
""")

print(module.pformat())
```

Outputs:

```py
Module(body=[
  Block(
    name='hello',
    args=[],
    body=[
      Attribute(key='name', value=Literal(value='World')),
    ]
  ),
])
```

Also check out the [hcl2-eval][] package to evaluate HCL2 configuration ASTs.

## Compatibility

hcl2-ast requires Python 3.6 or higher.

## Known issues

* No understanding of operator precedence in expressions (grouping with parentheses works as expected)
