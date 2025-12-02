import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MD_FILE = BASE_DIR.parent / "2-MANUSCRITO" / "Review_Article_Draft.md"
REFERENCE_HEADER_PATTERN = re.compile(
    "^## Referências", re.IGNORECASE | re.MULTILINE
)


def remove_references_section(content: str) -> str:
    """Return content truncated before the references header, if present."""
    match = REFERENCE_HEADER_PATTERN.search(content)
    if match:
        return content[: match.start()]
    return content


def count_words_excluding_references(file_path: Path) -> int:
    """Count words in the file while ignoring the references section."""
    with Path(file_path).open("r", encoding="utf-8") as handle:
        content = handle.read()
    text_without_references = remove_references_section(content)
    return len(text_without_references.split())


def main() -> None:
    if not MD_FILE.exists():
        print(f"Arquivo nao encontrado: {MD_FILE}")
        sys.exit(1)

    try:
        word_count = count_words_excluding_references(MD_FILE)
        print(f"Contagem de palavras em {MD_FILE.name} (sem referencias):")
        print(f"Total: {word_count} palavras")
    except Exception as exc:
        print(f"Erro ao processar {MD_FILE.name}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
