# -*- coding: utf-8 -*-
"""
Análise de dados de vendas — Trabalho de Probabilidade e Estatística
Grupo 06
"""
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

# Garante saída em UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------- Configuração visual ----------------
COR_PRIMARIA = "#1F3864"
COR_DESTAQUE = "#E63946"
PALETA_AZUL = "Blues_d"

sns.set_style("white")
plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 100,
    "savefig.dpi": 120,
    "savefig.bbox": "tight",
})

CAMINHO = r"C:\Users\Ryan\AppData\Local\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState\sessions\C219C86838064B5C439E8517AE5F1954D4500774\transfers\2026-20\Grupo_06_Dados_Vendas.xlsx"

FAIXAS_IDADE = [18, 25, 35, 45, 55, 75]
ROTULOS_IDADE = ["18–25", "26–35", "36–45", "46–55", "56–75"]

FAIXAS_ALTURA = [0, 1.60, 1.70, 1.80, 3.00]
ROTULOS_ALTURA = ["Até 1,60m", "1,61–1,70m", "1,71–1,80m", "Acima de 1,80m"]


# ---------------- Utilidades ----------------
def fmt_reais_k(x, _pos=None):
    if x >= 1000:
        return f"R$ {x/1000:.0f}k"
    return f"R$ {x:.0f}"


def cabecalho(titulo):
    print("\n" + "=" * 78)
    print(titulo)
    print("=" * 78)


def estilizar_eixo(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.3)


# ---------------- 1) Carregamento ----------------
def carregar_dados(caminho=CAMINHO):
    df = pd.read_excel(caminho, sheet_name="Dados")
    df.columns = [c.strip() for c in df.columns]
    # Tipos numéricos
    for c in ["Quantidade", "Valor Unitário (R$)", "Valor Total (R$)",
              "Idade do Cliente", "Altura do Cliente (m)"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Valor Total (R$)", "Idade do Cliente",
                           "Altura do Cliente (m)"]).reset_index(drop=True)

    df["Faixa Etária"] = pd.cut(df["Idade do Cliente"],
                                bins=FAIXAS_IDADE,
                                labels=ROTULOS_IDADE,
                                include_lowest=True, right=True)
    df["Faixa de Altura"] = pd.cut(df["Altura do Cliente (m)"],
                                   bins=FAIXAS_ALTURA,
                                   labels=ROTULOS_ALTURA,
                                   include_lowest=True, right=True)
    return df


# ---------------- 2) Estatística descritiva ----------------
def estatistica_descritiva(df):
    cabecalho("1) ESTATÍSTICA DESCRITIVA")
    cols = ["Quantidade", "Valor Unitário (R$)", "Valor Total (R$)",
            "Idade do Cliente", "Altura do Cliente (m)"]
    linhas = {}
    for c in cols:
        s = df[c].dropna()
        moda = s.mode()
        linhas[c] = {
            "Média": s.mean(),
            "Mediana": s.median(),
            "Moda": moda.iloc[0] if not moda.empty else np.nan,
            "Desv. Padrão (s)": s.std(ddof=1),
            "Variância (s²)": s.var(ddof=1),
            "CV (%)": (s.std(ddof=1) / s.mean()) * 100 if s.mean() else np.nan,
            "Q1": s.quantile(0.25),
            "Q2": s.quantile(0.50),
            "Q3": s.quantile(0.75),
            "IQR": s.quantile(0.75) - s.quantile(0.25),
            "Mínimo": s.min(),
            "Máximo": s.max(),
            "Assimetria": s.skew(),
            "Curtose": s.kurt(),
        }
    tabela = pd.DataFrame(linhas).round(3)
    with pd.option_context("display.float_format", "{:,.3f}".format,
                            "display.width", 200,
                            "display.max_columns", None):
        print(tabela)
    return tabela


