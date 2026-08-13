"""Fail on broken repository-relative Markdown links."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def main() -> None:
    failures: list[str] = []
    for document in sorted(ROOT.rglob("*.md")):
        if any(part in {".venv", "node_modules"} for part in document.parts):
            continue
        for line_number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
            for raw_target in LINK.findall(line):
                target = raw_target.split("#", 1)[0]
                if not target or target.startswith(("https://", "http://", "mailto:")):
                    continue
                resolved = (document.parent / unquote(target)).resolve()
                if not resolved.exists():
                    failures.append(f"{document.relative_to(ROOT)}:{line_number}: {raw_target}")
    if failures:
        raise SystemExit("Broken repository links:\n" + "\n".join(failures))
    print("Repository-relative documentation links are valid.")


if __name__ == "__main__":
    main()
