import requests
from bs4 import BeautifulSoup

def test_fetch():
    numero = "0865009-85.2023.8.19.0001"
    url = f"https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do?numProcesso={numero}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=20)
        print(f"Status: {response.status_code}")
        with open("tjrj_sample.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved to tjrj_sample.html")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch()
