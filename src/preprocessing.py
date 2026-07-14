# Pré-processamento de títulos de notícias com spaCy.
#
# Este módulo é o **elo compartilhado** entre o treino (`train.py`) e a API (`api.py`).
# Manter uma única implementação garante que o texto seja tratado exatamente da mesma forma
# nas duas fases, evitando o descasamento treino/serviço (*train/serve skew*).
#
# Regras de limpeza (PRD, seção 7 — lematização sem stemming agressivo):
#   - mantém apenas tokens alfabéticos (descarta números, pontuação e símbolos);
#   - remove stopwords em português;
#   - usa o lema em minúsculas (nomes próprios são preservados como lema, sem stemming).

from __future__ import annotations

from typing import Iterable

import spacy


class Preprocessador:
    # Limpa e lematiza títulos usando um modelo de português do spaCy.
    #
    # O modelo é carregado uma única vez na construção. Parser e NER são desabilitados
    # porque, para lematizar títulos, só precisamos de tokenizer + tagger + lemmatizer.
    #
    # Args:
    #     modelo: nome do modelo spaCy a carregar (padrão: ``pt_core_news_sm``).
    #
    # Raises:
    #     OSError: se o modelo não estiver instalado e o download automático falhar.

    def __init__(self, modelo: str = "pt_core_news_sm") -> None:
        self.modelo = modelo
        try:
            self._nlp = spacy.load(modelo, disable=["parser", "ner"])
        except OSError:
            # Baixa o modelo na primeira execução, caso ainda não esteja instalado.
            from spacy.cli import download

            download(modelo)
            self._nlp = spacy.load(modelo, disable=["parser", "ner"])

    def _limpar_doc(self, doc) -> str:
        # Converte um ``Doc`` do spaCy numa string limpa (lemas separados por espaço).
        return " ".join(
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop
        )

    def transformar(self, textos: Iterable[str], batch_size: int = 1000) -> list[str]:
        # Pré-processa uma coleção de títulos em lote (eficiente para grandes volumes).
        #
        # Args:
        #     textos: iterável de títulos crus.
        #     batch_size: tamanho do lote do ``nlp.pipe``.
        #
        # Returns:
        #     Lista de títulos pré-processados, na mesma ordem da entrada.
        # Garante strings (títulos nulos viram string vazia, tratados a jusante).
        textos = [t if isinstance(t, str) else "" for t in textos]
        return [self._limpar_doc(doc) for doc in self._nlp.pipe(textos, batch_size=batch_size)]

    def transformar_um(self, texto: str) -> str:
        # Pré-processa um único título (usado pela API a cada requisição).
        #
        # Args:
        #     texto: título cru.
        #
        # Returns:
        #     Título pré-processado.
        #
        # Raises:
        #     ValueError: se ``texto`` não for uma string não vazia.
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("O título deve ser uma string não vazia.")
        return self._limpar_doc(self._nlp(texto))
