import requests
from bs4 import BeautifulSoup
import time

def test_tjrj_session(numero):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Primeiro acessa a home para pegar cookies
    try:
        session.get("https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do", headers=headers, timeout=10)
        time.sleep(1)
        
        # Agora tenta a consulta
        url = f"https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do?numProcesso={numero}"
        print(f"Testando: {url}")
        response = session.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            if "não foi encontrado" in response.text.lower():
                print("Processo não encontrado no legacy.")
            else:
                print("Sucesso! Conteúdo recebido.")
                # print(response.text[:1000])
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_session("0343049-30.2011.8.19.0001")
