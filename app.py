from flask import Flask, request, jsonify
import requests
import csv
import io

app = Flask(__name__)

# URL xuất file CSV trực tiếp từ Google Sheet
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1pyqAiWBtDmyjpT9KEjtJt4UZKNoRHA_lgrGUUSyxen8/export?format=csv"
SHEET_CSV_URL2 = "https://docs.google.com/spreadsheets/d/1pyqAiWBtDmyjpT9KEjtJt4UZKNoRHA_lgrGUUSyxen8/export?format=csv&gid=1347701278"
@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "running", "message": "Samsung Proxy API is active"}), 200

# -------------------------------------------------------------
# 1. API TRA CỨU BẢO HÀNH
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
# 2. API LẤY DANH SÁCH TRIỆU CHỨNG
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
# 3. API TÍNH CHI PHÍ SỬA CHỮA
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


# -------------------------------------------------------------
# 4. API LẤY DANH SÁCH SẢN PHẨM TỪ GOOGLE SHEET (Dùng thư viện csv chuẩn)
# -------------------------------------------------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    search_query = request.args.get('search', '').strip().lower()
    limit = request.args.get('limit', 100, type=int)

    try:
        res = requests.get(SHEET_CSV_URL, timeout=10)
        if res.status_code != 200:
            return jsonify({"error": "Không thể tải Google Sheet"}), 500

        # Đọc dữ liệu CSV bằng thư viện chuẩn Python (không cần pandas)
        f = io.StringIO(res.text)
        reader = csv.DictReader(f)
        
        products_list = []
        for row in reader:
            # Làm sạch key và giá trị
            cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items() if k}
            
            # Kiểm tra nếu có từ khóa tìm kiếm
            if search_query:
                ten_hang = cleaned_row.get('Tên hàng', '').lower()
                if search_query not in ten_hang:
                    continue
            
            products_list.append(cleaned_row)
            if len(products_list) >= limit:
                break

        return jsonify({
            "returned": len(products_list),
            "data": products_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------
# API LẤY DANH SÁCH SẢN PHẨM & ID_SP TỪ TRANG TÍNH 2
# Endpoint mới: /api/samsung_name?search=S24&limit=50
# -------------------------------------------------------------
@app.route('/api/samsung_name', methods=['GET'])
def get_samsung_name():
    search_query = request.args.get('search', '').strip().lower()
    limit = request.args.get('limit', 100, type=int)

    try:
        res = requests.get(SHEET_CSV_URL2, timeout=10)
        if res.status_code != 200:
            return jsonify({"error": "Không thể tải Google Sheet"}), 500

        f = io.StringIO(res.text)
        reader = csv.DictReader(f)
        
        products_list = []
        for row in reader:
            cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items() if k}
            
            if search_query:
                ten_san_pham = cleaned_row.get('Sản phẩm', '').lower()
                if search_query not in ten_san_pham:
                    continue
            
            products_list.append(cleaned_row)
            if len(products_list) >= limit:
                break

        return jsonify({
            "returned": len(products_list),
            "data": products_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
