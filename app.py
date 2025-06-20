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

        soup = BeautifulSoup(response.text, 'parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else 'Not found'

        price_text = soup.find(text=re.compile(r'(AED|QAR|USD|ر\.ق|د\.إ|\$)'))
        price_value = re.sub(r'[^\d.]', '', price_text) if price_text else '0'
        price = float(price_value) if price_value else 0

        area_text = soup.find(text=re.compile(r'(sqft|م²|قدم)'))
        area_value = re.findall(r'\d+', area_text) if area_text else ['1']
        area = float(area_value[0]) if area_value else 1

        price_per_m2 = round(price / area, 2) if area > 0 else 0
        evaluation = "سعر جيد / Good price 👍" if price_per_m2 < 9000 else (
                     "سعر معقول / Moderate price 🟡" if price_per_m2 < 15000 else
                     "سعر مرتفع / High price 🔴")

        return jsonify({
            'title': title,
            'price': price_text.strip() if price_text else 'Not found',
            'area': area,
            'price_per_m2': price_per_m2,
            'evaluation': evaluation,
            'language': 'dual'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
