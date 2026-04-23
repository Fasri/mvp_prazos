import json
from scraper import consultar_processo

def test_cnj_api(numero):
    print(f"Testando CNJ para {numero}...")
    resultado = consultar_processo(numero)
    print(json.dumps(resultado, indent=2))

if __name__ == "__main__":
    test_cnj_api("0038656-23.2020.8.19.0001")
