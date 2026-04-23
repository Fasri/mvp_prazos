import requests
import json

def test_tjpe_srv01(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://srv01.tjpe.jus.br/consultaprocessualunificada/api/consulta-publica/{numero_limpo}"
    print(f"Testando TJPE srv01: {url}")
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
    test_tjpe_srv01("02609496620218170001")
