import requests
import json

def test_tjrj_api(numero_cnj):
    # Formato esperado: 08939753520238190001
    numero_limpo = numero_cnj.replace(".", "").replace("-", "")
    
    # URL provável da API interna (baseada em padrões comuns de SPAs de tribunais)
    # Vamos tentar o endpoint que o front-end costuma usar
    url = f"https://www3.tjrj.jus.br/consultaprocessual/api/publica/processos/{numero_limpo}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www3.tjrj.jus.br",
        "Referer": "https://www3.tjrj.jus.br/consultaprocessual/"
    }
    
    print(f"Testando URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Sucesso!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Falha ao acessar a API direta.")
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_api("0893975-35.2023.8.19.0001")
