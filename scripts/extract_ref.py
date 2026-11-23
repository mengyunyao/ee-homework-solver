#!/usr/bin/env python3
"""Extract table of contents, search snippets, page text/renders from PDFs and text/tables from Office files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pymupdf

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_page_spec(spec: str, max_pages: int) -> list[int]:
    """Parse 1-based page specification like '1,3-5,107' into ordered unique 1-based page numbers."""
    pages: list[int] = []
    seen: set[int] = set()

    for token in spec.split(","):
        part = token.strip()
        if not part:
            continue
        if "-" in part:
            bounds = part.split("-", 1)
            if len(bounds) != 2 or not bounds[0].strip().isdigit() or not bounds[1].strip().isdigit():
                raise ValueError(f"Invalid page range: '{part}'")
            start, end = int(bounds[0].strip()), int(bounds[1].strip())
            if start > end:
                raise ValueError(f"Reversed page range: '{part}'")
            for p in range(start, end + 1):
                if not (1 <= p <= max_pages):
                    raise ValueError(f"Page {p} out of bounds (1..{max_pages})")
                if p not in seen:
                    seen.add(p)
                    pages.append(p)
        else:
            if not part.isdigit():
                raise ValueError(f"Invalid page number: '{part}'")
            p = int(part)
            if not (1 <= p <= max_pages):
                raise ValueError(f"Page {p} out of bounds (1..{max_pages})")
            if p not in seen:
                seen.add(p)
                pages.append(p)

    if not pages:
        raise ValueError("No valid pages specified.")
    return pages


def _emit_output(text: str, out_path: Path | None) -> None:
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Saved to: {out_path.resolve()}")
    else:
        print(text)


def cmd_toc(pdf_path: Path) -> int:
    doc = pymupdf.open(str(pdf_path))
    try:
        toc = doc.get_toc()
        print(f"File: {pdf_path.name} ({len(doc)} pages)")
        if not toc:
            print("No embedded bookmarks (TOC) found. Use 'search' or 'pages' to inspect specific pages.")
            return 0
        for level, title, page_num in toc:
            indent = "  " * max(0, level - 1)
            clean_title = " ".join(title.split())
            print(f"{indent}- {clean_title}  [p.{page_num}]")
    finally:
        doc.close()
    return 0


def cmd_search(pdf_path: Path, query: str, max_hits: int) -> int:
    if not query.strip():
        print("ERROR: Search query cannot be empty.", file=sys.stderr)
        return 1

    pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
    doc = pymupdf.open(str(pdf_path))
    hits = 0
    try:
        print(f"Searching '{query}' in {pdf_path.name} ({len(doc)} pages):")
        for page_idx in range(len(doc)):
            raw_text = doc[page_idx].get_text("text")
            compact = re.sub(r"\s+", " ", raw_text).strip()
            if not compact:
                continue
            for m in pattern.finditer(compact):
                hits += 1
                start = max(0, m.start() - 45)
                end = min(len(compact), m.end() + 65)
                prefix = "..." if start > 0 else ""
                suffix = "..." if end < len(compact) else ""
                snippet = compact[start:end]
                print(f"[p.{page_idx + 1}] {prefix}{snippet}{suffix}")
                if hits >= max_hits:
                    print(f"(Stopped at --max {max_hits} hits)")
                    return 0
        if hits == 0:
            print("No text matches found (if the PDF is scanned without OCR, use 'render' + read_file).")
    finally:
        doc.close()
    return 0


def cmd_pages(pdf_path: Path, page_spec: str, out_path: Path | None) -> int:
    doc = pymupdf.open(str(pdf_path))
    try:
        pages = parse_page_spec(page_spec, len(doc))
        chunks: list[str] = []
        for p in pages:
            text = doc[p - 1].get_text("text").strip()
            chunks.append(f"=== Page {p} / {len(doc)} ===\n{text if text else '[No extractable text on this page]'}")
        _emit_output("\n\n".join(chunks), out_path)
    finally:
        doc.close()
    return 0


def cmd_render(pdf_path: Path, page_spec: str, out_dir: Path, dpi: int) -> int:
    doc = pymupdf.open(str(pdf_path))
    try:
        pages = parse_page_spec(page_spec, len(doc))
        out_dir.mkdir(parents=True, exist_ok=True)
        for p in pages:
            pix = doc[p - 1].get_pixmap(dpi=dpi)
            out_png = (out_dir / f"p{p:04d}.png").resolve()
            pix.save(str(out_png))
            print(str(out_png))
    finally:
        doc.close()
    return 0


def _extract_docx(file_path: Path) -> str:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(file_path))
    lines: list[str] = [f"# {file_path.name}"]

    for child in doc.element.body.iterchildren():
        tag = child.tag
        if tag.endswith("}p"):
            para = Paragraph(child, doc)
            txt = para.text.strip()
            if txt:
                style_name = para.style.name if para.style else ""
                if style_name.startswith("Heading"):
                    lines.append(f"\n## {txt}")
                else:
                    lines.append(txt)
        elif tag.endswith("}tbl"):
            tbl = Table(child, doc)
            lines.append("")
            for r_idx, row in enumerate(tbl.rows):
                cells = [" ".join(cell.text.split()) for cell in row.cells]
                lines.append("| " + " | ".join(cells) + " |")
                if r_idx == 0:
                    lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
            lines.append("")

    return "\n".join(lines).strip()


def _extract_pptx(file_path: Path) -> str:
    from pptx import Presentation

    prs = Presentation(str(file_path))
    slides_out: list[str] = [f"# {file_path.name} ({len(prs.slides)} slides)"]

    for idx, slide in enumerate(prs.slides, start=1):
        block: list[str] = [f"\n--- Slide {idx} ---"]
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    txt = p.text.strip()
                    if txt:
                        block.append(txt)
            if shape.has_table:
                tbl = shape.table
                for r_idx, row in enumerate(tbl.rows):
                    cells = [" ".join(cell.text.split()) for cell in row.cells]
                    block.append("| " + " | ".join(cells) + " |")
                    if r_idx == 0:
                        block.append("| " + " | ".join(["---"] * len(cells)) + " |")
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                block.append(f"[Notes] {notes}")
        slides_out.append("\n".join(block))

    return "\n".join(slides_out).strip()


def _extract_legacy_doc(file_path: Path) -> str:
    if sys.platform != "win32":
        raise RuntimeError(
            "Direct .doc extraction relies on Windows Word COM. "
            "On macOS/Linux, please convert to .docx first (e.g., `soffice --headless --convert-to docx file.doc`)."
        )
    try:
        import win32com.client
    except ImportError as exc:
        raise RuntimeError("pywin32 is required on Windows to read legacy .doc files.") from exc

    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(file_path.resolve()), ReadOnly=True, AddToRecentFiles=False)
        text = doc.Content.Text or ""
        return f"# {file_path.name}\n\n" + text.replace("\r\x07", "\t").replace("\r", "\n").strip()
    except Exception as exc:
        raise RuntimeError(f"Failed to read legacy .doc via Word COM: {exc}") from exc
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass


def _extract_legacy_ppt(file_path: Path) -> str:
    if sys.platform != "win32":
        raise RuntimeError(
            "Direct .ppt extraction relies on Windows PowerPoint COM. "
            "On macOS/Linux, please convert to .pptx first (e.g., `soffice --headless --convert-to pptx file.ppt`)."
        )
    try:
        import win32com.client
    except ImportError as exc:
        raise RuntimeError("pywin32 is required on Windows to read legacy .ppt files.") from exc

    ppt = None
    pres = None
    try:
        ppt = win32com.client.DispatchEx("PowerPoint.Application")
        pres = ppt.Presentations.Open(str(file_path.resolve()), ReadOnly=True, Untitled=False, WithWindow=False)
        out: list[str] = [f"# {file_path.name} ({pres.Slides.Count} slides)"]
        for idx in range(1, pres.Slides.Count + 1):
            slide = pres.Slides(idx)
            lines: list[str] = [f"\n--- Slide {idx} ---"]
            for shape in slide.Shapes:
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    txt = shape.TextFrame.TextRange.Text.strip()
                    if txt:
                        lines.append(txt.replace("\r", "\n"))
                if shape.HasTable:
                    tbl = shape.Table
                    for r in range(1, tbl.Rows.Count + 1):
                        row_cells = []
                        for c in range(1, tbl.Columns.Count + 1):
                            cell_txt = tbl.Cell(r, c).Shape.TextFrame.TextRange.Text
                            row_cells.append(" ".join(cell_txt.split()))
                        lines.append("| " + " | ".join(row_cells) + " |")
                        if r == 1:
                            lines.append("| " + " | ".join(["---"] * len(row_cells)) + " |")
            out.append("\n".join(lines))
        return "\n".join(out).strip()
    except Exception as exc:
        raise RuntimeError(f"Failed to read legacy .ppt via PowerPoint COM: {exc}") from exc
    finally:
        if pres is not None:
            try:
                pres.Close()
            except Exception:
                pass
        if ppt is not None:
            try:
                ppt.Quit()
            except Exception:
                pass


def cmd_office(file_path: Path, out_path: Path | None) -> int:
    ext = file_path.suffix.lower()
    if ext == ".docx":
        content = _extract_docx(file_path)
    elif ext == ".pptx":
        content = _extract_pptx(file_path)
    elif ext == ".doc":
        content = _extract_legacy_doc(file_path)
    elif ext == ".ppt":
        content = _extract_legacy_ppt(file_path)
    else:
        print(f"ERROR: Unsupported Office extension '{ext}'. Supported: .docx, .pptx, .doc, .ppt", file=sys.stderr)
        return 1

    _emit_output(content, out_path)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract textbook/courseware content for EE homework solving.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_toc = sub.add_parser("toc", help="List PDF bookmarks (table of contents)")
    p_toc.add_argument("pdf", type=Path)

    p_search = sub.add_parser("search", help="Search PDF text for a keyword/phrase")
    p_search.add_argument("pdf", type=Path)
    p_search.add_argument("query", type=str)
    p_search.add_argument("--max", type=int, default=20, dest="max_hits")

    p_pages = sub.add_parser("pages", help="Extract text from specified 1-based PDF pages")
    p_pages.add_argument("pdf", type=Path)
    p_pages.add_argument("page_spec", type=str, help="e.g. 1,3-5,107")
    p_pages.add_argument("--out", type=Path, default=None)

    p_render = sub.add_parser("render", help="Render PDF pages to PNG images")
    p_render.add_argument("pdf", type=Path)
    p_render.add_argument("page_spec", type=str, help="e.g. 1,3-5,107")
    p_render.add_argument("--out-dir", type=Path, required=True)
    p_render.add_argument("--dpi", type=int, default=180)

    p_office = sub.add_parser("office", help="Extract text and tables from .docx/.pptx/.doc/.ppt")
    p_office.add_argument("file", type=Path)
    p_office.add_argument("--out", type=Path, default=None)

    args = parser.parse_args()

    try:
        target = getattr(args, "pdf", None) or getattr(args, "file", None)
        if target is not None and not target.is_file():
            print(f"ERROR: File not found: {target}", file=sys.stderr)
            return 1

        if args.command == "toc":
            return cmd_toc(args.pdf)
        if args.command == "search":
            return cmd_search(args.pdf, args.query, args.max_hits)
        if args.command == "pages":
            return cmd_pages(args.pdf, args.page_spec, args.out)
        if args.command == "render":
            return cmd_render(args.pdf, args.page_spec, args.out_dir, args.dpi)
        if args.command == "office":
            return cmd_office(args.file, args.out)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
