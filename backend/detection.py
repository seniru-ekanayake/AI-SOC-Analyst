import sqlite3
import time
import json
import os

DB_FILE = "data/soc_database.db"
THREAT_DB_FILE = "data/threat_db.json"

try:
    with open(THREAT_DB_FILE, "r") as f:
        THREAT_DB = json.load(f)
except:
    THREAT_DB = {"known_ips": {}, "users": {}}

def enrich_data(ip, user):
    ip_info = THREAT_DB["known_ips"].get(ip, {"description": "Unregistered IP", "risk": "unknown"})
    user_info = THREAT_DB["users"].get(user, {"role": "Unknown", "location": "Unknown"})
    return ip_info, user_info

def monitor_db():
    print("TRIAGING LOGS (Async Mode)")
    
    last_processed_id = 0
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Read new logs
            c.execute("SELECT * FROM logs WHERE id > ?", (last_processed_id,))
            new_logs = c.fetchall()
            
            for row in new_logs:
                # Unpack the row
                log_id, timestamp, event_type, user, ip, status, risk, source, ai_analysis = row
                last_processed_id = log_id
                
                # CHECK
                ip_info, _ = enrich_data(ip, user)
                
                # Logic
                if status == "failed" and ip_info['risk'] in ['high', 'critical']:
                    print(f" 🚨 ALERT [ID: {log_id}] -> Marking for AI Agent!")
                    
                    c.execute("UPDATE logs SET ai_analysis = 'PENDING' WHERE id = ?", (log_id,))
                    conn.commit() 
                
            conn.close()
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    monitor_db()