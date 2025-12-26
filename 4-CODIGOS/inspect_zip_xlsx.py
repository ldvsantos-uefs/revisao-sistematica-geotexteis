from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd


def main() -> None:
    zip_path = Path(
        r"C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\20 - ARTIGOS\2 - ARTIGOS PUBLICADOS\ARTIGO GEOTEXTIL OURICURI\4 - DADOS\dados.zip"
    )

    if not zip_path.exists():
        raise FileNotFoundError(zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        xlsx_files = [n for n in z.namelist() if n.lower().endswith(".xlsx")]
        print("XLSX files:", xlsx_files)

        for name in xlsx_files:
            print("\n===", name, "===")
            data = z.read(name)
            bio = BytesIO(data)
            xls = pd.ExcelFile(bio)
            print("Sheets:", xls.sheet_names)

            for sheet in xls.sheet_names[:10]:
                bio.seek(0)
                df = pd.read_excel(bio, sheet_name=sheet, nrows=30)
                print("\nSheet:", sheet)
                print("Shape (preview):", df.shape)
                print("Columns:", list(df.columns))
                print(df.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
