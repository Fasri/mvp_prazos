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
                with st.spinner("Buscando dados no TJRJ..."):
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
    # Tratamento de datas - lida com valores nulos convertendo para data mínima
    df['data_ultima_movimentacao'] = pd.to_datetime(df['data_ultima_movimentacao'])
    df['dias_parado'] = (datetime.now() - df['data_ultima_movimentacao']).dt.days
    df['dias_parado'] = df['dias_parado'].fillna(0).astype(int)
    
    # --- KPIs ---
    st.subheader("📊 Indicadores de Desempenho (KPIs)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_processos = len(df)
    processos_parados = len(df[df['dias_parado'] > 15])
    mov_recentes = len(df[df['dias_parado'] <= 7])
    varas_unicas = df['vara'].nunique()

    kpi1.metric("Total de Processos", total_processos)
    kpi2.metric("Parados > 15 dias", processos_parados, delta=f"{processos_parados} críticos", delta_color="inverse")
    kpi3.metric("Atualizados (7 dias)", mov_recentes)
    kpi4.metric("Varas Atendidas", varas_unicas)

    st.divider()

    col_graf, col_stuck = st.columns([1, 1])

    with col_graf:
        st.subheader("🏢 Distribuição por Vara")
        # Agrupa por vara para garantir que não haja conflitos de "non-leaves"
        df_tree = df.copy()
        df_tree['vara'] = df_tree['vara'].fillna('Não Identificada').replace('', 'Não Identificada')
        df_counts = df_tree.groupby('vara').size().reset_index(name='quantidade')
        
        if not df_counts.empty:
            try:
                fig = px.treemap(df_counts, path=['vara'], values='quantidade',
                                 title="Volume por Órgão Julgador",
                                 color='quantidade',
                                 color_continuous_scale='Blues')
                fig.update_layout(margin=dict(t=30, l=10, r=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráfico: {e}")
        else:
            st.info("Aguardando extração de dados das varas...")

    with col_stuck:
        st.subheader("🚨 Processos Parados (> 15 dias)")
        df_stuck = df[df['dias_parado'] > 15][['numero_processo', 'ultima_movimentacao', 'dias_parado']]
        if not df_stuck.empty:
            st.dataframe(df_stuck, use_container_width=True, hide_index=True)
        else:
            st.success("Nenhum processo parado há mais de 15 dias! ✅")

    st.divider()

    # --- TABELA GERAL ---
    st.subheader("📋 Todos os Processos Monitorados")
    st.dataframe(df[[
        'numero_processo', 'vara', 'ultima_movimentacao', 'data_ultima_movimentacao', 'dias_parado'
    ]].rename(columns={
        'numero_processo': 'Processo',
        'vara': 'Vara/Órgão',
        'ultima_movimentacao': 'Último Movimento',
        'data_ultima_movimentacao': 'Data',
        'dias_parado': 'Dias s/ Mov.'
    }), use_container_width=True, hide_index=True)

else:
    st.info("Nenhum processo cadastrado. Use a barra lateral para começar.")
