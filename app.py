from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/check', methods=['GET'])
def check_warranty():
    imei = request.args.get('imei')
    if not imei:
        return jsonify({"error": "Thiếu mã imei"}), 400

    target_url = f"https://warranty.vnsamsungcampaign.com/api/index.php?imei={imei}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://warranty.vnsamsungcampaign.com/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        return response.text, response.status_code, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
