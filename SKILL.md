---
name: ee-homework-solver
description: >-
  Solve university EE/STEM homework and engineering exercises (半导体物理学、电子电力技术、通信原理、微机原理、单片机、电子线路、信号与系统等) with grounded textbook extraction, mandatory Python/SymPy symbolic and numerical verification, Typst typesetting, and PyMuPDF visual QA. Use when the user submits homework photos, textbook problem lists, DOCX/PPT problem sets, or asks for step-by-step derivations and formatted PDF solutions.
---

# EE Homework Solver

End-to-end workflow for reading problem statements from photos or course files, verifying every derivation with Python/SymPy, and delivering clean, publication-grade Typst PDFs.

## Bundled Resources

- Build & QA script: [build_homework_pdf.py](./scripts/build_homework_pdf.py)
- Reference extractor: [extract_ref.py](./scripts/extract_ref.py)
- Typst template: [ee_homework_tpl.typ](./resources/ee_homework_tpl.typ)
- Typst math cheatsheet: [typst-math-cheatsheet.md](./references/typst-math-cheatsheet.md)
- Subject verification checklists: [subject-checklists.md](./references/subject-checklists.md)
- Working example: [sample_homework.typ](./examples/sample_homework.typ)

Run scripts with `python -B` (`python3 -B` on macOS/Linux) so Python avoids generating `__pycache__` inside `scripts/`.

## 5-Step Workflow

### Step 1: Read & Ground Inputs

1. **Problem photos / screenshots**: inspect directly with your image-reading tool. Check subscripts, exponents, units, circuit node labels, and boundary conditions carefully; if any digit or symbol is blurred, ask or state the assumption explicitly.
2. **Textbook PDFs & courseware**: use [extract_ref.py](./scripts/extract_ref.py) instead of dumping huge files into context:
   ```bash
   python -B "<skill>/scripts/extract_ref.py" toc "<book.pdf>"
   python -B "<skill>/scripts/extract_ref.py" search "<book.pdf>" "关键词"
   python -B "<skill>/scripts/extract_ref.py" pages "<book.pdf>" 107,112-114
   python -B "<skill>/scripts/extract_ref.py" office "<slides_or_problems.pptx|.ppt|.docx|.doc>"
   ```
   For scanned PDFs or figure-heavy pages, render targeted pages to a temporary scratch folder and inspect the rendered PNGs:
   ```bash
   python -B "<skill>/scripts/extract_ref.py" render "<book.pdf>" 107-108 --out-dir "<scratch>/ref_pages"
   ```
3. **Edition & scope check**: confirm whether the course uses a specific edition or PPT scope (e.g., 刘恩科 第 8 版 vs 第 7 版 `n_i` values, or teacher-supplied PPT formulas).

### Step 2: Solve & Mandatory Python/SymPy Verification

Consult [subject-checklists.md](./references/subject-checklists.md) for the relevant subject before finalizing numbers.

1. Derive algebraic expressions symbolically first; keep intermediate steps transparent.
2. Run a Python verification script (`sympy`, `scipy.integrate`, `numpy`) checking:
   - Symbolic equivalence and boundary cases
   - Numerical substitution and significant figures
   - Dimensional/unit consistency (e.g., `cm^-3` vs `m^-3`, `dB` vs linear ratio, RMS vs average, CCM vs DCM)
3. When textbook editions or common approximations differ (e.g., `q = 1.602e-19 C` vs `1.6e-19 C`), compute and present both values in `#constants-box` and the solution.

### Step 3: Optional Engineering Figures

When waveforms, Bode plots, spectrum diagrams, or timing charts meaningfully clarify the solution:
- Generate clean vector SVG (preferred) or 300-DPI PNG via Matplotlib following the Chinese-safe font recipe in [subject-checklists.md](./references/subject-checklists.md) (`axes.unicode_minus = False`).
- Save figures in a local `figures/` subfolder next to the `.typ` file and embed with `#image("figures/...", width: 88%)`.

### Step 4: Typeset with Typst

Prefer Typst via [build_homework_pdf.py](./scripts/build_homework_pdf.py) (avoid invoking interactive TeX package installers).

1. Write `<homework_name>.typ` in the user's target course folder importing `#import "ee_homework_tpl.typ": *` (refer to [sample_homework.typ](./examples/sample_homework.typ) and [typst-math-cheatsheet.md](./references/typst-math-cheatsheet.md)).
2. Use template helpers consistently:
   - `#show: ee-doc.with(title: ..., subtitle: ..., course: ..., date: ...)`
   - `#constants-box[...]`, `#problem("第 1 题", title: ...)[...]`, `#solution()[...]`, `#answer-box[...]`, `#note-box[...]`, `#three-line-table(...)`, `#code-block(...)`
3. Use Typst upright strings for units (e.g., `Omega dot.c "cm"`, `"cm"^(-3)`) and `*bold*` for emphasis (already mapped to sans-serif bold CJK fonts in the template).

### Step 5: Compile & Mandatory Visual QA

Run [build_homework_pdf.py](./scripts/build_homework_pdf.py). It stages the `.typ` file, `ee_homework_tpl.typ`, and only referenced relative assets into an isolated temp directory (so cross-drive imports work without copying large textbook PDFs), compiles to PDF, checks for overflow/missing glyphs/sparse last pages, and renders previews:

```bash
python -B "<skill>/scripts/build_homework_pdf.py" "<dir>/homework.typ" "<dir>/homework.pdf" --preview-dir "<scratch>/homework_preview"
```

**Do NOT skip visual QA:**
1. Confirm `build_homework_pdf.py` exits `0` with `QA Status: OK (0 warnings)`.
2. Inspect **every** generated `page_XX.png` in `<scratch>/homework_preview` to verify:
   - True bold Chinese headings/labels, zero tofu boxes or missing math symbols
   - Balanced page breaks (no orphaned headers or cramped/overflowing tables)
   - Clear margins, legible equations, and intact figures
3. Fix any layout or formula issues in the `.typ` source and re-run until clean. Keep preview PNGs and scratch files in a temporary scratch directory—never leave temporary files in the user's homework folder or inside this skill directory.
