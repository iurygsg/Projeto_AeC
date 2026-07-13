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

## Como usar

O projeto tem duas fases (PRD, seção 8): **treino** (offline) e **serviço** (online).

### 1. Treinar o modelo

Gera o artefato `modelo/pipeline.joblib` a partir de `data/articles.csv`:

```bash
python -m src.train
```

### 2. Subir a API

Carrega o pipeline treinado e expõe o endpoint de classificação:

```bash
uvicorn src.api:app --reload
```

- Documentação interativa: http://127.0.0.1:8000/docs
- Exemplo de requisição:

```bash
curl -X POST http://127.0.0.1:8000/classificar \
  -H "Content-Type: application/json" \
  -d "{\"titulo\": \"Seleção brasileira vence e se classifica para a final da Copa\"}"
```

Resposta: `{"categoria_prevista": "esporte", "confianca": 0.87}`

## Estrutura

```
Projeto_AeC/
├── data/               # dataset (ignorado pelo git, exceto README/.gitkeep)
├── src/
│   ├── preprocessing.py # Preprocessador (spaCy) — compartilhado por treino e API
│   ├── train.py         # Fase 1: treina e serializa o pipeline
│   └── api.py           # Fase 2: API FastAPI (POST /classificar)
├── modelo/             # pipeline.joblib (ignorado pelo git; gerado pelo treino)
├── eda.ipynb           # análise exploratória + narrativa das decisões
├── PRD.md              # documento de requisitos do produto
├── requirements.txt    # dependências Python
└── .gitignore
```
