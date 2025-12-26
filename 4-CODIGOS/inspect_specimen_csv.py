from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pandas as pd


def main() -> None:
    zip_path = Path(
        r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\5-DADOS\NAOH\Punção-20251226T152058Z-3-001.zip"
    )

    with zipfile.ZipFile(zip_path, "r") as z:
        target = None
        for name in z.namelist():
            if name.endswith("Specimen_DadosEmBruto_1.csv") and "PUNÇÃO_EXP2_TABOA_T2_90DIAS" in name:
                target = name
                break
        if not target:
            for name in z.namelist():
                if re.search(r"Specimen_DadosEmBruto_\d+\.csv$", name):
                    target = name
                    break

        if not target:
            raise RuntimeError("No Specimen_DadosEmBruto_*.csv found in zip")

        print("Target:", target)
        raw = z.read(target)

    preview_text = raw.decode("utf-8", errors="replace")
    preview_lines = [ln for ln in preview_text.splitlines() if ln.strip()][:15]
    print("\n--- First lines (decoded) ---")
    for ln in preview_lines:
        print(ln)

    for sep in [";", ",", "\t"]:
        try:
            df = pd.read_csv(pd.io.common.BytesIO(raw), sep=sep, engine="python")
            print("\nParsed with sep=", repr(sep))
            print("Shape:", df.shape)
            print("Columns:", df.columns.tolist())
            print(df.head(5).to_string(index=False))
            break
        except Exception as exc:  # pragma: no cover
            print("sep", repr(sep), "failed:", type(exc).__name__, str(exc)[:160])


if __name__ == "__main__":
    main()
