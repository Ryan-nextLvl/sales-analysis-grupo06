# -*- coding: utf-8 -*-
"""
Dashboard interativo — Análise de Vendas (Grupo 06)
Execução:  streamlit run dashboard.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# ---------------- Configuração ----------------
COR_PRIMARIA = "#1F3864"
COR_DESTAQUE = "#E63946"
COR_SECUNDARIA = "#457B9D"
ESCALA_AZUL = ["#DCE7F2", "#B7CCE3", "#7FA3CB", "#4A78AE", "#1F3864"]

CAMINHO_PADRAO = str(Path(__file__).parent / "Grupo_06_Dados_Vendas.xlsx")

FAIXAS_IDADE = [18, 25, 35, 45, 55, 75]
ROTULOS_IDADE = ["18–25", "26–35", "36–45", "46–55", "56–75"]
FAIXAS_ALTURA = [0, 1.60, 1.70, 1.80, 3.00]
ROTULOS_ALTURA = ["Até 1,60m", "1,61–1,70m", "1,71–1,80m", "Acima de 1,80m"]

st.set_page_config(
    page_title="Vendas — Grupo 06",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CSS ----------------
st.markdown(
    f"""
    <style>
    .main .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; }}
    h1, h2, h3 {{ color: {COR_PRIMARIA}; }}
    .kpi-card {{
        background: linear-gradient(135deg, {COR_PRIMARIA} 0%, {COR_SECUNDARIA} 100%);
        padding: 1.1rem 1.3rem;
        border-radius: 14px;
        color: white;
        box-shadow: 0 4px 14px rgba(31,56,100,0.18);
    }}
    .kpi-card .label {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.85; }}
    .kpi-card .value {{ font-size: 1.7rem; font-weight: 700; margin-top: 0.25rem; }}
    .kpi-card .sub   {{ font-size: 0.78rem; opacity: 0.85; margin-top: 0.15rem; }}
    section[data-testid="stSidebar"] {{
        background: #0E1117;
    }}
    section[data-testid="stSidebar"] * {{ color: #E6E8EE !important; }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{ color: #FFFFFF !important; }}
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
        color: #B7BDCB !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {{
        background-color: #1C2230 !important;
        color: #E6E8EE !important;
        border-color: #2A3142 !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: {COR_SECUNDARIA} !important;
        color: #FFFFFF !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 2px; }}
    .stTabs [data-baseweb="tab"] {{
        background: #EEF2F7; border-radius: 10px 10px 0 0;
        padding: 8px 18px; font-weight: 600; color: {COR_PRIMARIA};
    }}
    .stTabs [aria-selected="true"] {{ background: {COR_PRIMARIA}; color: white; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Helpers ----------------
def fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def kpi(col, label, value, sub=""):
    col.markdown(
        f'<div class="kpi-card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )

def layout_plot(fig, height=420, legend_bottom=True):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Segoe UI, sans-serif", size=13, color="#222"),
        title_font=dict(size=16, color=COR_PRIMARIA),
        title_x=0.02,
    )
    if legend_bottom:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.18, x=0))
    fig.update_xaxes(showgrid=False, linecolor="#E2E6EE")
    fig.update_yaxes(gridcolor="#EEF2F7", linecolor="#E2E6EE")
    return fig

# ---------------- Carregamento ----------------
@st.cache_data(show_spinner=False)
def carregar(caminho: str) -> pd.DataFrame:
    df = pd.read_excel(caminho, sheet_name="5_Dados Brutos", header=1)
    df.columns = [c.strip() for c in df.columns]
    for c in ["Quantidade", "Valor Unitário (R$)", "Valor Total (R$)",
              "Idade do Cliente", "Altura do Cliente (m)"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Valor Total (R$)", "Idade do Cliente",
                           "Altura do Cliente (m)"]).reset_index(drop=True)
    df["Faixa Etária"] = pd.cut(df["Idade do Cliente"], bins=FAIXAS_IDADE,
                                labels=ROTULOS_IDADE, include_lowest=True)
    df["Faixa de Altura"] = pd.cut(df["Altura do Cliente (m)"], bins=FAIXAS_ALTURA,
                                   labels=ROTULOS_ALTURA, include_lowest=True)
    return df

# ---------------- Sidebar ----------------
st.sidebar.title("📊 Vendas — Grupo 06")
st.sidebar.caption("Probabilidade e Estatística")

with st.sidebar.expander("📁 Fonte de dados", expanded=False):
    caminho = st.text_input("Caminho do Excel", value=CAMINHO_PADRAO)
    upload = st.file_uploader("ou envie um arquivo .xlsx", type=["xlsx"])

try:
    if upload is not None:
        df_base = carregar(upload)
    else:
        df_base = carregar(caminho)
except Exception as e:
    st.error(f"Não foi possível carregar o arquivo. Detalhe: {e}")
    st.stop()

st.sidebar.markdown("### 🎛️ Filtros")
sexos = sorted(df_base["Sexo"].dropna().unique())
produtos = sorted(df_base["Produto"].dropna().unique())
vendedores = sorted(df_base["Nome do Vendedor"].dropna().unique())
faixas = [r for r in ROTULOS_IDADE if r in df_base["Faixa Etária"].astype(str).unique()]

f_sexo = st.sidebar.multiselect("Sexo", sexos, default=sexos)
f_prod = st.sidebar.multiselect("Produto", produtos, default=produtos)
f_vend = st.sidebar.multiselect("Vendedor", vendedores, default=vendedores)
f_faixa = st.sidebar.multiselect("Faixa etária", faixas, default=faixas)

idade_min = int(df_base["Idade do Cliente"].min())
idade_max = int(df_base["Idade do Cliente"].max())
f_idade = st.sidebar.slider(
    "Intervalo de idade", idade_min, idade_max, (idade_min, idade_max), step=1,
)

df = df_base[
    df_base["Sexo"].isin(f_sexo)
    & df_base["Produto"].isin(f_prod)
    & df_base["Nome do Vendedor"].isin(f_vend)
    & df_base["Faixa Etária"].astype(str).isin(f_faixa)
    & df_base["Idade do Cliente"].between(f_idade[0], f_idade[1])
].copy()

if df.empty:
    st.warning("Nenhum registro com os filtros atuais.")
    st.stop()

# ---------------- Header + KPIs ----------------
st.title("Análise de Vendas — Grupo 06")
st.caption("Dashboard interativo · ajuste os filtros à esquerda para explorar o conjunto.")

c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Receita total", fmt_brl(df["Valor Total (R$)"].sum()),
    f"{len(df)} vendas")
