import sqlite3

def migrate():
    conn = sqlite3.connect('processos.db')
    cursor = conn.cursor()
    
    # Lista de colunas a adicionar
    novas_colunas = [
        ("mov_tjrj", "TEXT"),
        ("data_tjrj", "DATE"),
        ("vara_tjrj", "TEXT"),
        ("mov_cnj", "TEXT"),
        ("data_cnj", "DATE"),
        ("vara_cnj", "TEXT")
    ]
    
    for col_name, col_type in novas_colunas:
        try:
            cursor.execute(f"ALTER TABLE processos ADD COLUMN {col_name} {col_type}")
            print(f"Coluna {col_name} adicionada.")
        except sqlite3.OperationalError:
            print(f"Coluna {col_name} já existe.")
            
    conn.commit()
    conn.close()
    print("Migração concluída.")

if __name__ == "__main__":
    migrate()
