import requests

def test_tjrj_modern(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://www3.tjrj.jus.br/consultaprocessual/api/publica/processos/numero/{numero_limpo}"
    print(f"Testando TJRJ Modern: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_modern("0343049-30.2011.8.19.0001")
