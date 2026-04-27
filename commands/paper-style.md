---
description: Apply venue-specific publication style (NeurIPS, ICML, ICLR, IEEE, CVPR, ACM, Nature) to a matplotlib figure script.
argument-hint: <venue> <path-to-figure-script.py>
allowed-tools: ["Bash", "Read", "Edit"]
---

Apply venue style `$ARGUMENTS` to a matplotlib figure script. Expected form: `<venue> <script.py>`.

Supported venues (from `skills/figura/scripts/pubstyle.py` `_VENUES`):

| Venue | Notes |
|---|---|
| `generic` | Default; works across most venues |
| `neurips` | 8pt body, double-column 6.75 in |
| `icml` | 8pt body, double-column 6.75 in |
| `iclr` | 8pt body, double-column 6.75 in |
| `ieee` | Narrow columns, 7pt ticks/legend |
| `cvpr` | IEEE-format two-column, 8pt body, 7pt ticks/legend |
| `acm` | 8pt body, double-column |
| `nature` | 7pt body, 6pt ticks; mandates Helvetica |

If `$ARGUMENTS` is empty or missing one of `<venue>` or `<script>`, ask the user. Do not improvise.

If the venue is not in the list above, error out and list the valid options. Don't invent.

Procedure:

1. Validate arguments. Reject unknown venues.
2. Read the script. Confirm it imports `pubstyle` and calls `pubstyle.apply()`.
3. Patch the `pubstyle.apply()` call to pass `venue="<venue>"`:
   - `pubstyle.apply()` → `pubstyle.apply(venue="neurips")`
   - `pubstyle.apply(extra={...})` → `pubstyle.apply(venue="neurips", extra={...})`
4. If the script does not yet import `pubstyle`, add the standard skill setup at the top (see `skills/figura/SKILL.md` § Setup) with the venue arg pre-applied.
5. Re-render the figure (`python <script>`) and view the output PNG to confirm fonts/sizes match expectations at print width.
6. Report what changed and what the rendered PNG looks like.

Do not modify anything other than the `pubstyle.apply()` call and (if needed) the import block. Don't restyle the plot itself — that's `/figura:beautify`.
