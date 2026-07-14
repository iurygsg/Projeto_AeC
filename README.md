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

> **Dois arquivos de dependências, de propósito:**
> - `requirements.txt` — ambiente **completo** (notebook/EDA, treino, testes). Use este para rodar o projeto localmente.
> - `requirements-api.txt` — só o **runtime da API** (sem jupyter, matplotlib, etc.). É o que o Docker instala, mantendo a imagem enxuta.

> O notebook `eda.ipynb` já tem um fallback que baixa o modelo automaticamente na primeira
> execução, então o passo 3 é opcional se você for rodar apenas o notebook.

## Dados

O dataset (`data/articles.csv`, ~480 MB) **não está no repositório** por causa do tamanho.

- **Fonte:** [News of the Brazilian Newspaper — Folha de S.Paulo (Kaggle)](https://www.kaggle.com/datasets/marlesson/news-of-the-site-folhauol)
- Baixe o `articles.csv` e coloque em `data/articles.csv` (veja também [`data/README.md`](data/README.md)).

> Só é necessário para **treinar** o modelo ou rodar o **notebook**. Para apenas **subir a API**,
> o modelo já treinado (`modelo/pipeline.joblib`) é suficiente — o dataset não é preciso.

## Como usar

O projeto tem duas fases (PRD, seção 8): **treino** (offline) e **serviço** (online).

### 1. Treinar o modelo

Na pasta do projeto > Gera o artefato `modelo/pipeline.joblib` a partir de `data/articles.csv` com o seguinte comando:

```bash
python -m src.train
```

### 2. Subir a API

Carrega o pipeline treinado e expõe o endpoint de classificação:

```bash
uvicorn src.api:app --reload
```

- Documentação interativa: http://127.0.0.1:8000/docs
Aqui, basta ir em POST e inserir o título da notícia em "string"

- Exemplo de requisição:

```bash
curl -X POST http://127.0.0.1:8000/classificar \
  -H "Content-Type: application/json" \
  -d "{\"titulo\": \"Seleção brasileira vence e se classifica para a final da Copa\"}"
```

Resposta: `{"categoria_prevista": "esporte", "confianca": 0.82}`

### 3. (Opcional) Rodar via Docker

A imagem serve a API com o modelo já treinado embutido (`pipeline.joblib`, ~6,8 MB);
o dataset de 480 MB não entra na imagem. Requer que `modelo/pipeline.joblib` exista
(rode `python -m src.train` antes, caso ainda não tenha treinado).

```bash
docker build -t classificador-noticias .
docker run -p 8000:8000 classificador-noticias
```

Ou, com um único comando via Docker Compose (usa o `docker-compose.yml`):

```bash
docker compose up --build     # sobe a API; Ctrl+C para parar
docker compose up -d --build  # em segundo plano; `docker compose down` para parar
```

A API fica disponível em http://127.0.0.1:8000/docs, igual à execução local.

## Testes

Testes com `pytest` cobrindo o pré-processamento e a API (endpoint de classificação,
validações e casos de erro). Requer o ambiente completo (`requirements.txt`) e o modelo
treinado em `modelo/pipeline.joblib`.

```bash
pytest -v
```

## Estrutura

```
Projeto_AeC/
├── data/               # dataset (ignorado pelo git, exceto README/.gitkeep)
├── src/
│   ├── preprocessing.py # Preprocessador (spaCy) — compartilhado por treino e API
│   ├── train.py         # Fase 1: treina e serializa o pipeline
│   └── api.py           # Fase 2: API FastAPI (POST /classificar)
├── modelo/             # pipeline.joblib (ignorado pelo git; gerado pelo treino)
├── tests/              # testes pytest (pré-processamento + API)
├── eda.ipynb           # análise exploratória + narrativa das decisões
├── Dockerfile          # imagem da API (serve o modelo embutido)
├── docker-compose.yml  # sobe a API com um único comando
├── .dockerignore       # exclui data/ e .venv/ do build
├── PRD.md              # documento de requisitos do produto
├── requirements.txt     # dependências completas (local: notebook, treino, testes)
├── requirements-api.txt # dependências mínimas de runtime (usadas pelo Docker)
└── .gitignore
```
