import requests

def enviar_whatsapp(numero, mensagem):
    # Configurações da Evolution API
    base_url = "SUA_URL_DA_EVOLUTION_API" # Ex: https://api.seudominio.com
    instance = "SUA_INSTANCIA"
    api_key = "SEU_API_KEY"
    
    url = f"{base_url}/message/sendText/{instance}"
    
    # Se ainda estiver usando os placeholders, apenas simula no console
    if "SUA_URL" in base_url or "SUA_INSTANCIA" in instance:
        print(f"[SIMULAÇÃO EVOLUTION API] Mensagem para {numero}: {mensagem}")
        return True
    
    payload = {
        "number": numero,
        "text": mensagem
    }
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            print(f"WhatsApp enviado com sucesso para {numero}")
            return True
        else:
            print(f"Erro ao enviar WhatsApp pela Evolution API. Status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"Erro de conexão com a Evolution API: {e}")
        return False

