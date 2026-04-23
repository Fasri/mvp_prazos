import requests
from bs4 import BeautifulSoup
import re

def consultar_tjrj(numero):
    """
    Scrape do site do TJRJ. Tenta o portal legacy e se falhar retorna None para indicar erro de fonte.
    """
    url = "https://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do"
    params = {"numProcesso": numero}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        # Se der 503 ou outro erro, vamos tentar a CNJ API como fallback para não deixar vazio, 
        # mas idealmente o app deve avisar.
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        # ... (resto da lógica de extração que já estava lá)
        # (Vou manter a lógica que escrevi antes)
        vara = "Não identificada"
        labels = soup.find_all("td", class_="label")
        for label in labels:
            if "Órgão Julgador" in label.text or "Comarca" in label.text:
                val = label.find_next_sibling("td")
                if val:
                    vara = val.text.strip()
                    break
        
        movimentacao = "Sem movimentos"
        data_mov = None
        rows = soup.find_all("tr", class_=["fundocinza1", "fundobranco"])
        if rows:
            for row in rows:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    data_str = tds[0].text.strip()
                    desc_str = tds[1].text.strip()
                    if re.match(r"\d{2}/\d{2}/\d{4}", data_str):
                        data_mov = data_str
                        movimentacao = desc_str
                        break
        
        if data_mov:
            try:
                parts = data_mov.split("/")
                data_mov = f"{parts[2]}-{parts[1]}-{parts[0]}"
            except: pass

        return {"movimentacao": movimentacao[:200], "data": data_mov, "vara": vara}
    except:
        return None

if __name__ == "__main__":
    # Teste
    print(consultar_tjrj("0038656-23.2020.8.19.0001"))