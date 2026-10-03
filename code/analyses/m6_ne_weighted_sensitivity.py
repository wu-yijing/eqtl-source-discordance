#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M6(b)/M6(d) sensitivity analyses: N_e-weighted re-merge of the RNH1 DR cross-cohort meta-analysis.

Background (Methods 1.10 of the manuscript): the primary merge combines cohort Z-scores as an
UNWEIGHTED arithmetic mean (each cohort enters with unit variance, SE = 1). This script repeats
the merge with sqrt(N_e) weights as a pre-specified sensitivity analysis, and additionally
reports the descriptive three-study merge that re-includes the underpowered UK Biobank dataset
GCST90043640 that was excluded from the primary estimate.

Framework
---------
Under a common standardized effect, an S-PrediXcan Z-score scales approximately with
sqrt(N_e):  Z_i ~ N(theta * sqrt(N_e,i), 1).
Hence the per-sqrt(N_e)-unit effect is  b_i = Z_i / sqrt(N_e,i)  with precision N_e,i, and
fixed-effect inverse-variance pooling of the b_i is algebraically identical to a weighted
Stouffer combination of the Z-scores with weights sqrt(N_e,i):

    Z_meta = sum_i Z_i * sqrt(N_e,i) / sqrt(sum_i N_e,i)

Cochran's Q is evaluated on the b scale:  Q = sum_i N_e,i * (b_i - b_hat)^2.
Random effects use the DerSimonian-Laird moment estimator for tau^2 on the b scale.

Inputs (all from archived official MetaXcan v0.8.1 outputs)
---------------------------------------------------------
  FinnGen R13 DR   : Z = +2.3091 (eQTLGen weights; data/processed/ukb_dr_official/finngen_r13_dr_eqtlgen_official.csv),
                     N_e = 49,304 = 4*15353*62519/77872
  UKB GCST90043640 : Z = +0.7225 (eQTLGen weights; data/processed/ukb_dr_official/ukb_gcst90043640_eqtlgen_official.csv),
                     N_e =  1,231 = 4*308*456040/456348
  UKB ieu-b-4803   : RETRACTED (2026-09-16). The dataset ID is absent from IEU OpenGWAS (audited against the
                     full 50,057-dataset catalogue) and its formerly carried Z = +0.95 had no traceable data
                     or code. It is retained below only as a labelled reference, never as an input.

Outputs
-------
  stdout / data/superseded/m6_ne_weighted_sensitivity_results.txt
