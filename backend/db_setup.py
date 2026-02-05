import sqlite3

DB_FILE = "data/soc_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    print("SETTING UP SQLITE)")
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            user TEXT,
            ip_address TEXT,
            status TEXT,
            risk_level TEXT,
            source TEXT,
            ai_analysis TEXT DEFAULT 'PENDING'
        )
    ''')
    
    print(" [✓] Table 'logs' created successfully.")
    
    conn.commit()
    conn.close()
    print(f" [✓] Database {DB_FILE} is ready.")

if __name__ == "__main__":
    init_db()