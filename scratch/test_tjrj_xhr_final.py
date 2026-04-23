import requests
import json

def test_tjrj_xhr_final(numero):
    numero_limpo = numero.replace(".", "").replace("-", "")
    url = f"https://www3.tjrj.jus.br/consultaprocessual/api/publica/processos/consulta-publica/{numero_limpo}"
    print(f"Testando TJRJ XHR Final: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www3.tjrj.jus.br/consultaprocessual/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    try:
        # Tenta primeiro pegar um cookie da home
        session = requests.Session()
        session.get("https://www3.tjrj.jus.br/consultaprocessual/", headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        
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
    test_tjrj_xhr_final("00260539820098190001")
