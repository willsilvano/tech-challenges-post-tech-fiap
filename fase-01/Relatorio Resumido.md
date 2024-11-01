# Relatório de Análise e Predição dos Custos Médicos com Base em Variáveis Socioeconômicas

### Introdução
Este relatório documenta a análise, o desenvolvimento e a avaliação de modelos preditivos voltados para a estimativa de custos médicos individuais. Utilizamos um conjunto de dados de seguro de saúde que contempla características como idade, gênero, índice de massa corporal (IMC), quantidade de filhos, status de fumante e região geográfica. O objetivo foi selecionar o modelo mais preciso para prever os custos médicos, considerando uma abordagem estatística e validação cruzada.

---

### 1. Análise Exploratória dos Dados (EDA)
#### Dicionário de Dados
O conjunto de dados possui 1.338 entradas e as variáveis são descritas abaixo:
- **age**: Idade da pessoa segurada.
- **sex**: Gênero (Masculino/Feminino).
- **bmi**: Índice de Massa Corporal, uma métrica utilizada para indicar sobrepeso e obesidade.
- **children**: Número de dependentes no plano de saúde.
- **smoker**: Status de fumante (Sim/Não).
- **region**: Região de residência (northeast, northwest, southeast, southwest).
- **charges**: Custo médico individual do seguro (variável dependente).

#### Características Gerais
- **Idade**: A idade média é de aproximadamente 39 anos, variando de 18 a 64 anos, refletindo uma população adulta.
- **IMC**: Média de 30, ligeiramente acima do limite saudável, indicando uma tendência a sobrepeso ou obesidade.
- **Filhos**: A maioria das pessoas possui entre 0 e 2 filhos, indicando famílias relativamente pequenas.
- **Custo Médico**: Média de aproximadamente $13.270, com valores variando de $1.121 a $63.770, sugerindo que alguns indivíduos têm custos médicos significativamente mais altos.

#### Distribuição das Variáveis Categóricas
- **Sexo**: Proporção equilibrada entre homens e mulheres.
- **Fumante**: A maioria dos indivíduos não fuma, sendo os fumantes uma minoria significativa.
- **Região**: As regiões têm distribuições similares, com o Sudeste sendo ligeiramente predominante.

#### Insights Iniciais
- **Impacto do IMC**: Indivíduos com IMC elevado tendem a ter custos médicos mais altos.
- **Tabagismo**: Forte correlação entre fumar e altos custos médicos, indicando um fator de risco importante.
- **Região**: A localização geográfica tem um impacto menor nos custos médicos.

---

### 2. Preparação dos Dados e Transformação de Variáveis
Para permitir o treinamento dos modelos de machine learning, foi necessário transformar variáveis categóricas em variáveis numéricas:
- **Gênero (sex)**: Transformado em valores binários (0 e 1) com `LabelEncoder`.
- **Tabagismo (smoker)**: Também transformado em valores binários (0 e 1) usando `LabelEncoder`.
- **Região (region)**: Codificado com `OneHotEncoder`, resultando em quatro novas colunas, cada uma representando uma região.

Após as transformações, uma nova matriz de correlação foi gerada, oferecendo uma visão mais clara das relações entre as variáveis.

#### Análise da Matriz de Correlação
- **Tabagismo**: Forte correlação positiva com o custo médico (0.79), sugerindo que fumar é um fator decisivo para despesas elevadas.
- **Idade**: Correlação moderada (0.3), indicando que o envelhecimento tende a aumentar as despesas.
- **IMC**: Correlação positiva com os custos médicos, mas menos significativa em relação ao tabagismo.

---

### 3. Modelos Testados e Métricas de Avaliação
Cinco modelos de regressão foram selecionados e avaliados com Validação Cruzada (10-fold) para medir a precisão em relação ao custo médico. Foram utilizados três principais métricas para análise dos resultados:
  - **R²**: Indica a proporção da variabilidade dos dados que é explicada pelo modelo.
  - **RMSE (Root Mean Square Error)**: Mede o erro médio ao quadrado, indicando a dispersão dos resíduos.
  - **MAE (Mean Absolute Error)**: Erro médio absoluto entre os valores reais e previstos.

#### Resultados dos Modelos

