import requests

def test_tjrj_initial_state(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://www3.tjrj.jus.br/consultaprocessual/#/consultapublica?numProcessoCNJ={numero_limpo}"
    print(f"Testando: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        # Procura por qualquer dado no HTML (JSON embutido?)
        if "0026053" in response.text:
            print("Encontrou o número no HTML!")
        else:
            print("Não encontrou o número no HTML. É 100% JS.")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_initial_state("0026053-98.2009.8.19.0001")