"""
import math

STUDIES = [
    ("FinnGen R13 DR (eQTLGen weights, official MetaXcan v0.8.1)", 2.3091, 49304),
    ("UKB GCST90043640 (eQTLGen weights, official MetaXcan v0.8.1)", 0.7225, 1231),
    ("UKB ieu-b-4803 (RETRACTED - dataset ID not resolvable in IEU OpenGWAS)", 0.95, 54209),
]


def pnorm_two_sided(z):
    return math.erfc(abs(z) / math.sqrt(2))


def weighted_stouffer(zs, nes):
    num = sum(z * math.sqrt(n) for z, n in zip(zs, nes))
    return num / math.sqrt(sum(nes))


def ivw_b(zs, nes):
    """Fixed-effect IVW of per-sqrt(N_e)-unit effects; returns (b_hat, Q)."""
    bs = [z / math.sqrt(n) for z, n in zip(zs, nes)]
    b_hat = sum(n * b for n, b in zip(nes, bs)) / sum(nes)
    Q = sum(n * (b - b_hat) ** 2 for n, b in zip(nes, bs))
    return b_hat, Q


def direct_nsqrt_weighting(zs, nes):
    """Sqrt(N_e) weights applied directly on the Z scale; returns (Z_w, Q_w).

    This is a DIFFERENT convention from ``weighted_stouffer`` above, and the two are
    printed as separate rows of Supporting Information Table S5a:

      * ``weighted_stouffer`` normalises by ``sqrt(sum N_e)`` and returns a Z statistic
        on the unit-variance scale -- that is the "beta-scale inverse-variance merge
        (beta = Z/sqrt(N_e))" row, pooled Z = +2.39, Q on the b scale = 0.13.
      * this function takes the sqrt(N_e)-weighted *arithmetic mean* of the Z-scores
        and evaluates Cochran's Q on the Z scale with the same weights -- that is the
        "sqrt(N_e) weights applied directly on the Z scale" row, pooled Z = +2.09,
        Q = 76.6, I^2 = 98.7 %.

    Both rows are legitimately reported; they answer different questions. Reporting
    only one of them, or conflating them, is the error this docstring exists to stop.
    """
    w = [math.sqrt(n) for n in nes]
    z_w = sum(wi * z for wi, z in zip(w, zs)) / sum(w)
    Q = sum(wi * (z - z_w) ** 2 for wi, z in zip(w, zs))
    return z_w, Q


def dl_random_effects(zs, nes):
    """DerSimonian-Laird random effects on the b scale."""
    b_hat, Q = ivw_b(zs, nes)
    k = len(zs)
    tau2 = max(0.0, (Q - (k - 1)) /
               (sum(nes) - sum(n * n for n in nes) / sum(nes)))
    w = [1.0 / (1.0 / n + tau2) for n in nes]
    b_re = sum(wi * (z / math.sqrt(n)) for wi, z, n in zip(w, zs, nes)) / sum(w)
    se_re = math.sqrt(1.0 / sum(w))
    z_re = b_re / se_re
    return b_re, se_re, tau2, z_re, pnorm_two_sided(z_re)


def report(label, zs, nes):
    k = len(zs)
    df = k - 1
    zw = weighted_stouffer(zs, nes)
    b_hat, Q = ivw_b(zs, nes)
    I2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0
    b_re, se_re, tau2, z_re, p_re = dl_random_effects(zs, nes)
    mean_unw = sum(zs) / k
    lines = [
        "=" * 78, label,
        "  studies: " + "; ".join("Z=%+.3f, N_e=%d" % (z, n) for z, n in zip(zs, nes)),
        "  N_e shares: " + ", ".join("%.1f%%" % (100.0 * n / sum(nes)) for n in nes),
        "  [primary reference] unweighted mean Z = %+.2f" % mean_unw,
        "  [sqrt(N_e)-weighted] pooled Z = %+.2f  (two-sided P = %.2g)" % (zw, pnorm_two_sided(zw)),
        "  [sqrt(N_e)-weighted] b-scale FE pooled b = %.5f" % b_hat,
        "  [heterogeneity] Cochran Q = %.1f (df=%d), I^2 = %.1f%%" % (Q, df, I2),
        "  [random effects] DL tau^2 = %.3g (b scale); pooled b = %.4f (SE %.4f); "
        "test Z = %.2f, P = %.3f" % (tau2, b_re, se_re, z_re, p_re),
    ]
    print("\n".join(lines))
    return lines


def main():
    lines = []
    z_all = [s[1] for s in STUDIES]
    ne_all = [s[2] for s in STUDIES]
    # M6(b): primary k=2 set (FinnGen + GCST90043640, both eQTLGen weights), sqrt(N_e)-weighted re-merge
    lines += report("M6(b)  k=2 primary set, sqrt(N_e)-weighted re-merge",
                    z_all[:2], ne_all[:2])
    # M6(c): the SAME weights applied a different way -- a weighted MEAN on the Z scale,
    # with Cochran's Q also on the Z scale. This is SI Table S5a's fourth data row
    # ("sqrt(N_e) weights applied directly on the Z scale"), and it is not the same
    # quantity as M6(b): the normalised Stouffer combination is M6(b) at +2.39, while
    # the direct weighting is +2.09 with Q = 76.3 (published 76.6 -- see the residual
    # note below). Both rows are printed because the SI prints both.
    z2 = z_all[:2]
    ne2 = ne_all[:2]
    df2 = len(z2) - 1
    z_direct, Q_direct = direct_nsqrt_weighting(z2, ne2)
    I2_direct = max(0.0, (Q_direct - df2) / Q_direct) * 100 if Q_direct > 0 else 0.0
    m6c = [
        "=" * 78,
        "M6(c)  k=2 primary set, sqrt(N_e) weights applied DIRECTLY on the Z scale",
        "  studies: " + "; ".join("Z=%+.4f, N_e=%d" % (z, n) for z, n in zip(z2, ne2)),
        "  sqrt(N_e)-weighted mean Z = %+.4f  (published +2.09)" % z_direct,
        "  [heterogeneity, Z scale] Cochran Q = %.2f (df=%d), I^2 = %.2f%%  (published 76.6; 98.7%%)"
        % (Q_direct, df2, I2_direct),
        "  RESIDUAL vs SI Table S5a row 4: Q differs by %+.2f (%.2f%%); the pooled Z and I^2 agree"
        % (Q_direct - 76.6, 100.0 * (Q_direct - 76.6) / 76.6),
        "  at the printed precision. The published Q is not reproducible to its third significant",
        "  figure from the two cohort Z/N_e pairs this archive ships -- recorded, not hidden.",
    ]
    print("\n".join(m6c))
    lines += m6c
    # M6(d): reference merge that retains the retracted ieu-b-4803 value (completeness only; NOT an estimate)
    lines += report("M6(d)  reference merge retaining the retracted ieu-b-4803 value (not an estimate)",
                    z_all, ne_all)
    # unweighted k=3 reference
    m3 = sum(z_all) / 3
    Q3 = sum((z - m3) ** 2 for z in z_all)
    I2_3 = max(0.0, (Q3 - 2) / Q3) * 100 if Q3 > 0 else 0.0
    lines += ["=" * 78,
              "REFERENCE  k=3 unweighted mean (retains the retracted value): Z = %+.2f ; Q = %.1f (df=2) ; I^2 = %.1f%%"
              % (m3, Q3, I2_3),
              "",
              "The primary k = 2 set is FinnGen R13 DR + UKB GCST90043640, both analysed with eQTLGen weights",
              "using the unmodified official MetaXcan v0.8.1 binary (max|dZ| between the raw-allele and",
              "pre-aligned input protocols = 0.003, from duplicate-rsID handling).",
              "UKB ieu-b-4803 is withdrawn: the accession is not resolvable in IEU OpenGWAS."]
    text = "\n".join(lines) + "\n"
    print()
    import os

    # Repository-root discovery by sentinel, the same convention as paths_config.py.
    # The previous revision wrote to <repo>/data/processed/, a directory that no longer
    # exists in this repository (it became data/superseded/), so the script produced its
    # report and then died on the write. code/README.md rule 3 forbids absolute paths.
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(8):
        if os.path.exists(os.path.join(root, ".zenodo.json")):
            break
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    out = os.path.join(root, "data", "superseded",
                       "m6_ne_weighted_sensitivity_results.txt")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("Saved:", os.path.normpath(out))


if __name__ == "__main__":
    main()
