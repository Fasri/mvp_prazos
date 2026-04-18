import requests
from bs4 import BeautifulSoup

def consultar_processo(numero):
    url = "https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do"

    params = {
        "numProcesso": numero
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    movimentacoes = soup.find_all("tr", class_="fundocinza1")

    if not movimentacoes:
        return None

    ultima = movimentacoes[0].text.strip()

    return ultima

def verificar_novidade(processo_db, nova_movimentacao):
    return processo_db["ultima_movimentacao"] != nova_movimentacao

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def job():
    processos = listar_processos()

    for p in processos:
        nova = consultar_processo(p["numero_processo"])

        if nova and nova != p["ultima_movimentacao"]:
            atualizar_movimentacao(p["id"], nova)
            enviar_whatsapp(p["telefone_cliente"], nova)

scheduler.add_job(job, 'interval', minutes=10)
scheduler.start()

import streamlit as st
import requests

st.title("Monitor de Processos")

numero = st.text_input("Número do processo")
telefone = st.text_input("WhatsApp")

if st.button("Cadastrar"):
    requests.post("http://localhost:8000/processos", json={
        "numero_processo": numero,
        "telefone": telefone
    })

    st.success("Processo cadastrado!")

from fastapi import FastAPI

app = FastAPI()

processos = []

@app.post("/processos")
def criar_processo(data: dict):
    processos.append({
        "numero_processo": data["numero_processo"],
        "telefone": data["telefone"],
        "ultima_movimentacao": None
    })
    return {"status": "ok"}

@app.get("/processos")
def listar():
    return processos
def enviar_whatsapp(numero, mensagem):
    print(f"Enviando para {numero}: {mensagem}")
import requests

def enviar_whatsapp(numero, mensagem):
    url = "https://api.z-api.io/instances/SUA_INSTANCIA/token/SEU_TOKEN/send-text"

    payload = {
        "phone": numero,
        "message": mensagem
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)