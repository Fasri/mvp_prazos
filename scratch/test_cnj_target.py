import json
from scraper import consultar_processo

def test_cnj_target(numero):
    print(f"Buscando no CNJ: {numero}")
    res = consultar_processo(numero)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    test_cnj_target("0026053-98.2009.8.19.0001")
