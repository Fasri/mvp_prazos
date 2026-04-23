import requests
from bs4 import BeautifulSoup

def test_tjrj_clean(numero):
    url = f"https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaMov.do?numProcesso={numero}"
    print(f"Testando TJRJ Clean: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Sucesso!")
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_clean("0343049-30.2011.8.19.0001")
