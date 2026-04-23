import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8000"


def _start_local_api():
    base_dir = Path(__file__).resolve().parent
    venv_python = base_dir / "venv" / "Scripts" / "python.exe"
    python_exec = str(venv_python if venv_python.exists() else Path(sys.executable))

    subprocess.Popen(
        [python_exec, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(base_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def ensure_api_online():
    try:
        requests.get(f"{API_URL}/processos", timeout=2)
        return True
    except requests.RequestException:
        if not st.session_state.get("api_autostart_attempted", False):
            st.session_state["api_autostart_attempted"] = True
            try:
                _start_local_api()
                for _ in range(10):
                    time.sleep(0.6)
                    try:
                        requests.get(f"{API_URL}/processos", timeout=2)
                        return True
                    except requests.RequestException:
                        continue
            except Exception:
                return False
        return False

st.set_page_config(page_title="Monitor Jurídico Pro", page_icon="⚖️", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #1f2937 !important;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    .css-1r6slb0 { /* Metric value */
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    h1, h2, h3 {
        color: #1a3a5f;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Monitor Jurídico de Processos")
st.markdown("Gestão inteligente de prazos e movimentações processuais.")

# --- BARRA LATERAL: CADASTRO ---
with st.sidebar:
    st.header("📋 Cadastrar Novo Processo")
    with st.form("cadastro_processo"):
        numero = st.text_input("Número do Processo", placeholder="Ex: 0865009-85.2023.8.19.0001")
        telefone = st.text_input("WhatsApp para Notificação", placeholder="Ex: 5521999999999")
        oab = st.text_input("OAB (Opcional)", placeholder="Ex: 123456 RJ")
        submit = st.form_submit_button("Monitorar Processo")
        
        if submit:
            if not numero or not telefone:
                st.error("Preencha o número do processo e WhatsApp.")
            else:
                with st.spinner("Buscando dados no CNJ..."):
                    if not ensure_api_online():
                        st.error("API off-line. Inicie com 'iniciar.bat' ou confirme dependências no venv.")
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/processos",
                                json={
                                    "numero_processo": numero,
                                    "telefone": telefone,
                                    "oab": oab if oab else None,
                                },
                                timeout=20,
                            )
                            if response.status_code == 200:
                                st.success("Processo cadastrado e em monitoramento!")
                                st.rerun()
                            else:
                                st.error(f"Erro ao cadastrar ({response.status_code}).")
                        except requests.RequestException:
                            st.error("API off-line. Inicie com 'iniciar.bat' ou confirme dependências no venv.")

# --- FETCH DATA ---
try:
    if ensure_api_online():
        response = requests.get(f"{API_URL}/processos", timeout=20)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
except requests.RequestException:
    st.warning("⚠️ Não foi possível conectar ao servidor. Verifique se o backend está rodando.")
    df = pd.DataFrame()

if not df.empty:
    # Tratamento de datas
    df['data_tjrj'] = pd.to_datetime(df['data_tjrj'])
    df['data_cnj'] = pd.to_datetime(df['data_cnj'])
    
    # Dias parado (usando CNJ como referência para o KPI geral, ou o mais recente)
    df['dias_parado_tjrj'] = (datetime.now() - df['data_tjrj']).dt.days
    df['dias_parado_cnj'] = (datetime.now() - df['data_cnj']).dt.days
    
    # --- KPIs ---
    st.subheader("📊 Resumo do Monitoramento")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_processos = len(df)
    processos_parados_cnj = len(df[df['dias_parado_cnj'] > 15])
    mov_recentes_tjrj = len(df[df['dias_parado_tjrj'] <= 7])
    varas_unicas = df['vara_cnj'].nunique()

    kpi1.metric("Total de Processos", total_processos)
    kpi2.metric("Críticos (CNJ > 15d)", processos_parados_cnj)
    kpi3.metric("Atualizados (TJRJ 7d)", mov_recentes_tjrj)
    kpi4.metric("Varas (Datajud)", varas_unicas)

    st.divider()

    # --- DUAS TABELAS: TJRJ vs CNJ ---
    tab1, tab2 = st.tabs(["🏛️ Fonte: TJRJ (Site Oficial)", "🌐 Fonte: CNJ (API Datajud)"])

    with tab1:
        st.subheader("Movimentações via Web Scraping TJRJ")
        st.dataframe(df[[
            'numero_processo', 'vara_tjrj', 'mov_tjrj', 'data_tjrj', 'dias_parado_tjrj'
        ]].rename(columns={
            'numero_processo': 'Processo',
            'vara_tjrj': 'Vara/Órgão',
            'mov_tjrj': 'Último Movimento',
            'data_tjrj': 'Data',
            'dias_parado_tjrj': 'Dias s/ Mov.'
        }), use_container_width=True, hide_index=True)
        st.info("💡 Dados obtidos diretamente do portal público do TJRJ.")

    with tab2:
        st.subheader("Movimentações via API Pública Datajud")
        st.dataframe(df[[
            'numero_processo', 'vara_cnj', 'mov_cnj', 'data_cnj', 'dias_parado_cnj'
        ]].rename(columns={
            'numero_processo': 'Processo',
            'vara_cnj': 'Vara/Órgão',
            'mov_cnj': 'Último Movimento',
            'data_cnj': 'Data',
            'dias_parado_cnj': 'Dias s/ Mov.'
        }), use_container_width=True, hide_index=True)
        st.info("💡 Dados consolidados pelo CNJ (pode haver atraso em relação ao site do tribunal).")

    st.divider()
    
    # Gráfico de comparação (opcional)
    st.subheader("📈 Comparativo de Atualização")
    fig_comp = px.bar(df, x='numero_processo', y=['dias_parado_tjrj', 'dias_parado_cnj'],
                     barmode='group', title="Dias sem movimentação: TJRJ vs CNJ",
                     labels={'value': 'Dias Parado', 'variable': 'Fonte', 'numero_processo': 'Processo'})
    st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.info("Nenhum processo cadastrado. Use a barra lateral para começar.")
