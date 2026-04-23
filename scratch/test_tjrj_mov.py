import requests
from bs4 import BeautifulSoup

def test_tjrj_mov(numero):
    url = f"https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaMov.do?v=2&numProcesso={numero}"
    print(f"Testando TJRJ Mov: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Procura por linhas de movimentação
            rows = soup.find_all("tr")
            for row in rows[:10]:
                print(row.text.strip())
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tjrj_mov("0343049-30.2011.8.19.0001")
