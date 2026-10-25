from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SUPABASE_URL = "https://clyrfxouashaidcnbypt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseXJmeG91YXNoYWlkY25ieXB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjkzNTMwMywiZXhwIjoyMTA4NTExMzAzfQ.0VURelvbUbVB4fmt1f5r2tbbC5EomPrbMQTtAFPzoCo"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "API Supabase Auth Aktif!"})
    
    try:
        username = request.form.get('username') or request.json.get('username') if request.is_json else request.form.get('username')
        password = request.form.get('password') or request.json.get('password') if request.is_json else request.form.get('password')
        android_id = request.form.get('android_id', '')
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username dan password wajib diisi!"})
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        resp = requests.get(f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}", headers=headers, timeout=10)
        
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": "Gagal terhubung ke database!"})
            
        users = resp.json()
        if not users or len(users) == 0:
            return jsonify({"status": "error", "message": "Username tidak terdaftar!"})
            
        user = users[0]
        db_id = user.get("id")
        db_password = user.get("password")
        db_status = user.get("status", 1)
        db_android_id = user.get("android_id")
        
        if db_status != 1:
            return jsonify({"status": "error", "message": "Akun Anda telah dinonaktifkan atau diblokir!"})
            
        if password != db_password:
            return jsonify({"status": "error", "message": "Password salah!"})
            
        if not db_android_id or db_android_id == "" or db_android_id == "NULL" or db_android_id is None:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/users?id=eq.{db_id}",
                headers=headers,
                json={"android_id": android_id},
                timeout=10
            )
        elif db_android_id != android_id:
            return jsonify({"status": "error", "message": "Perangkat tidak dikenali! Akun terkunci di perangkat lain."})
            
        return jsonify({"status": "success", "message": "Login Berhasil!"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": "API Error: " + str(e)})

if __name__ == '__main__':
    app.run()
