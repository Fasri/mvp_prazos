#!/bin/bash

# Script de Deploy - Monitor Jurídico TJRJ
# Execute: chmod +x deploy.sh && ./deploy.sh

echo "=== Deploy Monitor Jurídico TJRJ ==="

# Atualizar sistema
echo "[1/7] Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
echo "[2/7] Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv git

# Clonar projeto (substitua pela URL do seu repositório)
echo "[3/7] Baixando projeto..."
cd /opt
sudo git clone https://github.com/seu_usuario/mvp_prazos.git
cd mvp_prazos

# Criar ambiente virtual
echo "[4/7] Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "[5/7] Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar firewall
echo "[6/7] Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8501/tcp
sudo ufw --force enable

# Criar serviço systemd
echo "[7/7] Criando serviço systemd..."
sudo tee /etc/systemd/system/monitor-juridico.service > /dev/null <<EOF
[Unit]
Description=Monitor Jurídico TJRJ - API
After=network.target

[Service]
User=opc
WorkingDirectory=/opt/mvp_prazos
ExecStart=/opt/mvp_prazos/venv/bin/python -m uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable monitor-juridico
sudo systemctl restart monitor-juridico

echo ""
echo "=== Deploy concluído! ==="
echo "API: http://$(curl -s ifconfig.me):8000"
echo "Para rodar o Streamlit: source venv/bin/activate && streamlit run app.py"
echo ""
echo "Verificar status: sudo systemctl status monitor-juridico"
echo "Ver logs: sudo journalctl -u monitor-juridico -f"