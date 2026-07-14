# Treino do classificador de categorias de notícias (Fase 1 — offline).
#
# Fluxo (PRD, seção 8): dados -> corte de categorias raras -> pré-processamento (spaCy) ->
# TF-IDF + Regressão Logística -> avaliação -> serialização do pipeline.
#
# Este script é a **fonte da verdade** do artefato ``modelo/pipeline.joblib``. Ele usa o mesmo
# ``Preprocessador`` que a API usa em produção, garantindo consistência treino/serviço.
#
# Uso:
#     python -m src.train

from __future__ import annotations

import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.preprocessing import Preprocessador

# --- Configuração ---
CAMINHO_DADOS = "data/articles.csv"
CAMINHO_MODELO = "modelo/pipeline.joblib"
MIN_EXEMPLOS = 50   # categorias com menos que isso são removidas (long-tail / artefatos)
TEST_SIZE = 0.20
SEED = 42


def carregar_e_filtrar(caminho: str = CAMINHO_DADOS, min_exemplos: int = MIN_EXEMPLOS) -> pd.DataFrame:
    # Carrega os dados e remove categorias com poucos exemplos.
    #
    # Args:
    #     caminho: caminho do CSV com as colunas ``title`` e ``category``.
    #     min_exemplos: suporte mínimo por categoria para ser mantida.
    #
    # Returns:
    #     DataFrame com as colunas ``title`` e ``category`` já filtradas.
    #
    # Raises:
    #     FileNotFoundError: se o arquivo de dados não existir.
    if not Path(caminho).exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em '{caminho}'. "
            "Baixe o articles.csv e coloque em data/ (veja data/README.md)."
        )
    df = pd.read_csv(caminho, usecols=["title", "category"])
    contagem = df["category"].value_counts()
    validas = contagem[contagem >= min_exemplos].index
    df = df[df["category"].isin(validas)].reset_index(drop=True)
    print(f"Categorias mantidas: {len(validas)} (corte >= {min_exemplos} exemplos)")
    return df


def construir_pipeline() -> Pipeline:
    # Monta o Pipeline TF-IDF + Regressão Logística (baseline).
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=5,
            max_df=0.9,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",   # neutraliza o desbalanceamento das categorias
            n_jobs=-1,
            random_state=SEED,
        )),
    ])


def main() -> None:
    t0 = time.time()

    # 1. Dados + corte de categorias raras
    df = carregar_e_filtrar()

    # 2. Pré-processamento dos títulos (spaCy) — mesmo módulo usado pela API
    print("Pré-processando títulos (pode levar alguns minutos)...")
    prep = Preprocessador()
    df["title_proc"] = prep.transformar(df["title"].tolist())

    # Remove títulos que ficaram vazios (só tinham números/stopwords/pontuação)
    antes = len(df)
    df = df[df["title_proc"].str.strip() != ""].reset_index(drop=True)
    print(f"Títulos vazios removidos: {antes - len(df)} | restantes: {len(df):,}")

    # 3. Split estratificado (antes de qualquer transformação aprendida)
    X_train, X_test, y_train, y_test = train_test_split(
        df["title_proc"], df["category"],
        test_size=TEST_SIZE, stratify=df["category"], random_state=SEED,
    )
    print(f"Treino: {len(X_train):,} | Teste: {len(X_test):,}")

    # 4. Treino do pipeline (TF-IDF ajustado só no treino)
    pipeline = construir_pipeline()
    t1 = time.time()
    pipeline.fit(X_train, y_train)
    print(f"Treino concluído em {time.time() - t1:.0f}s")

    # 5. Avaliação no teste real (não rebalanceado)
    y_pred = pipeline.predict(X_test)
    print(f"\nAcurácia    : {accuracy_score(y_test, y_pred):.4f}")
    print(f"F1 macro    : {f1_score(y_test, y_pred, average='macro'):.4f}")
    print(f"F1 weighted : {f1_score(y_test, y_pred, average='weighted'):.4f}")
    print("\n=== classification_report ===")
    print(classification_report(y_test, y_pred, zero_division=0))

    # 6. Serialização do pipeline treinado (elo Fase 1 -> Fase 2)
    Path(CAMINHO_MODELO).parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, CAMINHO_MODELO)
    print(f"Pipeline salvo em: {CAMINHO_MODELO}")
    print(f"Tempo total: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