kpi(c2, "Ticket médio", fmt_brl(df["Valor Total (R$)"].mean()),
    f"mediana {fmt_brl(df['Valor Total (R$)'].median())}")
kpi(c3, "Clientes únicos",
    f"{df['Nome do Cliente'].nunique() if 'Nome do Cliente' in df.columns else len(df)}",
    f"{df['Nome do Vendedor'].nunique()} vendedores")
kpi(c4, "Idade média", f"{df['Idade do Cliente'].mean():.1f} anos",
    f"{df['Idade do Cliente'].min():.0f}–{df['Idade do Cliente'].max():.0f}")
kpi(c5, "Itens vendidos", f"{int(df['Quantidade'].sum())}",
    f"média {df['Quantidade'].mean():.1f}/venda")

st.write("")

# ---------------- Abas ----------------
aba_visao, aba_vend, aba_prod, aba_cliente, aba_stat, aba_dados = st.tabs(
    ["🏠 Visão geral", "👤 Vendedores", "📦 Produtos", "🧑‍🤝‍🧑 Clientes", "📐 Estatística", "🗂️ Dados"]
)

# ============ Visão geral ============
with aba_visao:
    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        valor_por_prod = (df.groupby("Produto")["Valor Total (R$)"]
                          .sum().sort_values(ascending=True).reset_index())
        fig = px.bar(valor_por_prod, x="Valor Total (R$)", y="Produto",
                     orientation="h", text="Valor Total (R$)",
                     color="Valor Total (R$)", color_continuous_scale=ESCALA_AZUL,
                     title="Receita por produto")
        fig.update_traces(texttemplate="R$ %{x:,.0f}", textposition="outside",
                          cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(layout_plot(fig, height=440), use_container_width=True)
    with col_b:
        vendas_prod = df.groupby("Produto")["Valor Total (R$)"].sum().reset_index()
        fig = px.pie(vendas_prod, values="Valor Total (R$)", names="Produto",
                     hole=0.55, color_discrete_sequence=ESCALA_AZUL[::-1],
                     title="Participação por produto")
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(layout_plot(fig, height=440), use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        fig = px.histogram(df, x="Valor Total (R$)", nbins=20,
                           color_discrete_sequence=[COR_PRIMARIA],
                           title="Distribuição do valor total por venda")
        fig.add_vline(x=df["Valor Total (R$)"].mean(), line_dash="dash",
                      line_color=COR_DESTAQUE,
                      annotation_text=f"Média {fmt_brl(df['Valor Total (R$)'].mean())}",
                      annotation_position="top")
        st.plotly_chart(layout_plot(fig), use_container_width=True)
    with col_d:
        fig = px.histogram(df, x="Idade do Cliente", nbins=15,
                           color_discrete_sequence=[COR_SECUNDARIA],
                           title="Distribuição de idade dos clientes")
        fig.add_vline(x=df["Idade do Cliente"].mean(), line_dash="dash",
                      line_color=COR_DESTAQUE,
                      annotation_text=f"Média {df['Idade do Cliente'].mean():.1f}",
                      annotation_position="top")
        st.plotly_chart(layout_plot(fig), use_container_width=True)

# ============ Vendedores ============
with aba_vend:
    media_geral = df["Valor Total (R$)"].mean()
    vend = (df.groupby("Nome do Vendedor")["Valor Total (R$)"]
              .agg(Total="sum", Ticket="mean", Vendas="count")
              .sort_values("Total", ascending=False).reset_index())
    vend["Posição"] = np.where(vend["Ticket"] >= media_geral, "Acima da média", "Abaixo da média")

    col1, col2 = st.columns([1.4, 1])
    with col1:
        top = vend.head(10).sort_values("Total")
        fig = px.bar(top, x="Total", y="Nome do Vendedor", orientation="h",
                     color="Total", color_continuous_scale=ESCALA_AZUL,
                     text="Total", title="Top 10 vendedores por receita")
        fig.update_traces(texttemplate="R$ %{x:,.0f}", textposition="outside",
                          cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(layout_plot(fig, height=480), use_container_width=True)
    with col2:
        fig = px.scatter(vend, x="Vendas", y="Ticket", size="Total",
                         color="Posição",
                         color_discrete_map={"Acima da média": COR_PRIMARIA,
                                             "Abaixo da média": COR_DESTAQUE},
                         hover_name="Nome do Vendedor",
                         title="Volume × Ticket médio")
        fig.add_hline(y=media_geral, line_dash="dot", line_color="gray",
                      annotation_text="Ticket médio geral",
                      annotation_position="top right")
        st.plotly_chart(layout_plot(fig, height=480), use_container_width=True)

    heat = df.pivot_table(values="Valor Total (R$)", index="Nome do Vendedor",
                          columns="Produto", aggfunc="mean", fill_value=0)
    fig = px.imshow(heat, color_continuous_scale=ESCALA_AZUL,
                    aspect="auto", text_auto=".0f",
                    title="Heatmap — Ticket médio por Vendedor × Produto")
    st.plotly_chart(layout_plot(fig, height=max(420, 28 * len(heat))),
                    use_container_width=True)

    st.subheader("Tabela detalhada")
    vend_show = vend.rename(columns={"Total": "Receita", "Vendas": "Nº vendas"})
    vend_show["Receita"] = vend_show["Receita"].map(fmt_brl)
    vend_show["Ticket"] = vend_show["Ticket"].map(fmt_brl)
    st.dataframe(vend_show, use_container_width=True, hide_index=True)

# ============ Produtos ============
with aba_prod:
    prod = (df.groupby("Produto")
              .agg(Quantidade=("Quantidade", "sum"),
                   Receita=("Valor Total (R$)", "sum"),
                   Vendas=("Valor Total (R$)", "count"),
                   Ticket=("Valor Total (R$)", "mean"))
              .sort_values("Receita", ascending=False).reset_index())

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(prod, x="Produto", y="Quantidade",
                     color="Quantidade", color_continuous_scale=ESCALA_AZUL,
                     text="Quantidade", title="Quantidade vendida por produto")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(layout_plot(fig), use_container_width=True)
    with col2:
        fig = px.bar(prod, x="Produto", y="Ticket",
                     color="Ticket", color_continuous_scale=ESCALA_AZUL,
                     text="Ticket", title="Ticket médio por produto")
        fig.update_traces(texttemplate="R$ %{y:,.0f}", textposition="outside",
                          cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(layout_plot(fig), use_container_width=True)

    # Pareto
    pareto = prod[["Produto", "Receita"]].copy()
    pareto["% Acumulado"] = pareto["Receita"].cumsum() / pareto["Receita"].sum() * 100
    fig = go.Figure()
    fig.add_bar(x=pareto["Produto"], y=pareto["Receita"],
                marker_color=COR_PRIMARIA, name="Receita")
    fig.add_trace(go.Scatter(x=pareto["Produto"], y=pareto["% Acumulado"],
                              mode="lines+markers", name="% Acumulado",
                              yaxis="y2", line=dict(color=COR_DESTAQUE, width=3),
                              marker=dict(size=9)))
    fig.add_hline(y=80, line_dash="dot", line_color="gray", yref="y2")
    fig.update_layout(title="Análise de Pareto — Produtos",
                      yaxis=dict(title="Receita (R$)"),
                      yaxis2=dict(title="% Acumulado", overlaying="y",
                                  side="right", range=[0, 110]))
    st.plotly_chart(layout_plot(fig, height=480), use_container_width=True)

    n80 = (pareto["% Acumulado"] <= 80).sum() + 1
    st.info(f"📌 Aproximadamente **{min(n80, len(pareto))} produto(s)** "
            f"concentram cerca de 80% da receita.")

# ============ Clientes ============
with aba_cliente:
    col1, col2 = st.columns(2)
    with col1:
        paleta_sexo = {"Masculino": COR_PRIMARIA, "Feminino": COR_DESTAQUE}
        fig = px.box(df, x="Sexo", y="Valor Total (R$)", color="Sexo",
                     color_discrete_map=paleta_sexo,
                     title="Valor total por sexo", points="outliers")
        st.plotly_chart(layout_plot(fig), use_container_width=True)
    with col2:
        fig = px.box(df, x="Faixa Etária", y="Valor Total (R$)",
                     color="Faixa Etária",
                     color_discrete_sequence=ESCALA_AZUL,
                     title="Valor total por faixa etária",
                     category_orders={"Faixa Etária": ROTULOS_IDADE})
        st.plotly_chart(layout_plot(fig), use_container_width=True)

    fig = px.scatter(df, x="Idade do Cliente", y="Valor Total (R$)",
                     color="Sexo", color_discrete_map=paleta_sexo,
                     opacity=0.7, title="Idade × Valor total")
    x_arr = df["Idade do Cliente"].to_numpy()
    y_arr = df["Valor Total (R$)"].to_numpy()
    coef = np.polyfit(x_arr, y_arr, 1)
    xs = np.linspace(x_arr.min(), x_arr.max(), 80)
    fig.add_trace(go.Scatter(x=xs, y=np.polyval(coef, xs), mode="lines",
                             name="Tendência (OLS)",
                             line=dict(color="black", dash="dash", width=2)))
    r = np.corrcoef(x_arr, y_arr)[0, 1]
    g_m_s = df.loc[df["Sexo"] == "Masculino", "Valor Total (R$)"].dropna()
    g_f_s = df.loc[df["Sexo"] == "Feminino", "Valor Total (R$)"].dropna()
    if len(g_m_s) > 1 and len(g_f_s) > 1:
        t_s, p_s = stats.ttest_ind(g_m_s, g_f_s, equal_var=False)
        decisao = "rejeita H₀" if p_s < 0.05 else "não rejeita H₀"
        anot = (f"r = {r:.3f}   r² = {r**2:.3f}<br>"
                f"t-test (Valor~Sexo): t={t_s:.2f}, p={p_s:.3f}<br>"
                f"<b>{decisao}</b> (α=0,05)")
    else:
        anot = f"r = {r:.3f}"
    fig.add_annotation(xref="paper", yref="paper", x=0.99, y=0.98,
                       showarrow=False, text=anot, align="right",
                       bgcolor="rgba(255,255,255,0.9)",
                       bordercolor=COR_PRIMARIA, borderwidth=1)
    st.plotly_chart(layout_plot(fig, height=460), use_container_width=True)

    pivot_sexo = df.pivot_table(values="Valor Total (R$)", index="Sexo",
                                columns="Produto", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot_sexo, color_continuous_scale=ESCALA_AZUL,
                    text_auto=".0f", aspect="auto",
                    title="Receita por Sexo × Produto")
    st.plotly_chart(layout_plot(fig, height=360), use_container_width=True)

# ============ Estatística ============
with aba_stat:
    st.subheader("Estatística descritiva")
    cols = ["Quantidade", "Valor Unitário (R$)", "Valor Total (R$)",
            "Idade do Cliente", "Altura do Cliente (m)"]
    desc_rows = {}
    for c in cols:
        s = df[c].dropna()
        desc_rows[c] = {
            "Média": s.mean(), "Mediana": s.median(),
            "Desv. Padrão": s.std(ddof=1), "Variância": s.var(ddof=1),
            "CV (%)": s.std(ddof=1) / s.mean() * 100 if s.mean() else np.nan,
            "Q1": s.quantile(0.25), "Q3": s.quantile(0.75),
            "Mínimo": s.min(), "Máximo": s.max(),
            "Assimetria": s.skew(), "Curtose": s.kurt(),
        }
    st.dataframe(pd.DataFrame(desc_rows).round(3), use_container_width=True)

    st.subheader("Teste t — Valor Total ~ Sexo (α = 0,05)")
    g_m = df.loc[df["Sexo"] == "Masculino", "Valor Total (R$)"].dropna()
    g_f = df.loc[df["Sexo"] == "Feminino", "Valor Total (R$)"].dropna()
    if len(g_m) > 1 and len(g_f) > 1:
        t_stat, p_valor = stats.ttest_ind(g_m, g_f, equal_var=False)
        col1, col2, col3 = st.columns(3)
        col1.metric("Estatística t", f"{t_stat:.4f}")
        col2.metric("p-valor", f"{p_valor:.4f}")
        col3.metric("Conclusão",
                    "Rejeita H₀" if p_valor < 0.05 else "Não rejeita H₀",
                    "Há diferença significativa" if p_valor < 0.05
                    else "Sem evidência de diferença")
        resumo = pd.DataFrame({
            "n": [len(g_m), len(g_f)],
            "Média": [g_m.mean(), g_f.mean()],
            "Desv. Padrão": [g_m.std(ddof=1), g_f.std(ddof=1)],
        }, index=["Masculino", "Feminino"]).round(2)
        st.dataframe(resumo, use_container_width=True)
    else:
        st.info("Filtros atuais não fornecem dois grupos para o teste t.")

# ============ Dados ============
with aba_dados:
    st.subheader("Dados filtrados")
    st.caption(f"{len(df)} registros · {df.shape[1]} colunas")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button("⬇️ Baixar CSV", data=csv,
                       file_name="vendas_filtradas.csv", mime="text/csv")

st.markdown("---")
st.caption("Grupo 06 · Probabilidade e Estatística · dashboard gerado com Streamlit + Plotly")
