from flask import Flask, request, Response
import requests

app = Flask(__name__)

BRIDGE_URL = "http://permanamods.byethost7.com/bridge.php"  # Ganti dengan URL domain hosting Byethost kamu

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return {"status": "online", "message": "API Vercel Bridge Aktif!"}
    
    try:
        api_key = request.headers.get('X-API-Key', '')
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'VercelBridge/1.0'
        }
        
        # Teruskan data POST dari game ke bridge.php di Byethost
        resp = requests.post(BRIDGE_URL, data=request.form, headers=headers, timeout=15)
        return Response(resp.content, status=resp.status_code, content_type='application/json')
        
    except Exception as e:
        return {"status": "error", "message": "Bridge Error: " + str(e)}

if __name__ == '__main__':
    app.run()
