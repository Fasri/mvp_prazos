from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
from contextlib import asynccontextmanager

import asyncio
import database
from scraper import consultar_processo as consultar_cnj
from scraper_tjrj_pw import consultar_tjrj_pw
from whatsapp import enviar_whatsapp

# Inicializa o banco de dados
database.init_db()

class ProcessoRequest(BaseModel):
    numero_processo: str
    telefone: str
    oab: str | None = None

def verificar_movimentacoes():
    print("Iniciando verificação de movimentações (TJRJ e CNJ)...")
    processos = database.listar_processos()
    for p in processos:
        numero = p["numero_processo"]
        
        # 1. Scrape TJRJ (via Playwright)
        print(f"Buscando TJRJ para {numero}...")
        try:
            info_tjrj = asyncio.run(consultar_tjrj_pw(numero))
        except Exception as e:
            print(f"Erro no scraper TJRJ PW para {numero}: {e}")
            info_tjrj = None

        if info_tjrj and info_tjrj["movimentacao"] != p.get("mov_tjrj"):
            print(f"Nova movimentação TJRJ para o processo {numero}")
            database.atualizar_tjrj(p["id"], info_tjrj["movimentacao"], info_tjrj["data"], info_tjrj["vara"])
            
            # Notifica se for mudança real
            if p.get("mov_tjrj") and info_tjrj["movimentacao"] != "Sem movimentos":
                mensagem = f"🔔 [TJRJ] Nova movimentação no processo {numero}:\n\n{info_tjrj['movimentacao']}"
                enviar_whatsapp(p["telefone_cliente"], mensagem)

        # 2. Scrape CNJ
        info_cnj = consultar_cnj(numero)
        if info_cnj and info_cnj["movimentacao"] != p.get("mov_cnj"):
            print(f"Nova movimentação CNJ para o processo {numero}")
            database.atualizar_cnj(p["id"], info_cnj["movimentacao"], info_cnj["data"], info_cnj["vara"])
            
            # Notifica se for mudança real
            if p.get("mov_cnj"):
                mensagem = f"🔔 [CNJ] Nova movimentação no processo {numero}:\n\n{info_cnj['movimentacao']}"
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
    processos = database.listar_processos()
    for p in processos:
        if p["numero_processo"] == data.numero_processo and p["telefone_cliente"] == data.telefone:
            # TJRJ
            try:
                info_tjrj = asyncio.run(consultar_tjrj_pw(data.numero_processo))
                if info_tjrj:
                    database.atualizar_tjrj(p["id"], info_tjrj["movimentacao"], info_tjrj["data"], info_tjrj["vara"])
            except: pass
            
            # CNJ
            info_cnj = consultar_cnj(data.numero_processo)
            if info_cnj:
                database.atualizar_cnj(p["id"], info_cnj["movimentacao"], info_cnj["data"], info_cnj["vara"])
            break
                
    return {"status": "ok", "mensagem": "Processo cadastrado e em monitoramento duplo!"}

@app.get("/processos")
def listar():
    return database.listar_processos()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
