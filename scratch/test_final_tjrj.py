import asyncio
from scraper_tjrj_pw import consultar_tjrj_pw
import json

async def test():
    numero = "0257058-08.2019.8.19.0001"
    print(f"--- TESTE SCRAPER TJRJ PW ---")
    print(f"Processo: {numero}")
    resultado = await consultar_tjrj_pw(numero)
    print("\nRESULTADO FINAL:")
    print(json.dumps(resultado, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test())
