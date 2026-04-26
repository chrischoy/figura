"""
Save matplotlib figures in multiple formats with correct settings for
publication.

Why a wrapper instead of just plt.savefig()?
- Write all requested formats (PDF/SVG/PNG) consistently in one call.
- Apply bbox_inches='tight' every time without re-typing it.
- Handle raster DPI separately from screen DPI.
- Warn when someone reaches for JPEG (compression artifacts on text and
  lines look terrible in print).
- Reject names that escape the destination directory (path-traversal
  guard) so a caller-supplied stem can't overwrite arbitrary files.
- Write atomically: each format goes to a temporary file and is moved
  into place only after every format saved successfully. On failure the
  caller is left with the previous artifact set, not a half-written mix.

Output goes to ./figures/ in the current working directory by default.
Override with `outdir=` for other environments (e.g. set to
"/mnt/user-data/outputs" inside the Anthropic analysis-tool sandbox).
"""

import os
from pathlib import Path
from typing import Union


DEFAULT_OUTDIR = Path("figures")


def _validated_path(outdir: Path, name: str, ext: str) -> Path:
    """Return outdir/name.ext, refusing names that escape outdir.

    `name` is treated as a basename stem. Path separators, parent-dir
    references, and absolute paths are rejected outright — they almost
    always indicate a caller bug or untrusted input. After joining we
    re-check that the resolved path stays under the resolved outdir.
    """
    if not name or name in (".", ".."):
        raise ValueError(f"export.save: invalid name {name!r}")
    if os.sep in name or (os.altsep and os.altsep in name):
        raise ValueError(
            f"export.save: name {name!r} contains a path separator. "
            "Pass a basename stem (e.g. 'fig_results') and use outdir= "
            "to choose the directory."
        )
    if Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError(
            f"export.save: name {name!r} must be a basename, not a path."
        )

    candidate = (outdir / f"{name}.{ext}").resolve()
    root = outdir.resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError(
            f"export.save: resolved path {candidate} escapes outdir {root}."
        )
    return candidate


def save(
    fig,
    name: str,
    formats: tuple = ("pdf", "svg", "png"),
    outdir: Union[str, Path] = DEFAULT_OUTDIR,
    dpi: int = 300,
    transparent: bool = False,
) -> list:
    """Save a matplotlib figure to one or more formats atomically.

    Args:
        fig: matplotlib Figure.
        name: Basename stem, no extension and no path separators
            (e.g. 'fig_results'). Names containing '/', '\\', or '..'
            are rejected.
        formats: Iterable of extensions. PDF/SVG are vector (preferred);
            PNG is raster at `dpi`.
        outdir: Destination directory. Defaults to ./figures/.
        dpi: DPI for raster formats (PNG, etc). Ignored for vector formats.
        transparent: If True, save with transparent background. Useful when
            embedding into slides or LaTeX with a non-white background.

    Returns:
        List of final paths written, in the order requested. If any
        format fails to save, no file in the destination is updated and
        the underlying exception propagates.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Plan every final path up front so a bad name fails before we touch disk.
    plan = []
    for ext in formats:
        ext = ext.lstrip(".").lower()
        final = _validated_path(outdir, name, ext)
        tmp = final.with_name(f".{final.name}.tmp")
        plan.append((ext, tmp, final))

    # Write each format to its temp path. On any failure, clean up every
    # temp written so the caller's previous artifacts stay intact.
    written_tmps = []
    try:
        for ext, tmp, final in plan:
            # `format=ext` is required because the temp filename ends in
            # ".tmp", which matplotlib would otherwise try to dispatch as
            # an unsupported format.
            kwargs = dict(
                format=ext,
                bbox_inches="tight",
                pad_inches=0.02,
                transparent=transparent,
            )
            if ext in ("png", "jpg", "jpeg", "tiff", "tif"):
                kwargs["dpi"] = dpi
            if ext in ("jpg", "jpeg"):
                print(
                    f"[export] warning: writing '{final.name}' as JPEG. "
                    "JPEG compresses text and lines badly — prefer PNG for "
                    "raster, PDF/SVG for vector."
                )
            fig.savefig(tmp, **kwargs)
            written_tmps.append(tmp)
    except Exception:
        for tmp in written_tmps:
            try:
                tmp.unlink()
            except OSError:
                pass
        raise

    # All writes succeeded. Promote temps to their final names atomically.
    finals = []
    for _, tmp, final in plan:
        os.replace(tmp, final)
        finals.append(final)
    return finals
