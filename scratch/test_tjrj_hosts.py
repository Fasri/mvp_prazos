import requests

def test_tjrj_hosts(numero):
    hosts = ["www1", "www2", "www3", "www4"]
    for host in hosts:
        url = f"https://{host}.tjrj.jus.br/consultaProcessoWebV2/consultaProcesso.do?numProcesso={numero}"
        print(f"Testando {host}...")
        try:
            res = requests.get(url, timeout=5)
            print(f"Status {host}: {res.status_code}")
        except:
            print(f"Erro no {host}")

if __name__ == "__main__":
    test_tjrj_hosts("0026053-98.2009.8.19.0001")
