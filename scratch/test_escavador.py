import requests
from bs4 import BeautifulSoup

def test_escavador(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://www.escavador.com/processos/{numero_limpo}"
    print(f"Testando Escavador: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Sucesso!")
            if "Publicado edital" in response.text:
                print("Encontrou o movimento no Escavador!")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_escavador("0026053-98.2009.8.19.0001")
