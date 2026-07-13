"""Testes de integração da API (FastAPI).

Usam o TestClient como context manager para disparar o ``lifespan`` — assim o pipeline
treinado e o Preprocessador são carregados de verdade, exercitando o mesmo caminho de
produção (carrega o modelo -> pré-processa -> classifica).

Requer que ``modelo/pipeline.joblib`` exista (rode ``python -m src.train`` antes).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api import CAMINHO_MODELO, app

# Sem o artefato treinado a API não sobe; pula os testes com uma mensagem clara.
pytestmark = pytest.mark.skipif(
    not Path(CAMINHO_MODELO).exists(),
    reason=f"Modelo '{CAMINHO_MODELO}' ausente — rode 'python -m src.train' primeiro.",
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    # O 'with' garante que o lifespan (carga do modelo) rode antes dos testes.
    with TestClient(app) as c:
        yield c


def test_health_check(client: TestClient) -> None:
    """GET / confirma que o serviço está no ar."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_classificar_titulo_valido(client: TestClient) -> None:
    """Um título claro de esporte deve retornar categoria e confiança coerentes."""
    resp = client.post(
        "/classificar",
        json={"titulo": "Seleção brasileira vence e se classifica para a final da Copa"},
    )
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["categoria_prevista"] == "esporte"
    assert 0.0 <= corpo["confianca"] <= 1.0


def test_classificar_titulo_vazio_retorna_422(client: TestClient) -> None:
    """Título vazio viola a validação do schema (min_length=1) -> 422."""
    resp = client.post("/classificar", json={"titulo": ""})
    assert resp.status_code == 422


def test_classificar_sem_termos_classificaveis_retorna_422(client: TestClient) -> None:
    """Título só com números/pontuação fica vazio após o pré-processamento -> 422."""
    resp = client.post("/classificar", json={"titulo": "123 456 !!!"})
    assert resp.status_code == 422


def test_classificar_campo_ausente_retorna_422(client: TestClient) -> None:
    """Corpo sem o campo obrigatório 'titulo' é rejeitado pela validação."""
    resp = client.post("/classificar", json={})
    assert resp.status_code == 422
