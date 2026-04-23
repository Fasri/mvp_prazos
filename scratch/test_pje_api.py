import requests
import json

def test_pje_api(url):
    print(f"Testando PJE API: {url}")
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
    # TJPE
    test_pje_api("https://pje.tjpe.jus.br/pje-consulta-api/api/v1/processos/02609496620218170001")
    # TJRJ (PJE) - Nem todos os processos do TJRJ estão no PJE, muitos estão no sistema antigo
    test_pje_api("https://tjrj.pje.jus.br/pje-consulta-api/api/v1/processos/00042986620198190001")
