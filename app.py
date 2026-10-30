from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Single endpoint / Home route
@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "running", "message": "Samsung Proxy API is active"}), 200

# -------------------------------------------------------------
# 1. API TRA CỨU BẢO HÀNH (Cũ)
# -------------------------------------------------------------
@app.route('/api/check', methods=['GET'])
def check_warranty():
    imei = request.args.get('imei')
    if not imei:
        return jsonify({"error": "Thiếu mã imei"}), 400

    target_url = f"https://warranty.vnsamsungcampaign.com/api/index.php?imei={imei}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://warranty.vnsamsungcampaign.com/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        return response.text, response.status_code, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------
# 2. API LẤY DANH SÁCH TRIỆU CHỨNG (Mới - GET)
# Endpoint gọi: /api/symptoms?productId=5943
# -------------------------------------------------------------
@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    product_id = request.args.get('productId')
    if not product_id:
        return jsonify({"error": "Thiếu productId"}), 400

    target_url = f"https://vn-repair-cost-estimator-api-11664-prod.azurewebsites.net/api/symptoms?productId={product_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        return response.text, response.status_code, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------
# 3. API TÍNH CHI PHÍ SỬA CHỮA (Mới - POST)
# Endpoint gọi: /api/estimate
# Body JSON gửi lên: {"productId": "5943", "symptomIds": ["29198"]}
# -------------------------------------------------------------
@app.route('/api/estimate', methods=['POST'])
def estimate_cost():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400

    target_url = "https://vn-repair-cost-estimator-api-11664-prod.azurewebsites.net/api/estimate"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }

    try:
        response = requests.post(target_url, json=payload, headers=headers, timeout=10)
        return response.text, response.status_code, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
