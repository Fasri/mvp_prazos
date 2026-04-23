import requests
from bs4 import BeautifulSoup
import json

def scrape_tjrj_legacy(numero):
    # Formato: 0038656-23.2020.8.19.0001
    url = "https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do"
    params = {"numProcesso": numero}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"Status {response.status_code}"}
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Tenta encontrar a vara
        vara = "Não encontrada"
        labels = soup.find_all("td", class_="label")
        for label in labels:
            if "Órgão Julgador" in label.text or "Comarca" in label.text:
                val = label.find_next_sibling("td")
                if val:
                    vara = val.text.strip()
                    break
        
        # Tenta encontrar a última movimentação
        # Na versão legacy, costuma estar em tabelas com classe 'fundocinza1' ou similar
        movimentacoes = []
        rows = soup.find_all("tr", class_=["fundocinza1", "fundobranco"])
        for row in rows:
            tds = row.find_all("td")
            if len(tds) >= 2:
                data = tds[0].text.strip()
                mov = tds[1].text.strip()
                if data and mov:
                    movimentacoes.append({"data": data, "movimentacao": mov})
        
        return {
            "vara": vara,
            "movimentacoes": movimentacoes[:5], # Pega as 5 últimas
            "source": "TJRJ Legacy"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(json.dumps(scrape_tjrj_legacy("0038656-23.2020.8.19.0001"), indent=2))
