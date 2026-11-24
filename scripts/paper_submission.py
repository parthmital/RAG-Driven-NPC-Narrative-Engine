"""Builds the IEEE Transactions on Games upload packages in `submission/`.

Run from the repository root: `.venv/Scripts/python.exe scripts/paper_submission.py`.

The manuscript and supplement packages are double-anonymised sources: every
`\\ifdefined\\Anonymised` block is resolved, the title-page and no-references
blocks are removed, the GitHub link and commit hashes are replaced, and the
build fails if any identifying string is left in a source or PDF. Each package
is compiled with Tectonic in a clean folder before it is zipped, so the zip
holds exactly what compiled. The title page and conflict-of-interest statement
are written as Word files, which the portal requires for the title page.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "docs" / "paper"
PLOTS = ROOT / "notebooks" / "outputs" / "plots"
TECTONIC = ROOT / "docs" / "tectonic.exe"
OUT = ROOT / "submission"
BUILD = ROOT / ".agent-local" / "tmp" / "submission-build"

GITHUB_REPO = "https://github.com/parthmital/RAG-Driven-NPC-Narrative-Engine"
ANON_REPO = "https://anonymous.4open.science/r/RAG-Driven-NPC-Narrative-Engine"
# Strings that would identify the authors to a reviewer (checked case-insensitively).
IDENTIFYING = [
    "parth",
    "mital",
    "bhumika",
    "pranesh",
    "kalyanaraman",
    "vitstudent",
    "vit.ac.in",
    "vellore",
    "obsidian flask",
    "github.com",
]
HASH = re.compile(r"\b[0-9a-f]{40}\b")
MAX_MANUSCRIPT_PAGES = 10

TITLE = (
    "Memory and State Control for LLM-Driven NPC Dialogue: Scoped Dual-Tier Memory "
    "and Pre-Commit Invariant Validation under a Paired, Oracle-Audited Evaluation"
)
AUTHORS = [
    ("Parth Mital", "parth.mital2023@vitstudent.ac.in"),
    ("Bhumika Singh", "bhumika.2023a@vitstudent.ac.in"),
    ("Pranesh Gopal", "pranesh.gopal2023@vitstudent.ac.in"),
    ("Kalyanaraman P", "pkalyanaraman@vit.ac.in"),
]
AFFILIATION = (
    "School of Computer Science and Engineering, Vellore Institute of Technology, "
    "Vellore 632014, Tamil Nadu, India"
)
CORRESPONDING = "Dr. Kalyanaraman P"


def resolve_switches(text: str) -> str:
    """Keeps the \\Anonymised branch of each switch and drops the TitlePage and
    NoReferences blocks. The blocks are line-based and never nested."""
    out: list[str] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        match = re.match(r"\s*\\ifdefined\\(\w+)\s*$", lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        keep_then = match.group(1) == "Anonymised"
        branch = "then"
        i += 1
        while True:
            line = lines[i]
            end = re.match(r"\s*(?:\\expandafter\\endinput)?\\fi(.*)$", line)
            if end:
                if end.group(1).strip():
                    out.append(end.group(1).strip())
                i += 1
                break
            if line.strip() == "\\else":
                branch = "else"
            elif (branch == "then") == keep_then:
                out.append(line)
            i += 1
    return "\n".join(out)


def scrub(text: str, partner: str) -> str:
    text = resolve_switches(text)
    text = text.replace(GITHUB_REPO, ANON_REPO)
    text = HASH.sub("withheld", text)
    text = re.sub(
        r"\\externaldocument\[(\w+)-\]\{\w+\\Variant\}",
        rf"\\externaldocument[\1-]{{{partner}}}",
        text,
    )
    text = text.replace(
        "\\graphicspath{{../../notebooks/outputs/plots/}}", "\\graphicspath{{figures/}}"
    )
    # Full-line comments describe the repository layout, not the paper.
    text = "\n".join(
        line for line in text.split("\n") if not line.lstrip().startswith("%")
    )
    return re.sub(r"\n{3,}", "\n\n", text)


def identifying_hits(text: str) -> list[str]:
    lower = text.lower()
    return [word for word in IDENTIFYING if word in lower] + HASH.findall(text)


def tectonic(folder: Path, name: str) -> None:
    result = subprocess.run(
        [
            str(TECTONIC),
            "--keep-logs",
            "--keep-intermediates",
            "--reruns",
            "3",
            f"{name}.tex",
        ],
        cwd=folder,
        capture_output=True,
        text=True,
        env={**os.environ, "TECTONIC_CACHE_DIR": str(ROOT / ".cache" / "tectonic")},
    )
    if result.returncode != 0:
        sys.exit(f"Tectonic failed on {name}.tex:\n{result.stderr[-3000:]}")


def log_problems(folder: Path, name: str) -> list[str]:
    patterns = re.compile(
        r"^! |Overfull \\[hv]box|undefined|multiply defined|Rerun to get|Missing character|Float too large"
    )
    log = (folder / f"{name}.log").read_text(encoding="utf-8", errors="replace")
    return [line for line in log.splitlines() if patterns.search(line)]


def stage_sources() -> Path:
    """Writes the scrubbed sources of both documents into one build folder."""
    shutil.rmtree(BUILD, ignore_errors=True)
    (BUILD / "figures").mkdir(parents=True)
    sources = {
        "manuscript.tex": scrub(
            (PAPER / "main.tex").read_text(encoding="utf-8"), "supplementary"
        ),
        "supplementary.tex": scrub(
            (PAPER / "supplementary.tex").read_text(encoding="utf-8"), "manuscript"
        ),
        "paper-preamble.tex": scrub(
            (PAPER / "paper-preamble.tex").read_text(encoding="utf-8"), ""
        ),
    }
    # Each document is compiled on its own, so each defines the anonymous switch.
    for name in ("manuscript.tex", "supplementary.tex"):
        sources[name] = "\\def\\Anonymised{}\n" + sources[name]
    for name, text in sources.items():
        hits = identifying_hits(text)
        if hits:
            sys.exit(f"{name} still identifies the authors: {hits}")
        (BUILD / name).write_bytes(text.encode("utf-8"))
    for name in ("IEEEtran.cls", "references.bib"):
        shutil.copy2(PAPER / name, BUILD / name)
    for png in PLOTS.glob("*.png"):
        shutil.copy2(png, BUILD / "figures" / png.name)
    return BUILD


def figures_of(tex: Path) -> list[str]:
    return re.findall(
        r"includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex.read_text(encoding="utf-8")
    )


def check_pdf(pdf: Path, max_pages: int | None = None) -> int:
    reader = PdfReader(pdf)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    meta = " ".join(str(value) for value in (reader.metadata or {}).values())
    hits = identifying_hits(text + "\n" + meta)
    if hits:
        sys.exit(f"{pdf.name} still identifies the authors: {hits}")
    if "??" in text:
        sys.exit(f"{pdf.name} has an unresolved reference (??)")
    if max_pages and len(reader.pages) > max_pages:
        sys.exit(
            f"{pdf.name} has {len(reader.pages)} pages, over the {max_pages}-page limit"
        )
    return len(reader.pages)


def write_zip(target: Path, folder: Path, names: list[str]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.write(folder / name, name)


def docx(target: Path, paragraphs: list[tuple[str, str]]) -> None:
    """Writes a minimal Word document. Each paragraph is (style, text), with
    style one of "title", "heading" or "body"."""
    runs = {
        "title": '<w:pPr><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr>',
        "heading": '<w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr>',
        "body": '<w:pPr><w:spacing w:after="60"/></w:pPr><w:r><w:rPr><w:sz w:val="22"/></w:rPr>',
    }
    body = "".join(
        f'<w:p>{runs[style]}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
        for style, text in paragraphs
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr></w:body></w:document>"
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
        '<w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    document_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/_rels/document.xml.rels", document_rels)
        archive.writestr("word/styles.xml", styles)


def main() -> None:
    build = stage_sources()
    for name in ("manuscript", "supplementary", "manuscript"):
        tectonic(build, name)
    problems = log_problems(build, "manuscript") + log_problems(build, "supplementary")
    if problems:
        sys.exit("Package build problems:\n  " + "\n  ".join(problems))
    pages = check_pdf(build / "manuscript.pdf", MAX_MANUSCRIPT_PAGES)
    supplement_pages = check_pdf(build / "supplementary.pdf")

    shutil.rmtree(OUT, ignore_errors=True)
    common = ["paper-preamble.tex", "IEEEtran.cls", "references.bib"]
    write_zip(
        OUT / "1-main-manuscript" / "manuscript-latex.zip",
        build,
        ["manuscript.tex", "manuscript.bbl", "supplementary.aux", *common]
        + [f"figures/{f}" for f in figures_of(build / "manuscript.tex")],
    )
    shutil.copy2(
        build / "manuscript.pdf", OUT / "1-main-manuscript" / "manuscript-preview.pdf"
    )
    write_zip(
        OUT / "5-latex-supplementary-file" / "supplementary-latex.zip",
        build,
        ["supplementary.tex", "supplementary.bbl", "manuscript.aux", *common]
        + [f"figures/{f}" for f in figures_of(build / "supplementary.tex")],
    )
    (OUT / "4-supplementary-material-for-review").mkdir(parents=True)
    shutil.copy2(
        build / "supplementary.pdf",
        OUT / "4-supplementary-material-for-review" / "supplementary.pdf",
    )

    docx(
        OUT / "2-title-page" / "title-page.docx",
        [
            ("title", TITLE),
            ("heading", "Authors"),
            *[
                ("body", f"{name}, {AFFILIATION} (e-mail: {mail})")
                for name, mail in AUTHORS
            ],
            ("heading", "Address for correspondence"),
            ("body", f"{CORRESPONDING} (corresponding author)"),
            ("body", AFFILIATION),
            ("body", f"E-mail: {AUTHORS[-1][1]}"),
            ("heading", "Acknowledgments"),
            ("body", "None."),
        ],
    )
    docx(
        OUT / "3-conflict-of-interest" / "conflict-of-interest.docx",
        [
            ("title", "Conflict of Interest Statement"),
            ("body", f"Manuscript: {TITLE}"),
            ("body", "Authors: " + ", ".join(name for name, _ in AUTHORS)),
            ("body", "None of the authors have a conflict of interest to disclose."),
        ],
    )
    print(f"Manuscript: {pages} pages. Supplement: {supplement_pages} pages.")
    print(f"Packages written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
