# Autoria: Douglas Honório · Projeto Dh73 CyberGuard SOC · 2026
"""Demonstração pública: dados fictícios isolados na sessão do navegador."""
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from cenarios import CENARIOS, gerar_cenario
from relatorios import criar_relatorio

st.set_page_config(page_title="Dh73 CyberGuard SOC", page_icon="🛡️", layout="wide")
logo = base64.b64encode(Path(__file__).with_name("logo.svg").read_bytes()).decode("ascii")
st.markdown("""
<style>
.stApp {background: radial-gradient(ellipse at 85% 5%, #0b2946, #061222 40%, #040a13 80%); color:#edf7ff}
header[data-testid="stHeader"]{background:transparent}
section[data-testid="stSidebar"]{background:#071321;border-right:1px solid #17364b}
.block-container{max-width:1250px;padding-top:2rem}
.brandbar{border:1px solid #23516a;border-radius:50px;padding:12px 25px;background:#0a2235;color:#fff;font-weight:800;letter-spacing:.1em}
.hero{margin:22px 0;padding:45px;border:1px solid #15364b;border-radius:20px;background:radial-gradient(circle at 90% 25%,#15476d,transparent 38%),#081827}
.hero h1{color:#f4fbff;font-size:clamp(2rem,4.5vw,4rem);line-height:1.05;letter-spacing:-.04em}
.hero h1 span{color:#5ecdf1}.hero p{color:#b0c7d5}.tag{color:#82efc4;font:12px monospace}
section[data-testid="stMetric"]{border:1px solid #1a4055;border-radius:14px;padding:20px;background:#0d2233}
h2,h3{color:#eaf8ff!important}
</style>
<div class="brandbar"><img src="data:image/svg+xml;base64,__LOGO__" alt="Logo DH73" style="width:44px;vertical-align:middle;margin-right:10px"> DH73 CYBERGUARD</div>
<div class="hero"><div class="tag">[ DH73 / CENTRO DE OPERAÇÕES ]</div>
<h1>Inteligência para<br><span>analisar ameaças.</span></h1>
<p>Explore cenários fictícios e entenda a análise de eventos de segurança.</p>
<div class="tag">● DEMONSTRAÇÃO PÚBLICA · DADOS FICTÍCIOS</div></div>
""".replace("__LOGO__", logo), unsafe_allow_html=True)

if "eventos" not in st.session_state:
    st.session_state.eventos = gerar_cenario("Cenário completo")
st.sidebar.subheader("🧪 Simulações")
cenario = st.sidebar.selectbox("Escolha um cenário", list(CENARIOS))
st.sidebar.caption(CENARIOS[cenario])
if st.sidebar.button("Executar simulação", type="primary"):
    if len(st.session_state.eventos) + len(gerar_cenario(cenario)) > 1000:
        st.sidebar.warning("Limite de 1.000 eventos nesta sessão. Reinicie a demonstração.")
    else:
        st.session_state.eventos.extend(gerar_cenario(cenario))
        st.sidebar.success("Cenário fictício adicionado.")
if st.sidebar.button("Reiniciar demonstração"):
    st.session_state.eventos = gerar_cenario("Cenário completo")
    st.rerun()

frame = pd.DataFrame(st.session_state.eventos)
st.info("Dados gerados para esta sessão. Nenhum sistema é monitorado e os dados são perdidos ao encerrar a sessão.")
tipo = st.selectbox("Filtrar por tipo", ["Todos"] + sorted(frame["tipo"].unique().tolist()))
filtrado = frame if tipo == "Todos" else frame[frame["tipo"] == tipo]
agora = pd.Timestamp.now(tz="UTC")
recentes = frame.assign(data=pd.to_datetime(frame["timestamp"], utc=True))
recentes = recentes[(recentes["data"] >= agora - pd.Timedelta(minutes=10)) & (recentes["data"] <= agora)]
alertas = []
for evento_tipo, limite, regra in [("login_falho", 5, "5 ou mais falhas de login em 10 minutos"),
                                   ("alteracao_arquivo", 3, "3 ou mais alterações de arquivo em 10 minutos")]:
    contagens = recentes[recentes["tipo"] == evento_tipo].groupby("ip").size()
    alertas.extend({"ip": ip, "total": int(total), "regra": regra}
                   for ip, total in contagens.items() if total >= limite)
a, b, c = st.columns(3)
a.metric("Eventos filtrados", len(filtrado))
b.metric("Falhas filtradas", int((filtrado["tipo"] == "login_falho").sum()))
c.metric("Alertas por regra · 10 min", len(alertas))
st.caption("Alertas usam todos os eventos da sessão e não seguem o filtro selecionado.")
st.subheader("Alertas de laboratório")
if alertas:
    st.dataframe(pd.DataFrame(alertas), hide_index=True, use_container_width=True)
else:
    st.info("Nenhuma regra acionada na janela atual.")
st.subheader("Eventos ao longo do tempo")
if not filtrado.empty:
    tempos = pd.to_datetime(filtrado["timestamp"], utc=True)
    st.bar_chart(tempos.dt.floor("h").value_counts().sort_index().rename("Eventos"), color="#59d8e7")
    st.caption("Eventos agrupados por hora em UTC.")
st.subheader("Eventos registrados")
st.dataframe(filtrado, hide_index=True, use_container_width=True)
relatorio = criar_relatorio(filtrado.to_dict("records"), alertas, {"tipo": tipo, "severidade": "Todas"})
st.download_button("Baixar relatório HTML", relatorio, file_name="relatorio-cyberguard.html", mime="text/html")
st.caption("Regras educativas, sem inteligência artificial ou monitoramento real. Criado por Douglas Honório.")

