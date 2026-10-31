from flask import Flask, request, jsonify
import requests
import pandas as pd
import io

app = Flask(__name__)

# URL xuất file CSV trực tiếp từ Google Sheet
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1pyqAiWBtDmyjpT9KEjtJt4UZKNoRHA_lgrGUUSyxen8/export?format=csv"

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
# 4. API LẤY DANH SÁCH SẢN PHẨM & GIÁ TỪ GOOGLE SHEET (MỚI)
# Cho phép lọc theo tên: /api/products?search=macbook
# -------------------------------------------------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    search_query = request.args.get('search', '').strip().lower()
    limit = request.args.get('limit', 100, type=int)

    try:
        # Tải dữ liệu từ Google Sheet dưới dạng CSV
        res = requests.get(SHEET_CSV_URL, timeout=10)
        if res.status_code != 200:
            return jsonify({"error": "Không thể tải Google Sheet"}), 500

        # Đọc dữ liệu CSV bằng Pandas
        df = pd.read_csv(io.StringIO(res.text))
        
        # Làm sạch tên cột
        df.columns = df.columns.str.strip()
        
        # Điền giá trị trống bằng chuỗi rỗng
        df = df.fillna('')

        # Tìm kiếm theo tên sản phẩm nếu người dùng cung cấp từ khóa
        if search_query:
            df = df[df['Tên hàng'].astype(str).str.lower().str.contains(search_query)]

        # Giới hạn số lượng bản ghi trả về
        df_limited = df.head(limit)

        # Chuyển đổi thành danh sách dict
        products_list = df_limited.to_dict(orient='records')

        return jsonify({
            "total_matches": len(df),
            "returned": len(products_list),
            "data": products_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
