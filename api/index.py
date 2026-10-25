from flask import Flask, request, jsonify
import psycopg2
import urllib.parse

app = Flask(__name__)

# URL Koneksi Supabase yang sudah kamu buat
DATABASE_URL = "postgresql://postgres:Admipoel314%40@db.clyrfxouashaidcnbypt.supabase.co:5432/postgres"

def get_db_connection():
    # Menggunakan psycopg2 untuk koneksi langsung ke PostgreSQL Supabase
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "API Supabase Auth Aktif!"})
    
    try:
        # Mengambil data dari request game (POST)
        username = request.form.get('username') or request.json.get('username') if request.is_json else request.form.get('username')
        password = request.form.get('password') or request.json.get('password') if request.is_json else request.form.get('password')
        android_id = request.form.get('android_id', '')
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username dan password wajib diisi!"})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Cek data user di database Supabase
        cursor.execute("SELECT id, password, status, android_id, max_devices FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Username tidak terdaftar!"})
            
        db_id, db_password, db_status, db_android_id, max_devices = user
        
        # Cek status akun (1 = aktif, 0 = dibanned/nonaktif)
        if db_status != 1:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Akun Anda telah dinonaktifkan atau diblokir!"})
            
        # Cek kecocokan password
        if password != db_password:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Password salah!"})
            
        # Logika HWID / Android ID Binding
        if not db_android_id or db_android_id == "" or db_android_id == "NONE":
            # Jika android_id masih kosong, bind otomatis dengan HP user saat ini
            cursor.execute("UPDATE users SET android_id = %s WHERE id = %s", (android_id, db_id))
            conn.commit()
        elif db_android_id != android_id:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Perangkat tidak dikenali! Akun terkunci di perangkat lain."})
            
        cursor.close()
        conn.close()
        
        # Jika semua pengecekan lolos, login sukses!
        return jsonify({"status": "success", "message": "Login Berhasil!"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": "Database Error: " + str(e)})

if __name__ == '__main__':
    app.run()
