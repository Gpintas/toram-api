from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Menggunakan Pooler Connection (Port 6543) khusus untuk Serverless/Vercel
def get_db_connection():
    conn = psycopg2.connect(
        host="aws-0-ap-southeast-1.pooler.supabase.com", # atau host pooler dari dashboard kamu
        database="postgres",
        user="postgres.clyrfxouashaidcnbypt", # format user pooler supabase
        password="Admipoel314#",
        port=6543
    )
    return conn

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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password, status, android_id, max_devices FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Username tidak terdaftar!"})
            
        db_id, db_password, db_status, db_android_id, max_devices = user
        
        if db_status != 1:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Akun Anda telah dinonaktifkan atau diblokir!"})
            
        if password != db_password:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Password salah!"})
            
        if not db_android_id or db_android_id == "" or db_android_id == "NONE":
            cursor.execute("UPDATE users SET android_id = %s WHERE id = %s", (android_id, db_id))
            conn.commit()
        elif db_android_id != android_id:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Perangkat tidak dikenali! Akun terkunci di perangkat lain."})
            
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": "Login Berhasil!"})
        
        except Exception as e:
        return jsonify({"status": "error", "message": "DB Error: " + str(e)})

if __name__ == '__main__':
    app.run()
