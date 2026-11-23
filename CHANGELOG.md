# Changelog

## [1.0.0] - 2026-11-23

### Added
- **5-Step EE/STEM Homework Workflow (`SKILL.md`)**: Grounded textbook/courseware extraction, mandatory Python/SymPy verification, optional Matplotlib figures, Typst 0.15 typesetting, and PyMuPDF visual QA.
- **Cross-Platform Typst 0.15 Template (`resources/ee_homework_tpl.typ`)**: Academic palette, CJK bold font fallback fix (`Microsoft YaHei` / `SimHei` / `PingFang SC` / `Noto Sans CJK SC`), `#ee-doc`, `#constants-box`, `#problem`, `#solution`, `#answer-box`, `#note-box`, `#code-block`, and `#three-line-table`.
- **Isolated Staging Compiler & PDF QA (`scripts/build_homework_pdf.py`)**: Cross-drive safe staging of `.typ` sources and referenced assets, plus automated checks for margin overflow, missing glyphs (`\ufffd`), sparse last pages, and PNG preview rendering.
- **Reference Extractor (`scripts/extract_ref.py`)**: PDF TOC (`toc`), keyword search (`search`), targeted page extraction (`pages`), high-DPI page rendering for scanned textbooks (`render`), and structured `.docx`/`.pptx`/`.doc`/`.ppt` extraction (`office`).
- **Progressive Reference Guides (`references/`) & Showcase Example (`examples/sample_homework.typ`)**: Typst vs LaTeX math cheatsheet and subject-specific verification checklists covering Semiconductor Physics, Power Electronics, Communication Principles, Microcomputers/MCU, and Analog/RF Circuits.