| Modelo                     | R² Original | R² Std  | R² MM   | RMSE Original | RMSE Std  | RMSE MM   | MAE Original | MAE Std  | MAE MM   |
|----------------------------|-------------|---------|---------|---------------|-----------|-----------|--------------|----------|----------|
| Linear Regression          | 0.747      | 0.746   | 0.747   | 6084.18      | 6089.60   | 6081.98   | 4204.82      | 4214.05  | 4203.74  |
| Decision Tree Regressor    | 0.849      | 0.848   | 0.849   | 4697.13      | 4704.25   | 4697.13   | 2723.25      | 2723.25  | 2723.25  |
| Random Forest Regressor    | 0.858      | 0.858   | 0.859   | 4547.17      | 4553.85   | 4545.42   | 2552.44      | 2553.47  | 2546.10  |
| Gradient Boosting Regressor| 0.859      | 0.859   | 0.859   | 4546.72      | 4544.47   | 4543.03   | 2497.56      | 2492.27  | 2492.45  |
| KNeighbors Regressor       | 0.133      | 0.794   | 0.772   | 11269.15     | 5493.03   | 5779.49   | 7756.32      | 3351.66  | 3546.19  |

**Melhor Modelo**: `Gradient Boosting Regressor` e `Random Forest Regressor` apresentaram os melhores resultados, com R² próximos de 0.859 e erros médios mais baixos. Optou-se pelo `Random Forest Regressor` devido ao desempenho robusto e familiaridade.

---

### 4. Ajuste Fino (Fine-Tuning) do Modelo
A técnica `GridSearchCV` foi aplicada ao `RandomForestRegressor` para encontrar a melhor combinação de hiperparâmetros. Os parâmetros finais foram:
  - **max_depth**: 5
  - **max_features**: 5
  - **min_samples_leaf**: 2
  - **min_samples_split**: 10

Esses valores geraram uma melhoria nos resultados finais, com R² de 0.876, RMSE de 4383 e MAE de 2544.

---

### 5. Validação Estatística e Visualização dos Resultados
Para validar e interpretar o desempenho do modelo, algumas análises gráficas foram realizadas.

#### Gráfico de Dispersão Real vs. Predito
O gráfico de dispersão entre os valores reais e previstos mostra que a maioria dos pontos está próxima da linha de previsão perfeita, indicando previsões precisas para a maioria dos casos.

- **Erros em Valores Altos**: O modelo apresenta uma dispersão maior para valores de custo médico acima de $30.000, sugerindo dificuldades na predição de custos extremos.
- **Precisão em Valores Baixos e Médios**: Para valores de custo até $20.000, o modelo se aproxima bem dos valores reais.
- **Outliers**: Pontos distantes da linha ideal indicam casos onde o modelo subestimou ou superestimou custos médicos.

#### Distribuição dos Erros
O gráfico de distribuição dos erros destaca a concentração da maioria dos erros entre 0 e 5.000 unidades.

- **Alta Frequência de Erros Pequenos**: A maioria dos erros está concentrada em valores baixos, indicando que o modelo é preciso em muitos casos.
- **Cauda Direita (Erros Altos)**: Alguns erros elevados indicam dificuldades em prever valores extremos, possivelmente associados a fatores específicos não capturados pelo modelo.

Conclusão: A validação estatística e os gráficos sugerem que o modelo Random Forest é confiável para previsões de custo médio e baixo, mas apresenta um leve viés em casos de altos custos.

---

### 6. Conclusão e Considerações Finais
O modelo Random Forest Regressor, ajustado e validado, apresentou excelente desempenho com R² alto e erros moderados (RMSE e MAE). A análise confirmou a influência significativa do tabagismo e do IMC nos custos médicos. 

Para casos futuros, a inclusão de variáveis adicionais ou a aplicação de técnicas avançadas de engenharia de atributos poderia ajudar a melhorar a precisão para custos médicos mais elevados.

---

### 7. Implementação do Modelo em Produção
O modelo foi salvo em formato `pickle` para integração em uma aplicação Streamlit, permitindo previsões de custos médicos com base nas características dos indivíduos.

A interface permite aos usuários inserir suas informações e obter estimativas personalizadas de custos médicos.



