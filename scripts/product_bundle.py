#!/usr/bin/env python3
"""Deterministic build and verification for docs/product/COMPLETE-DOCUMENTATION.md.

The split product documents in ``docs/product/`` are canonical. The bundle
``COMPLETE-DOCUMENTATION.md`` is a derived concatenation of them, in the order
declared by the ``BUNDLE-SOURCES`` block in ``00-README.md``. Nothing here makes
the bundle authoritative.

Commands::

    python scripts/product_bundle.py build    # regenerate the bundle
    python scripts/product_bundle.py verify   # fail (exit 1) on any drift

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


def command_build() -> int:
    names = declared_sources()
    missing = [n for n in names if not (PRODUCT_DIR / n).is_file()]
    if missing:
        raise SystemExit("declared source files not found: " + ", ".join(missing))
    bundle = build_bundle(names)
    out = PRODUCT_DIR / BUNDLE_NAME
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(bundle)
    print(f"wrote {out.relative_to(REPO_ROOT)} from {len(names)} sources")
    return 0


def command_verify() -> int:
    names = declared_sources()
    bundle = read_canonical(PRODUCT_DIR / BUNDLE_NAME)
    problems: list[str] = []

    missing_files = [n for n in names if not (PRODUCT_DIR / n).is_file()]
    if missing_files:
        problems.append("declared source files not found: " + ", ".join(missing_files))

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
        problems.append("bundle differs from a fresh build (formatting or trailing drift)")

    if problems:
        print("product bundle verification FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(
            "\nRun 'python scripts/product_bundle.py build' and commit the result.",
            file=sys.stderr,
        )
        return 1

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
