import sqlite3

def get_db_connection():
    conn = sqlite3.connect('processos.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Tabela unificada para cadastro, mas vamos separar os resultados
    conn.execute('''
        CREATE TABLE IF NOT EXISTS processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_processo TEXT NOT NULL,
            telefone_cliente TEXT NOT NULL,
            oab TEXT,
            
            -- Dados TJRJ
            mov_tjrj TEXT,
            data_tjrj DATE,
            vara_tjrj TEXT,
            
            -- Dados CNJ
            mov_cnj TEXT,
            data_cnj DATE,
            vara_cnj TEXT,
            
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_processo(numero, telefone, oab=None):
    conn = get_db_connection()
    existing = conn.execute('SELECT id FROM processos WHERE numero_processo = ? AND telefone_cliente = ?', (numero, telefone)).fetchone()
    if not existing:
        conn.execute('INSERT INTO processos (numero_processo, telefone_cliente, oab) VALUES (?, ?, ?)', (numero, telefone, oab))
        conn.commit()
    conn.close()

def listar_processos():
    conn = get_db_connection()
    processos = conn.execute('SELECT * FROM processos').fetchall()
    conn.close()
    return [dict(p) for p in processos]

def atualizar_tjrj(processo_id, mov, data, vara):
    conn = get_db_connection()
    conn.execute('''
        UPDATE processos 
        SET mov_tjrj = ?, data_tjrj = ?, vara_tjrj = ?
        WHERE id = ?
    ''', (mov, data, vara, processo_id))
    conn.commit()
    conn.close()

def atualizar_cnj(processo_id, mov, data, vara):
    conn = get_db_connection()
    conn.execute('''
        UPDATE processos 
        SET mov_cnj = ?, data_cnj = ?, vara_cnj = ?
        WHERE id = ?
    ''', (mov, data, vara, processo_id))
    conn.commit()
    conn.close()
