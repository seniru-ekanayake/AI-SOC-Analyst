import sqlite3
import random
import time
from datetime import datetime

DB_FILE = "data/soc_database.db"

# CONFIGURATION 
WEIGHTS = [70, 15, 10, 5] 

def log_to_db(log_entry):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (timestamp, event_type, user, ip_address, status, risk_level, source, ai_analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        log_entry['timestamp'],
        log_entry['event_type'],
        log_entry['user'],
        log_entry['ip_address'],
        log_entry['status'],
        log_entry['risk_level'],
        "simulation",
        "SKIPPED" 
    ))
    conn.commit()
    conn.close()

def generate_log():
    scenario = random.choices(
        ["normal", "low_risk", "high_risk", "critical"], 
        weights=WEIGHTS, 
        k=1
    )[0]
    
    # Defaults
    users = ["admin", "hr_manager", "ceo", "guest", "developer"]
    selected_user = random.choice(users)
    timestamp = datetime.now().isoformat()
    
    # 2. BUILD LOG BASED ON SCENARIO
    if scenario == "normal":
        return {
            "timestamp": timestamp,
            "event_type": "login_success",
            "user": selected_user,
            "ip_address": f"192.168.1.{random.randint(50, 200)}", # Random workstation
            "status": "success",
            "risk_level": "low"
        }
        
    elif scenario == "low_risk":
        return {
            "timestamp": timestamp,
            "event_type": "login_attempt",
            "user": selected_user,
            "ip_address": f"192.168.1.{random.randint(50, 200)}",
            "status": "failed",
            "risk_level": "low"
        }

    elif scenario == "high_risk":
        return {
            "timestamp": timestamp,
            "event_type": "access_denied",
            "user": "admin", # Usually targets admin
            "ip_address": "192.168.1.15", # MATCHES THREAT_DB (Finance Server)
            "status": "failed",
            "risk_level": "high"
        }

    elif scenario == "critical":
        return {
            "timestamp": timestamp,
            "event_type": "brute_force_attempt",
            "user": "unknown",
            "ip_address": "192.168.1.20", # MATCHES THREAT_DB (Unknown Device)
            "status": "failed",
            "risk_level": "critical"
        }

if __name__ == "__main__":
    print("--- TRAFFIC GENERATOR (50 logs/5mins) ---")
    print(f"--- PROBABILITIES: Normal={WEIGHTS[0]}% | Low={WEIGHTS[1]}% | High={WEIGHTS[2]}% | Crit={WEIGHTS[3]}% ---")
    
    try:
        while True:
            log = generate_log()
            
            if log['risk_level'] == 'critical':
                prefix = "🔴 CRITICAL"
            elif log['risk_level'] == 'high':
                prefix = "🟠 HIGH"
            elif log['status'] == 'success':
                prefix = "🟢 NORMAL"
            else:
                prefix = "🟡 LOW"

            print(f" [{prefix}] Generated log for {log['user']}")
            log_to_db(log)
            
            time.sleep(random.uniform(5, 7))
            
    except KeyboardInterrupt:
        print("\nStopping generator...")