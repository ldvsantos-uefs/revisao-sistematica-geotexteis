"""Frequentist regression (effect sizes) for tensile UTS.

Goal
----
Provide a statistically stronger description of the tensile results than point-by-point means.

Important note
--------------
These tensile tests are destructive (each specimen tested once). With the current dataset
(no specimen/batch IDs), a true multi-level model with specimen-level random effects is not
identifiable. Instead, we fit frequentist regression models with interaction terms and robust
standard errors (HC3) + effect sizes (partial eta-squared) for terms.

Outputs
-------
Writes CSV/TXT reports under:
  5-DADOS/MEV-ANALISE/resultados_en/tensile_stats/

Models
------
Resin:
  UTS ~ Days_c * Species * Treatment_Level

NaOH:
  UTS ~ Days_c * Species * NaOH_level

Where Days_c is centered exposure time.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm


ROOT = Path(__file__).resolve().parents[1]


def _load_resin_tensile(xlsx_path: Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, sheet_name="TRAÇÃO")
    df.columns = df.columns.str.strip()

    df = df[df["Geotextil"].isin(["Taboa", "Ouricuri"])].copy()
    df["Species"] = df["Geotextil"].map({
        "Taboa": "Typha domingensis",
        "Ouricuri": "Syagrus coronata",
    })

    treatments = {
        "0x resina": "Untreated",
        "1x resina": "Monolayer Resin",
        "2x resina": "Bilayer Resin",
    }

    df["Tratamentos"] = df["Tratamentos"].astype(str).str.strip()
    df["Treatment_Level"] = df["Tratamentos"].map(treatments)

    out = pd.DataFrame({
        "Treatment_Type": "Resin",
        "Species": df["Species"],
        "Treatment_Level": df["Treatment_Level"],
        "Days": pd.to_numeric(df["Tempos (dias)"], errors="coerce"),
        "UTS": pd.to_numeric(df["Tensão Max de ruptura (N/mm)"], errors="coerce"),
    })

    out = out.dropna(subset=["Species", "Treatment_Level", "Days", "UTS"]).copy()
    out["UTS"] = out["UTS"].astype(float)
    out["Days"] = out["Days"].astype(float)
    return out


def _load_naoh_typha_from_sav(sav_path: Path) -> pd.DataFrame:
    try:
        import pyreadstat  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("pyreadstat is required to read Typha NaOH .sav") from exc

    df, meta = pyreadstat.read_sav(sav_path)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    trat_col = "TRATAMENTO" if "TRATAMENTO" in df.columns else None
    dias_col = "DIAS" if "DIAS" in df.columns else None
    uts_col = next(
        (
            c
            for c in df.columns
            if isinstance(c, str) and c.lower().replace(" ", "") in {"tensãoaruptura", "tensaoaruptura"}
        ),
        None,
    )

    if trat_col is None or dias_col is None or uts_col is None:
        raise ValueError(
            f"Unexpected NaOH .sav schema in {sav_path}. Got columns: {df.columns.tolist()}"
        )

    labels = (meta.variable_value_labels or {}).get(trat_col, {})
    treatment_level = df[trat_col].map(labels) if labels else df[trat_col].map(lambda v: f"{v}% NaOH")

    out = pd.DataFrame({
        "Treatment_Type": "NaOH",
        "Species": "Typha domingensis",
        "Treatment_Level": treatment_level.astype(str).str.strip(),
        "Days": pd.to_numeric(df[dias_col], errors="coerce"),
        "UTS": pd.to_numeric(df[uts_col], errors="coerce"),
    })

    out = out.dropna(subset=["Treatment_Level", "Days", "UTS"]).copy()
    out["UTS"] = out["UTS"].astype(float)
    out["Days"] = out["Days"].astype(float)
    return out


def _load_naoh_syagrus_from_extracted_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    required = {"Treatment_Level", "Days", "UTS"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {csv_path}: {sorted(missing)}")

    out = pd.DataFrame({
        "Treatment_Type": "NaOH",
        "Species": "Syagrus coronata",
        "Treatment_Level": df["Treatment_Level"].astype(str).str.strip(),
        "Days": pd.to_numeric(df["Days"], errors="coerce"),
        "UTS": pd.to_numeric(df["UTS"], errors="coerce"),
    })

    out = out.dropna(subset=["Treatment_Level", "Days", "UTS"]).copy()
    out["UTS"] = out["UTS"].astype(float)
    out["Days"] = out["Days"].astype(float)
    return out


def _partial_eta_squared(anova_table: pd.DataFrame) -> pd.Series:
    # eta_p^2 = SS_effect / (SS_effect + SS_error)
    if "sum_sq" not in anova_table.columns:
        raise ValueError("ANOVA table must include sum_sq")
    if "Residual" not in anova_table.index:
        raise ValueError("ANOVA table must include Residual row")

    ss_error = float(anova_table.loc["Residual", "sum_sq"])
    eta = {}
    for term, row in anova_table.iterrows():
        if term == "Residual":
            continue
        ss_term = float(row["sum_sq"])
        eta[term] = ss_term / (ss_term + ss_error) if (ss_term + ss_error) > 0 else np.nan
    return pd.Series(eta, name="partial_eta_sq")


def _fit_ols_with_robust(formula: str, df: pd.DataFrame):
    model = smf.ols(formula, data=df)
    res = model.fit()
    res_hc3 = res.get_robustcov_results(cov_type="HC3")
    return res, res_hc3


def _save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def analyze_resin(resin_df: pd.DataFrame, out_dir: Path) -> None:
    df = resin_df.copy()

    # Optional: keep the same plotting window (<=150 days) for consistency
    df = df[df["Days"] <= 150].copy()

    # Set explicit reference levels for interpretable betas
    df["Species"] = pd.Categorical(
        df["Species"],
        categories=["Typha domingensis", "Syagrus coronata"],
        ordered=True,
    )
    df["Treatment_Level"] = pd.Categorical(
        df["Treatment_Level"],
        categories=["Untreated", "Monolayer Resin", "Bilayer Resin"],
        ordered=True,
    )
    df = df.dropna(subset=["Species", "Treatment_Level"]).copy()

    df["Days_c"] = df["Days"] - df["Days"].mean()

    # Full factorial with time as continuous predictor
    # Reference: Typha + Untreated
    formula = (
        'UTS ~ Days_c * C(Species, Treatment(reference="Typha domingensis"))'
        ' * C(Treatment_Level, Treatment(reference="Untreated"))'
    )

    res, res_hc3 = _fit_ols_with_robust(formula, df)

    # Robust (HC3) term-wise Wald tests for p-values
    wald_terms = res_hc3.wald_test_terms(skip_single=False)

    # Type-II ANOVA (for sums of squares / eta_p^2). Note: p-values here are classical.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        anova2 = anova_lm(res, typ=2)
    eta = _partial_eta_squared(anova2)

    # Save
    out_dir.mkdir(parents=True, exist_ok=True)

    coef = pd.DataFrame({
        "term": res.params.index,
        "coef": res_hc3.params,
        "se_hc3": res_hc3.bse,
        "t_hc3": res_hc3.tvalues,
        "p_hc3": res_hc3.pvalues,
    })
    coef.to_csv(out_dir / "resin_coefficients_hc3.csv", index=False)

    anova2_out = anova2.copy()
    anova2_out["partial_eta_sq"] = eta
    anova2_out.to_csv(out_dir / "resin_anova_type2.csv")

    # Wald term tests table
    wald_df = pd.DataFrame({
        "term": list(wald_terms.table.index),
        "stat": wald_terms.table["statistic"].values,
        "df_constraint": wald_terms.table["df_constraint"].values,
        "pvalue_hc3": wald_terms.table["pvalue"].values,
    })
    wald_df.to_csv(out_dir / "resin_wald_terms_hc3.csv", index=False)

    summary = []
    summary.append("RESIN MODEL (OLS + HC3 robust SE)\n")
    summary.append(f"Formula: {formula}\n")
    summary.append(f"N = {len(df)}\n")
    summary.append(f"R^2 = {res.rsquared:.3f} (adj {res.rsquared_adj:.3f})\n")
    summary.append("\nKey interpretation (fixed-effects):\n")
    summary.append("- Main effect of Days_c: average degradation/gain rate (MPa/day) at reference categories.\n")
    summary.append("- Interaction Days_c:Treatment indicates change in degradation rate under resin vs untreated.\n")
    summary.append("- Species interactions indicate different time trends between Typha and Syagrus.\n")
    summary.append("\nRobust (HC3) term tests are in resin_wald_terms_hc3.csv.\n")
    summary.append("Effect sizes (partial eta^2) are in resin_anova_type2.csv.\n")

    _save_text(out_dir / "resin_report.txt", "".join(summary))


def analyze_naoh(naoh_df: pd.DataFrame, out_dir: Path) -> None:
    df = naoh_df.copy()
    df = df[df["Treatment_Level"].isin(["0% NaOH", "3% NaOH", "6% NaOH", "9% NaOH"])].copy()

    # Set explicit reference levels for interpretable betas
    df["Species"] = pd.Categorical(
        df["Species"],
        categories=["Typha domingensis", "Syagrus coronata"],
        ordered=True,
    )
    df["Treatment_Level"] = pd.Categorical(
        df["Treatment_Level"],
        categories=["0% NaOH", "3% NaOH", "6% NaOH", "9% NaOH"],
        ordered=True,
    )
    df = df.dropna(subset=["Species", "Treatment_Level"]).copy()
    df["Days_c"] = df["Days"] - df["Days"].mean()

    # Reference: Typha + 0% NaOH
    formula = (
        'UTS ~ Days_c * C(Species, Treatment(reference="Typha domingensis"))'
        ' * C(Treatment_Level, Treatment(reference="0% NaOH"))'
    )

    res, res_hc3 = _fit_ols_with_robust(formula, df)
    wald_terms = res_hc3.wald_test_terms(skip_single=False)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        anova2 = anova_lm(res, typ=2)
    eta = _partial_eta_squared(anova2)

    out_dir.mkdir(parents=True, exist_ok=True)

    coef = pd.DataFrame({
        "term": res.params.index,
        "coef": res_hc3.params,
        "se_hc3": res_hc3.bse,
        "t_hc3": res_hc3.tvalues,
        "p_hc3": res_hc3.pvalues,
    })
    coef.to_csv(out_dir / "naoh_coefficients_hc3.csv", index=False)

    anova2_out = anova2.copy()
    anova2_out["partial_eta_sq"] = eta
    anova2_out.to_csv(out_dir / "naoh_anova_type2.csv")

    wald_df = pd.DataFrame({
        "term": list(wald_terms.table.index),
        "stat": wald_terms.table["statistic"].values,
        "df_constraint": wald_terms.table["df_constraint"].values,
        "pvalue_hc3": wald_terms.table["pvalue"].values,
    })
    wald_df.to_csv(out_dir / "naoh_wald_terms_hc3.csv", index=False)

    summary = []
    summary.append("NAOH MODEL (OLS + HC3 robust SE)\n")
    summary.append(f"Formula: {formula}\n")
    summary.append(f"N = {len(df)}\n")
    summary.append(f"R^2 = {res.rsquared:.3f} (adj {res.rsquared_adj:.3f})\n")
    summary.append("\nKey interpretation (fixed-effects):\n")
    summary.append("- Days_c: average time trend (MPa/day).\n")
    summary.append("- Days_c:Treatment indicates how NaOH level changes the time trend.\n")
    summary.append("- Species interactions indicate different NaOH sensitivity between Typha and Syagrus.\n")
    summary.append("\nRobust (HC3) term tests are in naoh_wald_terms_hc3.csv.\n")
    summary.append("Effect sizes (partial eta^2) are in naoh_anova_type2.csv.\n")

    _save_text(out_dir / "naoh_report.txt", "".join(summary))


def main() -> None:
    resin_xlsx = ROOT / "5-DADOS" / "TABELA PARA ESTATÍSTICA.xlsx"
    typha_naoh_sav = ROOT / "1-REFERENCIAS" / "TABOA" / "Dados completos.sav"
    syagrus_naoh_csv = ROOT / "1-REFERENCIAS" / "OURICURI" / "ouricuri_naoh_extracted.csv"

    out_dir = ROOT / "5-DADOS" / "MEV-ANALISE" / "resultados_en" / "tensile_stats"

    if not resin_xlsx.exists():
        raise FileNotFoundError(f"Missing resin XLSX: {resin_xlsx}")

    resin = _load_resin_tensile(resin_xlsx)

    naoh_frames: list[pd.DataFrame] = []
    if typha_naoh_sav.exists():
        naoh_frames.append(_load_naoh_typha_from_sav(typha_naoh_sav))
    else:
        print(f"WARNING: Typha NaOH .sav not found: {typha_naoh_sav}")

    if syagrus_naoh_csv.exists():
        naoh_frames.append(_load_naoh_syagrus_from_extracted_csv(syagrus_naoh_csv))
    else:
        print(
            "WARNING: Syagrus NaOH extracted CSV not found. "
            "Run generate_tensile_english.py once with access to the instrument folder, "
            "or place ouricuri_naoh_extracted.csv under 1-REFERENCIAS/OURICURI/."
        )

    naoh = pd.concat(naoh_frames, ignore_index=True) if naoh_frames else pd.DataFrame()

    print("Fitting resin model...")
    analyze_resin(resin, out_dir)

    if not naoh.empty:
        print("Fitting NaOH model...")
        analyze_naoh(naoh, out_dir)

    print(f"Done. Reports saved under: {out_dir}")


if __name__ == "__main__":
    main()
