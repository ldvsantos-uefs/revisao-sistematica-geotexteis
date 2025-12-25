from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class GroupStats:
    n: int
    mean: float
    ci95_lo: float
    ci95_hi: float
    sd: float


def mean_ci95(x: np.ndarray) -> GroupStats:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = int(x.size)
    if n == 0:
        raise ValueError("Empty sample")
    mean = float(np.mean(x))
    if n == 1:
        return GroupStats(n=n, mean=mean, ci95_lo=float("nan"), ci95_hi=float("nan"), sd=float("nan"))

    sd = float(np.std(x, ddof=1))
    se = sd / np.sqrt(n)
    tcrit = float(stats.t.ppf(0.975, df=n - 1))
    lo = mean - tcrit * se
    hi = mean + tcrit * se
    return GroupStats(n=n, mean=mean, ci95_lo=float(lo), ci95_hi=float(hi), sd=sd)


def cohens_d_pooled(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    n1 = int(a.size)
    n2 = int(b.size)
    if n1 < 2 or n2 < 2:
        return float("nan")
    s1 = float(np.std(a, ddof=1))
    s2 = float(np.std(b, ddof=1))
    sp = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    return float((float(np.mean(b)) - float(np.mean(a))) / sp)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    csv_path = root / "1-REFERENCIAS" / "_EXTRAIDOS" / "DADOS TABOA TRAÇÃO.csv"
    df = pd.read_csv(csv_path)

    # Expected columns
    required = {"Tratamentos", "Tempos", "Resistencia_tracao"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing columns in {csv_path}: {sorted(missing)}")

    # Normalize types
    df = df.copy()
    df["Tratamentos"] = pd.to_numeric(df["Tratamentos"], errors="coerce")
    df["Tempos"] = pd.to_numeric(df["Tempos"], errors="coerce")
    df["Resistencia_tracao"] = pd.to_numeric(df["Resistencia_tracao"], errors="coerce")
    df = df.dropna(subset=["Tratamentos", "Tempos", "Resistencia_tracao"])  # keep raw replicates

    treatments = sorted(df["Tratamentos"].unique().tolist())
    tempos = sorted(df["Tempos"].unique().tolist())

    print("Unique Tratamentos:", treatments)
    print("Unique Tempos:", tempos)

    # Heuristic mapping often used in this project: 0,1,2,3 -> 0,3,6,9% NaOH
    code_to_label = {0.0: "0% NaOH", 1.0: "3% NaOH", 2.0: "6% NaOH", 3.0: "9% NaOH"}
    df["Treatment_Level"] = df["Tratamentos"].map(code_to_label).fillna(df["Tratamentos"].astype(str))

    # Find a time where (0%,3%,6%) means are close to manuscript targets
    targets = {"0% NaOH": 18.88, "3% NaOH": 17.62, "6% NaOH": 21.39}
    tol = 0.25

    candidates: list[tuple[float, dict[str, float]]] = []
    for t in tempos:
        sub = df[df["Tempos"] == t]
        means = sub.groupby("Treatment_Level")["Resistencia_tracao"].mean().to_dict()
        if all(k in means for k in targets):
            ok = all(abs(means[k] - targets[k]) <= tol for k in targets)
            if ok:
                candidates.append((float(t), {k: float(means[k]) for k in targets}))

    if candidates:
        print("\nCandidate tempos that match manuscript means (within ±0.25):")
        for t, m in candidates:
            print(f"- Tempos={t}: 0%={m['0% NaOH']:.2f}, 3%={m['3% NaOH']:.2f}, 6%={m['6% NaOH']:.2f}")
    else:
        print("\nNo Tempos matched targets within tolerance. Showing closest Tempos by L2 distance:")
        scored = []
        for t in tempos:
            sub = df[df["Tempos"] == t]
            means = sub.groupby("Treatment_Level")["Resistencia_tracao"].mean().to_dict()
            if not all(k in means for k in targets):
                continue
            dist = float(np.sqrt(sum((means[k] - targets[k]) ** 2 for k in targets)))
            scored.append((dist, float(t), means))
        scored.sort(key=lambda x: x[0])
        for dist, t, means in scored[:5]:
            print(
                f"- Tempos={t}: dist={dist:.3f}, 0%={means['0% NaOH']:.2f}, 3%={means['3% NaOH']:.2f}, 6%={means['6% NaOH']:.2f}"
            )

    # Choose Tempos=0 if present, else best-scoring
    chosen_tempo: float
    if 0.0 in tempos:
        chosen_tempo = 0.0
    elif candidates:
        chosen_tempo = candidates[0][0]
    else:
        if not scored:
            raise SystemExit("Could not score any tempo: missing required treatment levels")
        chosen_tempo = scored[0][1]

    sub = df[df["Tempos"] == chosen_tempo]
    print(f"\nUsing Tempos={chosen_tempo} for reporting.")

    # Report groups
    for lvl in ["0% NaOH", "3% NaOH", "6% NaOH"]:
        x = sub.loc[sub["Treatment_Level"] == lvl, "Resistencia_tracao"].to_numpy(float)
        gs = mean_ci95(x)
        print(
            f"{lvl}: mean={gs.mean:.4f}, CI95% [{gs.ci95_lo:.4f}, {gs.ci95_hi:.4f}], n={gs.n}"
        )

    # Pairwise contrasts vs 0%
    x0 = sub.loc[sub["Treatment_Level"] == "0% NaOH", "Resistencia_tracao"].to_numpy(float)
    for lvl in ["3% NaOH", "6% NaOH"]:
        xb = sub.loc[sub["Treatment_Level"] == lvl, "Resistencia_tracao"].to_numpy(float)
        ttest = stats.ttest_ind(x0, xb, equal_var=False)  # Welch
        d = cohens_d_pooled(x0, xb)
        print(f"\nContrast {lvl} vs 0% NaOH (Welch): p={float(ttest.pvalue):.6g}, Cohen_d={d:.4f}")


if __name__ == "__main__":
    main()
