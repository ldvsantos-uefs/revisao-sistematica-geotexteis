"""
X-Ray Diffraction (XRD) Analysis Plot
Typha domingensis vs Syagrus coronata
English Version

Author: Diego Vidal
Date: December 2025
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def _extract_xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extracts the most likely (2θ, intensity) numeric columns from a sheet.

    Some DRX exports include headers/notes or shift the numeric columns.
    This function searches the first few columns for the pair with the
    largest amount of numeric (x, y) points.
    """
    best_pair: tuple[int, int] | None = None
    best_count = -1

    max_cols = min(6, df.shape[1])
    candidates: list[tuple[int, int]] = []
    for x_col in range(max_cols):
        for y_col in range(x_col + 1, max_cols):
            candidates.append((x_col, y_col))

    for x_col, y_col in candidates:
        x = pd.to_numeric(df.iloc[:, x_col], errors="coerce")
        y = pd.to_numeric(df.iloc[:, y_col], errors="coerce")
        count = int(((x.notna()) & (y.notna())).sum())
        if count > best_count:
            best_count = count
            best_pair = (x_col, y_col)

    if best_pair is None or best_count <= 0:
        return np.array([]), np.array([])

    x = pd.to_numeric(df.iloc[:, best_pair[0]], errors="coerce")
    y = pd.to_numeric(df.iloc[:, best_pair[1]], errors="coerce")
    mask = x.notna() & y.notna()
    x_vals = x[mask].to_numpy(dtype=float)
    y_vals = y[mask].to_numpy(dtype=float)
    return x_vals, y_vals


