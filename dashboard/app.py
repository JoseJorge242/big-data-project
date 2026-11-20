import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Trânsito · ODS 5 e 18", layout="wide")


@st.cache_resource
def engine():
    return create_engine(st.secrets["db_url"], pool_pre_ping=True)


@st.cache_data(ttl=60) 
def q(sql: str, **params) -> pd.DataFrame:
    with engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def opcoes(sql: str) -> list:
    return q(sql).iloc[:, 0].tolist()


def grafico(df, fig_fn, legenda, **kw):
    """Mostra o gráfico (ou aviso, se não houver dados) e a legenda da fonte."""
    if df.empty:
        st.info("Sem dados para o filtro.")
    else:
        st.plotly_chart(fig_fn(df, **kw), use_container_width=True)
    st.caption(legenda)


def lista(sel): 
    return sel or ["-"]


st.sidebar.header("Filtros")
anos = opcoes("""SELECT ano FROM (SELECT ano FROM tb_sim_genero UNION SELECT ano FROM tb_acidentes
                 UNION SELECT ano FROM tb_mgdi_indicadores) t WHERE ano IS NOT NULL ORDER BY ano""")
ini, fim = st.sidebar.select_slider("Período", anos, value=(2021 if 2021 in anos else anos[0], anos[-1]))

ufs = opcoes("SELECT DISTINCT uf FROM tb_acidentes WHERE uf IS NOT NULL ORDER BY uf")
uf = st.sidebar.selectbox("UF (PRF e MGDI)", ["Todas"] + ufs)

sexos = opcoes("SELECT DISTINCT sexo FROM tb_mgdi_indicadores WHERE sexo IS NOT NULL ORDER BY 1")
sexo_sel = lista(st.sidebar.multiselect("Sexo (MGDI)", sexos, default=sexos))

faixas = opcoes("SELECT DISTINCT faixa_etaria FROM tb_mgdi_indicadores WHERE faixa_etaria IS NOT NULL ORDER BY 1")
faixa_sel = lista(st.sidebar.multiselect("Faixa etária (MGDI)", faixas, default=faixas))

grupos = opcoes("SELECT DISTINCT grupo_cid10 FROM tb_sim_genero ORDER BY 1")
total = [g for g in grupos if g.strip().lower() == "acidentes de transporte"]
grupo_sel = lista(st.sidebar.multiselect(
    "Grupo CID-10 (SIM)", grupos, default=total or grupos,
    help="'Acidentes de transporte' é o total. Para detalhar, marque só os subgrupos "
         "e desmarque o total, senão há dupla contagem."))

todas = uf == "Todas"
periodo = dict(i=ini, f=fim, g=grupo_sel)

sim_g = q("""SELECT ano, SUM(masc) AS masculino, SUM(fem) AS feminino, SUM(total) AS total
             FROM tb_sim_genero WHERE ano BETWEEN :i AND :f AND grupo_cid10 = ANY(:g)
             GROUP BY ano ORDER BY ano""", **periodo)

sim_r = q("""SELECT ano, SUM(branca) AS branca, SUM(preta) AS preta, SUM(parda) AS parda,
                    SUM(amarela) AS amarela, SUM(indigena) AS indigena, SUM(ignorado) AS ignorado
             FROM tb_sim_raca WHERE ano BETWEEN :i AND :f AND grupo_cid10 = ANY(:g)
             GROUP BY ano ORDER BY ano""", **periodo)

mgdi = q("""SELECT faixa_etaria, sexo, SUM(obitos_transito) AS obitos, SUM(populacao_estimada) AS pop
            FROM tb_mgdi_indicadores
            WHERE ano BETWEEN :i AND :f AND (:todas OR uf = :uf)
              AND sexo = ANY(:s) AND faixa_etaria = ANY(:fx)
            GROUP BY faixa_etaria, sexo ORDER BY faixa_etaria""",
         i=ini, f=fim, todas=todas, uf=uf, s=sexo_sel, fx=faixa_sel)
mgdi["taxa_100k"] = mgdi["obitos"] * 100000 / mgdi["pop"].where(mgdi["pop"] > 0)
mgdi = mgdi.dropna(subset=["taxa_100k"])

prf = q("""SELECT uf, COUNT(DISTINCT id) AS acidentes,
                  COUNT(*) FILTER (WHERE estado_fisico ILIKE '%bito%') AS obitos,
                  COUNT(*) FILTER (WHERE estado_fisico ILIKE '%bito%' AND sexo ILIKE 'fem%') AS obitos_fem
           FROM tb_acidentes WHERE ano BETWEEN :i AND :f AND (:todas OR uf = :uf)
           GROUP BY uf ORDER BY obitos DESC""", i=ini, f=fim, todas=todas, uf=uf)

st.title("Trânsito e mortalidade no Brasil")
st.caption("ODS 5 (igualdade de gênero) e ODS 18 (igualdade étnico-racial) · SIM/DATASUS, PRF e MGDI/MS")


def pct(parte, todo):
    return f"{parte / todo:.1%}" if todo else "—"


tot = int(sim_g["total"].sum())
tot_raca = int(sim_r.drop(columns="ano").sum().sum())
k = st.columns(4)
k[0].metric("Óbitos no trânsito (SIM)", f"{tot:,}".replace(",", "."))
k[1].metric("% mulheres", pct(int(sim_g["feminino"].sum()), tot))
k[2].metric("% pretos + pardos", pct(int(sim_r[["preta", "parda"]].sum().sum()), tot_raca))
k[3].metric("UF com mais óbitos (PRF)", prf.iloc[0]["uf"] if not prf.empty else "—")

c1, c2 = st.columns(2)
with c1:
    st.subheader("1 · Óbitos por sexo ao longo dos anos (ODS 5)")
    grafico(sim_g.melt("ano", ["masculino", "feminino"], var_name="sexo", value_name="óbitos"),
            px.bar, "Fonte: SIM. Filtra por período e grupo CID-10; não filtra por UF.",
            x="ano", y="óbitos", color="sexo", barmode="group")
with c2:
    st.subheader("2 · Taxa por 100 mil hab. por sexo e faixa etária (ODS 5)")
    grafico(mgdi, px.bar, "Fonte: MGDI (2000–2024). Taxa = Σ óbitos ÷ Σ população × 100 mil. "
            "Compare taxas, não contagens: as faixas têm larguras diferentes.",
            x="faixa_etaria", y="taxa_100k", color="sexo", barmode="group",
            labels={"taxa_100k": "óbitos / 100 mil"})

c3, c4 = st.columns(2)
with c3:
    st.subheader("3 · Óbitos por raça/cor (ODS 18)")
    fig_raca = lambda d: px.bar(d.melt("ano", var_name="raça/cor", value_name="óbitos"),
                                x="ano", y="óbitos", color="raça/cor").update_layout(
        barnorm="percent", yaxis_title="% dos óbitos")
    grafico(sim_r, fig_raca, "Fonte: SIM (nacional). A fatia 'ignorado' indica a qualidade do registro.")
with c4:
    st.subheader("4 · Ranking de UFs: óbitos em rodovias federais (ODS 5)")
    grafico(prf.head(10).sort_values("obitos"), px.bar,
            "Fonte: PRF (só rodovias federais). Óbitos = pessoas com estado físico 'Óbito'.",
            x="obitos", y="uf", orientation="h", hover_data=["acidentes", "obitos_fem"])

with st.expander("Ver dados consultados"):
    for nome, df in [("SIM · gênero", sim_g), ("SIM · raça/cor", sim_r), ("MGDI", mgdi), ("PRF", prf)]:
        st.write(nome, df)