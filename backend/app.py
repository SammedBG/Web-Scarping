from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from scraper import scrape_amazon
import os

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    keyword = data.get('search_keyword')
    pincode = data.get('pincode')
    max_pages = int(data.get('pages', 1))

    if not keyword or not pincode:
        return jsonify({'error': 'Missing parameters'}), 400

    result = scrape_amazon(keyword, pincode, max_pages)
    return jsonify(result)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join("downloads", filename)
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
