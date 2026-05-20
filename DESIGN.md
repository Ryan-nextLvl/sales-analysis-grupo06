# Design Notes — Sales Analysis (Grupo 06)

Documento que registra as decisões de design aplicadas aos artefatos visuais do projeto: o script estático `analise_vendas.py` (PNGs para o relatório) e o dashboard interativo `dashboard.py` (Streamlit + Plotly).

---

## A. Paleta e tipografia

### Paleta corporativa unificada
Os dois artefatos (estático e interativo) compartilham as mesmas cores para manter coerência visual entre relatório e dashboard.

| Token            | Hex        | Uso                                                        |
| ---------------- | ---------- | ---------------------------------------------------------- |
| `COR_PRIMARIA`   | `#1F3864`  | Títulos, séries principais, identidade visual              |
| `COR_SECUNDARIA` | `#457B9D`  | Séries de apoio, KPI cards                                 |
| `COR_DESTAQUE`   | `#E63946`  | Médias, limites, atenção (Pareto, linha de tendência)      |
| `COR_NEUTRA`     | `#6C7A89`  | Texto secundário, grids                                    |
| `ESCALA_AZUL`    | 5 stops    | Escalas sequenciais (`#DCE7F2 → #1F3864`) para heatmap/bar |

**Por que não usar `viridis` ou `Spectral`?** São perceptualmente uniformes mas roubam protagonismo visual quando o objetivo é “relatório institucional”. A escala azul monocromática hierarquiza valores sem competir com o vermelho de destaque — que fica reservado a *uma* mensagem por gráfico (média, limite de Pareto, etc.).

### Quando usar cada tipo de colormap

| Tipo                                        | Onde aplicar                              | Exemplo no projeto                |
| ------------------------------------------- | ----------------------------------------- | --------------------------------- |
| **Categórico** (cores fixas por categoria)  | Variáveis nominais sem ordem              | Sexo (azul/vermelho), Produto     |
| **Sequencial** (claro → escuro de uma cor)  | Grandezas numéricas ordenadas (≥ 0)       | Heatmap, barras por receita       |
| **Divergente** (centro neutro, polos)       | Desvios em torno de um valor de referência (`RdBu_r`) | Não usado — sem variável centrada em zero |

### Tipografia
- `DejaVu Sans` (matplotlib) / `Segoe UI` (Streamlit) — sans-serif legível em tela e impressão.
- Hierarquia: título 13–16pt **bold** em `COR_PRIMARIA`; rótulos 11pt em `#222`; anotações estatísticas 9–10pt.
- `legend.frameon=False` para reduzir ruído visual.

---

## B. Anotações estatísticas integradas ao gráfico

Princípio: **o leitor não deveria precisar do texto para entender a mensagem do gráfico.** Por isso cada visualização foi anotada com a estatística-chave.

| Gráfico                         | Anotação aplicada                                                        |
| ------------------------------- | ------------------------------------------------------------------------ |
| 01 — Boxplots por sexo          | Resultado do teste t de Welch (t, p, decisão) abaixo do painel           |
| 02 — Histograma de idade        | Linhas de média/mediana + caixa com `n`, desvio padrão, assimetria       |
| 03 — Histograma de valor total  | Linhas média/mediana + receita total e CV%                               |
| 06 — Dispersão Idade × Valor    | Reta OLS, equação `y = ax + b`, r e r² em caixa fixa                     |
| 08 — Pareto                     | Rótulo `n produto(s) ≈ 80% da receita` + % acumulado nos pontos da linha |

**Por que caixa com borda em vez de texto solto?** Caixas com `bbox=round` e fundo branco semi-transparente impedem que a anotação se confunda com o gráfico em fundos densos (histograma, scatter com muitos pontos).

