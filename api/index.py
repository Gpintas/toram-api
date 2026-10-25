from flask import Flask, request, Response
import urllib.request
import urllib.parse
import json

app = Flask(__name__)

DATABASE_URL = "postgresql://postgres:Admipoel314%40@db.clyrfxouashaidcnbypt.supabase.co:5432/postgres"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return {"status": "online", "message": "API Vercel Bridge Aktif!"}
    
    try:
        api_key = request.headers.get('X-API-Key', '')
        form_data = request.form.to_dict()
        post_data = urllib.parse.urlencode(form_data).encode('utf-8')
        
        req = urllib.request.Request(BRIDGE_URL, data=post_data, method='POST')
        req.add_header('X-API-Key', api_key)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 10) VercelBridge')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_body = response.read().decode('utf-8', errors='ignore')
            
            # --- FILTER PEMBERSIH IKLAN BYETHOST ---
            # Cari posisi karakter kurung siku awal '{' dari format JSON
            json_start = raw_body.find('{')
            json_end = raw_body.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                clean_json = raw_body[json_start:json_end+1]
            else:
                clean_json = json.dumps({"status": "error", "message": "Invalid Server Response"})
                
            return Response(clean_json, status=200, content_type='application/json')
            
    except Exception as e:
        return {"status": "error", "message": "Bridge Error: " + str(e)}

if __name__ == '__main__':
    app.run()
