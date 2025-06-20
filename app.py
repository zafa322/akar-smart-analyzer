from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_file(os.path.join(os.path.dirname(__file__), 'index.html'))

@app.route('/api/analyze', methods=['POST'])
def analyze_property():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch the page.'}), 500

        soup = BeautifulSoup(response.text, 'html.parser')

        # استخراج العنوان
        title = soup.find('h1').text.strip() if soup.find('h1') else 'Not found'

        # السعر
        price = 0.0
        price_element = soup.find(text=re.compile(r'(AED|QAR|USD|ر\.ق|د\.إ|\$)'))
        if price_element:
            match = re.search(r'([\d,\.]+)', price_element)
            if match:
                try:
                    raw_price = match.group(1).replace(',', '')
                    price = float(raw_price)
                except:
                    price = 0.0

        # المساحة
        area = 1.0
        area_element = soup.find(text=re.compile(r'(sqft|م²|قدم)'))
        if area_element:
            match = re.search(r'([\d,\.]+)', area_element)
            if match:
                try:
                    raw_area = match.group(1).replace(',', '')
                    area = float(raw_area)
                except:
                    area = 1.0

        # سعر المتر المربع
        price_per_m2 = round(price / area, 2) if area > 0 else 0

        # التقييم الذكي
        if price_per_m2 < 9000:
            evaluation = "سعر جيد / Good price 👍"
        elif price_per_m2 < 15000:
            evaluation = "سعر معقول / Moderate price 🟡"
        else:
            evaluation = "سعر مرتفع / High price 🔴"

        return jsonify({
            'title': title,
            'price': f"{price} QAR",
            'area': area,
            'price_per_m2': price_per_m2,
            'evaluation': evaluation,
            'language': 'dual'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
