# figures/

## What goes here, and what does not

**In:** the rendered figure files produced by `code/figures/` — PDF (vector) and PNG (600 dpi), named by figure number (`Fig1.pdf`, `Fig1.png`, …), plus the Supporting Information figures under `supporting/`.

**Out:** figure captions, titles, and any layout text that belongs to the manuscript. Those live in the manuscript and its Supporting Information. Nothing in this directory should be a second, independently edited copy of a manuscript artefact.

The rule that makes this safe:

> **Everything in `figures/` is a build output.** If a file here differs from what `code/figures/` produces, the file is wrong, not the script. Regenerating is always the fix.

This is different from the predecessor archive, which deliberately excluded figures altogether. The reason for including them here is that a reader should be able to confirm the archive reproduces the *published* figure, not merely a numerically equivalent one. If you prefer the predecessor's policy, delete this directory and say so in `README.md` — but pick one policy and state it, rather than leaving it implicit.

## Naming and format

| Item | Convention |
|---|---|
| File name | `Fig<N>.pdf`, `Fig<N>.png` for main figures; `supporting/FigS<N>.pdf`, `.png` for Supporting Information figures |
| Vector | PDF, all text as text (no outlined fonts), fonts embedded |
| Raster | PNG, 600 dpi, RGB (not CMYK), width 160 mm |
| Panel labels | lowercase `(a)`, `(b)` — **no descriptive titles inside the image** |
| Font | one family across all figures (embed-shared style module, not per-script hard-coding) |
| Colour | colour-blind-safe palette; the same meaning gets the same colour across figures |

*(A prior revision of this project shipped figures in two different font families because each plotting script hard-coded its own `font.family` instead of importing the shared style module. Keep the shared module and enforce it in review.)*

## Verification before a release

```bash
# every main figure has both formats
for n in 1 2 3 4; do
  test -f figures/Fig${n}.pdf || echo "MISSING figures/Fig${n}.pdf"
  test -f figures/Fig${n}.png || echo "MISSING figures/Fig${n}.png"
done

# regenerated output must be byte-identical (or explain the difference)
# run: bash code/run_all.sh
# then: sha256sum figures/*.pdf figures/*.png
```

Record the figure checksums in `metadata/provenance.json`. A figure that cannot be regenerated must be listed as such, with the reason.

## Known gap to close

The script that produces the fourth main figure must be identified and committed **before** the first release of this archive. If it cannot be recovered, the figure must be listed in `metadata/ARCHIVE_MAP.md` as `➖ not reproducible` rather than left as an implicit claim. Never ship a figure whose producing script is missing without saying so.
