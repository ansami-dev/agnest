#!/usr/bin/env python3
"""Deterministic build and verification for docs/product/COMPLETE-DOCUMENTATION.md.

The split product documents in ``docs/product/`` are canonical. The bundle
``COMPLETE-DOCUMENTATION.md`` is a derived concatenation of them, in the order
declared by the ``BUNDLE-SOURCES`` block in ``00-README.md``. Nothing here makes
the bundle authoritative.

Commands::

    python scripts/product_bundle.py build    # regenerate the bundle
    python scripts/product_bundle.py verify   # fail (exit 1) on any drift

The declaration is checked against the product-document inventory before any
source is read or output is written, so the bundle can neither omit a product
document nor embed a file from outside ``docs/product``.

The verifier is offline and platform independent. It compares canonical text
after normalising line endings to LF, because the repository normalises line
endings through ``core.autocrlf`` and the committed form is LF.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_DIR = REPO_ROOT / "docs" / "product"
README_NAME = "00-README.md"
BUNDLE_NAME = "COMPLETE-DOCUMENTATION.md"
BUNDLE_TITLE = "# Complete Product Documentation Bundle"
HEADER = BUNDLE_TITLE + "\n\n\n---\n\n"
SEPARATOR = "\n---\n\n"
MARKER_RE = re.compile(r"<!-- SOURCE: ([^\n]+?) -->\n\n")
SOURCES_RE = re.compile(r"<!-- BUNDLE-SOURCES\s*\n(.*?)-->", re.DOTALL)
# A declared source is a plain product-document filename directly under
# docs/product/: no separators, no traversal, no leading dot, must be Markdown.
SOURCE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.md$")


def canonical(text: str) -> str:
    """Return the platform-independent canonical text used for comparison."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_canonical(path: Path) -> str:
    return canonical(path.read_text(encoding="utf-8"))


def declared_sources() -> list[str]:
    """Read the ordered source list from the BUNDLE-SOURCES block in 00-README.md."""
    readme = read_canonical(PRODUCT_DIR / README_NAME)
    match = SOURCES_RE.search(readme)
    if not match:
        raise SystemExit(
            f"{README_NAME}: no <!-- BUNDLE-SOURCES ... --> block found; "
            "the bundle source list is not declared"
        )
    names = []
    for line in match.group(1).splitlines():
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        names.append(name)
    if not names:
        raise SystemExit(
            f"{README_NAME}: the <!-- BUNDLE-SOURCES ... --> block declares no sources"
        )
    return names


def product_inventory() -> list[str]:
    """Return every canonical product document: *.md under docs/product, minus the bundle."""
    return sorted(
        entry.name
        for entry in PRODUCT_DIR.glob("*.md")
        if entry.is_file() and entry.name != BUNDLE_NAME
    )


def validate_declaration(names: list[str]) -> list[str]:
    """Return every problem with the declared source list.

    Rejects traversal, absolute and separator-bearing names, symlinks that
    resolve outside ``docs/product``, the generated bundle itself, duplicates,
    and any product document that is present but not declared.
    """
    problems: list[str] = []
    product_root = PRODUCT_DIR.resolve()

    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        if name == BUNDLE_NAME:
            problems.append("declared source is the generated bundle itself: " + name)
            continue
        if ".." in name or not SOURCE_NAME_RE.match(name):
            problems.append(
                "declared source must be a plain .md filename directly under "
                f"docs/product: {name!r}"
            )
            continue
        resolved = (PRODUCT_DIR / name).resolve()
        if product_root not in resolved.parents:
            problems.append(
                f"declared source resolves outside docs/product: {name!r}"
            )

    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        problems.append("duplicate declared sources: " + ", ".join(duplicates))

    inventory = product_inventory()
    inventory_set = set(inventory)
    declared_set = set(names)
    undeclared = [name for name in inventory if name not in declared_set]
    if undeclared:
        problems.append(
            "product documents not declared in BUNDLE-SOURCES: " + ", ".join(undeclared)
        )
    absent = [name for name in names if name not in inventory_set]
    if absent:
        problems.append(
            "declared sources that are not product documents on disk: "
            + ", ".join(absent)
        )
    return problems


def build_bundle(names: list[str]) -> str:
    """Return the exact bundle text for the declared source list."""
    parts = [HEADER]
    for index, name in enumerate(names):
        content = read_canonical(PRODUCT_DIR / name)
        parts.append(f"<!-- SOURCE: {name} -->\n\n")
        parts.append(content)
        if index != len(names) - 1:
            parts.append(SEPARATOR)
    return "".join(parts)


def parse_sections(bundle: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a bundle into its header and its (name, content) sections."""
    matches = list(MARKER_RE.finditer(bundle))
    header = bundle[: matches[0].start()] if matches else bundle
    sections = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(bundle)
        content = bundle[start:end]
        if content.endswith(SEPARATOR):
            content = content[: -len(SEPARATOR)]
        sections.append((match.group(1), content))
    return header, sections


def report_failure(heading: str, problems: list[str]) -> int:
    print(f"{heading} FAILED:", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    print(
        "\nRun 'python scripts/product_bundle.py build' and commit the result.",
        file=sys.stderr,
    )
    return 1


def command_build() -> int:
    names = declared_sources()
    problems = validate_declaration(names)
    if problems:
        return report_failure("product bundle build", problems)
    bundle = build_bundle(names)
    out = PRODUCT_DIR / BUNDLE_NAME
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(bundle)
    try:
        shown = out.relative_to(REPO_ROOT)
    except ValueError:
        shown = out
    print(f"wrote {shown} from {len(names)} sources")
    return 0


def command_verify() -> int:
    names = declared_sources()
    declaration_problems = validate_declaration(names)
    problems = list(declaration_problems)

    bundle = read_canonical(PRODUCT_DIR / BUNDLE_NAME)
    header, sections = parse_sections(bundle)
    actual_names = [name for name, _ in sections]

    if not sections:
        problems.append("bundle contains no '<!-- SOURCE: ... -->' sections")
    if sections and header != HEADER:
        problems.append("bundle header differs from the expected header")

    missing = [n for n in names if n not in actual_names]
    extra = [n for n in actual_names if n not in names]
    duplicate = sorted({n for n in actual_names if actual_names.count(n) > 1})
    if missing:
        problems.append("declared sources absent from bundle: " + ", ".join(missing))
    if extra:
        problems.append("bundle sections with no declared source: " + ", ".join(extra))
    if duplicate:
        problems.append("bundle sections repeated: " + ", ".join(duplicate))
    if not missing and not extra and not duplicate and actual_names != names:
        problems.append("bundle section order does not match the declared order")

    if not declaration_problems:
        by_name: dict[str, str] = {}
        for name, content in sections:
            by_name.setdefault(name, content)
        for name in names:
            if name not in by_name or not (PRODUCT_DIR / name).is_file():
                continue
            expected = read_canonical(PRODUCT_DIR / name)
            if by_name[name] != expected:
                problems.append(f"content drift in embedded source: {name}")

        if not problems and bundle != build_bundle(names):
            problems.append(
                "bundle differs from a fresh build (formatting or trailing drift)"
            )

    if problems:
        return report_failure("product bundle verification", problems)

    print(
        f"product bundle OK: {len(names)} sources, "
        "every embedded section matches its canonical file"
    )
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"build", "verify"}:
        print(f"usage: {Path(argv[0]).name} {{build|verify}}", file=sys.stderr)
        return 2
    return command_build() if argv[1] == "build" else command_verify()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