# ---------------- 3) Gráficos ----------------
def gerar_graficos(df):
    cabecalho("2) GRÁFICOS")
    paleta_sexo = {"Masculino": COR_PRIMARIA, "Feminino": COR_DESTAQUE}

    # 2.1 Boxplots por sexo
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    variaveis = [("Valor Total (R$)", "Valor Total por Sexo"),
                 ("Idade do Cliente", "Idade por Sexo"),
                 ("Altura do Cliente (m)", "Altura por Sexo")]
    for ax, (col, titulo) in zip(axes, variaveis):
        sns.boxplot(data=df, x="Sexo", y=col, ax=ax,
                    palette=paleta_sexo, hue="Sexo", legend=False)
        ax.set_title(titulo, fontweight="bold", color=COR_PRIMARIA)
        ax.set_xlabel("")
        estilizar_eixo(ax)
        if "R$" in col:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_reais_k))
    plt.tight_layout()
    plt.savefig("01_boxplot_por_sexo.png")
    plt.show()

    # 2.2 Histograma Idade com média/mediana
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["Idade do Cliente"], bins=15, color=COR_PRIMARIA,
            edgecolor="white", alpha=0.85)
    media_i = df["Idade do Cliente"].mean()
    mediana_i = df["Idade do Cliente"].median()
    ax.axvline(media_i, color=COR_DESTAQUE, linewidth=2,
               label=f"Média = {media_i:.1f}")
    ax.axvline(mediana_i, color="black", linestyle="--", linewidth=2,
               label=f"Mediana = {mediana_i:.1f}")
    ax.set_title("Distribuição da Idade do Cliente",
                 fontweight="bold", color=COR_PRIMARIA)
    ax.set_xlabel("Idade")
    ax.set_ylabel("Frequência")
    ax.legend()
    estilizar_eixo(ax)
    plt.tight_layout()
    plt.savefig("02_hist_idade.png")
    plt.show()

    # 2.3 Histograma Valor Total
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["Valor Total (R$)"], bins=20, color=COR_PRIMARIA,
            edgecolor="white", alpha=0.85)
    media_v = df["Valor Total (R$)"].mean()
    ax.axvline(media_v, color=COR_DESTAQUE, linewidth=2,
               label=f"Média = R$ {media_v:,.0f}")
    ax.set_title("Distribuição do Valor Total por Venda",
                 fontweight="bold", color=COR_PRIMARIA)
    ax.set_xlabel("Valor Total (R$)")
    ax.set_ylabel("Frequência")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_reais_k))
    ax.legend()
    estilizar_eixo(ax)
    plt.tight_layout()
    plt.savefig("03_hist_valor_total.png")
    plt.show()

    # 2.4 Top 5 vendedores — barras horizontais
    top5 = (df.groupby("Nome do Vendedor")["Valor Total (R$)"]
              .sum().sort_values(ascending=True).tail(5))
    fig, ax = plt.subplots(figsize=(10, 5))
    cores = sns.color_palette(PALETA_AZUL, n_colors=len(top5))
    barras = ax.barh(top5.index, top5.values, color=cores, edgecolor="white")
    for b, v in zip(barras, top5.values):
        ax.text(v, b.get_y() + b.get_height() / 2,
                f"  R$ {v:,.0f}", va="center", fontweight="bold",
                color=COR_PRIMARIA)
    ax.set_title("Top 5 Vendedores por Valor Total",
                 fontweight="bold", color=COR_PRIMARIA)
    ax.set_xlabel("Valor Total acumulado")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_reais_k))
    estilizar_eixo(ax)
    plt.tight_layout()
    plt.savefig("04_top5_vendedores.png")
    plt.show()

    # 2.5 Pizza — vendas por produto
    vendas_prod = df.groupby("Produto")["Valor Total (R$)"].sum().sort_values(ascending=False)
    cores_pizza = sns.color_palette(PALETA_AZUL, n_colors=len(vendas_prod))
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(vendas_prod.values, labels=vendas_prod.index,
           autopct="%1.1f%%", colors=cores_pizza,
           wedgeprops={"edgecolor": "white", "linewidth": 1.5},
           textprops={"fontsize": 10})
    ax.set_title("Distribuição de Vendas por Produto (Valor Total)",
                 fontweight="bold", color=COR_PRIMARIA)
    plt.tight_layout()
    plt.savefig("05_pizza_produtos.png")
    plt.show()

    # 2.6 Dispersão Idade x Valor Total
    fig, ax = plt.subplots(figsize=(10, 6))
    for sexo, cor in paleta_sexo.items():
        sub = df[df["Sexo"] == sexo]
        ax.scatter(sub["Idade do Cliente"], sub["Valor Total (R$)"],
                   color=cor, alpha=0.6, edgecolor="white",
                   s=50, label=sexo)
    x = df["Idade do Cliente"].values
    y = df["Valor Total (R$)"].values
    coef = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, np.polyval(coef, xs), color="black",
            linestyle="--", linewidth=2,
            label=f"Tendência (r = {r:.3f})")
    ax.set_title("Idade × Valor Total por Sexo",
                 fontweight="bold", color=COR_PRIMARIA)
    ax.set_xlabel("Idade")
    ax.set_ylabel("Valor Total (R$)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_reais_k))
    ax.legend()
    estilizar_eixo(ax)
    plt.tight_layout()
    plt.savefig("06_dispersao_idade_valor.png")
    plt.show()


# ---------------- 4) Análises estratégicas ----------------
def analises_estrategicas(df):
    cabecalho("3) ANÁLISES ESTRATÉGICAS")
    total_geral = df["Valor Total (R$)"].sum()

    # 3.1 Top 5 vendedores com % participação
    top5_vend = (df.groupby("Nome do Vendedor")["Valor Total (R$)"]
                   .sum().sort_values(ascending=False).head(5).to_frame())
    top5_vend["% Participação"] = (top5_vend["Valor Total (R$)"] /
                                    total_geral) * 100
    print("\n>> Top 5 vendedores por Valor Total")
    print(top5_vend.round(2).to_string())

    # 3.2 Produtos por quantidade e valor
    prod = df.groupby("Produto").agg(
        Quantidade=("Quantidade", "sum"),
        Valor_Total=("Valor Total (R$)", "sum"),
    ).sort_values("Valor_Total", ascending=False)
    prod["% Quantidade"] = prod["Quantidade"] / prod["Quantidade"].sum() * 100
    prod["% Valor"] = prod["Valor_Total"] / prod["Valor_Total"].sum() * 100
    print("\n>> Produtos mais vendidos (quantidade e valor)")
    print(prod.round(2).to_string())

    # 3.3 Valor por faixa etária
    fe = df.groupby("Faixa Etária", observed=True)["Valor Total (R$)"].agg(
        ["count", "sum", "mean"]).round(2)
    fe.columns = ["Nº Vendas", "Valor Total", "Ticket Médio"]
    print("\n>> Valor Total por Faixa Etária")
    print(fe.to_string())

    # 3.4 Produtos preferidos por sexo
    pivot_sexo = df.pivot_table(values="Valor Total (R$)",
                                index="Sexo", columns="Produto",
                                aggfunc="sum", fill_value=0).round(2)
    print("\n>> Produtos preferidos por Sexo (Valor Total)")
    print(pivot_sexo.to_string())

    # 3.5 Vendedor: média/total + comparação à média geral
    media_geral_venda = df["Valor Total (R$)"].mean()
    vend = df.groupby("Nome do Vendedor")["Valor Total (R$)"].agg(
        ["mean", "sum", "count"]).round(2)
    vend.columns = ["Ticket Médio", "Valor Total", "Nº Vendas"]
    vend["Posição vs Média Geral"] = np.where(
        vend["Ticket Médio"] >= media_geral_venda, "Acima", "Abaixo")
    vend = vend.sort_values("Valor Total", ascending=False)
    print(f"\n>> Vendedores — média geral por venda: R$ {media_geral_venda:,.2f}")
    print(vend.to_string())


# ---------------- 5) Análises complementares ----------------
def analises_complementares(df):
    cabecalho("4) ANÁLISES COMPLEMENTARES")

    # 4.1 Heatmap vendedor x produto (valor médio)
    heat = df.pivot_table(values="Valor Total (R$)",
                          index="Nome do Vendedor",
                          columns="Produto",
                          aggfunc="mean", fill_value=0)
    fig, ax = plt.subplots(figsize=(11, max(5, 0.45 * len(heat))))
    sns.heatmap(heat, cmap="Blues", annot=True, fmt=".0f",
                linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Valor médio (R$)"}, ax=ax)
    ax.set_title("Heatmap — Vendedor × Produto (Valor Total médio)",
                 fontweight="bold", color=COR_PRIMARIA)
    plt.tight_layout()
    plt.savefig("07_heatmap_vendedor_produto.png")
    plt.show()

    # 4.2 Pareto — produtos que acumulam 80% das vendas
    pareto = (df.groupby("Produto")["Valor Total (R$)"].sum()
                .sort_values(ascending=False).to_frame())
    pareto["% Acumulado"] = pareto["Valor Total (R$)"].cumsum() / pareto["Valor Total (R$)"].sum() * 100
    pareto["Compõe 80%?"] = np.where(pareto["% Acumulado"] <=
                                      80 + 1e-9, "Sim", "Não")
    # Marca também o primeiro que ultrapassa 80% como "Sim" (fronteira)
    if (pareto["Compõe 80%?"] == "Não").any():
        idx_primeiro_nao = pareto.index[pareto["Compõe 80%?"] == "Não"][0]
        if pareto.loc[idx_primeiro_nao, "% Acumulado"] > 80 \
                and (pareto["Compõe 80%?"] == "Sim").sum() == 0 \
                or (pareto.loc[:idx_primeiro_nao, "% Acumulado"].iloc[-2] < 80
                    if len(pareto) > 1 else False):
            pareto.loc[idx_primeiro_nao, "Compõe 80%?"] = "Sim (fronteira)"
    print("\n>> Análise de Pareto — Produtos × Valor Total")
    print(pareto.round(2).to_string())
    n80 = (pareto["Compõe 80%?"].isin(["Sim", "Sim (fronteira)"])).sum()
    print(f"\n   → {n80} produto(s) concentram aproximadamente 80% das vendas.")

    # Gráfico de Pareto
    fig, ax1 = plt.subplots(figsize=(11, 5))
    cores = sns.color_palette(PALETA_AZUL, n_colors=len(pareto))
    ax1.bar(pareto.index, pareto["Valor Total (R$)"],
            color=cores, edgecolor="white")
    ax1.set_ylabel("Valor Total (R$)", color=COR_PRIMARIA)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_reais_k))
    ax1.tick_params(axis="x", rotation=30)
    estilizar_eixo(ax1)

    ax2 = ax1.twinx()
    ax2.plot(pareto.index, pareto["% Acumulado"],
             color=COR_DESTAQUE, marker="o", linewidth=2)
    ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
    ax2.set_ylabel("% Acumulado", color=COR_DESTAQUE)
    ax2.set_ylim(0, 110)
    ax2.spines["top"].set_visible(False)
    ax1.set_title("Análise de Pareto — Produtos",
                  fontweight="bold", color=COR_PRIMARIA)
    plt.tight_layout()
    plt.savefig("08_pareto_produtos.png")
    plt.show()

    # 4.3 Teste t bicaudal — Valor Total por sexo
    g_m = df.loc[df["Sexo"] == "Masculino", "Valor Total (R$)"].dropna()
    g_f = df.loc[df["Sexo"] == "Feminino", "Valor Total (R$)"].dropna()
    t_stat, p_valor = stats.ttest_ind(g_m, g_f, equal_var=False)
    resumo = pd.DataFrame({
        "n":       [len(g_m), len(g_f)],
        "Média":   [g_m.mean(), g_f.mean()],
        "Desv.Pad.": [g_m.std(ddof=1), g_f.std(ddof=1)],
    }, index=["Masculino", "Feminino"]).round(2)
    print("\n>> Teste t bicaudal — Valor Total ~ Sexo (α = 0,05)")
    print(resumo.to_string())
    print(f"\n   Estatística t = {t_stat:.4f}")
    print(f"   p-valor       = {p_valor:.4f}")
    if p_valor < 0.05:
        print("   Conclusão: rejeita-se H0 → há diferença significativa entre as médias.")
    else:
        print("   Conclusão: não se rejeita H0 → não há evidência de diferença entre as médias.")

    # 4.4 Valor Total por faixa de altura × produto
    tabela_alt = df.pivot_table(values="Valor Total (R$)",
                                index="Faixa de Altura",
                                columns="Produto",
                                aggfunc="sum", fill_value=0,
                                observed=True).round(2)
    tabela_alt["TOTAL"] = tabela_alt.sum(axis=1)
    print("\n>> Valor Total por Faixa de Altura × Produto")
    print(tabela_alt.to_string())


# ---------------- main ----------------
def main():
    df = carregar_dados()
    print(f"Registros carregados: {len(df)}")
    estatistica_descritiva(df)
    gerar_graficos(df)
    analises_estrategicas(df)
    analises_complementares(df)
    cabecalho("FIM DA ANÁLISE")


if __name__ == "__main__":
    main()
