from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "sql107.byetcluster.com",
    "user": "b7_43267317",
    "password": "Admipoel314#",
    "database": "b7_43267317_configuration_db"
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "API Toram Mod aktif!"})
    
    try:
        api_key = request.headers.get('X-API-Key')
        if api_key != 'my_Secure_Api_Key_@2026!':
            return jsonify({"status": "error", "message": "Unauthorized API Access!"}), 401

        username = request.form.get('username', '')
        password = request.form.get('password', '')
        android_id = request.form.get('android_id', '')
        hwid = request.form.get('hwid', 'TORAM_MOD_HWID')

        if not username or not password or not android_id:
            return jsonify({"status": "error", "message": "Data login tidak lengkap!"})

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, password, android_id, status, max_devices FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Username tidak terdaftar!"})

        if password != user['password']:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Password salah!"})

        if user['status'] == 0:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Akun ini telah diblokir!"})

        max_devices = int(user['max_devices'] or 1)
        bound_devices = user['android_id'].split(',') if user['android_id'] else []

        if not user['android_id']:
            cursor.execute("UPDATE users SET android_id = %s, hwid = %s WHERE id = %s", (android_id, hwid, user['id']))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"status": "success", "message": "Device berhasil di-lock! Login Berhasil."})
        else:
            if android_id in bound_devices:
                cursor.close()
                conn.close()
                return jsonify({"status": "success", "message": "Login Berhasil!"})
            elif len(bound_devices) < max_devices:
                bound_devices.append(android_id)
                new_devices = ','.join(bound_devices)
                cursor.execute("UPDATE users SET android_id = %s WHERE id = %s", (new_devices, user['id']))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"status": "success", "message": "Perangkat baru ditambahkan! Login Berhasil."})
            else:
                cursor.close()
                conn.close()
                return jsonify({"status": "error", "message": f"Batas Maksimal {max_devices} Perangkat Tercapai!"})

    except Exception as e:
        return jsonify({"status": "error", "message": "Server Error: " + str(e)})

if __name__ == '__main__':
    app.run()
