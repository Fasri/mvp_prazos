import requests
import json

def test_tjrj_session_modern(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www3.tjrj.jus.br/consultaprocessual/",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        # 1. Home
        print("Acessando home...")
        session.get("https://www3.tjrj.jus.br/consultaprocessual/", headers=headers, timeout=10)
        
        # 2. API
        # Tenta o endpoint que o front costuma chamar
        url = f"https://www3.tjrj.jus.br/consultaprocessual/api/publica/processos/consulta-publica/{numero_limpo}"
        print(f"Testando API Modern: {url}")
        response = session.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Sucesso!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_session_modern("00260539820098190001")
