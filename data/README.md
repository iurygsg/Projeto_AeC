# Dados

Esta pasta contém o dataset do projeto, **não versionado no GitHub** por causa do tamanho.

## Arquivo esperado

| Arquivo | Tamanho | Descrição |
|---|---|---|
| `articles.csv` | ~480 MB | Acervo de notícias da Folha de S.Paulo (2015–2017), ~167 mil registros. Colunas: título, texto, data, categoria, subcategoria e link. |

## Como obter

O arquivo não está no repositório (ignorado via `.gitignore`). Para reproduzir o projeto,
coloque o `articles.csv` original nesta pasta:

```
data/articles.csv
```

O notebook de EDA e o pipeline de treino esperam o arquivo exatamente neste caminho relativo.
