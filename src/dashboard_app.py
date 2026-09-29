from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

REMOTE_DATASET_URL = (
    "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/"
    "dados-imersao-final.csv"
)
PLOTLY_TEMPLATE = "plotly_white"


def configure_page() -> None:
    st.set_page_config(
        page_title="Dashboard de Salários na Área de Dados",
        page_icon="📊",
        layout="wide",
    )
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #f8fafc 0%, #edf2ff 100%);
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
            div[data-testid="stSidebar"] {
                background: #0f172a;
                color: white;
            }
            .css-1d391kg, .css-1v0mbdj {
                background: #ffffff;
                border-radius: 14px;
                padding: 1rem;
                border: 1px solid #e2e8f0;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            }
            .metric-container {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 0.8rem 1rem;
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
            }
            h1, h2, h3 {
                color: #0f172a;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def resolve_data_path(csv_path: str | Path | None = None) -> Path | None:
    if csv_path is not None:
        path = Path(csv_path)
        if path.exists():
            return path

    project_root = Path(__file__).resolve().parents[1]
    local_candidates = [
        project_root / "dados-imersao-final.csv",
        project_root / "data" / "dados-imersao-final.csv",
    ]

    for candidate in local_candidates:
        if candidate.exists():
            return candidate

    return None


@st.cache_data(show_spinner="Carregando dados...")
def load_data(csv_path: str | Path | None = None) -> pd.DataFrame:
    resolved_path = resolve_data_path(csv_path)
    if resolved_path is not None:
        return pd.read_csv(resolved_path)

    return pd.read_csv(REMOTE_DATASET_URL)


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for column in ["cargo", "senioridade", "contrato", "tamanho_empresa", "remoto", "residencia", "residencia_iso3"]:
        if column in df.columns:
            df[column] = df[column].fillna("N/D").astype(str)
    if "usd" in df.columns:
        df["usd"] = pd.to_numeric(df["usd"], errors="coerce")
    return df


def apply_filters(
    df: pd.DataFrame,
    anos: Iterable[int] | None = None,
    senioridades: Iterable[str] | None = None,
    contratos: Iterable[str] | None = None,
    tamanhos: Iterable[str] | None = None,
    cargos: Iterable[str] | None = None,
    tipos_trabalho: Iterable[str] | None = None,
    paises: Iterable[str] | None = None,
    faixa_salarial: tuple[float, float] | None = None,
    busca_cargo: str = "",
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    filtered = df.copy()

    if anos is not None and len(anos) > 0:
        filtered = filtered[filtered["ano"].isin(anos)]
    if senioridades is not None and len(senioridades) > 0:
        filtered = filtered[filtered["senioridade"].isin(senioridades)]
    if contratos is not None and len(contratos) > 0:
        filtered = filtered[filtered["contrato"].isin(contratos)]
    if tamanhos is not None and len(tamanhos) > 0:
        filtered = filtered[filtered["tamanho_empresa"].isin(tamanhos)]
    if cargos is not None and len(cargos) > 0:
        filtered = filtered[filtered["cargo"].isin(cargos)]
    if tipos_trabalho is not None and len(tipos_trabalho) > 0:
        filtered = filtered[filtered["remoto"].isin(tipos_trabalho)]
    if paises is not None and len(paises) > 0:
        country_column = "residencia_iso3" if "residencia_iso3" in filtered.columns else "residencia"
        filtered = filtered[filtered[country_column].isin(paises)]
    if faixa_salarial is not None:
        min_salary, max_salary = faixa_salarial
        filtered = filtered[(filtered["usd"].between(min_salary, max_salary))]
    if busca_cargo:
        search_term = busca_cargo.strip().lower()
        filtered = filtered[filtered["cargo"].astype(str).str.lower().str.contains(search_term, na=False)]

    return filtered.copy()


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | int | str]:
    if df.empty:
        return {
            "salario_medio": 0.0,
            "salario_maximo": 0.0,
            "salario_mediano": 0.0,
            "total_registros": 0,
            "cargo_mais_frequente": "N/D",
        }

    return {
        "salario_medio": float(df["usd"].mean()),
        "salario_maximo": float(df["usd"].max()),
        "salario_mediano": float(df["usd"].median()),
        "total_registros": int(df.shape[0]),
        "cargo_mais_frequente": (
            df["cargo"].mode().iat[0]
            if "cargo" in df.columns and not df["cargo"].mode().empty
            else "N/D"
        ),
    }


def build_insight_cards(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Nenhum dado disponível para análises adicionais.")
        return

    senioridade_media = (
        df.groupby("senioridade")["usd"].mean().sort_values(ascending=False).reset_index()
    )
    top_senioridade = senioridade_media.iloc[0]["senioridade"] if not senioridade_media.empty else "N/D"
    top_senioridade_valor = float(senioridade_media.iloc[0]["usd"]) if not senioridade_media.empty else 0.0

    top_country = (
        df.groupby("residencia_iso3")["usd"].mean().sort_values(ascending=False).reset_index()
    )
    pais_lider = top_country.iloc[0]["residencia_iso3"] if not top_country.empty else "N/D"
    pais_valor = float(top_country.iloc[0]["usd"]) if not top_country.empty else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Maior nível salarial", top_senioridade, f"${top_senioridade_valor:,.0f}")
    col2.metric("País com maior média", pais_lider, f"${pais_valor:,.0f}")
    col3.metric("Registros focados", f"{len(df):,}", "dados filtrados")


def render_landing_page(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div style='padding: 1.2rem 0 1.6rem 0; border-radius: 18px; background: linear-gradient(135deg,#1d4ed8,#7c3aed);'>
            <h1 style='color:white; margin-bottom:0.2rem;'>Dashboard de Salários na Área de Dados</h1>
            <p style='color:#dbeafe; font-size: 1.05rem;'>Acompanhamento de remuneração, senioridade, tipos de contrato e tendências do mercado de dados.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    build_insight_cards(df)

    st.subheader("Resumo executivo")
    if df.empty:
        st.warning("Nenhum registro atende aos filtros atuais.")
        return

    overview = df.copy()
    media_por_ano = overview.groupby("ano")["usd"].mean().reset_index()
    top_cargos = overview.groupby("cargo")["usd"].mean().sort_values(ascending=False).head(5).reset_index()
    escolha_modalidade = overview["remoto"].value_counts().reset_index()
    escolha_modalidade.columns = ["modalidade", "quantidade"]

    col1, col2 = st.columns(2)
    with col1:
        fig_trend = px.line(
            media_por_ano,
            x="ano",
            y="usd",
            markers=True,
            title="Evolução da média salarial por ano",
            labels={"ano": "Ano", "usd": "Média salarial (USD)"},
            template=PLOTLY_TEMPLATE,
        )
        fig_trend.update_traces(line=dict(color="#2563eb", width=3))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        fig_modalidade = px.pie(
            escolha_modalidade,
            names="modalidade",
            values="quantidade",
            title="Distribuição da modalidade de trabalho",
            template=PLOTLY_TEMPLATE,
        )
        fig_modalidade.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_modalidade, use_container_width=True)

    st.subheader("Principais cargos por média salarial")
    fig_top_cargos = px.bar(
        top_cargos,
        x="cargo",
        y="usd",
        title="Top 5 cargos com maior remuneração média",
        labels={"cargo": "Cargo", "usd": "Média anual (USD)"},
        template=PLOTLY_TEMPLATE,
    )
    fig_top_cargos.update_layout(xaxis_tickangle=-25)
    st.plotly_chart(fig_top_cargos, use_container_width=True)

    st.markdown("---")
    st.caption("Insights gerados a partir dos dados filtrados no dashboard.")


def render_dashboard(df: pd.DataFrame) -> None:
    st.subheader("Painel analítico")

    metrics = calculate_kpis(df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-container"><div style="font-size:0.8rem; color:#64748b;">Salário médio</div><div style="font-size:1.9rem; font-weight:700;">${:,.0f}</div></div>'.format(metrics["salario_medio"]), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-container"><div style="font-size:0.8rem; color:#64748b;">Salário máximo</div><div style="font-size:1.9rem; font-weight:700;">${:,.0f}</div></div>'.format(metrics["salario_maximo"]), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-container"><div style="font-size:0.8rem; color:#64748b;">Mediana</div><div style="font-size:1.9rem; font-weight:700;">${:,.0f}</div></div>'.format(metrics["salario_mediano"]), unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-container"><div style="font-size:0.8rem; color:#64748b;">Cargo mais frequente</div><div style="font-size:1.3rem; font-weight:700;">{}</div></div>'.format(metrics["cargo_mais_frequente"]), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if not df.empty:
            top_cargos = (
                df.groupby("cargo")["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
            )
            fig = px.bar(
                top_cargos,
                x="usd",
                y="cargo",
                orientation="h",
                title="Top 10 cargos por salário médio",
                labels={"usd": "Média salarial anual (USD)", "cargo": "Cargo"},
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=["#4f46e5"],
            )
            fig.update_layout(title_x=0.05, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para o gráfico de cargos.")

    with col2:
        if not df.empty:
            fig = px.histogram(
                df,
                x="usd",
                nbins=30,
                title="Distribuição de salários anuais",
                labels={"usd": "Faixa salarial (USD)"},
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=["#22c55e"],
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para a distribuição salarial.")

    col3, col4 = st.columns(2)

    with col3:
        if not df.empty:
            modalidad = df["remoto"].value_counts(dropna=False).reset_index()
            modalidad.columns = ["modalidade", "quantidade"]
            pie = px.pie(
                modalidad,
                names="modalidade",
                values="quantidade",
                title="Distribuição de modalidades de trabalho",
                hole=0.4,
                template=PLOTLY_TEMPLATE,
            )
            pie.update_traces(textinfo="percent+label")
            st.plotly_chart(pie, use_container_width=True)

    with col4:
        if not df.empty and "residencia_iso3" in df.columns:
            paises_mapa = df.groupby("residencia_iso3")["usd"].mean().reset_index()
            fig_map = px.choropleth(
                paises_mapa,
                locations="residencia_iso3",
                color="usd",
                color_continuous_scale="Viridis",
                title="Média por país",
                labels={"residencia_iso3": "País", "usd": "Salário médio (USD)"},
                template=PLOTLY_TEMPLATE,
            )
            st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.subheader("Análises complementares")

    if df.empty:
        st.info("Não há dados suficientes para análises complementares.")
        return

    aba1, aba2, aba3, aba4 = st.tabs([
        "Boxplot por senioridade",
        "Comparativo de cargos",
        "Tendência por ano",
        "Dados detalhados",
    ])

    with aba1:
        fig_box = px.box(
            df,
            x="senioridade",
            y="usd",
            points="all",
            title="Distribuição salarial por senioridade",
            labels={"senioridade": "Senioridade", "usd": "Salário anual (USD)"},
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with aba2:
        top_cargos = (
            df.groupby("cargo")["usd"].mean().nlargest(8).sort_values(ascending=True).reset_index()
        )
        fig_cargos = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Comparativo do salário médio por cargo",
            labels={"cargo": "Cargo", "usd": "Média anual (USD)"},
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_cargos, use_container_width=True)

    with aba3:
        linha = df.groupby(["ano", "cargo"], as_index=False)["usd"].median()
        top5 = linha["cargo"].value_counts().nlargest(5).index.tolist()
        trend = linha[linha["cargo"].isin(top5)]
        fig_trend = px.line(
            trend,
            x="ano",
            y="usd",
            color="cargo",
            markers=True,
            title="Tendência salarial por cargo ao longo do tempo",
            labels={"ano": "Ano", "usd": "Mediana salarial (USD)", "cargo": "Cargo"},
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with aba4:
        st.dataframe(df, use_container_width=True)


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros avançados")

    anos_disponiveis = sorted(df["ano"].dropna().unique().tolist())
    senioridades_disponiveis = sorted(df["senioridade"].dropna().unique().tolist())
    contratos_disponiveis = sorted(df["contrato"].dropna().unique().tolist())
    tamanhos_disponiveis = sorted(df["tamanho_empresa"].dropna().unique().tolist())
    modalidades_disponiveis = sorted(df["remoto"].dropna().unique().tolist())
    cargos_disponiveis = sorted(df["cargo"].dropna().unique().tolist())
    paises_disponiveis = sorted(df["residencia_iso3"].dropna().unique().tolist())

    anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)
    senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)
    contratos_selecionados = st.sidebar.multiselect("Tipo de contrato", contratos_disponiveis, default=contratos_disponiveis)
    tamanhos_selecionados = st.sidebar.multiselect("Tamanho da empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)
    modalidades_selecionadas = st.sidebar.multiselect("Modalidade de trabalho", modalidades_disponiveis, default=modalidades_disponiveis)
    paises_selecionados = st.sidebar.multiselect("País", paises_disponiveis, default=paises_disponiveis)
    cargos_selecionados = st.sidebar.multiselect("Cargo", cargos_disponiveis, default=cargos_disponiveis)

    sal_min = float(df["usd"].min()) if not df.empty else 0.0
    sal_max = float(df["usd"].max()) if not df.empty else 0.0
    faixa_salarial = st.sidebar.slider(
        "Faixa salarial (USD)",
        min_value=int(sal_min),
        max_value=int(sal_max),
        value=(int(sal_min), int(sal_max)),
        step=5000,
    )
    busca_cargo = st.sidebar.text_input("Buscar cargo", placeholder="Ex.: Data Scientist")

    return apply_filters(
        df,
        anos=anos_selecionados,
        senioridades=senioridades_selecionadas,
        contratos=contratos_selecionados,
        tamanhos=tamanhos_selecionados,
        cargos=cargos_selecionados,
        tipos_trabalho=modalidades_selecionadas,
        paises=paises_selecionados,
        faixa_salarial=faixa_salarial,
        busca_cargo=busca_cargo,
    )


def render_main() -> None:
    configure_page()
    df = prepare_dataframe(load_data())
    filtered_df = render_sidebar(df)

    tab_overview, tab_dashboard, tab_data = st.tabs(["Visão geral", "Dashboard", "Dados"])

    with tab_overview:
        render_landing_page(filtered_df)

    with tab_dashboard:
        render_dashboard(filtered_df)

    with tab_data:
        st.subheader("Base filtrada")
        st.dataframe(filtered_df, use_container_width=True)


def main() -> None:
    render_main()


if __name__ == "__main__":
    main()
