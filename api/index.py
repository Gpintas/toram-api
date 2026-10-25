from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SUPABASE_URL = "https://clyrfxouashaidcnbypt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseXJmeG91YXNoYWlkY25ieXB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjkzNTMwMywiZXhwIjoyMTA4NTExMzAzfQ.0VURelvbUbVB4fmt1f5r2tbbC5EomPrbMQTtAFPzoCo"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "API Supabase RPC Aktif!"})
    
    try:
        username = request.form.get('username') or (request.json.get('username') if request.is_json else '')
        password = request.form.get('password') or (request.json.get('password') if request.is_json else '')
        android_id = request.form.get('android_id') or request.form.get('hwid') or (request.json.get('android_id') if request.is_json else '')
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username lan password wajib diisi!"})
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        rpc_payload = {
            "p_username": username,
            "p_password": password,
            "p_android_id": android_id if android_id else "UNKNOWN_DEVICE"
        }
        
        resp = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/verify_and_bind_user", headers=headers, json=rpc_payload, timeout=10)
        
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": f"Database RPC Error: {resp.text}"})
            
        result = resp.json()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": "API Error: " + str(e)})

if __name__ == '__main__':
    app.run()
