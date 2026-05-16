# Análise de Vendas — Grupo 06

Trabalho de Probabilidade e Estatística — análise descritiva, gráficos e testes sobre a base `Grupo_06_Dados_Vendas.xlsx` (400 vendas).

## Estrutura

- `analise_vendas.py` — script único organizado em funções:
  - `carregar_dados()` — leitura do Excel + criação das faixas etárias e de altura via `pd.cut`
  - `estatistica_descritiva()` — média, mediana, moda, desvio, variância, CV%, quartis, IQR, mín/máx, assimetria e curtose
  - `gerar_graficos()` — boxplots por sexo, histogramas, top 5 vendedores, pizza, dispersão Idade × Valor
  - `analises_estrategicas()` — top vendedores, produtos, faixa etária, sexo × produto, ranking vs média geral
  - `analises_complementares()` — heatmap, Pareto, teste t bicaudal (M vs F), tabela altura × produto
  - `main()` — orquestra tudo

## Como executar

```bash
pip install pandas numpy matplotlib seaborn scipy openpyxl
python analise_vendas.py
```

Ajuste a constante `CAMINHO` no início do script para apontar ao seu arquivo Excel.

## Saídas

Os 8 gráficos são salvos como `.png` no diretório de execução e exibidos com `plt.show()`. Todas as tabelas são impressas no terminal.

## Galeria de gráficos

### 1. Boxplots por Sexo — Valor Total, Idade e Altura
![Boxplots por sexo](01_boxplot_por_sexo.png)

### 2. Histograma da Idade do Cliente (média e mediana)
![Histograma de Idade](02_hist_idade.png)

### 3. Histograma do Valor Total por venda
![Histograma de Valor Total](03_hist_valor_total.png)

### 4. Top 5 vendedores por Valor Total
![Top 5 vendedores](04_top5_vendedores.png)

### 5. Distribuição de vendas por Produto
![Pizza de produtos](05_pizza_produtos.png)

### 6. Dispersão Idade × Valor Total por Sexo (com linha de tendência)
![Dispersão Idade x Valor](06_dispersao_idade_valor.png)

### 7. Heatmap — Vendedor × Produto (Valor Total médio)
![Heatmap Vendedor x Produto](07_heatmap_vendedor_produto.png)

### 8. Análise de Pareto — Produtos
![Pareto de Produtos](08_pareto_produtos.png)

## Principais resultados

- Vendedor líder: **Fernando Oliveira Neto** — R$ 631.008,53 (14,67% do total).
- Produto líder: **Smartphone Premium** — 44,54% do faturamento.
- Pareto: **3 produtos** (Smartphone + Notebook + Smart TV) concentram ~98,7% das vendas; 80% saem dos 2 primeiros.
- Teste t bicaudal Valor Total ~ Sexo: t = −1,77; p = 0,077 → **não se rejeita H0** (sem diferença significativa entre médias masculina e feminina ao nível α = 0,05).
