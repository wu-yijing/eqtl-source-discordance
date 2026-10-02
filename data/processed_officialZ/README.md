# `data/processed_officialZ/` — this directory holds no data

It exists for one reason: **many files in this repository still name
`data/processed_officialZ/`**, and a reader who follows one of those references would
otherwise land on nothing. It contains no data.

## Where the name comes from

`data/processed_officialZ/` is the layout of the **predecessor repository**
[`wu-yijing/eqtl-source-discordance-audit`](https://github.com/wu-yijing/eqtl-source-discordance-audit).
The analysis scripts in `code/analyses/reproduction_20261002/` originally read a *local clone*
of it — which is why the archive as first committed could not be run by anyone else. When this
repository adopted its canonical layout, that layer was renamed **`data/derived/`**: the same
six tables, under shorter names.

## They are the same files

Verified 2026-10-02 by MD5 against the predecessor repository — 6 of 6 byte-identical:

| Predecessor `data/processed_officialZ/` | Here | MD5 (both) |
|---|---|---|
| `scz_z_4arm_official.csv` | [`data/derived/scz_z_4arm.csv`](../derived/scz_z_4arm.csv) | `55caa68e5015a43c98f19a0556c40dd2` |
| `gtex_official_Z.csv` | [`data/derived/gtex_Z.csv`](../derived/gtex_Z.csv) | `9b8520dda0a689533ae778a431e1561d` |
| `eqtlgen_official_Z.csv` | [`data/derived/eqtlgen_Z.csv`](../derived/eqtlgen_Z.csv) | `0e99cfce14d7216d46ef261f794ba35a` |
| `gene_groups_TableS1_official.csv` | [`data/derived/gene_groups.csv`](../derived/gene_groups.csv) | `5fe2e3f520222899b4a7a253c4bdf3ff` |
| `primary_arm_96pairs_official.csv` | [`data/derived/primary_arm_96pairs.csv`](../derived/primary_arm_96pairs.csv) | `fc437aee0925c8b78925fae3fdf914a3` |
| `crosscohort_TableS4_official.csv` | [`data/derived/crosscohort.csv`](../derived/crosscohort.csv) | `20b5da3ba7cc0899b8592b63881cbe34` |

Two further predecessor names resolve the same way:

| Predecessor name | Here |
|---|---|
| `data/processed/ukb_dr_official/` | [`data/derived/ukb_dr/`](../derived/ukb_dr/) |
| `data/processed/covariate_matrix.csv` | [`data/superseded/covariate_matrix.csv`](../superseded/covariate_matrix.csv) — declared exemption, see [`../README.md`](../README.md) |
| `data/hk_reselect_20260830/data/` | [`data/superseded/hk_reselect_20260830/data/`](../superseded/hk_reselect_20260830/data/) |

## What to do

Read `data/derived/`. If a script still names `data/processed_officialZ/`,
[`code/analyses/reproduction_20261002/paths.py`](../../code/analyses/reproduction_20261002/paths.py)
rewrites it automatically via `legacy_alias()`, so nothing breaks.

The references that remain in the **historical** documents — the audit notes, the predecessor
README, the deprecation notices — are part of the record of what those documents described, and
have been left as written. Every reference a reader is meant to *act on* now says `data/derived/`.
