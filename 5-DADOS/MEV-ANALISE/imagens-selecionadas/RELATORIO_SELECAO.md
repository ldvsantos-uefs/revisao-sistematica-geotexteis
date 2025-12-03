# Relatório de Seleção de Imagens MEV

**Data**: 1764790192.595333

**Formato**: PNG (imagens processadas)

## Imagens Selecionadas

### TABOA (*Typha domingensis*)

| Tratamento | Período | Arquivo Original |
|------------|---------|------------------|
| Sem Tratamento | 30 dias | `30d_1.png` |
| Sem Tratamento | 180 dias | `180d_1.png` |
| Duas Camadas | 30 dias | `30d_1.png` |
| Duas Camadas | 180 dias | `180d_1.png` |

### OURICURI (*Syagrus coronata*)

| Tratamento | Período | Arquivo Original |
|------------|---------|------------------|
| Sem Tratamento | 30 dias | `30d_1.png` |
| Sem Tratamento | 180 dias | `180d_1.png` |
| Duas Camadas | 30 dias | `30d_1.png` |
| Duas Camadas | 180 dias | `180d_1.png` |

## Estrutura de Saída

```
imagens-selecionadas/
├── taboa/
│   ├── taboa_ST_30d.png     (Sem Tratamento, 30 dias)
│   ├── taboa_ST_180d.png    (Sem Tratamento, 180 dias)
│   ├── taboa_DC_30d.png     (Dupla Camada, 30 dias)
│   └── taboa_DC_180d.png    (Dupla Camada, 180 dias)
├── ouricuri/
│   ├── ouricuri_ST_30d.png
│   ├── ouricuri_ST_180d.png
│   ├── ouricuri_DC_30d.png
│   └── ouricuri_DC_180d.png
└── RELATORIO_SELECAO.md
```

## Próximos Passos

1. Executar `analise_mev_fraturas_danos.py` nas imagens selecionadas
2. Gerar figura comparativa para o manuscrito
3. Atualizar Tabela 2 com dados morfométricos
