import requests
from bs4 import BeautifulSoup

def consultar_processo(numero):
    url = "https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do"
    params = {
        "numProcesso": numero
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        movimentacoes = soup.find_all("tr", class_="fundocinza1")
        if not movimentacoes:
            return None
        
        ultima = movimentacoes[0].text.strip()
        # Remove empty lines and fix spacing
        ultima = " ".join(ultima.split())
        return ultima
    except Exception as e:
        print(f"Erro ao consultar processo {numero}: {e}")
        return None