### Posicionamento de anotações
- Coordenadas em `transform=ax.transAxes` (0–1) — independentes da escala dos eixos.
- Cantos preferenciais: superior-direito para resumo; inferior-direito para fórmulas/regressão.
- Em painéis multi-gráfico, anotação centralizada **abaixo** do primeiro subplot quando o resultado se aplica a todo o painel (caso do teste t no boxplot).

---

## C. Tamanho de figura e DPI para relatório

| Uso                          | figsize         | DPI savefig | Resultado |
| ---------------------------- | --------------- | ----------- | --------- |
| Gráfico simples (1 painel)   | `(10, 5)`       | 150         | ~1500×750px — cabe em meia página A4 sem perder nitidez |
| Painel 3 subplots horizontal | `(15, 5)`       | 150         | proporção wide para slides 16:9                        |
| Heatmap denso                | `(11, 0.45·n)`  | 150         | altura proporcional ao nº de linhas (vendedores)        |
| Pareto                       | `(11, 5)`       | 150         | combina barra + linha sem espremer rótulos              |

**150 DPI** é o ponto de equilíbrio para PDF acadêmico: imprime nítido a 100% sem inflar o tamanho do arquivo (PNGs ficam entre 80–250 KB cada).

---

## D. Dashboard interativo (`dashboard.py`)

### Layout adotado

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Vendas — Grupo 06    [Sidebar: filtros]                │
├─────────────────────────────────────────────────────────────┤
│  Título · Subtítulo                                         │
│  [KPI] [KPI] [KPI] [KPI] [KPI]   ← 5 cards em gradiente    │
├─────────────────────────────────────────────────────────────┤
│  Tabs: Visão geral │ Vendedores │ Produtos │ Clientes │ ...│
├─────────────────────────────────────────────────────────────┤
│  Visão: [barra produto      ][donut produto      ]          │
│         [hist valor + média ][hist idade + média ]          │
└─────────────────────────────────────────────────────────────┘
```

### Filtros na sidebar (todos aplicados em conjunto via máscara booleana)
- Sexo (multiselect)
- Produto (multiselect)
- Vendedor (multiselect)
- Faixa etária (multiselect)
- **Intervalo de idade (slider)** — granularidade fina que complementa as faixas

### KPIs
Cards com gradiente `COR_PRIMARIA → COR_SECUNDARIA`, valor em destaque (1.7rem) e sub-rótulo discreto (0.78rem). Reúnem: receita total, ticket médio, clientes únicos, idade média, itens vendidos.

### Interatividade nativa
- Tooltips em **todos** os Plotly charts (default — sem código adicional)
- Zoom/pan em scatter e Pareto
- Botões de download CSV (aba **Dados**) com encoding `utf-8-sig` para Excel-BR

### Anotação do teste t no scatter
A aba Estatística já mostra t, p, decisão em `st.metric`. Adicionalmente, a aba Clientes exibe r, r², t, p **dentro do próprio scatter** — assim quem só olha um gráfico ainda recebe a inferência completa.

---

## E. Como rodar

```bash
# instalar dependências
pip install -r requirements.txt

# gráficos estáticos (gera 8 PNGs no diretório)
python analise_vendas.py

# dashboard interativo
streamlit run dashboard.py
```

O arquivo `Grupo_06_Dados_Vendas.xlsx` deve estar na raiz do projeto (mesmo diretório dos `.py`).

---

## F. Decisões que foram consideradas e *não* adotadas

| Ideia                                      | Por que não |
| ------------------------------------------ | ----------- |
| Migrar para Dash em vez de Streamlit       | Streamlit já entrega tudo que o briefing pede com 1/3 do código; Dash compensa quando há callbacks complexos encadeados |
| Colormap divergente no heatmap             | Não há valor central de referência (todos ≥ 0); divergente induziria leitura errada de “positivo vs negativo” |
| Animações Plotly por período               | Dataset não tem dimensão temporal (sem coluna de data) — animar produto/sexo seria artificial |
| Tema dark do Plotly                        | Reduz legibilidade em projeções de slides; tema branco é mais seguro para apresentação acadêmica |
