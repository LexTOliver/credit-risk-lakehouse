# AGENTS.md

## Visão do projeto

- Laboratório de engenharia de dados e MLOps para risco de crédito com o
  dataset Home Credit Default Risk.
- O objetivo é construir um Lakehouse no Databricks: CSVs de origem → Bronze
  (Delta bruto) → Silver (tipagem e qualidade) → Gold (atributos por
  `SK_ID_CURR`) → treinamento, MLflow e scoring em lote.
- O repositório não implementa uma decisão real de concessão de crédito nem
  reproduz toda a competição.

## Stack e ambiente

- Use Python 3.11 e `uv`; a versão está em `.python-version` e as dependências
  estão em `pyproject.toml`/`uv.lock`.
- Instale o ambiente com `uv sync`.
- `kagglehub` é dependência de runtime; PySpark é dependência de desenvolvimento
  para verificações locais. Spark, Delta, Unity Catalog e MLflow são executados
  no ambiente Databricks.
- Os dados completos da competição não são versionados. Obtenha-os apenas
  após aceitar as regras do Kaggle; não adicione CSVs nem credenciais ao Git.

## Comandos conhecidos

```bash
uv sync
uv run python -c "import credit_risk_lakehouse; print('Ambiente pronto')"
uv run ruff check src
uv run pytest
uv run mypy src
```

- `pytest` procura testes em `tests/`, mas não há testes versionados no estado
  atual.
- Ruff usa linha máxima de 88 caracteres e seleciona `E`, `F`, `I`, `B` e
  `UP`. Mypy é estrito para o pacote `credit_risk_lakehouse`.
- Não há comando de servidor, build de aplicação, CI, Docker ou migrações
  versionados neste momento.

## Estrutura e dados

- `notebooks/01_ingest_bronze.ipynb` e
  `src/credit_risk_lakehouse/jobs/ingest_bronze.py` implementam a Bronze. Eles
  criam o catálogo `credit_risk_lakehouse`, os schemas `landing` e `bronze`, e
  o Volume `landing.home_credit_default_risk` no Databricks.
- O job oferece `bootstrap` (provisiona, baixa e recria a Bronze) e `rebuild`
  (valida os arquivos existentes no landing e recria a Bronze).
- A ingestão usa `kagglehub` para baixar `application_train.csv`, `bureau.csv`
  e `previous_application.csv`, e grava tabelas Delta no schema `bronze`.
- Bronze preserva os campos de origem como strings e adiciona proveniência
  técnica (`_source_path`, `_ingested_at`). Tipagem, valores sentinela,
  deduplicação de negócio e regras de qualidade pertencem à Silver.
- A Silver é a etapa atual: tipagem, valores sentinela, qualidade e
  deduplicação de negócio ainda não foram implementadas.
- `docs/PLAN.md` descreve a arquitetura e o escopo futuros.

## Regras para mudanças

- Leia `README.md`, `docs/PLAN.md` e `docs/adendo_credit_risk_estatistica.md`
  antes de alterar pipeline, modelo ou métrica.
- Preserve a granularidade: a Gold planejada deve ter uma linha por
  `SK_ID_CURR`; históricos devem ser agregados sem introduzir leakage.
- Em modelagem, ajuste imputação, encoding, seleção de atributos e calibração
  somente com dados de treino/validação, mantendo o teste final isolado.
- Documente limites do dataset observacional e a ausência de backtest temporal.
- Antes de editar, confira `git status --short`. Preserve alterações não
  relacionadas na worktree e não as use como base para mudanças sem instrução
  explícita.
- Adicione testes ao introduzir lógica reutilizável e execute as verificações
  relevantes. Não instale ou atualize dependências sem aprovação.

## Segurança e operação

- Não registre tokens do Kaggle, dados brutos, resultados de produção ou
  credenciais Databricks. Mantenha segredos fora de notebooks e do repositório.
- Executar o notebook ou job pode criar ou substituir tabelas Delta no catálogo
  Databricks e requer acesso ao Kaggle e ao workspace. O job Serverless recebe
  a credencial da API Kaggle por configuração externa; não inclua segredos no
  código. Confirme o catálogo e o Volume alvo antes de rodá-lo em ambiente
  compartilhado.
