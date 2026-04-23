import requests
import json

def test_tjpe_api(numero):
    # Formato: 0260949-66.2021.8.17.0001
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://www.tjpe.jus.br/consultaprocessualv2/api/v1/processos/{numero_limpo}"
    print(f"Testando TJPE API: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjpe_api("0260949-66.2021.8.17.0001")
