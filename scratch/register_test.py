import requests

def register():
    url = "http://localhost:8000/processos"
    data = {
        "numero_processo": "0865009-85.2023.8.19.0001",
        "telefone": "5521999999999"
    }
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    register()
