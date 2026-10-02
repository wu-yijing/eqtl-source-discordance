# results/

Two kinds of file, and the difference matters when you are checking something.

## 1. Written by a script, into this directory

These are produced by the scripts in `../scripts/` and are the machine-readable
evidence for the reported values. Outputs land here regardless of the working
directory (paths come from `../paths_config.py`).

| File | Written by |
|---|---|
| `recompute_results.json`, `recompute_log.txt`, `merged_pairs.csv` | `scripts/recompute.py` |
| `recompute_scz_results.json`, `recompute_scz_log.txt` | `scripts/recompute_scz.py` |
| `recompute_r3_s9_s20_results.json`, `recompute_r3_s9_s20_log.txt` | `scripts/r3/recompute_r3_s9_s20.py` |
| `_sim_results.json` | `scripts/r3/simulation_validation.py` |
| `m15_positive_control.json` | `scripts/r3/m15/m15_pc.py` |

Each of the first three logs opens with the MD5 and byte count of every input it
read, so a run either matches the recorded hashes or says so. The three JSON files
also carry those hashes under `inputs`; for the gzipped layers they include a
`content_md5` of the decompressed bytes, so an input's hash does not depend on the
compressor.

`m15_positive_control.json` here is produced by the recovered generator and matches
`../../figures/m15_positive_control.json` key for key (to 1 × 10⁻¹²).

## 2. Transcripts of diagnostic scripts

The scripts under `../scripts/repo_crosscheck/`, `../scripts/bmc_ref/` and
`../scripts/r2_fix/` print to stdout and write no file. These `*_out.txt` are those
transcripts, captured with `> file 2>&1`:

| File | Script |
|---|---|
| `bh_official_out.txt` | `repo_crosscheck/verify_bh_official.py` |
| `diag_gtex_bh2_out.txt` | `repo_crosscheck/diag_gtex_bh2.py` |
| `crosscheck_out.txt` | `repo_crosscheck/crosscheck_ge_vs_repo.py` |
| `crosscohort_out.txt` | `repo_crosscheck/verify_crosscohort_exact.py` |
| `cluster_out.txt`, `cluster2_out.txt` … `cluster5_out.txt` | `repo_crosscheck/verify_cluster*.py` |
| `perm_out.txt` | `repo_crosscheck/perm_variants.py` |
| `search_boot_out.txt` | `repo_crosscheck/search_boot.py` |
| `s17_cluster_out.txt` | `bmc_ref/verify_s17_cluster.py` |
| `se_band_out.txt` | `r2_fix/se_band.py` |
| `pin_sandwich_out.txt` | `r2_fix/pin_sandwich.py` |
| `diag_s9_s20b_out.txt` | `r3/diag_s9_s20b.py` |
| `diag_s20_out.txt` | `r3/diag_s20.py` |
| `m15_diff_out.txt` | `r3/m15/_diff.py` |
| `s9s20_stdout.txt`, `scz_stdout.txt`, `sim_stdout.txt` | the three long-running scripts, same run as the JSON above |

`m15_diff_out.txt` is worth reading: it compares the regenerated
`m15_positive_control.json` against the tracked `code/figures/m15_positive_control.json`.
`PC1a_BH_boundary`, the shared `PC1b_null_calibration` strata and `PC2a`/`PC2b` agree
exactly; the residual differences are in `PC3_*` and `spot_check`, plus three extra
`PC1b` strata in the tracked file — an SI-version difference in the patched document,
recorded in `docs/audit_notes/复现核验_GE投稿两份文档_20261002.md`.

All of them were regenerated on 2026-10-02 with the current scripts, so each
transcript corresponds to a committed script version. They are diagnostics: none of
them is on the path that produces a reported value, and none is needed to verify one.

Regenerate with:

```bash
python code/analyses/reproduction_20261002/paths_config.py     # check the wiring first
python code/analyses/reproduction_20261002/scripts/recompute.py > /tmp/recompute.out 2>&1
```
