"""EBook typesetting → video frame generation tool.

Generates styled "book page" layouts from HTML, Markdown (via Pandoc), or
ReStructuredText and renders them as 16:9 video frames (PNG) that can be
used directly as source material for OpenMontage composition. Fully local, free.

Renderers (choose with `renderer`):
- `weasyprint` (default) — HTML/CSS paged-media → PDF → PNG. Best for
  rich, styled editorial/typographic layouts. Requires Python `weasyprint`.
- `vivliostyle` — Vivliostyle CLI (`vivliostyle build`) → PDF → PNG.
  Best for EPUB-style HTML books with cross-references and complex page masters.
- `quarto` — Quarto (`quarto render`) → PDF (LaTeX-free) or HTML → PNG.
  Best for academic/technical documents with equations and code.
- `fpdf` — ReportLab-style programmatic PDF via fpdf2. Simple, fast, no
  browser dependency, but the page model is portrait-biased (see notes).

Inputs may be provided as raw text (`html`, `markdown`, `rst`) or a file
(`source`). `pipeline_compatible` accepts a `cut.type` in `typographic`
family and honor it when possible (weasy/vivliostyle).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    DependencyError,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolCommandError,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

DEFAULT_DIMENSIONS = {"width": 1920, "height": 1080}

RENDERER_DEPENDENCIES = {
    "weasyprint": ("python:weasyprint",),
    "vivliostyle": ("cmd:vivliostyle",),
    "quarto": ("cmd:quarto",),
    "fpdf": ("python:fpdf",),
}


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class EbookGen(BaseTool):
    name = "ebook_gen"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "typography"
    provider = "openmontage"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = (
        "Install at least one renderer:\n"
        "  weasyprint: python -m pip install weasyprint   (recommended default)\n"
        "  vivliostyle: npm install -g @vivliostyle/cli\n"
        "  quarto: brew install quarto (or official installer)\n"
        "  fpdf: python -m pip install fpdf2\n"
        "And poppler's pdftoppm for PDF->PNG frame conversion.\n"
        "  macOS: brew install poppler"
    )
    agent_skills = ["visual-style", "hyperframes"]

    capabilities = [
        "typeset_html",
        "typeset_markdown",
        "typeset_rst",
        "render_frame",
        "render_video",
    ]

    input_schema = {
        "type": "object",
        "properties": {
            "use": {
                "type": "string",
                "enum": ["html", "markdown", "rst"],
                "description": "Input format. If `source` is provided it is inferred from its extension.",
            },
            "source": {"type": "string", "description": "Path to a source file to typeset."},
            "html": {"type": "string", "description": "Inline HTML content."},
            "markdown": {"type": "string", "description": "Inline Markdown content."},
            "rst": {"type": "string", "description": "Inline reStructuredText content."},
            "renderer": {
                "type": "string",
                "enum": list(RENDERER_DEPENDENCIES.keys()),
                "default": "weasyprint",
                "description": "Typesetting/render engine. weasyprint is default and preferred for true 16:9 layout.",
            },
            "format": {
                "type": "string",
                "enum": ["frame", "pdf", "video"],
                "default": "frame",
                "description": "frame = PNG; pdf = PDF only; video = MP4.",
            },
            "width": {"type": "integer", "default": 1920},
            "height": {"type": "integer", "default": 1080},
            "dpi": {"type": "number", "default": 96,
                    "description": "Raster DPI for pdftoppm frame conversion."},
            "duration_seconds": {"type": "number", "default": 4.0,
                               "description": "Video clip length when format == video."},
            "fps": {"type": "integer", "default": 24},
            "frame": {"type": "integer", "default": 1,
                     "description": "Which page/frame to output (1-indexed)."},
            "page_margin_mm": {"type": "number", "default": 0,
                               "description": "Override page margin for PDF renderers."},
            "css": {"type": "string",
                    "description": "Extra CSS injected for HTML/weasy/hyperframes renderers."},
            "theme": {
                "type": "string",
                "enum": ["dark", "light", "sepia", "ink"],
                "default": "dark",
                "description": "Preset color/background theme for HTML rendering.",
            },
            "pipeline_compatible": {
                "type": "object",
                "description": "Optional scene info (cut.type, art_direction) to honour.",
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=200, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])
    idempotency_key_fields = ["use", "source", "html", "markdown", "renderer", "format"]
    side_effects = ["writes PDF/PNG/MP4 to output_path"]
    user_visible_verification = [
        "Inspect the PNG frame / MP4 for readable typography and correct layout",
        "Confirm Korean/CJK text renders (system fonts) in each renderer",
    ]

    def get_status(self) -> ToolStatus:
        available = False
        for deps in RENDERER_DEPENDENCIES.values():
            if all(self._dep_ok(d) for d in deps):
                available = True
                break
        if not available:
            return ToolStatus.UNAVAILABLE
        # Poppler needed to turn PDF into PNG for frame output.
        if shutil.which("pdftoppm") is None:
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        missing = []
        declared = self.dependencies
        for dep in declared:
            self._check_raw(dep)
        if not any(
            all(self._dep_ok(d) for d in deps)
            for deps in RENDERER_DEPENDENCIES.values()
        ):
            missing.append("no typeset renderer installed")
        if missing:
            raise DependencyError(
                "; ".join(missing) + ". " + self.install_instructions
            )

    @staticmethod
    def _dep_ok(dep: str) -> bool:
        if dep.startswith("python:"):
            try:
                __import__(dep[7:])
                return True
            except ImportError:
                return False
        if dep.startswith("cmd:"):
            return shutil.which(dep[4:]) is not None
        return False

    @staticmethod
    def _check_raw(dep: str) -> None:
        if dep.startswith("python:"):
            try:
                __import__(dep[7:])
            except ImportError:
                raise DependencyError(dep[7:])
        elif dep.startswith("cmd:"):
            if shutil.which(dep[4:]) is None:
                raise DependencyError(dep[4:])

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0  # all renderers are local and free

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        renderer = inputs.get("renderer", "weasyprint")
        base = {"weasyprint": 3.0, "vivliostyle": 8.0, "quarto": 10.0, "fpdf": 1.0}
        return base.get(renderer, 5.0)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        try:
            result = self._execute(inputs)
        except ToolCommandError as e:
            return ToolResult(
                success=False,
                error=f"{self.name}: {e}",
                data={"full_stderr": getattr(e, "stderr", None)},
            )
        except Exception as e:
            return ToolResult(success=False, error=f"{self.name}: {e}")
        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _execute(self, inputs: dict[str, Any]) -> ToolResult:
        output_path = inputs.get("output_path")
        fmt = inputs.get("format", "frame")
        renderer = inputs.get("renderer", "weasyprint")
        width = int(inputs.get("width", DEFAULT_DIMENSIONS["width"]))
        height = int(inputs.get("height", DEFAULT_DIMENSIONS["height"]))

        if not any(
            all(self._dep_ok(d) for d in deps)
            for deps in RENDERER_DEPENDENCIES.values()
        ):
            return ToolResult(
                success=False,
                error="No typeset renderer installed. " + self.install_instructions,
            )

        if fmt not in ("frame", "pdf", "video"):
            return ToolResult(success=False, error=f"Unknown format: {fmt}")

        # Resolve source content
        source = inputs.get("source")
        use = inputs.get("use")
        if source:
            src_path = Path(source)
            if not src_path.is_file():
                return ToolResult(success=False, error=f"Source file not found: {source}")
            if not use:
                suffix = src_path.suffix.lower()
                if suffix == ".md":
                    use = "markdown"
                elif suffix == ".rst":
                    use = "rst"
                elif suffix in (".html", ".htm"):
                    use = "html"
                else:
                    use = "html"
            content = src_path.read_text(encoding="utf-8", errors="replace")
        elif use == "html":
            content = inputs.get("html", "")
        elif use == "markdown":
            content = inputs.get("markdown", "")
        elif use == "rst":
            content = inputs.get("rst", "")
        else:
            return ToolResult(success=False, error="Provide 'use' + content, or a 'source' file")

        if not content.strip():
            return ToolResult(success=False, error="Empty document content")

        renderer = _normalize_renderer(renderer, use)

        with tempfile.TemporaryDirectory(prefix="ebook_") as tmp:
            tmpdir = Path(tmp)
            pdf_path: Path | None = None
            method = renderer

            if renderer == "fpdf":
                pdf_path = self._render_fpdf(content, tmpdir, width, height)
            elif renderer == "weasyprint":
                html = content if use == "html" else _markup_to_html(content, use, tmpdir, inputs)
                pdf_path = _weasy_render(html, tmpdir, width, height)
            elif renderer == "vivliostyle":
                html = content if use == "html" else _markup_to_html(content, use, tmpdir, inputs)
                pdf_path = _vivliostyle_render(html, tmpdir, width, height)
            elif renderer == "quarto":
                pdf_path = _quarto_render(content, use, tmpdir, width, height)

            if pdf_path is None or not pdf_path.exists():
                return ToolResult(success=False, error=f"{renderer} produced no PDF")

            if fmt == "pdf":
                if output_path:
                    final = Path(output_path)
                    final.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(pdf_path), str(final))
                    return ToolResult(
                        success=True,
                        data={"renderer": method, "format": "pdf", "output": str(final)},
                        artifacts=[str(final)],
                    )
                return ToolResult(
                    success=True,
                    data={"renderer": method, "format": "pdf", "output": str(pdf_path)},
                    artifacts=[str(pdf_path)],
                )

            return self._frame_or_video(pdf_path, inputs, method)

    def _render_fpdf(self, content: str, tmpdir: Path, width: int, height: int) -> Path:
        from fpdf import FPDF

        # fpdf2's landscape page model yields a portrait media box (1080x1920pt).
        # We render the portrait page and let pdftoppm rasterize it fully; the
        # 16:9 geometry is handled by the weasy/vivliostyle path, while fpdf is
        # offered for simple programmatic text frames.
        pdf = FPDF(orientation="P", unit="pt", format=(height, width))
        pdf.add_page()
        pdf.set_font("helvetica", "", 28)
        pages = self._render_fpdf_content(pdf, content)
        path = tmpdir / "book.pdf"
        pdf.output(str(path))
        return path

    def _render_fpdf_content(self, pdf, content: str):
        # Simple line-by-line text flow inside the 1080x1920 page.
        margin = 90
        y = margin
        x = margin
        max_w = pdf.w - 2 * margin
        for raw_line in content.splitlines():
            for line in (raw_line or [""]):
                if y > pdf.h - margin - 40:
                    pdf.add_page()
                    y = margin
                pdf.set_xy(x, y)
                pdf.cell(max_w, 40, line[:120] if line else " ")
                y += 44

    def _frame_or_video(self, pdf_path: Path, inputs: dict[str, Any], method: str) -> ToolResult:
        if shutil.which("pdftoppm") is None:
            return ToolResult(
                success=False,
                error="pdftoppm (poppler) not found for PDF->PNG. " + self.install_instructions,
                data={"pdf": str(pdf_path)},
            )
        width = int(inputs.get("width", DEFAULT_DIMENSIONS["width"]))
        height = int(inputs.get("height", DEFAULT_DIMENSIONS["height"]))
        dpi = float(inputs.get("dpi", 96))
        frame_n = max(1, int(inputs.get("frame", 1)))
        output = Path(inputs.get("output_path", "ebook_frame.png"))

        stem = output.stem
        tmpdir = pdf_path.parent
        prefix = tmpdir / (stem + "_pg")

        # WeasyPrint/Vivliostyle/Quarto express @page in px and convert to
        # points at 96/72. A 1920x1080 @page becomes a 1440x810 pt page,
        # so rasterizing at the requested dpi already yields the target 16:9 frame.
        # No manual crop is needed for the standard path.
        if method == "quarto":
            # %page geometry: 544.25x306.14pt. A 96dpi raster gives 726x409,
            # so raise target to the exact 1920x1080 pixel grid: 96*1920/544.25.
            dpi = 96 * (1920.0 / 544.25)
            subprocess.run(
                ["pdftoppm", "-png", "-r", str(dpi), "-f", str(frame_n),
                 "-l", str(frame_n), str(pdf_path), str(prefix)],
                check=True, capture_output=True, text=True,
            )
        else:
            subprocess.run(
                ["pdftoppm", "-png", "-r", str(dpi), "-f", str(frame_n),
                 "-l", str(frame_n), str(pdf_path), str(prefix)],
                check=True, capture_output=True, text=True,
            )
        pngs = sorted(prefix.parent.glob(prefix.name + "*.png"))
        if not pngs:
            return ToolResult(success=False, error="pdftoppm produced no frame")
        png = pngs[0]

        if inputs.get("format") == "video":
            video = self._png_to_video(png, inputs)
            return ToolResult(
                success=True,
                data={"renderer": method, "format": "video", "output": str(video)},
                artifacts=[str(video)],
            )

        if output.suffix.lower() == ".png":
            final = output
        else:
            final = output.with_suffix(".png")
        final.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(png), str(final))
        return ToolResult(
            success=True,
            data={"renderer": method, "format": "frame", "output": str(final)},
            artifacts=[str(final)],
        )

    def _png_to_video(self, png: Path, inputs: dict[str, Any]) -> Path:
        output = Path(inputs.get("output_path", "ebook_clip.mp4"))
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix.lower() != ".mp4":
            output = output.with_suffix(".mp4")
        dur = float(inputs.get("duration_seconds", 4.0))
        fps = int(inputs.get("fps", 24))
        self.run_command(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(png),
             "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
             "-t", str(dur), "-r", str(fps), "-pix_fmt", "yuv420p", str(output)],
            timeout=120,
        )
        return output


# --------------------------------------------------------------------------- #
# Renderer helpers
# --------------------------------------------------------------------------- #

THEME_CSS = {
    "dark": "body{background:#0d1117;color:#e6edf3}h1,h2,h3{color:#58a6ff}a{color:#79c0ff}", 
    "light": "body{background:#ffffff;color:#1f2328}h1,h2,h3{color:#0969da}",
    "sepia": "body{background:#f4ecd8;color:#433422}h1,h2,h3{color:#7a3e0f}",
    "ink": "body{background:#fffdf7;color:#1f1a17;font-family:Georgia,serif}h1,h2,h3{color:#111}",
}


def _normalize_renderer(renderer: str, use: str) -> str:
    if use in ("markdown", "rst") and renderer == "weasyprint":
        return renderer  # weasy handles via pandoc-style html below (we build HTML directly)
    return renderer


def _markup_to_html(content: str, use: str, tmpdir: Path, inputs: dict[str, Any]) -> str:
    """Convert markdown/rst to a self-contained styled HTML string."""
    css = inputs.get("css", "")
    theme = inputs.get("theme", "dark")
    theme_block = THEME_CSS.get(theme, THEME_CSS["dark"])
    page_css = (
        f"@page{{size:1920px 1080px;margin:{_page_margin(inputs)}mm}}"
        f"html,body{{margin:0;padding:0;font-size:34px;line-height:1.55}}"
        f"{theme_block}{css}"
    )
    if use == "markdown":
        body = _markdown_to_html(content, tmpdir)
    elif use == "rst":
        body = _rst_to_html(content, tmpdir)
    else:
        body = content
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{page_css}</style></head><body>{body}</body></html>"
    )


def _page_margin(inputs: dict[str, Any]) -> str:
    m = inputs.get("page_margin_mm", 14)
    return str(m)


def _markdown_to_html(content: str, tmpdir: Path) -> str:
    if shutil.which("pandoc"):
        src = tmpdir / "doc.md"
        src.write_text(content, encoding="utf-8")
        out = tmpdir / "doc.html"
        subprocess.run(
            ["pandoc", str(src), "-f", "markdown", "-t", "html", "-o", str(out)],
            check=True, capture_output=True, text=True,
        )
        return out.read_text(encoding="utf-8")
    # Fallback: minimal conversion (headings + paragraphs).
    lines = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("# "):
            lines.append(f"<h1>{_escape_html(s[2:])}</h1>")
        elif s.startswith("## "):
            lines.append(f"<h2>{_escape_html(s[3:])}</h2>")
        elif s.startswith("### "):
            lines.append(f"<h3>{_escape_html(s[4:])}</h3>")
        elif s:
            lines.append(f"<p>{_escape_html(s)}</p>")
    return "\n".join(lines)


def _rst_to_html(content: str, tmpdir: Path) -> str:
    if shutil.which("pandoc"):
        src = tmpdir / "doc.rst"
        src.write_text(content, encoding="utf-8")
        out = tmpdir / "doc.html"
        subprocess.run(
            ["pandoc", str(src), "-f", "rst", "-t", "html", "-o", str(out)],
            check=True, capture_output=True, text=True,
        )
        return out.read_text(encoding="utf-8")
    return f"<pre>{_escape_html(content)}</pre>"


def _weasy_render(html: str, tmpdir: Path, width: int, height: int) -> Path:
    from weasyprint import HTML

    out = tmpdir / "book.pdf"

    def _page_rule(css: str, w: int, h: int) -> str:
        return f"@page{{size:{w}px {h}px;margin:0}}"

    # Inject/force a 16:9 @page if the provided CSS didn't set a size.
    import re
    if "@page" not in html:
        html = html.replace("</style>", f"@page{{size:{width}px {height}px;margin:0}}</style>", 1)
    HTML(string=html).write_pdf(str(out))
    return out


def _vivliostyle_render(html: str, tmpdir: Path, width: int, height: int) -> Path:
    src = tmpdir / "book.html"
    src.write_text(html, encoding="utf-8")
    out = tmpdir / "book.pdf"
    subprocess.run(
        ["vivliostyle", "build", str(src), "-o", str(out)],
        check=True, capture_output=True, text=True,
    )
    return out


def _quarto_render(content: str, use: str, tmpdir: Path, width: int, height: int) -> Path:
    src = tmpdir / "book.qmd"
    body = content
    # 16:9 geometry via LaTeX geometry option, no TeX size calc needed.
    yaml = (
        "---\ntitle: ''\nformat: pdf\n"
        f"geometry: paperwidth=192mm, paperheight=108mm, margin=8mm\n---\n"
    )
    if use == "html":
        body = _html_to_markdown(content)
    src.write_text(yaml + body, encoding="utf-8")
    out = tmpdir / "book.pdf"
    subprocess.run(
        ["quarto", "render", str(src)],
        check=True, capture_output=True, text=True,
    )
    # Quarto writes alongside the source file; locate the PDF.
    candidates = sorted(tmpdir.glob("book.*")) + sorted(tmpdir.glob("*.pdf"))
    for c in candidates:
        if c.suffix == ".pdf":
            return c
    return out


def _html_to_markdown(html: str) -> str:
    # Lightweight: strip tags so quarto has plain text to typeset.
    import re
    text = re.sub(r"<style.*?</style>", "", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return text.strip()
