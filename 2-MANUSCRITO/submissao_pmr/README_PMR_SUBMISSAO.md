# Public Management Review (Taylor & Francis) — pacote de submissão

Este diretório reúne os arquivos mínimos para uma submissão inicial à **Public Management Review (PMR)**.

## Regras-chave (PMR)

- Manuscrito **em inglês**.
- **Abstract em inglês (não estruturado) com ~150 palavras**.
- **2 a 5 keywords**.
- Revisão **double-anonymous**: normalmente há **um arquivo “anonymous manuscript”** e **uma “title page”** separada com autores/afiliação.
- Limite de submissão inicial: **até 8.000 palavras** (referências e apêndices excluídos; tabelas e figuras contam como 280 palavras cada, segundo as instruções).

## Arquivos aqui

- `manuscript_anonymous_en.docx`: manuscrito anônimo (arquivo principal para submissão).
- `title_page.md`: dados de autores, afiliação e autor correspondente (preencher campos).
- `cover_letter_en.md`: carta de submissão (editar campos entre colchetes).
- `statements.md`: funding, disclosure e data availability (editar conforme o caso).
- `biographical_notes.md`: notas biográficas (até ~200 palavras por autor, como regra prática).

Arquivos gerados (DOCX):

Por padrão, são gerados em `_build/`:

- `_build/title_page.docx`
- `_build/cover_letter_en.docx`
- `_build/statements.docx`
- `_build/biographical_notes.docx`

## Como gerar DOCX (recomendado)

Os arquivos `.md` deste diretório podem ser convertidos para `.docx` via o script do projeto `2 - MANUSCRITO/gerar-docx.py`.

Para facilitar, use o gerador do pacote PMR (gera todos os DOCX de uma vez):

`python "2 - MANUSCRITO/submissao_pmr/gerar_pacote_docx.py"`

Isso gera/atualiza:

- `_build/title_page.docx`
- `_build/cover_letter_en.docx`
- `_build/statements.docx`
- `_build/biographical_notes.docx`

E também (do diretório `2 - MANUSCRITO/`):

- `_build/artigo_cref_2.docx`
- `_build/apendice_tabelas_informacionais.docx`

Manuscrito anônimo (opcional): como o manuscrito principal pode estar em outro arquivo (e precisa estar em inglês e anonimizado), ele **só é gerado** se você informar um Markdown de entrada:

`python "2 - MANUSCRITO/submissao_pmr/gerar_pacote_docx.py" --manuscript-input "CAMINHO/DO/SEU_MANUSCRITO_ANONIMO_EN.md"`

Se você quiser sobrescrever o diretório de saída, use:

`python "2 - MANUSCRITO/submissao_pmr/gerar_pacote_docx.py" --out-dir "2 - MANUSCRITO/submissao_pmr/_build"`
