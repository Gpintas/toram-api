from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
from urllib.parse import parse_qs

db_config = {
    "host": "sql107.byetcluster.com",
    "user": "b7_43267317",
    "password": "Admipoel314#",
    "database": "b7_43267317_configuration_db"
}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            api_key = self.headers.get('X-API-Key')
            if api_key != 'my_Secure_Api_Key_@2026!':
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Unauthorized API Access!"}).encode('utf-8'))
                return

            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            android_id = params.get('android_id', [''])[0]
            hwid = params.get('hwid', [''])[0]

            if not username or not password or not android_id:
                self.send_json({"status": "error", "message": "Data login tidak lengkap!"})
                return

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id, password, android_id, status, max_devices FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                self.send_json({"status": "error", "message": "Username tidak terdaftar!"})
                cursor.close()
                conn.close()
                return

            if password != user['password']:
                self.send_json({"status": "error", "message": "Password salah!"})
                cursor.close()
                conn.close()
                return

            if user['status'] == 0:
                self.send_json({"status": "error", "message": "Akun ini telah diblokir!"})
                cursor.close()
                conn.close()
                return

            max_devices = int(user['max_devices'] or 1)
            bound_devices = user['android_id'].split(',') if user['android_id'] else []

            if not user['android_id']:
                cursor.execute("UPDATE users SET android_id = %s, hwid = %s WHERE id = %s", (android_id, hwid, user['id']))
                conn.commit()
                self.send_json({"status": "success", "message": "Device berhasil di-lock! Login Berhasil."})
            else:
                if android_id in bound_devices:
                    self.send_json({"status": "success", "message": "Login Berhasil!"})
                elif len(bound_devices) < max_devices:
                    bound_devices.append(android_id)
                    new_devices = ','.join(bound_devices)
                    cursor.execute("UPDATE users SET android_id = %s WHERE id = %s", (new_devices, user['id']))
                    conn.commit()
                    self.send_json({"status": "success", "message": "Perangkat baru ditambahkan! Login Berhasil."})
                else:
                    self.send_json({"status": "error", "message": f"Batas Maksimal {max_devices} Perangkat Tercapai!"})

            cursor.close()
            conn.close()

        except Exception as e:
            self.send_json({"status": "error", "message": str(e)})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
