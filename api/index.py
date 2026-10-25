from http.server import BaseHTTPRequestHandler
import json
import os
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
API_KEY = os.environ.get("API_KEY", "my_Secure_Api_Key_@2026!")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            req_data = json.loads(body.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())
            return

        client_api_key = self.headers.get('X-API-Key')
        if client_api_key != API_KEY:
            self.send_response(403)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Unauthorized API Key"}).encode())
            return

        action = req_data.get("action")
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        response_data = {"status": "error", "message": "Action tidak dikenali"}

        try:
            # 1. MENU LOGIN GAME & BIND DEVICE
            if not action or action == "login":
                rpc_payload = {
                    "payload": {
                        "username": req_data.get("username"),
                        "password": req_data.get("password"),
                        "device_id": req_data.get("device_id")
                    }
                }
                resp = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/login_user", headers=headers, json=rpc_payload, timeout=10)
                response_data = resp.json()

            # 2. ADMIN: REGISTER AKUN BARU
            elif action == "register":
                username = req_data.get("username")
                password = req_data.get("password")
                days = int(req_data.get("days", 30))
                max_dev = int(req_data.get("max_dev", 1))
                
                # Hitung expired_at jika days > 0
                expired_iso = None
                if days > 0:
                    import datetime
                    exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=days)
                    expired_iso = exp_date.isoformat() + "Z"

                new_user = {
                    "username": username,
                    "password": password,
                    "status": 1,
                    "max_dev": max_dev,
                    "expired_at": expired_iso,
                    "hwid": ""
                }
                resp = requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=headers, json=new_user, timeout=10)
                if resp.status_code in [200, 201]:
                    response_data = {"status": "success", "message": f"Akun {username} berhasil didaftarkan!"}
                else:
                    response_data = {"status": "error", "message": f"Gagal register: {resp.text}"}

            # 3. ADMIN: RESET HWID
            elif action == "reset":
                username = req_data.get("username")
                resp = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}",
                    headers=headers,
                    json={"hwid": ""},
                    timeout=10
                )
                if resp.status_code in [200, 204]:
                    response_data = {"status": "success", "message": f"HWID akun {username} berhasil di-reset!"}
                else:
                    response_data = {"status": "error", "message": f"Gagal reset: {resp.text}"}

            # 4. ADMIN: EXTEND / PERPANJANG MASA AKTIF
            elif action == "extend":
                username = req_data.get("username")
                days = int(req_data.get("days", 30))
                import datetime
                exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=days)
                expired_iso = exp_date.isoformat() + "Z"

                resp = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}",
                    headers=headers,
                    json={"expired_at": expired_iso},
                    timeout=10
                )
                if resp.status_code in [200, 204]:
                    response_data = {"status": "success", "message": f"Masa aktif {username} diperpanjang {days} hari!"}
                else:
                    response_data = {"status": "error", "message": f"Gagal extend: {resp.text}"}

            # 5. ADMIN: UPDATE SLOT (MAX DEV)
            elif action == "update_slot":
                username = req_data.get("username")
                max_dev = int(req_data.get("max_dev", 1))
                resp = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}",
                    headers=headers,
                    json={"max_dev": max_dev},
                    timeout=10
                )
                if resp.status_code in [200, 204]:
                    response_data = {"status": "success", "message": f"Slot device {username} diubah menjadi {max_dev} perangkat!"}
                else:
                    response_data = {"status": "error", "message": f"Gagal update slot: {resp.text}"}

            # 6. ADMIN: LIST / CEK SEMUA AKUN
            elif action == "list":
                resp = requests.get(f"{SUPABASE_URL}/rest/v1/users?select=username,status,expired_at,max_dev,hwid", headers=headers, timeout=10)
                if resp.status_code == 200:
                    response_data = {"status": "success", "data": resp.json()}
                else:
                    response_data = {"status": "error", "message": f"Gagal ambil data: {resp.text}"}

            # 7. ADMIN: DELETE AKUN
            elif action == "delete":
                username = req_data.get("username")
                resp = requests.delete(f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}", headers=headers, timeout=10)
                if resp.status_code in [200, 204]:
                    response_data = {"status": "success", "message": f"Akun {username} berhasil dihapus!"}
                else:
                    response_data = {"status": "error", "message": f"Gagal hapus: {resp.text}"}

        except Exception as e:
            response_data = {"status": "error", "message": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "active", "message": "Toram API Vercel + Supabase Ready"}).encode())
