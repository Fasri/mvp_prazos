import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Monitor de Processos TJRJ", page_icon="⚖️", layout="wide")

st.title("⚖️ Monitor de Processos - TJRJ")
st.markdown("Cadastre os processos que você deseja monitorar e receba atualizações via WhatsApp.")

with st.form("cadastro_processo"):
    col1, col2 = st.columns(2)
    with col1:
        numero = st.text_input("Número do Processo", placeholder="Ex: 0266014-93.2018.8.19.0001")
    with col2:
        telefone = st.text_input("Seu WhatsApp", placeholder="Ex: 5521999999999")
    
    submit = st.form_submit_button("Cadastrar Processo")
    
    if submit:
        if not numero or not telefone:
            st.error("Por favor, preencha todos os campos.")
        else:
            with st.spinner("Cadastrando e buscando primeira movimentação..."):
                try:
                    response = requests.post(f"{API_URL}/processos", json={
                        "numero_processo": numero,
                        "telefone": telefone
                    })
                    if response.status_code == 200:
                        st.success(response.json()["mensagem"])
                    else:
                        st.error("Erro ao cadastrar processo.")
                except Exception as e:
                    st.error("Erro de conexão com a API: certifique-se que o backend (api.py) está rodando.")

st.divider()

st.subheader("Processos Monitorados")
if st.button("Atualizar Lista"):
    pass # O rerun da página já cuida disso

try:
    response = requests.get(f"{API_URL}/processos")
    if response.status_code == 200:
        processos = response.json()
        if processos:
            df = pd.DataFrame(processos)
            df = df.rename(columns={
                "id": "ID",
                "numero_processo": "Processo",
                "telefone_cliente": "WhatsApp",
                "ultima_movimentacao": "Última Movimentação"
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum processo cadastrado ainda.")
except Exception:
    st.warning("Não foi possível carregar a lista de processos. A API está rodando?")
