from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# -------------------- Paths --------------------
csv_path = Path(
    r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\5-DADOS\drx_taboa_syagrus_dados_originais_e_normalizados.csv"
)
out_dir = Path(
    r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\5-DADOS"
)
out_dir.mkdir(parents=True, exist_ok=True)

# -------------------- Plot window --------------------
x_min_plot = 5.0
x_max_plot = 50.0

# -------------------- Offsets (mantém a geometria aprovada) --------------------
sy_offset = 0.00
ty_offset = -0.35

# -------------------- Smoothing --------------------
smooth_window = 9  # 7–15 (ímpar). Use 1 para desligar.

# -------------------- Peak annotations (estilo artigo) --------------------
annotate_peaks = True

# Posições típicas (2θ) de celulose I em fibras lignocelulósicas (aproximadas)
cellulose_I_targets_deg = {
    "110": 14.9,
    "200": 22.3,
    "004": 34.8,
}

# Região/posição típica do halo amorfo em fibras naturais (aprox.)
amorphous_target_deg = 18.0

def smooth_ma(y: np.ndarray, w: int) -> np.ndarray:
    """Simple moving-average smoothing."""
    if w is None or w <= 1:
        return y
    w = int(w)
    if w % 2 == 0:
        w += 1
    kernel = np.ones(w, dtype=float) / float(w)
    return np.convolve(y, kernel, mode="same")


def peak_near(x: np.ndarray, y: np.ndarray, target: float, window: float = 0.9) -> tuple[float, float] | None:
    """Return (x_peak, y_peak) as max in [target-window, target+window], or None."""
    mask = (x >= (target - window)) & (x <= (target + window))
    if not np.any(mask):
        return None
    xx = x[mask]
    yy = y[mask]
    if yy.size == 0:
        return None
    idx = int(np.nanargmax(yy))
    return float(xx[idx]), float(yy[idx])


def y_at_near(x: np.ndarray, y: np.ndarray, target: float, window: float = 0.8) -> tuple[float, float] | None:
    """Return (x_near, y_near) at the closest x within window, else None."""
    mask = (x >= (target - window)) & (x <= (target + window))
    if not np.any(mask):
        return None
    xx = x[mask]
    yy = y[mask]
    idx = int(np.nanargmin(np.abs(xx - target)))
    return float(xx[idx]), float(yy[idx])

# -------------------- Style (template clássico de paper) --------------------
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 10,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.linewidth": 0.8,
        "lines.linewidth": 0.85,
        "lines.antialiased": True,
        "lines.solid_capstyle": "round",
        "lines.dash_capstyle": "round",
    }
)

