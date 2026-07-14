# PRD — Classificador de Categorias de Notícias

| Campo | Valor |
|---|---|
| Projeto | Classificador de Categorias de Notícias |
| Autor | Iury Gabriel Silva Gomes |
| Data | 2026-07-12 |
| Versão | 0.2 |
| Status | Definido — pronto para implementação |
| Prazo de entrega | 2026-07-13, 23h59 (link do repositório para `c.maria.aguiar@aec.com.br`) |

## 1. Contexto e problema

Uma empresa de comunicação jornalística precisa de um serviço que classifique automaticamente notícias por categoria a partir do seu título, apoiando o fluxo editorial de organização de conteúdo. Este documento consolida as decisões de escopo, dados e arquitetura da solução antes do início da implementação, servindo como referência única para o desenvolvimento no VS Code.

## 2. Objetivo e prioridades

Entregar um serviço de classificação de notícias funcional de ponta a ponta — da análise dos dados até a disponibilização via API — com código organizado, comentado e reprodutível.

Prioridades do projeto, em ordem:

1. Qualidade e legibilidade do código.
2. Robustez da entrega — um serviço executável que responde a requisições reais.
3. Solidez da abordagem de modelagem — técnicas, algoritmos e métricas coerentes com o problema.
4. Aproveitamento efetivo da EDA nas decisões de modelagem.

## 3. Contexto dos dados

- Fonte: acervo de notícias da Folha de S.Paulo, aproximadamente 167 mil registros (após remoção de nulos em texto), publicados entre 2015 e 2017.
- Estrutura: título, texto completo, data, categoria, subcategoria e link de origem.
- `category` reúne 46 rótulos com distribuição heterogênea — três categorias concentram a maior parte do volume, enquanto os demais rótulos aparecem com frequências bem menores. Essa característica será considerada na escolha das métricas de avaliação (seção 10).
- `subcategory` está preenchida em cerca de 18% dos registros, volume insuficiente para uso como rótulo ou feature.

## 4. Escopo

**Dentro do escopo**
- Análise exploratória (EDA) do dataset.
- Classificador de categoria a partir do título da notícia.
- API com endpoint de classificação, executável localmente como um serviço real.

**Fora do escopo (nesta versão)**
- Uso do corpo completo da notícia (`text`) como feature — decisão deliberada para manter o projeto alinhado às variáveis descritas no teste técnico e ao tempo disponível. Pode ser revisitado como evolução futura.
- Classificação por `subcategory` — descartada pela baixa cobertura de dados.
- Containerização (Docker), suíte de testes automatizados e documentação formal — descartadas nesta versão, dado o prazo de entrega; só entram se sobrar tempo real após o MVP funcional.
- Definição antecipada de estrutura de pastas/módulos — será construída de forma incremental ao longo do desenvolvimento.

## 5. Requisitos funcionais

| ID | Descrição |
|---|---|
| RF1 | O projeto deve incluir uma EDA cobrindo distribuição de categorias, características dos títulos e período do dataset. |
| RF2 | O projeto deve treinar um modelo supervisionado que preveja a categoria de uma notícia a partir do seu título. |
| RF3 | O projeto deve expor um endpoint HTTP que receba um título e retorne a categoria prevista. |

## 6. Requisitos não funcionais e restrições técnicas

- Código em Python, organizado em classes por responsabilidade (pré-processamento, vetorização/treino, API), com docstrings e comentários em português e tratamento de exceções.
- API deve subir localmente e responder de forma síncrona a requisições reais (não restrita a notebook).
- Pipeline de treino deve ser reprodutível (seed fixo).

## 7. Decisões de arquitetura e stack

- Pré-processamento de texto: spaCy (`pt_core_news`) — tokenização e lematização, sem stemming agressivo, para preservar nomes próprios (políticos, empresas, etc.).
- Vetorização: TF-IDF via `scikit-learn`.
- Modelo: Regressão Logística como baseline.
- Framework de API: FastAPI (validação via Pydantic, documentação interativa automática).
- Serialização do pipeline treinado: `joblib`.

## 8. Arquitetura em duas fases

O projeto separa claramente treino (offline) de servimento (online); a API nunca retreina, apenas carrega um artefato já pronto.

**Fase 1 — Treinamento (offline, executado uma vez):**
`Dataset (articles.csv)` → `EDA` → `Pré-processamento (spaCy + TF-IDF)` → `Treino do modelo (regressão logística)` → `Modelo serializado (pipeline.joblib)`.

**Fase 2 — Serviço de classificação (online, a cada requisição):**
`Cliente` → `API FastAPI (POST /classificar)` → `Pipeline carregado (o mesmo pipeline.joblib)` → `Resposta (categoria prevista em JSON)`.

O artefato gerado ao final da Fase 1 é o elo entre as duas fases: a API carrega esse pipeline uma única vez na inicialização, e cada requisição executa apenas a etapa de inferência.

## 9. Roadmap de implementação

1. EDA.
2. Pré-processamento dos títulos.
3. Vetorização e split treino/teste estratificado por categoria.
4. Treino e avaliação do modelo baseline.
5. Serialização do pipeline treinado.
6. Construção da API de classificação.
7. Verificação manual ponta a ponta (subir a API e testar requisições reais).
8. Extensões futuras, apenas se sobrar tempo real: Docker, testes automatizados, documentação formal.

## 10. Métricas e avaliação do modelo — em definição

- Split sugerido: 80/20, estratificado por categoria, com seed fixo para reprodutibilidade.
- Métricas candidatas: acurácia geral, F1-score macro e weighted, relatório de classificação (`classification_report`) — a escolha final considera a distribuição heterogênea das 46 categorias.
- Ponto em aberto: como tratar categorias com poucos exemplos (manter todas, agrupar ou excluir as mais raras). Decidir durante a EDA.

## 11. Contrato da API

- Endpoint: `POST /classificar`.
- Requisição: JSON `{"titulo": "<string>"}`.
- Resposta: JSON `{"categoria_prevista": "<string>"}`, com um indicador de confiança como campo opcional a avaliar durante a implementação.
- Documentação interativa disponível em `/docs` (gerada automaticamente pelo FastAPI).

## 12. Dependências e ambiente

- Ambiente de desenvolvimento: Windows; implementação em VS Code com Claude Code.
- Repositório: `Projeto_AeC` (GitHub: `iurygsg/Projeto_AeC`).
- Dataset local: `dados/articles.csv`.
- Notebook de EDA: arquivo `.ipynb` versionado no repositório, editado localmente com Claude Code (co-coding). O Google Colab é usado apenas como executor/visualizador, abrindo o mesmo arquivo direto do GitHub — não é a fonte da verdade do notebook.


