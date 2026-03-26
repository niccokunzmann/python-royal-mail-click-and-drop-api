"""List all available examples with their descriptions."""

import ast
import textwrap
from pathlib import Path

_BASE = "click_and_drop_api.examples"
_DIR = Path(__file__).parent


def _docstring(name: str) -> str:
    source = (_DIR / f"{name}.py").read_text()
    tree = ast.parse(source)
    return ast.get_docstring(tree) or ""


_examples = sorted(p.stem for p in _DIR.glob("*.py") if not p.stem.startswith("_"))

for name in _examples:
    doc = _docstring(name).strip()
    first_line, _, rest = doc.partition("\n")
    detail = textwrap.indent(rest.strip(), "    ") if rest.strip() else ""
    print(f"python -m {_BASE}.{name}")
    print(f"  {first_line}")
    if detail:
        print(detail)
    print()
