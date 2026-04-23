import requests

def test_tjrj_mobile(numero):
    url = f"https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaMovMobile.do?numProcesso={numero}"
    print(f"Testando TJRJ Mobile: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Sucesso!")
            print(response.text[:500])
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_mobile("0343049-30.2011.8.19.0001")
