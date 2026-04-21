import requests
from datetime import datetime

API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

def consultar_processo(numero):
    # Formata o número (remove pontos e hifens)
    numero_limpo = numero.replace(".", "").replace("-", "")
    
    url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search"
    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Busca com wildcard no meio do número
    parte_meio = numero_limpo[2:8]  # Pega parte do número para buscar
    
    query = {
        "query": {
            "wildcard": {
                "numeroProcesso": f"*{parte_meio}*"
            }
        },
        "size": 20
    }
    
    try:
        response = requests.post(url, headers=headers, json=query, timeout=30)
        
        if response.status_code != 200:
            return {
                "movimentacao": f"Erro na API: {response.status_code}",
                "data": None,
                "vara": None
            }
        
        data = response.json()
        hits = data.get("hits", {}).get("hits", [])
        
        if not hits:
            return {
                "movimentacao": "Processo não encontrado",
                "data": None,
                "vara": None
            }
        
        # Procura o processo exato
        processo_encontrado = None
        for hit in hits:
            proc = hit["_source"]
            num_proc = proc.get("numeroProcesso", "")
            
            # Verifica se é exatamente o processo procurado
            # O número na base tem 20 dígitos
            if numero_limpo in num_proc or num_proc in numero_limpo:
                processo_encontrado = proc
                break
        
        if not processo_encontrado:
            # Se não achou exacto, pega o primeiro que contenha o número
            processo_encontrado = hits[0]["_source"]
        
        # Extrai dados
        vara = processo_encontrado.get("orgaoJulgador", {}).get("nome", "Não identificado")
        
        data_ultima = None
        movimentacao = "Sem movimentações"
        
        movimentos = processo_encontrado.get("movimentos", [])
        if movimentos:
            # Ordena movimentos por dataHora (mais recente primeiro)
            movimentos_ordenados = sorted(
                movimentos, 
                key=lambda x: x.get("dataHora", ""), 
                reverse=True
            )
            ultimo = movimentos_ordenados[0]  # Mais recente
            data_mov = ultimo.get("dataHora")
            if data_mov:
                data_ultima = data_mov[:10]
            
            # Tenta diferentes campos
            mov_nome = ultimo.get("nome", "")
            mov_desc = ultimo.get("descricao", "")
            movimentacao = mov_nome or mov_desc
            if not movimentacao:
                movimentacao = "Movimentação sem descrição"
            movimentacao = movimentacao[:200]
        
        return {
            "movimentacao": movimentacao,
            "data": data_ultima,
            "vara": vara
        }
        
    except Exception as e:
        return {
            "movimentacao": f"Erro: {str(e)[:50]}",
            "data": None,
            "vara": None
        }

if __name__ == "__main__":
    import json
    print(json.dumps(consultar_processo("0893975-35.2023.8.19.0001"), indent=2, default=str))