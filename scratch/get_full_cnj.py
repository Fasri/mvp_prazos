import requests
import json

API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

def get_full_cnj_json(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search"
    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }
    query = {
        "query": {
            "match": {
                "numeroProcesso": numero_limpo
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=query, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}", "body": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    numero = "0101022-60.2020.5.01.0483"
    resultado = get_full_cnj_json(numero)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
