import sqlite3
from datetime import datetime, timedelta

def insert_dummy():
    conn = sqlite3.connect('processos.db')
    # Stuck process
    stuck_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
    conn.execute('''
        INSERT INTO processos (numero_processo, telefone_cliente, ultima_movimentacao, data_ultima_movimentacao, vara)
        VALUES (?, ?, ?, ?, ?)
    ''', ("0000001-01.2023.8.19.0001", "5521999998888", "Aguardando Despacho", stuck_date, "2ª Vara Cível"))
    
    # Recent process
    recent_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    conn.execute('''
        INSERT INTO processos (numero_processo, telefone_cliente, ultima_movimentacao, data_ultima_movimentacao, vara)
        VALUES (?, ?, ?, ?, ?)
    ''', ("0000002-02.2023.8.19.0001", "5521999997777", "Publicado no DJE", recent_date, "3ª Vara de Família"))
    
    conn.commit()
    conn.close()
    print("Dummy data inserted.")

if __name__ == "__main__":
    insert_dummy()
