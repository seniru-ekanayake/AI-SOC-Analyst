import os
from dotenv import load_dotenv  
from google import genai
import json

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("ERROR: Could not find GEMINI_API_KEY in the .env file!")

client = genai.Client(api_key=API_KEY)

def analyze_alert(alert_json):
    print("   ... Asking AI for advice (via New SDK) ...")
    
    prompt = f"""
    You are a Senior SOC Analyst. 
    Analyze the following security alert JSON.
    
    ALERT DATA:
    {json.dumps(alert_json, indent=2)}
    
    YOUR TASK:
    1. Summarize what happened in 1 sentence.
    2. Assess the risk (Low/Medium/High/Critical).
    3. Recommend 2 immediate actions.
    
    Keep it brief.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        return f"AI Error: {e}"

if __name__ == "__main__":
    test_alert = {
        "timestamp": "2026-01-24T10:00:00",
        "event_type": "login_attempt",
        "user": "admin",
        "status": "failed",
        "ip_address": "192.168.1.20",
        "enrichment": {
            "source_ip_desc": "UNKNOWN DEVICE",
            "user_role": "IT Admin",
            "ip_risk_level": "critical"
        }
    }
    print(analyze_alert(test_alert))