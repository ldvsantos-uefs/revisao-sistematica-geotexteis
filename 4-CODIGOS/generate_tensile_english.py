"""Tensile Strength Analysis Plot (English)

Generates two separate figures for clarity:

Figure 6A (Resin):
- Typha domingensis and Syagrus coronata
- Resin coatings (Untreated / Monolayer / Bilayer)

Figure 6B (NaOH):
- Typha domingensis and Syagrus coronata
- Four subplots (0%, 3%, 6%, 9% NaOH)

Author: Diego Vidal
Date: December 2025
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
    from scipy.stats import linregress  # type: ignore
except Exception:  # pragma: no cover
    linregress = None

try:
    import pyreadstat  # type: ignore
except Exception:  # pragma: no cover
    pyreadstat = None


def _annotate_panel_label(fig: plt.Figure, panel_label: str) -> None:
    fig.text(
        0.01,
        0.99,
        f"({panel_label})",
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
    )


def _linear_fit_r2(x: pd.Series, y: pd.Series) -> tuple[float, float, Optional[float]]:
    """Return slope/intercept and R² of a simple linear fit y = a*x + b."""

    x_vals = np.asarray(x, dtype=float)
    y_vals = np.asarray(y, dtype=float)

    valid = np.isfinite(x_vals) & np.isfinite(y_vals)
    x_vals = x_vals[valid]
    y_vals = y_vals[valid]

    if x_vals.size < 2 or np.unique(x_vals).size < 2:
        return 0.0, float(np.mean(y_vals)) if y_vals.size else 0.0, None

    slope, intercept = np.polyfit(x_vals, y_vals, deg=1)
    y_hat = slope * x_vals + intercept

    ss_res = float(np.sum((y_vals - y_hat) ** 2))
    ss_tot = float(np.sum((y_vals - float(np.mean(y_vals))) ** 2))
    if ss_tot <= 0:
        return float(slope), float(intercept), None

    r2 = 1.0 - ss_res / ss_tot
    return float(slope), float(intercept), float(r2)


def _write_group_stats(
    df: pd.DataFrame,
    *,
    group_cols: list[str],
    value_col: str,
    out_path: Path,
) -> pd.DataFrame:
    stats = (
        df.groupby(group_cols, as_index=False, observed=False)[value_col]
        .agg(n="count", mean="mean", std="std", min="min", max="max")
        .sort_values(group_cols)
        .reset_index(drop=True)
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(out_path, index=False)
    return stats


def _linregress_summary(x: pd.Series, y: pd.Series) -> dict[str, object]:
    x_vals = pd.to_numeric(x, errors="coerce").astype(float)
    y_vals = pd.to_numeric(y, errors="coerce").astype(float)
    valid = np.isfinite(x_vals.to_numpy()) & np.isfinite(y_vals.to_numpy())
    x_vals = x_vals[valid]
    y_vals = y_vals[valid]

    n = int(x_vals.shape[0])
    if n < 2 or pd.Series(x_vals).nunique() < 2 or linregress is None:
        return {
            "n": n,
            "beta": None,
            "intercept": None,
            "t": None,
            "p": None,
            "r2": None,
        }

    r = linregress(x_vals.to_numpy(), y_vals.to_numpy())
    r2 = float(r.rvalue ** 2)
    t_val = float(r.slope / r.stderr) if getattr(r, "stderr", None) not in (None, 0) else None
    return {
        "n": n,
        "beta": float(r.slope),
        "intercept": float(r.intercept),
        "t": t_val,
        "p": float(r.pvalue),
        "r2": r2,
    }


def _report_missing_combinations(
    *,
    df: pd.DataFrame,
    out_path: Path,
    expected_days: list[int],
    species: list[str],
    levels: list[str],
    level_col: str,
    title: str,
    strict: bool,
) -> pd.DataFrame:
    clean = df.copy()
    clean = clean.dropna(subset=["Days", "UTS", "Species", level_col])
    clean["Days"] = pd.to_numeric(clean["Days"], errors="coerce")
    clean = clean.dropna(subset=["Days"])
    clean["Days"] = clean["Days"].astype(int)
    clean["Species"] = clean["Species"].astype(str).str.strip()
    clean[level_col] = clean[level_col].astype(str).str.strip()

    present = set(zip(clean["Species"].tolist(), clean[level_col].tolist(), clean["Days"].tolist()))

    missing_rows: list[dict[str, object]] = []
    for sp in species:
        for lvl in levels:
            for day in expected_days:
                if (sp, lvl, day) not in present:
                    missing_rows.append({"Species": sp, level_col: lvl, "Days": day})

    missing_df = pd.DataFrame(missing_rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    missing_df.to_csv(out_path, index=False)

    if not missing_df.empty:
        msg = (
            f"{title}: faltam dados para {len(missing_df)} combinações (Species x {level_col} x Days). "
            f"Veja o relatório: {out_path}"
        )
        if strict:
            raise ValueError(msg)
        print(f"WARNING: {msg}")

    return missing_df


def _load_resin_tensile(data_path: Path) -> pd.DataFrame:
    df = pd.read_excel(data_path, sheet_name="TRAÇÃO")
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
    df = df.dropna(subset=["Species", "Treatment_Level", "Tempos (dias)", "Tensão Max de ruptura (N/mm)"])

    out = pd.DataFrame({
        "Treatment_Type": "Resin",
        "Species": df["Species"],
        "Treatment_Level": df["Treatment_Level"],
        "Days": pd.to_numeric(df["Tempos (dias)"], errors="coerce"),
        "UTS": pd.to_numeric(df["Tensão Max de ruptura (N/mm)"], errors="coerce"),
    })
    return out.dropna(subset=["Days", "UTS"]).copy()


def _load_naoh_tensile_from_sav(sav_path: Path, species_label: str) -> pd.DataFrame:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is required to read .sav files. Install with: pip install pyreadstat")

    df, meta = pyreadstat.read_sav(sav_path)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # Expected columns in the current dataset:
    # - TRATAMENTO (0,3,6,9) with labels like '0% NaOH'
    # - DIAS (30..180)
    # - TENSÃOARUPTURA (UTS)
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
            f"Unexpected NaOH .sav schema in {sav_path}. "
            f"Need TRATAMENTO/DIAS/TENSÃOARUPTURA (got columns: {df.columns.tolist()})"
        )

    # Map treatment codes to labels if present
    labels = (meta.variable_value_labels or {}).get(trat_col, {})
    treatment_level = df[trat_col].map(labels) if labels else df[trat_col].map(lambda v: f"{v}% NaOH")

    out = pd.DataFrame({
        "Treatment_Type": "NaOH",
        "Species": species_label,
        "Treatment_Level": treatment_level,
        "Days": pd.to_numeric(df[dias_col], errors="coerce"),
        "UTS": pd.to_numeric(df[uts_col], errors="coerce"),
    })
    return out.dropna(subset=["Treatment_Level", "Days", "UTS"]).copy()


def _find_syagrus_naoh_sav() -> Optional[Path]:
    # Placeholder: no Syagrus+NaOH dataset has been found inside the workspace so far.
    # If you add it later, put it under 1-REFERENCIAS/OURICURI/ and name it with "NaOH".
    candidates = list(Path("1-REFERENCIAS/OURICURI").glob("**/*NaOH*.sav"))
    return candidates[0] if candidates else None


def _parse_decimal_pt(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def _read_text_best_effort(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace")


def _load_syagrus_naoh_from_instrument_results_dir(results_dir: Path) -> pd.DataFrame:
    """Load Syagrus (Ouricuri) + NaOH tensile data from instrument-export CSVs.

    Expected files in results_dir:
      TRAÇÃO-NaOH-OURICURI-O1-60DIAS.is_tens_Resultados.csv

    These files contain the maximum load (N). We convert to stress (MPa = N/mm²)
    using the reported specimen diameter.
    """

    if not results_dir.exists():
        raise FileNotFoundError(f"Syagrus NaOH results directory not found: {results_dir}")

    pattern = re.compile(
        r"(?i)TRAÇÃO-NaOH-OURICURI-(O[0-3]|OE)-(\d+)(?:DIAS|DIA)\.is_tens_Resultados\.csv$"
    )
    files = [p for p in results_dir.glob("*.csv") if pattern.search(p.name)]
    if not files:
        raise FileNotFoundError(
            f"No matching Syagrus NaOH result CSVs found in: {results_dir} (pattern: {pattern.pattern})"
        )

    code_to_level = {
        "O0": "0% NaOH",
        "O1": "3% NaOH",
        "O2": "6% NaOH",
        "O3": "9% NaOH",
    }

    rows: list[dict[str, object]] = []

    for file_path in sorted(files):
        match = pattern.search(file_path.name)
        if not match:
            continue

        code, days_str = match.group(1).upper(), match.group(2)
        if code == "OE":
            # Typically an extra/experimental group; skip to keep aligned with 0/3/6/9%.
            continue

        treatment_level = code_to_level.get(code)
        if treatment_level is None:
            continue

        days = int(days_str)

        # Read as raw text: semicolon-separated, comma decimals. These exports are
        # commonly cp1252 on Windows (accented PT-BR strings).
        text = _read_text_best_effort(file_path).splitlines()

        diameter_mm: Optional[float] = None
        for line in text[:50]:
            normalized = line.strip().lower()
            if ("dimensão" in normalized or "dimensao" in normalized) and ("diâmetro" in normalized or "diametro" in normalized):
                parts = [p.strip() for p in line.strip().split(";")]
                if len(parts) >= 2 and parts[1]:
                    diameter_mm = _parse_decimal_pt(parts[1])
                break

        if diameter_mm is None or diameter_mm <= 0:
            raise ValueError(f"Could not parse specimen diameter from: {file_path}")

        area_mm2 = 3.141592653589793 * (diameter_mm ** 2) / 4.0

        # Parse specimen rows: first column numeric index; columns include comment and max load.
        in_table = False
        for line in text:
            if line.strip().startswith("Tabela de Resultados"):
                in_table = True
                continue
            if not in_table:
                continue

            parts = [p.strip() for p in line.split(";")]
            if not parts:
                continue

            # Data rows start with integer index.
            if parts[0].isdigit():
                comment = parts[2] if len(parts) >= 3 else ""
                max_load_str = parts[3] if len(parts) >= 4 else ""
                if not max_load_str:
                    continue

                # Filter obvious invalid breaks.
                if isinstance(comment, str) and "GARRA" in comment.upper():
                    continue

                max_load_n = _parse_decimal_pt(max_load_str)
                uts_mpa = max_load_n / area_mm2
                rows.append(
                    {
                        "Treatment_Type": "NaOH",
                        "Species": "Syagrus coronata",
                        "Treatment_Level": treatment_level,
                        "Days": days,
                        "UTS": uts_mpa,
                    }
                )
            elif parts[0].lower().startswith("média") or parts[0].lower().startswith("media"):
                # End of table.
                break

    out = pd.DataFrame(rows)
    return out.dropna(subset=["Treatment_Level", "Days", "UTS"]).copy()


def _default_syagrus_naoh_results_dir() -> Path:
    # Allows overriding via env var to make the script portable.
    env = os.environ.get("OURICURI_NAOH_RESULTS_DIR")
    if env:
        return Path(env)
    return Path(
        r"C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\20 - ARTIGOS\2 - ARTIGOS PUBLICADOS"
        r"\ARTIGO NAOH TABOA (PUBLICADO)\2 - DADOS\GEONaOH-TRAÇÃO-BRUTOS\GEONaOH-TRAÇÃO\OURICURI"
    )


def load_and_plot_tensile() -> None:
    resin_xlsx = Path("./5-DADOS/TABELA PARA ESTATÍSTICA.xlsx")
    naoh_taboa_sav = Path("./1-REFERENCIAS/TABOA/Dados completos.sav")
    naoh_syagrus_sav = _find_syagrus_naoh_sav()

    output_dir = Path("./5-DADOS/MEV-ANALISE/resultados_en")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not resin_xlsx.exists():
        raise FileNotFoundError(f"Resin tensile table not found: {resin_xlsx}")

    print("Loading tensile data (Resin + NaOH)...")

    resin = _load_resin_tensile(resin_xlsx)
    frames = [resin]

    if naoh_taboa_sav.exists():
        frames.append(_load_naoh_tensile_from_sav(naoh_taboa_sav, species_label="Typha domingensis"))
    else:
        print(f"WARNING: NaOH dataset for Typha not found at: {naoh_taboa_sav}")

    if naoh_syagrus_sav and naoh_syagrus_sav.exists():
        frames.append(_load_naoh_tensile_from_sav(naoh_syagrus_sav, species_label="Syagrus coronata"))
    else:
        external_dir = _default_syagrus_naoh_results_dir()
        if external_dir.exists():
            print(f"Loading Syagrus+NaOH from instrument exports at: {external_dir}")
            syagrus_naoh = _load_syagrus_naoh_from_instrument_results_dir(external_dir)
            frames.append(syagrus_naoh)

            # Persist a compact copy inside the workspace for reproducibility.
            out_csv = Path("1-REFERENCIAS/OURICURI/ouricuri_naoh_extracted.csv")
            out_csv.parent.mkdir(parents=True, exist_ok=True)
            syagrus_naoh.to_csv(out_csv, index=False)
            print(f"Saved extracted Syagrus+NaOH summary to: {out_csv}")
        else:
            print("WARNING: Syagrus+NaOH dataset not found inside workspace or external folder; NaOH panel may show only Typha.")

    df = pd.concat(frames, ignore_index=True)
    # Não mascarar problemas: removemos NaN só para cálculo/plot, mas geramos relatórios de completude.
    df = df.dropna(subset=["Days", "UTS", "Species", "Treatment_Type", "Treatment_Level"]).copy()

    strict_validate = os.environ.get("STRICT_TENSILE_VALIDATE", "0").strip() in {"1", "true", "True", "YES", "yes"}

    # Styling aligned with the puncture curve figures (gray vs red, light grid, boxed axes)
    plt.rcParams.update(
        {
            'font.family': 'serif',
            'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
            'font.size': 10,
            'axes.labelsize': 10,
            'axes.titlesize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'axes.linewidth': 1.0,
            'lines.linewidth': 1.2,
            'axes.grid': True,
            'grid.alpha': 0.4,
            'grid.linewidth': 0.5,
        }
    )

    sns.set_style(
        "white",
        {
            'axes.edgecolor': 'black',
            'axes.spines.top': True,
            'axes.spines.right': True,
        },
    )

    # Resin (3 levels): keep a neutral baseline and red shades for coatings
    treatment_colors = ["0.35", "#c0392b", "#8e2a1f"]  # untreated, monolayer, bilayer
    treatment_markers = ['o', 'o', 'o']

    # Species styling for NaOH panels (match puncture gray vs red)
    species_palette = {
        "Typha domingensis": "0.35",
        "Syagrus coronata": "#c0392b",
    }
    species_markers = {
        "Typha domingensis": 'o',
        "Syagrus coronata": 'o',
    }

    resin_order = ["Untreated", "Monolayer Resin", "Bilayer Resin"]
    naoh_order = ["0% NaOH", "3% NaOH", "6% NaOH", "9% NaOH"]

    # X-axis ticks: show only the exact field exposure days (30, 60, 90, ...)
    preferred_day_ticks = [30, 60, 90, 120, 150, 180]
    available_days = sorted({int(d) for d in df["Days"].dropna().unique().tolist() if float(d).is_integer()})
    day_ticks = [d for d in preferred_day_ticks if d in available_days] or available_days

    # ----------------------
    # Figure 6A: Resin
    # ----------------------
    resin_df = df[df["Treatment_Type"] == "Resin"].copy()
    resin_df["Treatment_Level"] = pd.Categorical(resin_df["Treatment_Level"], categories=resin_order, ordered=True)

    _write_group_stats(
        resin_df,
        group_cols=["Species", "Treatment_Level", "Days"],
        value_col="UTS",
        out_path=output_dir / "tensile_resin_stats_by_day.csv",
    )

    # IMPORTANT: avoid zig-zag/polygon lines by aggregating replicates per day
    # and ensuring monotonic x ordering.
    resin_plot = (
        resin_df.groupby(["Species", "Treatment_Level", "Days"], as_index=False, observed=False)["UTS"]
        .mean()
        .rename(columns={"UTS": "UTS_mean"})
    )

    # Auditoria de regressão (usa as mesmas médias por dia plotadas)
    regression_rows: list[dict[str, object]] = []

    # Resin figure: show up to 150 days (no 180d panel/ticks)
    resin_min_day = 30
    resin_max_day = 150
    resin_plot = resin_plot[resin_plot["Days"] <= resin_max_day].copy()
    resin_available_days = sorted({int(d) for d in resin_plot["Days"].dropna().unique().tolist() if float(d).is_integer()})
    resin_day_ticks = [d for d in preferred_day_ticks if d <= resin_max_day and d in resin_available_days] or resin_available_days
    if resin_available_days:
        resin_min_day = min(resin_available_days)

    _report_missing_combinations(
        df=resin_df,
        out_path=output_dir / "tensile_missing_resin.csv",
        expected_days=[int(d) for d in resin_day_ticks],
        species=["Typha domingensis", "Syagrus coronata"],
        levels=resin_order,
        level_col="Treatment_Level",
        title="Figura 6A (Resin)",
        strict=strict_validate,
    )

    for species_name in ["Typha domingensis", "Syagrus coronata"]:
        for treatment in resin_order:
            sub = (
                resin_plot[
                    (resin_plot["Species"] == species_name)
                    & (resin_plot["Treatment_Level"] == treatment)
                ]
                .dropna(subset=["Days", "UTS_mean"])
                .sort_values("Days")
            )
            summary = _linregress_summary(sub["Days"], sub["UTS_mean"])
            regression_rows.append(
                {
                    "panel": "6A-Resin",
                    "Species": species_name,
                    "Series": treatment,
                    "n_days": summary["n"],
                    "beta_MPa_per_day": summary["beta"],
                    "t": summary["t"],
                    "p": summary["p"],
                    "R2": summary["r2"],
                    "days_used": ",".join([str(int(d)) for d in sub["Days"].tolist()]),
                }
            )

    # Small padding so edge markers are not clipped
    resin_xpad = max(1.0, 0.02 * (resin_max_day - resin_min_day))

    fig, axes = plt.subplots(1, 2, figsize=(7.08, 3.2), sharey=True, dpi=300)

    ax = axes[0]
    a_df = resin_plot[resin_plot["Species"] == "Typha domingensis"].copy()
    a_r2_lines: list[str] = []
    for idx, treatment in enumerate(resin_order):
        subset = a_df[a_df["Treatment_Level"] == treatment].sort_values("Days")
        subset = subset.dropna(subset=["Days", "UTS_mean"])
        if not subset.empty:
            _, _, r2 = _linear_fit_r2(subset["Days"], subset["UTS_mean"])
            ax.plot(
                subset["Days"],
                subset["UTS_mean"],
                color=treatment_colors[idx],
                linestyle='-' if idx == 0 else '--' if idx == 1 else ':',
                marker=treatment_markers[idx],
                markersize=5,
                label=treatment,
                zorder=3,
                antialiased=True,
            )

            if r2 is not None:
                a_r2_lines.append(f"{treatment}: R²={r2:.2f}")

    ax.set_xlabel("Exposure time (days)")
    ax.set_ylabel("UTS (MPa)")
    ax.set_title("Typha domingensis")
    ax.minorticks_on()
    ax.tick_params(which='both', direction='in', top=True, right=True, length=4)
    ax.tick_params(which='minor', length=2)
    ax.grid(True, which='major', linewidth=0.5, alpha=0.4)
    ax.set_xticks(resin_day_ticks)
    ax.set_xlim(resin_min_day - resin_xpad, resin_max_day + resin_xpad)
    ax.margins(y=0.08)
    if a_r2_lines:
        ax.text(
            0.98,
            0.98,
            "\n".join(a_r2_lines),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
        )
    sns.despine(ax=ax, left=False, bottom=False, top=False, right=False)

    ax = axes[1]
    b_df = resin_plot[resin_plot["Species"] == "Syagrus coronata"].copy()
    b_r2_lines: list[str] = []
    for idx, treatment in enumerate(resin_order):
        subset = b_df[b_df["Treatment_Level"] == treatment].sort_values("Days")
        subset = subset.dropna(subset=["Days", "UTS_mean"])
        if not subset.empty:
            _, _, r2 = _linear_fit_r2(subset["Days"], subset["UTS_mean"])
            ax.plot(
                subset["Days"],
                subset["UTS_mean"],
                color=treatment_colors[idx],
                linestyle='-' if idx == 0 else '--' if idx == 1 else ':',
                marker=treatment_markers[idx],
                markersize=5,
                label=treatment,
                zorder=3,
                antialiased=True,
            )

            if r2 is not None:
                b_r2_lines.append(f"{treatment}: R²={r2:.2f}")

    ax.set_xlabel("Exposure time (days)")
    ax.set_title("Syagrus coronata")
    ax.minorticks_on()
    ax.tick_params(which='both', direction='in', top=True, right=True, length=4)
    ax.tick_params(which='minor', length=2)
    ax.grid(True, which='major', linewidth=0.5, alpha=0.4)
    ax.set_xticks(resin_day_ticks)
    ax.set_xlim(resin_min_day - resin_xpad, resin_max_day + resin_xpad)
    ax.margins(y=0.08)
    if b_r2_lines:
        ax.text(
            0.98,
            0.98,
            "\n".join(b_r2_lines),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
        )
    sns.despine(ax=ax, left=False, bottom=False, top=False, right=False)

    # Shared legend at top (treatments)
    handles, labels = axes[0].get_legend_handles_labels()
    if handles and labels:
        fig.legend(
            handles,
            labels,
            loc="upper center",
            ncol=3,
            frameon=True,
            fancybox=False,
            edgecolor='black',
            bbox_to_anchor=(0.5, 1.02),
        )

    _annotate_panel_label(fig, panel_label="a")
    plt.tight_layout(rect=[0.04, 0.04, 1.00, 0.92])

    output_file_resin = output_dir / "fig_tensile_resin_english.png"
    plt.savefig(output_file_resin, dpi=300, bbox_inches="tight")
    print(f"Resin tensile figure saved to: {output_file_resin}")
    plt.close(fig)

    # ----------------------
    # Figure 6B: NaOH
    # ----------------------
    naoh_df = df[df["Treatment_Type"] == "NaOH"].copy()
    naoh_df["Treatment_Level"] = naoh_df["Treatment_Level"].astype(str).str.strip()
    naoh_df = naoh_df[naoh_df["Treatment_Level"].isin(naoh_order)].copy()
    naoh_df["Treatment_Level"] = pd.Categorical(naoh_df["Treatment_Level"], categories=naoh_order, ordered=True)

    _write_group_stats(
        naoh_df,
        group_cols=["Treatment_Level", "Species", "Days"],
        value_col="UTS",
        out_path=output_dir / "tensile_naoh_stats_by_day.csv",
    )

    _report_missing_combinations(
        df=naoh_df,
        out_path=output_dir / "tensile_missing_naoh.csv",
        expected_days=[int(d) for d in day_ticks],
        species=["Typha domingensis", "Syagrus coronata"],
        levels=naoh_order,
        level_col="Treatment_Level",
        title="Figura 6B (NaOH)",
        strict=strict_validate,
    )

    # Aggregate replicates per day within each subplot/species
    naoh_plot = (
        naoh_df.groupby(["Treatment_Level", "Species", "Days"], as_index=False, observed=False)["UTS"]
        .mean()
        .rename(columns={"UTS": "UTS_mean"})
    )

    for level in naoh_order:
        sublevel = naoh_plot[naoh_plot["Treatment_Level"] == level]
        for species_name in ["Typha domingensis", "Syagrus coronata"]:
            sub = (
                sublevel[sublevel["Species"] == species_name]
                .dropna(subset=["Days", "UTS_mean"])
                .sort_values("Days")
            )
            summary = _linregress_summary(sub["Days"], sub["UTS_mean"])
            regression_rows.append(
                {
                    "panel": "6B-NaOH",
                    "Species": species_name,
                    "Series": level,
                    "n_days": summary["n"],
                    "beta_MPa_per_day": summary["beta"],
                    "t": summary["t"],
                    "p": summary["p"],
                    "R2": summary["r2"],
                    "days_used": ",".join([str(int(d)) for d in sub["Days"].tolist()]),
                }
            )

    if regression_rows:
        pd.DataFrame(regression_rows).to_csv(output_dir / "tensile_regression_summary.csv", index=False)

    # NaOH padding so edge markers are not clipped
    naoh_xmin = min(day_ticks) if day_ticks else float(naoh_plot["Days"].min())
    naoh_xmax = max(day_ticks) if day_ticks else float(naoh_plot["Days"].max())
    naoh_xpad = max(1.0, 0.02 * (naoh_xmax - naoh_xmin))

    fig, axes = plt.subplots(2, 2, figsize=(7.08, 5.6), sharex=True, sharey=True, dpi=300)

    axes_list = [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]
    legend_handles = None
    legend_labels = None

    for idx, (ax, level) in enumerate(zip(axes_list, naoh_order)):
        sub = naoh_plot[naoh_plot["Treatment_Level"] == level].copy()

        r2_lines: list[str] = []
        for species_name, color in species_palette.items():
            species_data = sub[sub["Species"] == species_name].sort_values("Days")
            species_data = species_data.dropna(subset=["Days", "UTS_mean"])
            if not species_data.empty:
                _, _, r2 = _linear_fit_r2(species_data["Days"], species_data["UTS_mean"])
                short_name = species_name.replace(' domingensis', '').replace(' coronata', '')
                linestyle = '-' if species_name == "Typha domingensis" else '--'
                ax.plot(
                    species_data["Days"],
                    species_data["UTS_mean"],
                    color=color,
                    linestyle=linestyle,
                    marker=species_markers.get(species_name, 'o'),
                    markersize=4.5,
                    label=short_name,
                    zorder=3,
                    antialiased=True,
                )

                if r2 is not None:
                    r2_lines.append(f"{short_name}: R²={r2:.2f}")

        if r2_lines:
            ax.text(
                0.98,
                0.98,
                "\n".join(r2_lines),
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=8,
            )

        ax.set_title(level)
        ax.minorticks_on()
        ax.tick_params(which='both', direction='in', top=True, right=True, length=4)
        ax.tick_params(which='minor', length=2)
        ax.grid(True, which='major', linewidth=0.5, alpha=0.4)
        ax.set_xticks(day_ticks)
        ax.set_xlim(naoh_xmin - naoh_xpad, naoh_xmax + naoh_xpad)
        ax.margins(y=0.08)
        sns.despine(ax=ax, left=False, bottom=False, top=False, right=False)
        
        if idx == 0:
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                legend_handles, legend_labels = handles, labels

    # Shared legend at top (species)
    if legend_handles and legend_labels:
        fig.legend(
            legend_handles,
            legend_labels,
            loc="upper center",
            ncol=2,
            frameon=True,
            fancybox=False,
            edgecolor='black',
            bbox_to_anchor=(0.5, 1.02),
        )

    # Shared axis labels
    fig.text(0.5, 0.02, "Exposure time (days)", ha='center')
    fig.text(0.02, 0.5, "UTS (MPa)", va='center', rotation='vertical')

    _annotate_panel_label(fig, panel_label="b")

    plt.tight_layout(rect=[0.04, 0.04, 1.00, 0.92])

    output_file_naoh = output_dir / "fig_tensile_naoh_english.png"
    plt.savefig(output_file_naoh, dpi=300, bbox_inches="tight")
    print(f"NaOH tensile figure saved to: {output_file_naoh}")
    plt.close(fig)


if __name__ == "__main__":
    load_and_plot_tensile()
