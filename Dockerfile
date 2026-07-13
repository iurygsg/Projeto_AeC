# Imagem da API de classificação de notícias (Fase 2 — serviço).
# Estratégia: imagem leve que serve a API com o modelo já treinado embutido
# (pipeline.joblib, ~6,8 MB). O dataset de 480 MB NÃO entra (ver .dockerignore).

FROM python:3.10-slim

WORKDIR /app

# 1. Dependências Python — apenas o runtime da API (requirements-api.txt).
#    O requirements.txt completo (jupyter, matplotlib, seaborn...) serve para
#    rodar o projeto localmente e NÃO precisa entrar na imagem do serviço.
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# 2. Modelo de português do spaCy (não vem no requirements.txt)
RUN python -m spacy download pt_core_news_sm

# 3. Código da aplicação e artefato treinado
COPY src/ ./src/
COPY modelo/pipeline.joblib ./modelo/pipeline.joblib

# 4. Sobe a API. host 0.0.0.0 para ser acessível de fora do container.
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
