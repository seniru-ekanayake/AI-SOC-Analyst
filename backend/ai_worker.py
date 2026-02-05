import sqlite3
import time
import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
DB_FILE = "data/soc_database.db"
THREAT_DB_FILE = "data/threat_db.json" 

if not API_KEY:
    print("❌ ERROR: No API Key found in .env")
    exit()

client = genai.Client(api_key=API_KEY)

def load_context():
    try:
        with open(THREAT_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"known_ips": {}, "users": {}}

THREAT_CONTEXT = load_context()

def get_asset_info(ip, user):
    """ Look up what the IP and User actually ARE """
    ip_data = THREAT_CONTEXT["known_ips"].get(ip, {"description": "Unknown Device", "risk": "unknown"})
    user_data = THREAT_CONTEXT["users"].get(user, {"role": "Unknown User", "location": "Unknown"})
    return ip_data, user_data

def ask_gemini(log_details):
    user = log_details.get("user")
    ip = log_details.get("ip")
    
    # FETCH CONTEXT BEFORE ASKING AI
    asset_info, user_info = get_asset_info(ip, user)
    
    print(f"   ... AI is analyzing context: {asset_info['description']} ...")
    
    prompt = f"""
    You are a Tier 3 SOC Analyst. A security event has occurred.
    
    --- THE FACTS ---
    User: {user} (Role: {user_info['role']}, Location: {user_info['location']})
    Target IP: {ip} (Asset: {asset_info['description']}, Inherent Risk: {asset_info['risk']})
    Event Type: {log_details.get('event')}
    
    --- YOUR INSTRUCTIONS ---
    1. Don't just say "check logs." 
    2. Use the CONTEXT provided above. (e.g., If it's the Finance Server, treat it as critical).
    3. Output exactly ONE sentence actionable summary.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"AI Failed: {e}"

def start_worker():
    print("--- AI ANALYST IS READY ---")
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            c.execute("SELECT id, user, ip_address, event_type FROM logs WHERE ai_analysis = 'PENDING'")
            pending_tasks = c.fetchall()
            
            for task in pending_tasks:
                log_id, user, ip, event = task
                print(f" [🍳] Processing Case #{log_id}...")
                
                log_details = {"user": user, "ip": ip, "event": event}
                
                # Ask Gemini with Context)
                analysis = ask_gemini(log_details)
                
                c.execute("UPDATE logs SET ai_analysis = ? WHERE id = ?", (analysis, log_id))
                conn.commit()
                print(f"Analysis stored.")
                
            conn.close()
            time.sleep(2)
            
        except Exception as e:
            print(f"Worker Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    start_worker()