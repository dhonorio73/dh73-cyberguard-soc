# Autoria: Douglas Honório · Projeto Dh73 CyberGuard SOC · 2026
import os
import base64
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from cenarios import CENARIOS, gerar_cenario
from relatorios import criar_relatorio, ler_csv

st.set_page_config(page_title="Dh73 CyberGuard SOC", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
API = os.environ.get("CYBERGUARD_API", "http://127.0.0.1:5000").rstrip("/")

logo = base64.b64encode(Path(__file__).with_name('logo.svg').read_bytes()).decode('ascii')
st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at 84% 5%, #0b2946 0%, #061222 34%, #040a13 72%); color: #edf7ff; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #071321; border-right: 1px solid #17364b; }
section[data-testid="stSidebar"] * { color: #d8eaf2; }
.block-container { max-width: 1320px; padding-top: 2rem; padding-bottom: 2rem; }
.brandbar { border: 1px solid #23516a; border-radius: 50px; padding: 15px 26px;
  background: linear-gradient(105deg,#071421,#0b2943); box-shadow: 0 0 24px #21c9ff14;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.brand { color: #f5fcff; font-size: 17px; font-weight: 800; letter-spacing: .11em; }
.brand span { color: #58d5f8; }
.brandnote { color: #a1becb; font-size: 11px; letter-spacing: .13em; text-transform: uppercase; }
.hero { position: relative; overflow: hidden; margin: 22px 0 28px; padding: 48px 48px 42px;
  border: 1px solid #15364b; border-radius: 20px;
  background: radial-gradient(circle at 86% 28%,#15476d 0%,transparent 30%), linear-gradient(115deg,#07121d 5%,#0a2034 65%,#071422); }
.hero:after { content: "0101 1010 0011 0101 1010 0011 0101 1010 0011 0101 1010 0011 0101 1010 0011 0101 1010";
  position: absolute; right: 3%; top: 8%; width: 27%; color: #59ffc1; opacity: .12; font: 18px/2.2 monospace;
  overflow-wrap: anywhere; letter-spacing: .3em; transform: rotate(-8deg); pointer-events: none; }
.eyebrow { color: #58e9bb; font: 700 11px monospace; letter-spacing: .18em; }
.hero h1 { max-width: 780px; margin: 14px 0 15px; color: #f4fbff; font-size: clamp(2.1rem,4.5vw,4.1rem);
  font-weight: 800; line-height: 1.04; letter-spacing: -.045em; }
.hero h1 span { color: #5ecdf1; }
.hero p { max-width: 610px; color: #b0c7d5; line-height: 1.7; font-size: 15px; }
.hero-tag { display: inline-block; margin-top: 12px; padding: 8px 13px; border: 1px solid #245b55;
  border-radius: 30px; color: #82efc4; background: #0a302c80; font: 11px monospace; }
.section-label { color: #67e5bd; font: 700 11px monospace; letter-spacing: .16em; text-transform: uppercase; margin: 28px 0 6px; }
section[data-testid="stMetric"] { border: 1px solid #1a4055; border-radius: 14px; padding: 20px 22px;
  background: linear-gradient(145deg,#0d2233,#091927); min-height: 112px; }
[data-testid="stMetricLabel"] p { color: #9fbac8 !important; font-size: 13px !important; }
[data-testid="stMetricValue"] { color: #f1fbff; font-weight: 700; }
h2, h3 { color: #eaf8ff !important; }
[data-testid="stDataFrame"] { border: 1px solid #1a4055; border-radius: 12px; overflow: hidden; }
.footer { border-top: 1px solid #17364b; padding-top: 22px; margin-top: 34px; color: #87a8b6;
  font-size: 12px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
.footer strong { color: #60d5f3; }
@media (max-width: 700px) { .hero { padding: 30px 24px; } .hero:after { display:none; } .brandnote { display:none; } }
</style>
<div class="brandbar"><div class="brand"><img src="data:image/svg+xml;base64,__LOGO__" alt="Logo DH73" style="width:45px; height:45px; vertical-align:middle; margin-right:10px">DH73 <span>CYBERGUARD</span></div>
<div class="brandnote">Security operations &nbsp; / &nbsp; Laboratório</div></div>
<div class="hero">
<div class="eyebrow">[ DH73 / CENTRO DE OPERAÇÕES ]</div>
<h1>Inteligência para<br><span>analisar ameaças.</span></h1>
<p>Explore eventos fictícios, acompanhe indicadores e entenda como regras de segurança ajudam na análise de dados.</p>
<div class="hero-tag">● &nbsp; MODO LABORATÓRIO &nbsp; // &nbsp; DADOS SIMULADOS</div>
</div>
""".replace("__LOGO__", logo), unsafe_allow_html=True)

st.sidebar.markdown("### ◈ DH73 / CONTROLES")
st.sidebar.caption("Personalize a visão dos eventos.")
tipo = st.sidebar.selectbox("Tipo de evento", ["Todos", "login_falho", "login_sucesso", "alteracao_arquivo", "conexao_suspeita"])
severidade = st.sidebar.selectbox("Severidade", ["Todas", "baixa", "media", "alta", "critica"])
st.sidebar.divider()
st.sidebar.caption("LAB 01 / As regras são demonstrativas. Nenhuma ação automática de bloqueio é realizada.")
if st.sidebar.button("↻ Atualizar dados", use_container_width=True):
    st.rerun()
st.sidebar.divider()
st.sidebar.markdown("### 🧪 Simulações")
st.sidebar.caption("Os testes apenas registram exemplos fictícios; nenhuma ação real é executada.")
cenario = st.sidebar.selectbox("Escolha um cenário", list(CENARIOS), key="cenario")
st.sidebar.caption(CENARIOS[cenario])
if st.sidebar.button("Executar simulação", type="primary", use_container_width=True):
    enviados = 0
    try:
        for evento in gerar_cenario(cenario):
            retorno = requests.post(f"{API}/eventos", json=evento, timeout=5)
            retorno.raise_for_status()
            enviados += 1
    except requests.RequestException:
        st.sidebar.error(f"Falha de comunicação. {enviados} evento(s) foram registrados antes da interrupção.")
    else:
        st.session_state["simulacao_sucesso"] = f"{cenario}: {enviados} evento(s) fictício(s) registrados."
        st.rerun()
if st.session_state.get("simulacao_sucesso"):
    st.sidebar.success(st.session_state.pop("simulacao_sucesso"))

parametros = {}
if tipo != "Todos":
    parametros["tipo"] = tipo
if severidade != "Todas":
    parametros["severidade"] = severidade
try:
    resposta = requests.get(f"{API}/eventos", params=parametros, timeout=5)
    resposta.raise_for_status()
    eventos = resposta.json()
    alertas_resposta = requests.get(f"{API}/alertas", timeout=5)
    alertas_resposta.raise_for_status()
    alertas = alertas_resposta.json()
except (requests.RequestException, ValueError):
    st.error("API indisponível. Inicie o serviço local para consultar os eventos.")
    st.caption("Consulte o README do projeto para ver como iniciar a API e gerar os dados fictícios.")
    st.stop()

with st.expander("📥 Importar eventos de exemplo em CSV"):
    st.caption("UTF-8, até 1 MB e 1.000 linhas. Colunas: timestamp,ip,tipo,severidade,descricao. A API valida o lote completo.")
    arquivo = st.file_uploader("Selecione um CSV", type=["csv"])
    if arquivo is not None:
        try:
            registros = ler_csv(arquivo.getvalue())
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.write(f"{len(registros)} registro(s) para importar.")
            st.dataframe(pd.DataFrame(registros).head(10), hide_index=True)
            if st.button("Importar lote", type="primary"):
                try:
                    retorno = requests.post(f"{API}/eventos/lote", json=registros, timeout=15)
                    if not retorno.ok:
                        st.error(retorno.json().get("erro", "Falha ao importar."))
                    else:
                        st.session_state["importacao_sucesso"] = f"{retorno.json()['inseridos']} evento(s) importado(s)."
                        st.rerun()
                except (requests.RequestException, ValueError):
                    st.error("Não foi possível confirmar a importação. Confira a API antes de tentar novamente.")
if st.session_state.get("importacao_sucesso"):
    st.success(st.session_state.pop("importacao_sucesso"))
frame = pd.DataFrame(eventos)
st.markdown('<div class="section-label">// 01 — Visão geral</div>', unsafe_allow_html=True)
st.subheader("Seu laboratório em números")
a, b, c = st.columns(3)
a.metric("Eventos filtrados", len(frame))
b.metric("Falhas de login filtradas", int((frame["tipo"] == "login_falho").sum()) if not frame.empty else 0)
c.metric("Alertas por regra · 10 min", len(alertas))
st.caption("Até 1.000 eventos. Os alertas abaixo consideram todos os eventos e não seguem os filtros.")
left, right = st.columns([1.15, 1], gap="large")
with left:
    st.markdown('<div class="section-label">// 02 — Sinais</div>', unsafe_allow_html=True)
    st.subheader("Alertas do laboratório")
    st.caption("Regras em 10 minutos: 5 falhas de login ou 3 alterações de arquivo por IP.")
    if alertas:
        st.dataframe(pd.DataFrame(alertas), hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum alerta nesta janela. Gere eventos fictícios para testar a regra.")
with right:
    st.markdown('<div class="section-label">// 03 — Distribuição</div>', unsafe_allow_html=True)
    st.subheader("Eventos por severidade")
    if not frame.empty:
        contagem = frame.groupby("severidade").size().rename("Eventos")
        st.bar_chart(contagem, color="#59d8e7")
    else:
        st.info("Os indicadores aparecerão após a inclusão de eventos.")
st.markdown('<div class="section-label">// 04 — Linha do tempo</div>', unsafe_allow_html=True)
st.subheader("Eventos ao longo do tempo")
if not frame.empty:
    tempos = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True).dropna()
    if not tempos.empty:
        por_hora = tempos.dt.floor("h").value_counts().sort_index().rename("Eventos")
        st.bar_chart(por_hora, color="#59d8e7")
        st.caption("Eventos filtrados agrupados por hora em UTC.")
    else:
        st.info("Não há datas válidas para a linha do tempo.")
else:
    st.info("A linha do tempo aparecerá quando houver eventos.")

st.markdown('<div class="section-label">// 05 — Relatório</div>', unsafe_allow_html=True)
st.subheader("Relatório de laboratório")
st.caption("O relatório HTML pode ser impresso ou salvo como PDF no navegador.")
relatorio = criar_relatorio(eventos, alertas, {"tipo": tipo, "severidade": severidade})
st.download_button("Baixar relatório HTML", relatorio, file_name="relatorio-cyberguard.html", mime="text/html")
st.markdown('<div class="section-label">// 06 — Investigação</div>', unsafe_allow_html=True)
st.subheader("Eventos registrados")
if not frame.empty:
    cores_eventos = {
        "login_falho": ("#592828", "Falha de login"),
        "login_sucesso": ("#164737", "Login bem-sucedido"),
        "alteracao_arquivo": ("#59431e", "Alteração de arquivo"),
        "conexao_suspeita": ("#3b305f", "Conexão suspeita"),
    }
    st.caption("🔴 Falha de login  ·  🟢 Login bem-sucedido  ·  🟠 Alteração de arquivo  ·  🟣 Conexão suspeita")

    def destacar_evento(linha):
        cor = cores_eventos.get(linha["tipo"], ("#1d3440", ""))[0]
        return [f"background-color: {cor}; color: #ffffff"] * len(linha)

    exibicao = frame.copy()
    exibicao["tipo"] = exibicao["tipo"].map(
        lambda valor: cores_eventos.get(valor, ("", valor))[1]
    )
    # Usa o tipo original para escolher a cor sem alterar os dados da API.
    cores_linhas = pd.DataFrame(frame.apply(destacar_evento, axis=1).tolist(), index=frame.index, columns=frame.columns)
    estilo = exibicao.style.apply(lambda _: cores_linhas, axis=None)
    st.dataframe(estilo, hide_index=True, use_container_width=True)
else:
    st.info("Sem registros para os filtros selecionados. Execute o simulador para gerar exemplos.")
st.caption("Os alertas usam regras simples; esta versão não possui análise por inteligência artificial.")
st.markdown('<div class="footer"><span>◈ <strong>DH73 CYBERGUARD</strong> &nbsp; / &nbsp; Segurança em prática</span><span>Criado por Douglas Honório</span></div>', unsafe_allow_html=True)

