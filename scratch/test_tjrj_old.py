import requests
from bs4 import BeautifulSoup

def test_tjrj_old_number(old_numero):
    # Formato: 2009.001.026343-0 -> 20090010263430
    numero_limpo = old_numero.replace(".", "").replace("-", "")
    url = f"https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do?numProcesso={numero_limpo}"
    print(f"Testando TJRJ com número antigo: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            if "não foi encontrado" in response.text.lower():
                print("Não encontrado.")
            else:
                print("Sucesso! Conteúdo recebido.")
                # print(response.text[:500])
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_old_number("2009.001.026343-0")
