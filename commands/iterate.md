---
description: Run the render → view → fix loop on a figure script until print-size defects are gone or two cycles pass.
argument-hint: <path-to-figure-script.py>
allowed-tools: ["Bash", "Read", "Edit", "Write"]
---

Run the iteration loop on `$ARGUMENTS`. The skill at `skills/PaperFigureSkill/` ships the full procedure in `references/iteration.md` — use it.

Steps:

1. Read the script to understand what it builds and where it writes output. If it does not call `export.save(...)` or write into `figures/`, ask the user where the rendered PNG will land.
2. Run the script: `python $ARGUMENTS`. Capture the output paths.
3. View the resulting PNG with the `Read` tool. The PNG is at native print resolution — what you see is what a reader sees on paper.
4. Inspect for defects using the prompt in `skills/PaperFigureSkill/references/iteration.md` § "Visual Inspection Prompt". Be specific: name the element, name the defect, name the severity (blocking vs minor).
5. Apply fixes from the defect catalog in the same file. Edit the script in place. Prefer per-axes fixes (`ax.tick_params`, `ax.set_xlabel(..., fontsize=...)`) over re-applying the whole `pubstyle` block.
6. Re-render and re-view.
7. Stop after at most **2 fix cycles**, or sooner if only sub-pixel / cosmetic issues remain. Do not chase perfection.

Report what defects you found, what you changed, and what (if anything) still bothers you.
