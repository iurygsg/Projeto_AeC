# Testes do Preprocessador (spaCy) — o elo compartilhado entre treino e API.
#
# Como o Preprocessador é usado igual nas duas fases, garantir seu comportamento aqui
# protege contra o descasamento treino/serviço (train/serve skew).

from __future__ import annotations

import pytest

from src.preprocessing import Preprocessador


# O modelo spaCy é caro de carregar; instancia uma única vez para todos os testes.
@pytest.fixture(scope="module")
def prep() -> Preprocessador:
    return Preprocessador()


def test_remove_stopwords_e_pontuacao(prep: Preprocessador) -> None:
    # Stopwords ('a', 'de', 'para') e pontuação não devem sobrar no texto limpo.
    saida = prep.transformar_um("A vitória do time de futebol foi importante!")
    tokens = saida.split()
    assert "a" not in tokens
    assert "de" not in tokens
    assert "!" not in saida


def test_saida_em_minusculas(prep: Preprocessador) -> None:
    # O lema é sempre retornado em minúsculas, mesmo para nomes próprios.
    saida = prep.transformar_um("Brasil vence Argentina")
    assert saida == saida.lower()


def test_descarta_numeros(prep: Preprocessador) -> None:
    # Tokens não-alfabéticos (números) são descartados.
    saida = prep.transformar_um("Empresa cresce 25% em 2017")
    assert "25" not in saida
    assert "2017" not in saida


def test_titulo_vazio_levanta_erro(prep: Preprocessador) -> None:
    # Título vazio ou só com espaços não é uma entrada válida.
    with pytest.raises(ValueError):
        prep.transformar_um("   ")


def test_transformar_em_lote_preserva_ordem(prep: Preprocessador) -> None:
    # O processamento em lote mantém a ordem e o tamanho da entrada.
    entradas = ["Governo anuncia medidas", "Time vence campeonato"]
    saidas = prep.transformar(entradas)
    assert len(saidas) == len(entradas)
    assert isinstance(saidas, list)