def _sort_xy(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if x.size == 0:
        return x, y
    order = np.argsort(x)
    return x[order], y[order]


def _rolling_quantile_baseline(y: np.ndarray, window: int = 301, q: float = 0.05) -> np.ndarray:
    """
    Estimate XRD background using a rolling low-quantile (robust baseline).

    window: number of points (odd is preferable).
    q: low quantile (0.02–0.10 is common for lignocellulosic diffractograms).
    """
    if y.size == 0:
        return y.astype(float)

    window = int(window)
    if window < 51:
        window = 51
    if window % 2 == 0:
        window += 1

    s = pd.Series(y.astype(float))
    baseline = s.rolling(window=window, center=True, min_periods=window // 3).quantile(q).to_numpy()

    if np.all(np.isnan(baseline)):
        return np.zeros_like(y, dtype=float)

    # Fill edges with nearest valid values
    valid_idx = np.where(~np.isnan(baseline))[0]
    first_valid = int(valid_idx[0])
    last_valid = int(valid_idx[-1])
    baseline[:first_valid] = baseline[first_valid]
    baseline[last_valid + 1 :] = baseline[last_valid]

    baseline = baseline.astype(float)
    baseline[~np.isfinite(baseline)] = 0.0
    return baseline


def _bgsub_and_norm_max(y: np.ndarray, window: int = 301, q: float = 0.05) -> np.ndarray:
    """Subtract rolling-quantile baseline and normalize by post-correction max."""
    if y.size == 0:
        return y.astype(float)

    baseline = _rolling_quantile_baseline(y, window=window, q=q)
    y_corr = y.astype(float) - baseline
    y_corr[~np.isfinite(y_corr)] = np.nan
    y_corr = np.clip(y_corr, 0, None)

    m = float(np.nanmax(y_corr)) if np.any(np.isfinite(y_corr)) else 0.0
    if not np.isfinite(m) or m == 0.0:
        return np.zeros_like(y_corr, dtype=float)

    return (y_corr / m).astype(float)


def load_and_plot_xrd() -> None:
    # Paths
    data_path = Path("./5-DADOS/Planilha DRX (1).xlsx")
    output_dir = Path("./5-DADOS/MEV-ANALISE/resultados_en")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Match the Illustrator figure range
    x_min_plot = 10.0
    x_max_plot = 50.0

    # Vertical separation (offset) to mimic the published figure
    y_offset_syagrus = 0.20  # adjust to taste (0.15–0.30)

    # Baseline parameters (tune if needed)
    baseline_window = 301   # points; depends on step size (~0.026° => 301 ~ 7.8° span)
    baseline_q = 0.05       # low quantile

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        return

    print("Loading XRD data...")
    try:
        df_taboa = pd.read_excel(data_path, sheet_name="TABOA", header=None)
        df_ouricuri = pd.read_excel(data_path, sheet_name="OURICURI", header=None)

        # Extract numeric series
        x_taboa, y_taboa = _extract_xy(df_taboa)
        x_ouricuri, y_ouricuri = _extract_xy(df_ouricuri)

        if x_taboa.size == 0 or y_taboa.size == 0:
            raise ValueError("TABOA sheet: no numeric (x,y) data found")
        if x_ouricuri.size == 0 or y_ouricuri.size == 0:
            raise ValueError("OURICURI sheet: no numeric (x,y) data found")

        # Heuristic: some exports store 2θ scaled by 1000
        if np.nanmax(x_taboa) > 100:
            x_taboa = x_taboa / 1000.0
        if np.nanmax(x_ouricuri) > 100:
            x_ouricuri = x_ouricuri / 1000.0

        # Ensure increasing 2θ
        x_taboa, y_taboa = _sort_xy(x_taboa, y_taboa)
        x_ouricuri, y_ouricuri = _sort_xy(x_ouricuri, y_ouricuri)

        # Keep only the displayed 2θ range (so baseline and normalization match the figure)
        taboa_range = (x_taboa >= x_min_plot) & (x_taboa <= x_max_plot)
        ouricuri_range = (x_ouricuri >= x_min_plot) & (x_ouricuri <= x_max_plot)

        x_taboa_plot = x_taboa[taboa_range]
        y_taboa_raw = y_taboa[taboa_range].astype(float)

        x_ouricuri_plot = x_ouricuri[ouricuri_range]
        y_ouricuri_raw = y_ouricuri[ouricuri_range].astype(float)

        # Baseline subtraction + max normalization (recommended for matching the original figure)
        y_taboa_plot = _bgsub_and_norm_max(y_taboa_raw, window=baseline_window, q=baseline_q)
        y_ouricuri_plot = _bgsub_and_norm_max(y_ouricuri_raw, window=baseline_window, q=baseline_q)

        print(
            f"TABOA: n={x_taboa.size}, x=[{np.nanmin(x_taboa):.3f}, {np.nanmax(x_taboa):.3f}], "
            f"y=[{np.nanmin(y_taboa):.3f}, {np.nanmax(y_taboa):.3f}]"
        )
        print(
            f"OURICURI: n={x_ouricuri.size}, x=[{np.nanmin(x_ouricuri):.3f}, {np.nanmax(x_ouricuri):.3f}], "
            f"y=[{np.nanmin(y_ouricuri):.3f}, {np.nanmax(y_ouricuri):.3f}]"
        )

        # --- Figure with offset (as in the Illustrator/PDF figure) ---
        plt.figure(figsize=(10, 6))

        plt.plot(
            x_ouricuri_plot,
            y_ouricuri_plot + y_offset_syagrus,
            label="Syagrus",
            color="black",
            linewidth=1.6,
            linestyle="-",
            zorder=3,
        )
        plt.plot(
            x_taboa_plot,
            y_taboa_plot,
            label="Typha",
            color="black",
            linewidth=1.6,
            linestyle="--",
            zorder=3,
        )

        plt.xlabel("2θ (°)", fontsize=12)
        plt.ylabel("Intensity (a. u.)", fontsize=12)
        plt.legend(fontsize=10, loc="upper right", frameon=False)
        plt.grid(False)
        plt.xlim(x_min_plot, x_max_plot)
        plt.ylim(0.0, 1.05 + y_offset_syagrus)

        plt.tight_layout()
        output_file = output_dir / "fig_drx_english.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"XRD Figure saved to: {output_file}")

        # --- Debug/validation: no-offset version ---
        plt.clf()
        plt.figure(figsize=(10, 6))

        plt.plot(
            x_ouricuri_plot,
            y_ouricuri_plot,
            label="Syagrus",
            color="black",
            linewidth=1.6,
            linestyle="-",
        )
        plt.plot(
            x_taboa_plot,
            y_taboa_plot,
            label="Typha",
            color="black",
            linewidth=1.6,
            linestyle="--",
        )

        plt.xlabel("2θ (°)", fontsize=12)
        plt.ylabel("Intensity (a. u.)", fontsize=12)
        plt.legend(fontsize=10, loc="upper right", frameon=False)
        plt.grid(False)
        plt.xlim(x_min_plot, x_max_plot)
        plt.ylim(0.0, 1.05)

        plt.tight_layout()
        output_file_no = output_dir / "fig_drx_english_no_offset.png"
        plt.savefig(output_file_no, dpi=300, bbox_inches="tight")
        print(f"XRD (no offset) saved to: {output_file_no}")

    except Exception as e:
        print(f"Error processing XRD data: {e}")


if __name__ == "__main__":
    load_and_plot_xrd()
