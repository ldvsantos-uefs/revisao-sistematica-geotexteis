from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SpecimenEntry:
    entry_name: str
    species: str
    treatment_code: str
    treatment_label: str
    days: int


def _to_float_pt(value: str) -> float:
    v = value.strip().strip('"')
    if not v:
        return float('nan')
    v = v.replace('.', '').replace(',', '.') if v.count(',') == 1 and v.count('.') >= 1 else v.replace(',', '.')
    try:
        return float(v)
    except Exception:
        return float('nan')


def read_specimen_curve(raw_bytes: bytes) -> pd.DataFrame:
    text = raw_bytes.decode('ISO-8859-1', errors='replace')
    lines = [ln.strip() for ln in text.splitlines()]

    start_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith('Tempo;') and 'Carga' in ln:
            start_idx = i + 2  # skip header + units line
            break

    if start_idx is None:
        raise ValueError('Could not find data header (Tempo;...)')

    data_lines = [ln for ln in lines[start_idx:] if ln]
    if not data_lines:
        raise ValueError('No data lines found')

    rows: list[tuple[float, float, float]] = []
    for ln in data_lines:
        parts = [p.strip() for p in ln.split(';') if p.strip() != '']
        if len(parts) < 3:
            continue
        t = _to_float_pt(parts[0])
        ext = _to_float_pt(parts[1])
        load = _to_float_pt(parts[2])
        rows.append((t, ext, load))

    df = pd.DataFrame(rows, columns=['Time_s', 'Extension_mm', 'Load_N'])
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['Extension_mm', 'Load_N'])
    return df


def parse_entry_name(entry_name: str) -> SpecimenEntry | None:
    if not re.search(r'Specimen_DadosEmBruto_\d+\.csv$', entry_name, flags=re.IGNORECASE):
        return None

    upper = entry_name.upper()

    if 'OURICURI' not in upper:
        return None

    species = 'Syagrus coronata'

    # Days: many entries have "-60 DIAS"; some have none (assume 0 days).
    m_days = re.search(r'(_|\s|-)(\d+)\s*DIAS', upper)
    days = int(m_days.group(2)) if m_days else 0

    # Resin treatments appear as OURICURI0 / OURICURI2 in folder names.
    # In older exported sets they can also appear as OURICURI01 (camada simples).
    # Ignore NaOH-like markers (_O1_) here.
    if re.search(r'_O\d_', upper):
        return None

    # Explicit overrides first (avoid matching only the first digit in OURICURI01)
    if 'OURICURI01' in upper:
        treatment_code = 'R1'
        treatment_label = 'Resina — camada simples'
    else:
        m_r = re.search(r'OURICURI\s*[-_]?\s*(\d)', upper)
        if not m_r:
            return None

        r = int(m_r.group(1))
        treatment_code = f'R{r}'
        if treatment_code == 'R0':
            treatment_label = 'Sem resina'
        elif treatment_code == 'R1':
            treatment_label = 'Resina — camada simples'
        elif treatment_code == 'R2':
            treatment_label = 'Resina — camada dupla'
        else:
            return None

    return SpecimenEntry(
        entry_name=entry_name,
        species=species,
        treatment_code=treatment_code,
        treatment_label=treatment_label,
        days=days,
    )


def plot_resin_ouricuri_from_zip(zip_path: Path, output_path: Path) -> None:
    with zipfile.ZipFile(zip_path, 'r') as z:
        entries: list[SpecimenEntry] = []
        for name in z.namelist():
            parsed = parse_entry_name(name)
            if parsed:
                entries.append(parsed)

        if not entries:
            raise RuntimeError('No Ouricuri resin specimen curves found in zip')

        by_treat: dict[str, list[SpecimenEntry]] = {}
        for e in entries:
            by_treat.setdefault(e.treatment_code, []).append(e)

        # Global baseline: use time zero from double layer (R2) as "tempo zero" for all.
        baseline_group = by_treat.get('R2', [])
        baseline_days = sorted({e.days for e in baseline_group})
        if baseline_days:
            baseline_day = 0 if 0 in baseline_days else baseline_days[0]
            baseline_entries = [e for e in baseline_group if e.days == baseline_day][:4]
        else:
            baseline_day = min({e.days for e in entries})
            baseline_entries = [e for e in entries if e.days == baseline_day][:4]

        fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=False, sharey=False)
        axes = axes.flatten()

        treat_order = ['R0', 'R1', 'R2', 'R3']
        for ax, treat in zip(axes, treat_order):
            group = by_treat.get(treat, [])
            if not group:
                ax.set_axis_off()
                continue

            days_sorted = sorted({e.days for e in group})

            # User request: use the same "tempo zero" for all treatments.
            # Here we take "tempo zero" from camada dupla (R2) as baseline.
            day_a = baseline_day
            day_b = days_sorted[-1]

            a_entries = baseline_entries
            b_entries = [e for e in group if e.days == day_b][:4]

            for e in a_entries:
                df = read_specimen_curve(z.read(e.entry_name))
                ax.plot(df['Extension_mm'], df['Load_N'], color='0.35', alpha=0.75, linewidth=1.2)

            if day_b != day_a:
                for e in b_entries:
                    df = read_specimen_curve(z.read(e.entry_name))
                    ax.plot(df['Extension_mm'], df['Load_N'], color='#c0392b', alpha=0.75, linewidth=1.2)

            title = f"{group[0].treatment_label} | 0 d (baseline) (n={len(a_entries)}) vs {day_b} d (n={len(b_entries)})"

            ax.set_title(title, fontsize=10)
            ax.set_xlabel('Extensão compressiva (mm)')
            ax.set_ylabel('Carga compressiva (N)')
            ax.grid(True, which='major', linewidth=0.5, alpha=0.4)
            ax.minorticks_on()

        from matplotlib.lines import Line2D

        legend_lines = [
            Line2D([0], [0], color='0.35', lw=2, label='Antes: 0 d (baseline) - curvas individuais'),
            Line2D([0], [0], color='#c0392b', lw=2, label='Depois (maior tempo) - curvas individuais'),
        ]
        fig.legend(handles=legend_lines, loc='upper center', ncol=2, frameon=True, bbox_to_anchor=(0.5, 1.02))

        fig.suptitle('Punção (CBR) — Ouricuri (Syagrus coronata) — Resina', y=1.05, fontsize=13, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)


def main() -> None:
    base = Path(r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO")
    # Prefer the external published-article dataset (contains OURICURI01 = camada simples)
    zip_path = Path(
        r"C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\20 - ARTIGOS\2 - ARTIGOS PUBLICADOS\ARTIGO NAOH TABOA (PUBLICADO)\2 - DADOS\Punção-BRUTOS.zip"
    )
    out_path = base / r"3-IMAGENS\puncao_ouricuri_resina_curvas.png"

    plot_resin_ouricuri_from_zip(zip_path, out_path)
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    main()
