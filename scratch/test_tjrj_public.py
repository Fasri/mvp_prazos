import requests
import json

def test_tjrj_public(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://www3.tjrj.jus.br/consultaprocessual/api/publica/processos/consulta-publica/{numero_limpo}"
    print(f"Testando TJRJ Public: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www3.tjrj.jus.br",
        "Referer": "https://www3.tjrj.jus.br/consultaprocessual/"
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
    test_tjrj_public("03430493020118190001")
