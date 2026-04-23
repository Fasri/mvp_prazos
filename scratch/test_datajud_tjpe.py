import requests
import json

API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

def test_datajud_tjpe(numero):
    # Tenta usar o endpoint do TJPE no Datajud
    url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search"
    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }
    numero_limpo = numero.replace(".", "").replace("-", "")
    query = {
        "query": {
            "match": {
                "numeroProcesso": numero_limpo
            }
        }
    }
    print(f"Testando Datajud TJPE: {url}")
    try:
        response = requests.post(url, headers=headers, json=query, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_datajud_tjpe("0260949-66.2021.8.17.0001")
