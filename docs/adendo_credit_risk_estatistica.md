# Adendo — Rigor estatístico no Credit Risk Lakehouse

**Propósito:** complementar o planejamento existente, sem alterar arquitetura medalhão, stack ou cronograma. Implementar apenas após o pipeline principal estar funcional.

## Incrementos mínimos

1. **EDA na Silver/Gold:** distribuição e assimetria de renda, crédito e idade; quantis, valores ausentes, outliers e taxa de default por faixa. Explicar quando média e mediana divergem e por que correlação não implica causalidade.
2. **Baseline interpretável:** regressão logística regularizada, com split reproduzível e pré-processamento sem vazamento. Documentar sigmoide, log-odds, coeficientes e limitações interpretativas.
3. **Comparação justa:** confrontar baseline e modelo principal (por exemplo, XGBoost) no mesmo conjunto de teste. Reportar ROC-AUC, PR-AUC, matriz de confusão e custo de erros sob thresholds definidos.
4. **Probabilidades confiáveis:** Brier Score e curva de calibração; distinguir discriminação de calibração. Calibrar somente com dados separados do teste, se necessário.
5. **Opcional se houver tempo:** IC por bootstrap para ROC-AUC ou PR-AUC, reamostrando observações do teste; declarar limites de representatividade e independência.

## Cuidados metodológicos

- Ajustar imputação, encoding e seleção de variáveis apenas no treino.
- Evitar variáveis com informação posterior ao momento de concessão de crédito.
- Reconhecer que o dataset é observacional e não permite concluir causalidade.
- Explicar desbalanceamento e impactos de negócio, não escolher threshold apenas pelo F1.

## Entrega mínima

Uma seção de EDA, um notebook de modelagem/avaliação e uma síntese no README: **hipótese → método → resultado → limitação → decisão**. Não acrescentar modelos ou dashboards só para demonstrar volume de trabalho.

**Referências:** https://www.statlearning.com/ ; https://scikit-learn.org/stable/modules/calibration.html ; https://scikit-learn.org/stable/modules/model_evaluation.html
