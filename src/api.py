# API de classificação de categorias de notícias (FastAPI).
#
# Serviço FastAPI que carrega o pipeline treinado uma única vez na inicialização e classifica
# o título recebido a cada requisição. O título passa pelo mesmo ``Preprocessador`` usado no
# treino antes do ``predict``, garantindo consistência treino/serviço.
#
# Contrato (PRD, seção 11):
#     POST /classificar   Body: {"titulo": "<string>"}
#     Resposta: {"categoria_prevista": "<string>", "confianca": <float|null>}
#
# Uso:
#     uvicorn src.api:app --reload
# Documentação interativa em http://127.0.0.1:8000/docs

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.preprocessing import Preprocessador

CAMINHO_MODELO = "modelo/pipeline.joblib"

# Objetos carregados na inicialização (preenchidos no lifespan).
recursos: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carrega o pipeline e o pré-processador uma vez, ao subir o serviço.
    if not Path(CAMINHO_MODELO).exists():
        raise RuntimeError(
            f"Modelo não encontrado em '{CAMINHO_MODELO}'. "
            "Rode o treino primeiro: python -m src.train"
        )
    recursos["pipeline"] = joblib.load(CAMINHO_MODELO)
    recursos["preprocessador"] = Preprocessador()
    yield
    recursos.clear()


app = FastAPI(
    title="Classificador de Categorias de Notícias",
    description="Prevê a categoria de uma notícia a partir do seu título. Siga para POST para o teste.",
    version="1.0.0",
    lifespan=lifespan,
)


class Requisicao(BaseModel):
    # Corpo da requisição de classificação.

    titulo: str = Field(..., min_length=1, description="Título da notícia a classificar.")


class Resposta(BaseModel):
    # Corpo da resposta de classificação.

    categoria_prevista: str
    confianca: float | None = Field(
        None, description="Probabilidade da categoria prevista (0 a 1), se disponível."
    )


@app.get("/")
def raiz() -> dict:
    """Endpoint de saúde: confirma que o serviço está no ar."""
    return {"status": "ok", "servico": "classificador de notícias"}


@app.post("/classificar", response_model=Resposta)
def classificar(requisicao: Requisicao) -> Resposta:
    """Classifica um título de notícia e retorna a categoria prevista.

    Envie o título no campo "string". Se o texto vier vazio ou não tiver
    nenhuma palavra significativa para o modelo analisar, a API retorna erro 422 pedindo um título válido.
    """
    pipeline = recursos["pipeline"]
    preprocessador = recursos["preprocessador"]

    titulo_proc = preprocessador.transformar_um(requisicao.titulo)
    if not titulo_proc.strip():
        raise HTTPException(
            status_code=422,
            detail="O título não contém termos classificáveis após o pré-processamento.",
        )

    categoria = pipeline.predict([titulo_proc])[0]

    # Confiança = maior probabilidade prevista (LogisticRegression expõe predict_proba).
    confianca = None
    if hasattr(pipeline, "predict_proba"):
        confianca = float(pipeline.predict_proba([titulo_proc]).max())

    return Resposta(categoria_prevista=str(categoria), confianca=confianca)