def main() -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

    df = pd.read_csv(csv_path)

    required = {"two_theta_deg", "syagrus_bgsub_norm", "typha_bgsub_norm"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV não possui colunas esperadas: {sorted(missing)}. Colunas disponíveis: {list(df.columns)}")

    # Dados
    x = df["two_theta_deg"].to_numpy(dtype=float)
    sy = df["syagrus_bgsub_norm"].to_numpy(dtype=float)  # já normalizado
    ty = df["typha_bgsub_norm"].to_numpy(dtype=float)    # já normalizado

    # Recorte do domínio
    mask = (x >= x_min_plot) & (x <= x_max_plot)
    x, sy, ty = x[mask], sy[mask], ty[mask]

    # Suavização leve (mantém a forma, reduz serrilhado)
    sy = smooth_ma(sy, smooth_window)
    ty = smooth_ma(ty, smooth_window)

    # Offsets (mesma lógica da figura aprovada)
    sy_plot = sy + sy_offset
    ty_plot = ty + ty_offset

    # -------------------- Plot --------------------
    # Tamanho “1 coluna” (~8,6 cm × 6,0 cm) em polegadas
    fig, ax = plt.subplots(figsize=(3.39, 2.36))

    ax.plot(x, sy_plot, color="black", lw=0.85, ls="-", label="Syagrus")
    ax.plot(x, ty_plot, color="black", lw=0.85, ls="--", label="Typha")

    ax.set_xlim(x_min_plot, x_max_plot)
    ax.set_xlabel(r"2$\theta$ (°)")
    ax.set_ylabel("Intensity (a.u.)")

    # Ticks (estilo clássico): inward, com minor ticks e caixa completa
    ax.xaxis.set_major_locator(plt.MultipleLocator(10))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
    ax.minorticks_on()
    ax.tick_params(which="major", direction="in", length=4, width=0.8, colors="black", top=True, right=True)
    ax.tick_params(which="minor", direction="in", length=2, width=0.6, colors="black", top=True, right=True)

    # Remover escala numérica do eixo Y (estilo comum em difratogramas publicados)
    ax.tick_params(axis="y", which="both", labelleft=False)

    # Spines (boxed axes)
    for spine in ("top", "right", "left", "bottom"):
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_color("black")
        ax.spines[spine].set_linewidth(0.8)

    # Limites Y com folga automática (evita “corte” e dá espaço p/ rótulos)
    y_min = float(np.nanmin([sy_plot.min(), ty_plot.min()]))
    y_max = float(np.nanmax([sy_plot.max(), ty_plot.max()]))
    y_range = (y_max - y_min) if y_max > y_min else 1.0
    pad_bottom = 0.06 * y_range
    # mais folga no topo para acomodar as anotações (ex.: pico 200)
    pad_top = 0.22 * y_range
    ax.set_ylim(y_min - pad_bottom, y_max + pad_top)

    # -------------------- Peak labels (estilo do exemplo) --------------------
    if annotate_peaks:
        # Anotar picos da celulose I na curva superior (Syagrus) com setas
        y_range = (y_max - y_min) if y_max > y_min else 1.0
        arrow_kw = dict(arrowstyle="->", lw=0.6, color="black")

        # offsets (x,y) para não baterem entre si
        text_offsets = {
            "110": (-5.0, 0.14 * y_range),
            "200": (3.0, 0.10 * y_range),
            "004": (2.5, 0.08 * y_range),
        }

        for lbl, t in cellulose_I_targets_deg.items():
            pk = peak_near(x, sy_plot, t)
            if pk is None:
                continue
            xp, yp = pk
            dx, dy = text_offsets.get(lbl, (2.0, 0.08 * y_range))
            ha = "right" if lbl == "110" else "center"
            ax.annotate(
                lbl,
                xy=(xp, yp),
                xytext=(xp + dx, yp + dy),
                ha=ha,
                va="bottom",
                fontsize=8,
                annotation_clip=True,
                arrowprops=arrow_kw,
            )

        # Halo amorfo (região típica ~18°): seta para o “fundo” entre os picos
        am = y_at_near(x, sy_plot, amorphous_target_deg)
        if am is not None:
            xa, ya = am
            ax.annotate(
                "amorphous\ncellulose",
                xy=(xa, ya),
                xytext=(xa + 8.0, ya + 0.12 * y_range),
                ha="left",
                va="bottom",
                fontsize=8,
                annotation_clip=True,
                arrowprops=arrow_kw,
            )

    # Legenda compacta (inclui marcador de pico) — evita texto solto no gráfico
    handles = [
        Line2D([], [], color="black", lw=0.85, ls="-", label="Syagrus"),
        Line2D([], [], color="black", lw=0.85, ls="--", label="Typha"),
    ]

    leg = ax.legend(
        handles=handles,
        frameon=True,
        fancybox=False,
        edgecolor="black",
        facecolor="white",
        loc="upper right",
        fontsize=8,
        handlelength=1.6,
        borderpad=0.25,
        labelspacing=0.25,
        handletextpad=0.5,
    )
    leg.get_frame().set_linewidth(0.8)
    ax.grid(False)

    fig.tight_layout(pad=0.5)

    # -------------------- Save (PNG + vetoriais) --------------------
    out_png = out_dir / "fig_drx_final.png"
    out_pdf = out_dir / "fig_drx_final.pdf"
    out_svg = out_dir / "fig_drx_final.svg"

    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")  # PDF vetorial
    fig.savefig(out_svg, bbox_inches="tight")  # SVG vetorial (ótimo p/ Illustrator)

    print("Salvo:", out_png)
    print("Salvo:", out_pdf)
    print("Salvo:", out_svg)

    plt.close(fig)

if __name__ == "__main__":
    main()
