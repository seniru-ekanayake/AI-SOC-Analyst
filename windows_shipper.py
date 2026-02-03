import win32evtlog
import sqlite3
import time
import os

# CONFIGURATION
DB_FILE = "soc_database.db"

print("--- AI SOC: ACTIVE DEFENSE (SQLite Connected) ---")
print("--- MODE: SURGICAL DEFENSE (Target Specific PIDs) ---")

failure_tracker = {}

def log_to_db(log_entry):
    try:
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
            log_entry['source'],
            "PENDING" if log_entry['risk_level'] == 'critical' else "SKIPPED"
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging to DB: {e}")

def neutralize_threat(user_name, pid=None):
    print(f" [!!!] TERMINATOR ACTIVATED against: {user_name}")
    if pid and pid != "0":
        try:
            os.system(f"taskkill /F /PID {pid} >nul 2>&1")
            print(f"   [✓] THREAT ELIMINATED: Process {pid} killed.")
            return "THREAT_ELIMINATED"
        except:
            pass
    return "monitoring"

def should_trigger_defense(user):
    current_time = time.time()
    if user not in failure_tracker: failure_tracker[user] = []
    failure_tracker[user].append(current_time)
    failure_tracker[user] = [t for t in failure_tracker[user] if current_time - t < 10]
    return len(failure_tracker[user]) >= 3

def listen():
    server = 'localhost'
    log_type = 'Security'
    h_log = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    
    print(" [.] Listening for Failed Logins...")
    
    while True:
        events = win32evtlog.ReadEventLog(h_log, flags, 0)
        for event in events:
            if event.EventID == 4625: # Failed Login
                try:
                    target_user = event.StringInserts[5]
                except:
                    target_user = "Unknown"
                
                malicious_pid = "0" 

                if should_trigger_defense(target_user):
                    action_taken = neutralize_threat(target_user, pid=malicious_pid)
                    
                    log = {
                        "timestamp": str(event.TimeGenerated).replace(" ", "T"),
                        "event_type": "active_defense_trigger",
                        "user": target_user, 
                        "ip_address": "Internal/VPN", 
                        "status": action_taken,
                        "risk_level": "critical",
                        "source": "windows_smart_defense"
                    }
                    log_to_db(log)
        
        time.sleep(1)

if __name__ == "__main__":
    listen()