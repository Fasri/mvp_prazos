# Deploy Monitor Jurídico TJRJ - VPS Oracle

## 1. Criar instância na Oracle Cloud

1. Acesse: https://cloud.oracle.com/
2. Faça login ou crie uma conta
3. Vá em **Compute** → **Instances**
4. Clique em **Create Instance**
5. Configure:
   - **Name**: `monitor-juridico`
   - **Image**: Ubuntu 22.04 LTS
   - **Shape**: Selecione Always Free Eligible (ARM ou AMD)
   - **SSH Keys**: Gere ou use uma chave existente
6. Clique em **Create** e aguarde iniciar

## 2. Conectar ao servidor

Abra o terminal (PowerShell ou Git Bash no Windows):

```bash
ssh -i sua_chave.pem ubuntu@<IP_DO_SERVIDOR>
```

## 3. Atualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
```

## 4. Instalar dependências

```bash
sudo apt install -y python3 python3-pip python3-venv git ufw net-tools iptables-persistent
```

## 5. Criar diretório e ambiente virtual

```bash
cd /home/ubuntu
mkdir -p monitor-juridico
cd monitor-juridico
python3 -m venv venv
source venv/bin/activate
```

## 6. Instalar dependências Python

```bash
pip install --upgrade pip
pip install fastapi uvicorn streamlit pandas plotly requests beautifulsoup4 apscheduler pydantic
```

## 7. Enviar arquivos do projeto

Você pode fazer de duas formas:

### Opção A: Git (recomendado)
```bash
# Vá para a pasta do projeto
cd /home/ubuntu/monitor-juridico

# Clone o conteúdo DIRETAMENTE na pasta atual (o ponto final é importante!)
git clone https://github.com/seu_usuario/seu_repositorio.git .
```

### Opção B: SFTP (FileZilla/WinSCP)
- Conecte no servidor usando SFTP
- Envie os arquivos: `api.py`, `app.py`, `database.py`, `scraper.py`

## 8. Configurar firewall

### 8.1 Firewall do Ubuntu (UFW)
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # API
sudo ufw allow 8501/tcp  # Streamlit
sudo ufw --force enable
```

### 8.2 Firewall da Oracle Cloud (IPtables)
*As instâncias Oracle precisam deste passo extra para liberar o tráfego interno:*
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save
```

### 8.3 Painel Web (Security List)
**Importante:** Vá no painel da Oracle Cloud -> Networking -> Security Lists e adicione uma "Ingress Rule" para as portas 8000 e 8501 (Source: 0.0.0.0/0).

## 9. Criar serviço systemd

```bash
sudo nano /etc/systemd/system/monitor-juridico.service
```

Cole este conteúdo:

```ini
[Unit]
Description=Monitor Jurídico TJRJ - API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/monitor-juridico
ExecStart=/home/ubuntu/monitor-juridico/venv/bin/python -m uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Salve (Ctrl+O, Enter, Ctrl+X).

## 10. Ativar serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor-juridico
sudo systemctl start monitor-juridico
sudo systemctl status monitor-juridico
```

## 11. Acessar

- **API**: `http://<IP>:8000`
- **Streamlit**: `http://<IP>:8501` (.execute abaixo)

## 12. Rodar Streamlit (opcional)

```bash
cd /home/ubuntu/monitor-juridico
source venv/bin/activate
streamlit run app.py --server.address 0.0.0.0
```

---

## Comandos úteis

```bash
# Ver logs da API
sudo journalctl -u monitor-juridico -f

# Reiniciar API
sudo systemctl restart monitor-juridico

# Parar API
sudo systemctl stop monitor-juridico
```

---

## Observações

1. **IP Dinâmico**: O IP da Oracle pode mudar ao reiniciar. Configure um IP estático se necessário.

2. **Streamlit**: O Streamlit não está configurado como serviço. Para rodar 24h, crie outro serviço systemd ou use `nohup`.

3. **Dados**: O banco `processos.db` fica no diretório do projeto. Faça backup regularmente.

4. **Reiniciar após reboot**: A API inicia automaticamente, mas o Streamlit precisa ser iniciado manualmente ou configurado como serviço adicional.