# Projeto_AeC — Classificador de Categorias de Notícias

Serviço que classifica notícias por categoria a partir do **título**, usando o acervo da
Folha de S.Paulo (2015–2017, ~167 mil registros). Ver escopo e decisões em [`PRD.md`](PRD.md).

## Setup do ambiente

Pré-requisito: Python 3.10.

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate         # Linux/macOS

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Baixar o modelo de português do spaCy
#    (não vem no requirements.txt — é distribuído à parte pelo spaCy)
python -m spacy download pt_core_news_sm
```

> O notebook `eda.ipynb` já tem um fallback que baixa o modelo automaticamente na primeira
> execução, então o passo 3 é opcional se você for rodar apenas o notebook.

## Dados

O dataset (`data/articles.csv`, ~480 MB) **não está no repositório** por causa do tamanho.
Veja [`data/README.md`](data/README.md) para saber onde obtê-lo. Coloque o arquivo em
`data/articles.csv` antes de executar o notebook.

## Estrutura

```
Projeto_AeC/
├── data/               # dataset (ignorado pelo git, exceto README/.gitkeep)
├── eda.ipynb           # análise exploratória + pré-processamento
├── PRD.md              # documento de requisitos do produto
├── requirements.txt    # dependências Python
└── .gitignore
```
