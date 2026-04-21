import sqlite3

def update_db():
    conn = sqlite3.connect('processos.db')
    cursor = conn.cursor()
    
    # Try to add columns if they don't exist
    columns_to_add = [
        ("data_ultima_movimentacao", "DATE"),
        ("vara", "TEXT"),
        ("data_cadastro", "DATETIME DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE processos ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists or error occurred.")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_db()
