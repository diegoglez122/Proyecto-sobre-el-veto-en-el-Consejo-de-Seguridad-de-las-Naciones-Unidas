import os
import time

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="El veto en la ONU", page_icon="🗳️", layout="wide")

# Evita que el navegador traduzca la página (si no, "China" pasa a "Porcelana")
components.html(
    """<script>
    const d = window.parent.document;
    d.documentElement.lang = 'es';
    if (!d.querySelector('meta[name=google]')) {
      const m = d.createElement('meta'); m.name = 'google'; m.content = 'notranslate';
      d.head.appendChild(m);
    }
    </script>""",
    height=0,
)

COLORES = {"URSS/Rusia": "#e5484d", "EE. UU.": "#4f8cff", "Reino Unido": "#a07bff",
           "Francia": "#2fbf8f", "China": "#f5b83d"}
ESTATICO = {"staticPlot": True}          # sin interacción
LIGERO = {"displayModeBar": False}       # con hover, sin barra de herramientas

st.markdown("""
<style>
.hero{padding:28px 30px;border-radius:16px;margin-bottom:14px;
 background:linear-gradient(135deg,#16233f 0%,#2b1f4f 100%);border:1px solid #2f3b57}
.hero h1{margin:0 0 6px 0;font-size:2.1rem}
.hero p{margin:0;color:#c3cbe0;font-size:1.05rem}
.ctx{background:#1a1f2b;border:1px solid #2a3142;border-radius:14px;padding:18px 22px;margin-bottom:14px}
.ctx h3{margin:0 0 8px 0}
.ctx p{margin:0 0 10px 0;color:#d5dae6;line-height:1.55}
.pasos{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px}
.paso{flex:1;min-width:200px;background:#232a3a;border-radius:10px;padding:10px 14px;font-size:.92rem}
div[data-testid="stMetric"]{background:#1a1f2b;border:1px solid #2a3142;
 padding:14px 16px;border-radius:12px}
.insight{background:#1a1f2b;border-left:4px solid #4f8cff;padding:12px 16px;
 border-radius:8px;margin:8px 0}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cargar():
    df = pd.read_csv("vetos.csv")
    df["pais"] = df["pais"].str.strip()
    df["vetos"] = pd.to_numeric(df["vetos"], errors="coerce").fillna(0).astype(int)
    det = pd.read_csv("vetos_detalle.csv") if os.path.exists("vetos_detalle.csv") else None
    return df, det


df, det = cargar()
anios = sorted(int(d[:4]) for d in df["decada"].unique())
DECADAS = [f"{a}s" for a in range(anios[0], anios[-1] + 1, 10)]
PAISES = [p for p in COLORES if p in set(df["pais"])]
TOTAL = int(df["vetos"].sum())


def elegir(label, opciones, default, key, multi=False):
    """Botones tipo 'pills' (más visibles); si la versión no los trae, usa widgets clásicos."""
    if hasattr(st, "pills"):
        return st.pills(label, opciones, selection_mode="multi" if multi else "single",
                        default=default, key=key)
    if multi:
        return st.multiselect(label, opciones, default=default, key=key)
    return st.radio(label, opciones, index=opciones.index(default), horizontal=True, key=key)


# ---------- Cabecera y contexto ----------
st.markdown("""
<div class="hero">
<h1>🗳️ El veto en el Consejo de Seguridad</h1>
<p>Cinco países pueden bloquear cualquier resolución del Consejo de Seguridad de la ONU. Explora quién usó ese poder, cuándo y cuánto.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="ctx">
<h3>¿De qué trata este panel?</h3>
<p>El Consejo de Seguridad es el órgano de la ONU encargado de la paz y la seguridad internacionales.
Tiene 15 miembros, y cinco de ellos (EE. UU., Rusia, Reino Unido, Francia y China) son permanentes y tienen
<b>derecho de veto</b>: si uno vota en contra, la resolución no se aprueba, aunque todos los demás voten a favor.</p>
<p>Aquí analizamos los <b>{TOTAL} vetos</b> de la lista oficial de la ONU entre los {DECADAS[0]} y los {DECADAS[-1]}:
quién los usó, en qué épocas y con qué frecuencia.</p>
<div class="pasos">
<div class="paso">1️⃣ <b>Elige</b> países y años en el cuadro de abajo</div>
<div class="paso">2️⃣ <b>Recorre</b> las pestañas: Resumen, Evolución y Compara</div>
<div class="paso">3️⃣ <b>Pulsa ▶</b> en Evolución y prueba el Desafío</div>
</div>
</div>
""", unsafe_allow_html=True)

# ---------- Filtros ----------
with st.container(border=True):
    st.markdown("#### 🎛️ Personaliza tu análisis")
    st.caption("Toca los países para activarlos o quitarlos y mueve el selector de años: todo se actualiza al instante.")
    paises = elegir("Países", PAISES, PAISES, "f_paises", multi=True)
    rango = st.select_slider("Años (por décadas)", DECADAS, value=(DECADAS[0], DECADAS[-1]))

if not paises:
    st.warning("Selecciona al menos un país.")
    st.stop()

dec_rango = DECADAS[DECADAS.index(rango[0]): DECADAS.index(rango[1]) + 1]
f = df[df["pais"].isin(paises) & df["decada"].isin(dec_rango)]
if f.empty:
    st.info("Esa combinación no tiene vetos. Prueba con más países o un rango de años distinto.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🎬 Evolución", "⚔️ Compara", "🎯 Desafío"])

# ---------- Resumen ----------
with tab1:
    por_dec = f.groupby("decada")["vetos"].sum().reindex(dec_rango, fill_value=0)
    por_pais = f.groupby("pais")["vetos"].sum().reindex(paises, fill_value=0).sort_values(ascending=False)
    total = int(por_pais.sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Vetos en la selección", total)
    c2.metric("Década más intensa", por_dec.idxmax(), f"{int(por_dec.max())} vetos", delta_color="off")
    c3.metric("Mayor usuario", por_pais.index[0], f"{por_pais.iloc[0] / total:.0%} del total", delta_color="off")

    st.markdown(f"<div class='insight'>💡 <b>{por_pais.index[0]}</b> concentra "
                f"<b>{por_pais.iloc[0] / total:.0%}</b> de los vetos de esta selección, "
                f"y la década de <b>{por_dec.idxmax()}</b> fue la de mayor actividad.</div>",
                unsafe_allow_html=True)

    g1, g2 = st.columns([3, 2])
    color = COLORES[paises[0]] if len(paises) == 1 else "#4f8cff"
    fig1 = px.bar(x=list(por_dec.index), y=list(por_dec.values), text=list(por_dec.values))
    fig1.update_traces(marker_color=color, textposition="outside", cliponaxis=False)
    fig1.update_layout(title="Vetos por década", height=360, bargap=0.4, xaxis_title=None,
                       yaxis=dict(visible=False, range=[0, max(1, por_dec.max()) * 1.2]),
                       margin=dict(t=50, b=10, l=10, r=10))
    g1.plotly_chart(fig1, use_container_width=True, config=ESTATICO)

    fig2 = px.bar(x=list(por_pais.values), y=list(por_pais.index), orientation="h",
                  color=list(por_pais.index), color_discrete_map=COLORES, text=list(por_pais.values))
    fig2.update_traces(textposition="outside", cliponaxis=False)
    fig2.update_layout(title="Por país", height=360, showlegend=False, bargap=0.4,
                       xaxis=dict(visible=False, range=[0, max(1, por_pais.max()) * 1.2]),
                       yaxis=dict(autorange="reversed", title=None),
                       margin=dict(t=50, b=10, l=10, r=10))
    g2.plotly_chart(fig2, use_container_width=True, config=ESTATICO)

    with st.expander("📋 Ver y descargar los datos"):
        st.dataframe(f.pivot_table(index="decada", columns="pais", values="vetos",
                                   aggfunc="sum", fill_value=0))
        st.download_button("Descargar CSV", f.to_csv(index=False), "vetos_filtrado.csv")

# ---------- Evolución ----------
with tab2:
    st.subheader("La carrera de los vetos")
    st.caption("Pulsa ▶ y mira cómo se van acumulando los vetos de cada país, década a década.")
    acum = (f.pivot_table(index="decada", columns="pais", values="vetos", aggfunc="sum")
              .reindex(index=dec_rango, columns=paises).fillna(0).cumsum())
    tope = max(1, acum.values.max())

    def carrera(d):
        s = acum.loc[d].sort_values(ascending=False)
        fig = px.bar(x=list(s.values), y=list(s.index), orientation="h", color=list(s.index),
                     color_discrete_map=COLORES, text=[int(v) for v in s.values])
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(title=f"Vetos acumulados hasta los {d}", height=380, showlegend=False,
                          bargap=0.55, xaxis=dict(visible=False, range=[0, tope * 1.15]),
                          yaxis=dict(autorange="reversed", title=None),
                          margin=dict(t=50, b=10, l=10, r=10))
        return fig

    c1, c2 = st.columns([1, 3])
    play = c1.button("▶ Reproducir", type="primary", use_container_width=True)
    if len(dec_rango) > 1:
        dec_sel = c2.select_slider("…o elige una década", dec_rango, value=dec_rango[-1])
    else:
        dec_sel = dec_rango[0]
    hueco = st.empty()
    if play:
        for d in dec_rango:
            hueco.plotly_chart(carrera(d), use_container_width=True, config=ESTATICO, key=f"race_{d}")
            time.sleep(0.9)
    else:
        hueco.plotly_chart(carrera(dec_sel), use_container_width=True, config=ESTATICO, key="race_sel")

# ---------- Compara ----------
with tab3:
    st.subheader("Cara a cara")
    st.caption("Toca un país en cada fila para enfrentarlos. El gráfico cambia al instante (historial completo).")
    p1 = elegir("Primer país", PAISES, PAISES[0], "pa") or PAISES[0]
    p2 = elegir("Segundo país", PAISES, PAISES[1], "pb") or PAISES[1]
    if p1 == p2:
        st.info("Elige dos países distintos para compararlos.")
    else:
        pv = (df.pivot_table(index="decada", columns="pais", values="vetos", aggfunc="sum")
                .reindex(index=DECADAS, columns=[p1, p2]).fillna(0))
        figc = px.line(pv, markers=True, color_discrete_map=COLORES,
                       labels={"decada": "", "value": "Vetos", "pais": "País"})
        figc.update_layout(legend_title=None, height=380, margin=dict(t=20, b=10))
        st.plotly_chart(figc, use_container_width=True, config=LIGERO)
        t1, t2 = int(df[df.pais == p1].vetos.sum()), int(df[df.pais == p2].vetos.sum())
        m1, m2 = st.columns(2)
        m1.metric(p1, f"{t1} vetos", f"{t1 - t2:+d} frente a {p2}", delta_color="off")
        m2.metric(p2, f"{t2} vetos", f"{t2 - t1:+d} frente a {p1}", delta_color="off")

# ---------- Desafío ----------
with tab4:
    st.subheader("🎯 ¿Cuánto sabes del veto?")
    st.caption("Responde y descubre tu puntuación. Las respuestas salen de los datos reales de este panel.")
    tot_dec = df.groupby("decada")["vetos"].sum()
    tot_pais = df.groupby("pais")["vetos"].sum()
    dq = "1980s" if "1980s" in DECADAS else DECADAS[-1]
    en_dq = df[df.decada == dq].groupby("pais")["vetos"].sum()
    us = "EE. UU."
    n_us = int(tot_pais.get(us, 0))

    preg = [
        (f"¿Qué país usó más vetos en los {dq}?", PAISES, en_dq.idxmax(),
         f"Fue {en_dq.idxmax()}, con {int(en_dq.max())} vetos."),
        ("¿Qué década registró más vetos en total?", DECADAS, tot_dec.idxmax(),
         f"Los {tot_dec.idxmax()}, con {int(tot_dec.max())} vetos."),
        (f"¿Cuántos vetos ha usado {us} en total?",
         sorted({n_us, round(n_us * 0.5), round(n_us * 1.5), round(n_us * 2)}), n_us,
         f"{us} suma {n_us} vetos."),
    ]
    if det is not None and {"anio", "pais", "tema"} <= set(det.columns):
        primer = int(det[det.pais == us]["anio"].min())
        preg.append((f"¿En qué año usó {us} su primer veto?",
                     sorted({1946, 1956, primer, 1990}), primer,
                     f"En {primer}: fue miembro fundador de la ONU, pero tardó décadas en vetar."))
        temas = det[det.tema != "Otros"]["tema"].value_counts()
        if not temas.empty:
            preg.append(("¿Sobre qué tema se concentran más vetos?", list(temas.index), temas.index[0],
                         f"{temas.index[0]}, con {int(temas.iloc[0])} vetos."))

    with st.form("trivia"):
        resp = [st.radio(f"{i + 1}. {q}", op, index=None, horizontal=True, key=f"q{i}")
                for i, (q, op, ok, ex) in enumerate(preg)]
        enviado = st.form_submit_button("Comprobar respuestas", type="primary")

    if enviado:
        if any(r is None for r in resp):
            st.warning("Responde todas las preguntas antes de comprobar.")
        else:
            aciertos = sum(r == p[2] for r, p in zip(resp, preg))
            for i, (r, p) in enumerate(zip(resp, preg)):
                (st.success if r == p[2] else st.error)(
                    f"{'✅' if r == p[2] else '❌'} {i + 1}. {p[3]}")
            st.metric("Tu puntuación", f"{aciertos} / {len(preg)}")
            if aciertos == len(preg):
                st.balloons()

st.caption("📊 Fuente: Biblioteca Dag Hammarskjöld, ONU. Datos oficiales extraídos mediante web scraping "
           "(consultado en noviembre de 2026). Cada fila de la lista cuenta como un veto por país, incluidos "
           "los de enmiendas y párrafos. Nota: la década de 2020 está en curso.")
