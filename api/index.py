from flask import Flask, request, Response
import urllib.request
import urllib.parse

app = Flask(__name__)

BRIDGE_URL = "http://permanamods.byethost7.com/bridge.php"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return {"status": "online", "message": "API Vercel Bridge Aktif!"}
    
    try:
        api_key = request.headers.get('X-API-Key', '')
        
        # Ambil data POST dari game, lalu encode untuk dikirim ke bridge.php
        post_data = urllib.parse.urlencode(request.form).encode('utf-8')
        
        req = urllib.request.Request(BRIDGE_URL, data=post_data, method='POST')
        req.add_header('X-API-Key', api_key)
        req.add_header('User-Agent', 'VercelBridge/1.0')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            resp_body = response.read()
            return Response(resp_body, status=response.status, content_type='application/json')
            
    except Exception as e:
        return {"status": "error", "message": "Bridge Error: " + str(e)}

if __name__ == '__main__':
    app.run()
