from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
from contextlib import asynccontextmanager

import database
from scraper import consultar_processo
from whatsapp import enviar_whatsapp

# Inicializa o banco de dados
database.init_db()

class ProcessoRequest(BaseModel):
    numero_processo: str
    telefone: str
    oab: str | None = None

def verificar_movimentacoes():
    print("Iniciando verificação de movimentações...")
    processos = database.listar_processos()
    for p in processos:
        numero = p["numero_processo"]
        ultima_db = p["ultima_movimentacao"]
        
        info = consultar_processo(numero)
        
        if info and info["movimentacao"] != ultima_db:
            print(f"Nova movimentação encontrada para o processo {numero}")
            database.atualizar_processo_full(
                p["id"], 
                info["movimentacao"], 
                info["data"], 
                info["vara"]
            )
            
            mensagem = f"Nova movimentação no processo {numero}:\n\n{info['movimentacao']}"
            enviar_whatsapp(p["telefone_cliente"], mensagem)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(verificar_movimentacoes, 'interval', minutes=10)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/processos")
def criar_processo(data: ProcessoRequest):
    database.add_processo(data.numero_processo, data.telefone, data.oab)
    
    # Faz uma verificação inicial logo ao cadastrar
    info = consultar_processo(data.numero_processo)
    if info:
        processos = database.listar_processos()
        for p in processos:
            if p["numero_processo"] == data.numero_processo and p["telefone_cliente"] == data.telefone:
                database.atualizar_processo_full(
                    p["id"], 
                    info["movimentacao"], 
                    info["data"], 
                    info["vara"]
                )
                break
                
    return {"status": "ok", "mensagem": "Processo cadastrado com sucesso!"}

@app.get("/processos")
def listar():
    return database.listar_processos()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
