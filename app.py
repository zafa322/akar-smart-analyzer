from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

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
        title = soup.find('h1').text.strip() if soup.find('h1') else 'Not found'

        price = 0.0
        price_element = soup.find(text=re.compile(r'(AED|QAR|USD|ر\.ق|د\.إ|\$)'))
        if price_element:
            match = re.search(r'([\d,\.]+)', price_element)
            if match:
                raw_price = match.group(1).replace(',', '')
                price = float(raw_price)

        area = 1.0
        area_element = soup.find(text=re.compile(r'(sqft|م²|قدم)'))
        if area_element:
            match = re.search(r'([\d,\.]+)', area_element)
            if match:
                raw_area = match.group(1).replace(',', '')
                area = float(raw_area)

        price_per_m2 = round(price / area, 2) if area > 0 else 0

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
