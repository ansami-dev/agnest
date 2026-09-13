#!/usr/bin/env python3
"""Regression tests for scripts/product_bundle.py.

Run::

    python scripts/test_product_bundle.py

Each test works on a temporary copy of ``docs/product`` so the real documents
and bundle are never touched.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import re
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "product_bundle", HERE / "product_bundle.py"
)
pb = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pb)

REAL_PRODUCT_DIR = HERE.parent / "docs" / "product"


class ProductBundleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._original = pb.PRODUCT_DIR
        self._tmp = Path(tempfile.mkdtemp(prefix="agnest-bundle-"))
        self.product = self._tmp / "product"
        shutil.copytree(REAL_PRODUCT_DIR, self.product)
        pb.PRODUCT_DIR = self.product

    def tearDown(self) -> None:
        pb.PRODUCT_DIR = self._original
        shutil.rmtree(self._tmp, ignore_errors=True)

    def run_command(self, command) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = command()
        return code, buffer.getvalue()

    def set_declared(self, names: list[str]) -> None:
        readme_path = self.product / pb.README_NAME
        readme = readme_path.read_text(encoding="utf-8")
        block = "<!-- BUNDLE-SOURCES\n" + "\n".join(names) + "\n-->"
        readme = re.sub(
            r"<!-- BUNDLE-SOURCES.*?-->", lambda _match: block, readme, count=1, flags=re.S
        )
        readme_path.write_text(readme, encoding="utf-8", newline="\n")

    def bundle_bytes(self) -> bytes:
        return (self.product / pb.BUNDLE_NAME).read_bytes()

    def test_checkout_bundle_is_current(self) -> None:
        self.assertEqual(
            self.bundle_bytes(),
            (REAL_PRODUCT_DIR / pb.BUNDLE_NAME).read_bytes(),
        )

    def test_build_and_verify_succeed(self) -> None:
        code, _ = self.run_command(pb.command_verify)
        self.assertEqual(code, 0)
        code, _ = self.run_command(pb.command_build)
        self.assertEqual(code, 0)
        code, _ = self.run_command(pb.command_verify)
        self.assertEqual(code, 0)

    def test_undeclared_product_document_is_rejected(self) -> None:
        (self.product / "11-new-product-document.md").write_text(
            "# New\n", encoding="utf-8", newline="\n"
        )
        code, output = self.run_command(pb.command_verify)
        self.assertEqual(code, 1)
        self.assertIn("not declared", output)
        self.assertIn("11-new-product-document.md", output)

    def test_build_rejects_undeclared_document_without_writing(self) -> None:
        (self.product / "11-new-product-document.md").write_text(
            "# New\n", encoding="utf-8", newline="\n"
        )
        before = self.bundle_bytes()
        code, _ = self.run_command(pb.command_build)
        self.assertEqual(code, 1)
        self.assertEqual(self.bundle_bytes(), before)

    def test_traversal_and_absolute_names_are_rejected(self) -> None:
        bad_names = [
            "../../.env",
            "../sentinel.txt",
            "/etc/passwd",
            "C:\\Windows\\win.ini",
            "sub/file.md",
            "sub\\file.md",
            "..",
            ".",
            ".env",
        ]
        for bad in bad_names:
            with self.subTest(name=bad):
                self.assertTrue(pb.validate_declaration([bad]), bad)
        absolute = str((self._tmp / "sentinel.txt").resolve())
        self.assertTrue(pb.validate_declaration([absolute]))

    def test_traversal_does_not_modify_bundle(self) -> None:
        sentinel = self._tmp / "sentinel.txt"
        sentinel.write_text("LOCAL-SECRET-SENTINEL\n", encoding="utf-8")
        self.set_declared(["../sentinel.txt"])
        before = self.bundle_bytes()
        code, _ = self.run_command(pb.command_build)
        self.assertEqual(code, 1)
        self.assertEqual(self.bundle_bytes(), before)
        self.assertNotIn(b"LOCAL-SECRET-SENTINEL", self.bundle_bytes())

    def test_absolute_path_does_not_modify_bundle(self) -> None:
        sentinel = self._tmp / "absolute-sentinel.md"
        sentinel.write_text("ABSOLUTE-SENTINEL\n", encoding="utf-8")
        self.set_declared([str(sentinel.resolve())])
        before = self.bundle_bytes()
        code, _ = self.run_command(pb.command_build)
        self.assertEqual(code, 1)
        self.assertEqual(self.bundle_bytes(), before)
        self.assertNotIn(b"ABSOLUTE-SENTINEL", self.bundle_bytes())

    def test_bundle_cannot_declare_itself(self) -> None:
        problems = pb.validate_declaration([pb.BUNDLE_NAME])
        self.assertTrue(
            any("generated bundle itself" in problem for problem in problems),
            problems,
        )

    def test_symlink_escaping_product_dir_is_rejected(self) -> None:
        outside = self._tmp / "outside.md"
        outside.write_text("# outside\n", encoding="utf-8")
        link = self.product / "linked.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are not available in this environment")
        problems = pb.validate_declaration(["linked.md"])
        self.assertTrue(
            any("outside docs/product" in problem for problem in problems),
            problems,
        )

    def test_content_drift_is_detected(self) -> None:
        path = self.product / pb.BUNDLE_NAME
        bundle = path.read_text(encoding="utf-8")
        path.write_text(
            bundle.replace(
                "# Cross-MVP Traceability Matrix",
                "# Cross-MVP Traceability MatriX",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        code, output = self.run_command(pb.command_verify)
        self.assertEqual(code, 1)
        self.assertIn("content drift", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
