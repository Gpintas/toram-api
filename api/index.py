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
        # Ambil API key dari request game
        api_key = request.headers.get('X-API-Key', '')
        
        # Ambil semua data form POST dari game
        form_data = request.form.to_dict()
        post_data = urllib.parse.urlencode(form_data).encode('utf-8')
        
        # Buat request ke bridge.php Byethost
        req = urllib.request.Request(BRIDGE_URL, data=post_data, method='POST')
        req.add_header('X-API-Key', api_key)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 10) VercelBridge')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            resp_body = response.read()
            return Response(resp_body, status=response.status, content_type='application/json')
            
    except Exception as e:
        return {"status": "error", "message": "Bridge Error: " + str(e)}

if __name__ == '__main__':
    app.run()
