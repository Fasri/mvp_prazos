#!/bin/bash

echo "=== Deploy Monitor Jurídico TJRJ ==="

# Atualizar sistema (isso precisa de sudo)
echo "[1/8] Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
echo "[2/8] Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv git

# Criar diretório do projeto
echo "[3/8] Preparando projeto..."
cd /home/ubuntu
mkdir -p monitor-juridico
cd monitor-juridico

# Criar ambiente virtual (SEM sudo!)
echo "[4/8] Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip e instalar dependências (SEM sudo!)
echo "[5/8] Instalando Python packages..."
pip install --upgrade pip
pip install fastapi uvicorn streamlit pandas plotly requests beautifulsoup4 apscheduler pydantic

# Configurar firewall
echo "[6/8] Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp  
sudo ufw allow 8501/tcp
sudo ufw --force enable

# Criar serviço systemd
echo "[7/8] Criando serviço..."
sudo tee /etc/systemd/system/monitor-juridico.service > /dev/null << 'EOF'
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
EOF

# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable monitor-juridico
sudo systemctl restart monitor-juridico

# Obter IP do servidor
IP=$(curl -s ifconfig.me)

echo ""
echo "=== Deploy concluído! ==="
echo "API: http://$IP:8000"
echo ""
echo "Comandos úteis:"
echo "  Ver status:   sudo systemctl status monitor-juridico"
echo "  Ver logs:     sudo journalctl -u monitor-juridico -f"
echo "  Reiniciar:    sudo systemctl restart monitor-juridico"