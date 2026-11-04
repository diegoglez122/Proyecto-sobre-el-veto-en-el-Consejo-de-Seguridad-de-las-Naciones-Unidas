import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="El veto en la ONU", page_icon="🗳️", layout="wide")

COLORES = {"URSS/Rusia": "#e5484d", "EE. UU.": "#4f8cff", "Reino Unido": "#a07bff",
           "Francia": "#2fbf8f", "China": "#f5b83d"}

st.markdown("""
<style>
.hero{padding:28px 30px;border-radius:16px;margin-bottom:18px;
 background:linear-gradient(135deg,#16233f 0%,#2b1f4f 100%);border:1px solid #2f3b57}
.hero h1{margin:0 0 6px 0;font-size:2.1rem}
.hero p{margin:0;color:#c3cbe0;font-size:1.05rem}
div[data-testid="stMetric"]{background:#1a1f2b;border:1px solid #2a3142;
 padding:14px 16px;border-radius:12px}
.insight{background:#1a1f2b;border-left:4px solid #4f8cff;padding:12px 16px;
 border-radius:8px;margin:8px 0}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cargar_datos():
    df = pd.read_csv("vetos.csv")
    df["pais"] = df["pais"].str.strip()
    df["vetos"] = pd.to_numeric(df["vetos"], errors="coerce").fillna(0).astype(int)
    return df


df = cargar_datos()
DECADAS = sorted(df["decada"].unique())

st.markdown("""
<div class="hero">
<h1>🗳️ El veto en el Consejo de Seguridad</h1>
<p>Cinco países pueden bloquear cualquier resolución de la ONU. Explora quién usó ese poder, cuándo y cuánto.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Filtros globales ----------
with st.sidebar:
    st.header("🎛️ Filtros")
    paises = st.multiselect("Países", list(COLORES), default=list(COLORES))
    rango = st.select_slider("Rango de décadas", DECADAS, value=(DECADAS[0], DECADAS[-1]))
    st.caption("Los filtros afectan a las pestañas Resumen y Evolución.")

f = df[df["pais"].isin(paises) & df["decada"].between(*rango)]
if f.empty:
    st.warning("Selecciona al menos un país.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🎬 Evolución", "⚔️ Compara", "🎯 Desafío"])

# ---------- Resumen ----------
with tab1:
    por_dec = f.groupby("decada")["vetos"].sum()
    por_pais = f.groupby("pais")["vetos"].sum().sort_values(ascending=False)
    total = int(por_pais.sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Vetos en la selección", total)
    c2.metric("Década más intensa", por_dec.idxmax(), f"{int(por_dec.max())} vetos")
    c3.metric("Mayor usuario", por_pais.index[0], f"{por_pais.iloc[0] / total:.0%} del total")

    st.markdown(f"<div class='insight'>💡 <b>{por_pais.index[0]}</b> concentra "
                f"<b>{por_pais.iloc[0] / total:.0%}</b> de los vetos de esta selección, "
                f"y la década de <b>{por_dec.idxmax()}</b> fue la de mayor actividad.</div>",
                unsafe_allow_html=True)

    g1, g2 = st.columns([3, 2])
    fig = px.bar(f, x="decada", y="vetos", color="pais", color_discrete_map=COLORES,
                 labels={"decada": "Década", "vetos": "Vetos", "pais": "País"})
    fig.update_layout(title="Vetos por década", legend_title=None)
    g1.plotly_chart(fig, use_container_width=True)
    fig2 = px.pie(por_pais.reset_index(), names="pais", values="vetos", hole=0.5,
                  color="pais", color_discrete_map=COLORES)
    fig2.update_layout(title="Reparto por país", legend_title=None)
    g2.plotly_chart(fig2, use_container_width=True)

    with st.expander("📋 Ver y descargar los datos"):
        st.dataframe(f.pivot_table(index="decada", columns="pais", values="vetos",
                                   aggfunc="sum", fill_value=0))
        st.download_button("Descargar CSV", f.to_csv(index=False), "vetos_filtrado.csv")

# ---------- Evolución animada ----------
with tab2:
    st.subheader("Carrera acumulada de vetos")
    st.caption("Pulsa ▶ para ver cómo crece el total de cada país década a década.")
    p = f.pivot_table(index="decada", columns="pais", values="vetos", aggfunc="sum", fill_value=0)
    acum = p.cumsum().stack().reset_index(name="acumulado")
    figa = px.bar(acum, x="pais", y="acumulado", color="pais", color_discrete_map=COLORES,
                  animation_frame="decada", range_y=[0, max(1, acum["acumulado"].max() * 1.1)],
                  labels={"pais": "", "acumulado": "Vetos acumulados"})
    figa.update_layout(showlegend=False, height=480)
    st.plotly_chart(figa, use_container_width=True)

# ---------- Comparador ----------
with tab3:
    st.subheader("Cara a cara")
    a, b = st.columns(2)
    p1 = a.selectbox("País A", list(COLORES), index=0)
    p2 = b.selectbox("País B", list(COLORES), index=1)
    d2 = df[df["pais"].isin([p1, p2])]
    figc = px.line(d2, x="decada", y="vetos", color="pais", markers=True,
                   color_discrete_map=COLORES, labels={"decada": "Década", "vetos": "Vetos"})
    st.plotly_chart(figc, use_container_width=True)
    t1, t2 = int(df[df.pais == p1].vetos.sum()), int(df[df.pais == p2].vetos.sum())
    m1, m2 = st.columns(2)
    m1.metric(p1, t1, f"{t1 - t2:+d} vs {p2}")
    m2.metric(p2, t2, f"{t2 - t1:+d} vs {p1}")

# ---------- Desafío ----------
with tab4:
    st.subheader("¿Cuánto sabes del veto?")
    dec = st.selectbox("Elige una década", DECADAS, index=3)
    with st.form("juego"):
        apuesta = st.radio("¿Qué país usó más veto en esa década?", list(COLORES), horizontal=True)
        ok = st.form_submit_button("Comprobar")
    if ok:
        dd = df[df["decada"] == dec].set_index("pais")["vetos"]
        real = dd.idxmax()
        if apuesta == real:
            st.success(f"🎉 ¡Correcto! {real} lideró en los {dec} con {int(dd.max())} vetos.")
            st.balloons()
        else:
            st.error(f"No exactamente. Fue {real} con {int(dd.max())} vetos "
                     f"({apuesta} tuvo {int(dd[apuesta])}).")

st.caption("📊 Fuente: Biblioteca Dag Hammarskjöld, ONU. Datos oficiales extraídos mediante web scraping. (Consultado en noviembre de 2026). Nota: la década de 2020 está en curso.")
