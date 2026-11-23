#!/usr/bin/env python3
"""Compile a Typst homework document in an isolated staging root and run PyMuPDF QA."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pymupdf
import typst

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Match Typst asset/import calls: image("..."), import "...", include "...", read("...")
_ASSET_PATTERNS = [
    re.compile(r'\bimage\(\s*"([^"\r\n]+)"'),
    re.compile(r'\bread\(\s*"([^"\r\n]+)"'),
    re.compile(r'\b(?:import|include)\s+"([^"\r\n]+)"'),
]


def _collect_relative_assets(typ_file: Path, base_dir: Path, visited: set[Path]) -> list[Path]:
    """Recursively find referenced relative assets inside base_dir without copying unrelated files."""
    resolved = typ_file.resolve()
    if resolved in visited or not resolved.is_file():
        return []
    visited.add(resolved)

    text = resolved.read_text(encoding="utf-8", errors="replace")
    assets: list[Path] = []

    for pat in _ASSET_PATTERNS:
        for match in pat.finditer(text):
            raw_ref = match.group(1).strip()
            if not raw_ref or raw_ref.startswith("@"):
                continue
            if re.match(r"^[a-zA-Z]+://", raw_ref):
                continue
            if Path(raw_ref).name == "ee_homework_tpl.typ" and raw_ref in (
                "ee_homework_tpl.typ",
                "./ee_homework_tpl.typ",
            ):
                continue

            ref_path = Path(raw_ref)
            if ref_path.is_absolute():
                continue

            candidate = (typ_file.parent / ref_path).resolve()
            try:
                candidate.relative_to(base_dir.resolve())
            except ValueError:
                continue

            if candidate.is_file():
                assets.append(candidate)
                if candidate.suffix.lower() == ".typ":
                    assets.extend(_collect_relative_assets(candidate, base_dir, visited))

    unique: list[Path] = []
    seen: set[Path] = set()
    for p in assets:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _stage_and_compile(input_typ: Path, output_pdf: Path, skill_dir: Path) -> None:
    """Copy .typ, template, and referenced assets into a temporary root and compile."""
    src_dir = input_typ.parent.resolve()
    local_tpl = src_dir / "ee_homework_tpl.typ"
    default_tpl = skill_dir / "resources" / "ee_homework_tpl.typ"
    tpl_path = local_tpl if local_tpl.is_file() else default_tpl
    if not tpl_path.is_file():
        raise FileNotFoundError(f"Template not found: {tpl_path}")

    with tempfile.TemporaryDirectory(prefix="ee_typst_") as tmp_root:
        stage_dir = Path(tmp_root)
        staged_typ = stage_dir / input_typ.name
        shutil.copy2(input_typ, staged_typ)
        shutil.copy2(tpl_path, stage_dir / "ee_homework_tpl.typ")

        assets = _collect_relative_assets(input_typ, src_dir, set())
        for asset in assets:
            rel = asset.resolve().relative_to(src_dir)
            dest = stage_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, dest)

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        typst.compile(str(staged_typ), output=str(output_pdf), root=str(stage_dir))


def _run_qa(
    output_pdf: Path,
    preview_dir: Path | None,
    dpi: int,
) -> tuple[int, float, list[str], list[Path]]:
    """Inspect compiled PDF for overflow, missing glyphs, sparse last page, and render previews."""
    warnings: list[str] = []
    preview_paths: list[Path] = []
    margin_guard = 8.0  # pt

    doc = pymupdf.open(str(output_pdf))
    try:
        total_pages = len(doc)
        size_kb = output_pdf.stat().st_size / 1024.0

        if preview_dir is not None:
            preview_dir.mkdir(parents=True, exist_ok=True)

        for idx, page in enumerate(doc, start=1):
            rect = page.rect
            w, h = rect.width, rect.height

            for blk in page.get_text("blocks"):
                x0, y0, x1, y1, btext, _bno, btype = blk
                if btype == 0 and not btext.strip():
                    continue
                if x0 < margin_guard or x1 > w - margin_guard or y0 < margin_guard or y1 > h - margin_guard:
                    kind = "text" if btype == 0 else "block"
                    warnings.append(
                        f"OVERFLOW_WARNING: page {idx} {kind} bbox=({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}) "
                        f"outside safe bounds ({margin_guard:.0f}..{w - margin_guard:.1f}, {margin_guard:.0f}..{h - margin_guard:.1f})"
                    )

            for img in page.get_image_info(xrefs=True):
                x0, y0, x1, y1 = img["bbox"]
                if x0 < margin_guard or x1 > w - margin_guard or y0 < margin_guard or y1 > h - margin_guard:
                    warnings.append(
                        f"OVERFLOW_WARNING: page {idx} image bbox=({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}) "
                        f"outside safe bounds"
                    )

            full_text = page.get_text("text")
            if "\ufffd" in full_text:
                count = full_text.count("\ufffd")
                warnings.append(
                    f"MISSING_GLYPH_WARNING: page {idx} contains {count} replacement character(s) (\\ufffd)"
                )

            if idx == total_pages and total_pages > 1:
                body_clip = pymupdf.Rect(0, 0.08 * h, w, 0.90 * h)
                body_text = page.get_text("text", clip=body_clip)
                non_ws_len = len(re.sub(r"\s+", "", body_text))
                if non_ws_len < 60 and len(page.get_images()) == 0:
                    warnings.append(
                        f"SPARSE_LAST_PAGE_WARNING: page {idx} has only {non_ws_len} non-whitespace body chars and 0 images"
                    )

            if preview_dir is not None:
                pix = page.get_pixmap(dpi=dpi)
                out_png = (preview_dir / f"page_{idx:02d}.png").resolve()
                pix.save(str(out_png))
                preview_paths.append(out_png)
    finally:
        doc.close()

    return total_pages, size_kb, warnings, preview_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile Typst homework to PDF and run QA checks.")
    parser.add_argument("input_typ", type=Path, help="Input .typ file path")
    parser.add_argument("output_pdf", type=Path, nargs="?", help="Output .pdf path (defaults to input stem .pdf)")
    parser.add_argument("--preview-dir", type=Path, default=None, help="Directory to render page_XX.png previews")
    parser.add_argument("--dpi", type=int, default=150, help="Preview rendering DPI (default: 150)")
    args = parser.parse_args()

    input_typ = args.input_typ.resolve()
    if not input_typ.is_file():
        print(f"ERROR: Input file not found: {input_typ}", file=sys.stderr)
        return 1

    output_pdf = (args.output_pdf if args.output_pdf is not None else input_typ.with_suffix(".pdf")).resolve()
    skill_dir = Path(__file__).resolve().parent.parent

    try:
        _stage_and_compile(input_typ, output_pdf, skill_dir)
    except Exception as exc:
        print(f"TYPST_COMPILE_ERROR:\n{exc}", file=sys.stderr)
        return 1

    total_pages, size_kb, warnings, preview_paths = _run_qa(output_pdf, args.preview_dir, args.dpi)

    print(f"PDF: {output_pdf}")
    print(f"Pages: {total_pages} | Size: {size_kb:.1f} KB")
    if preview_paths:
        print("Previews:")
        for p in preview_paths:
            print(f"  {p}")

    if warnings:
        print("QA Status: WARNINGS")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("QA Status: OK (0 warnings)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
