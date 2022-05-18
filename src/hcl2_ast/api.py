import warnings

warnings.warn("Use hcl2_ast.parse instead of hcl2_ast.api", DeprecationWarning)

import sys  # noqa: E402

from . import parse  # noqa: E402

sys.modules[__name__] = parse
