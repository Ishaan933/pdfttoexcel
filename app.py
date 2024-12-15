from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
import pandas as pd
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # Serves the HTML frontend

def convert_pdf_to_csv_and_excel(pdf_path, output_base_name):
    reader = PdfReader(pdf_path)
    data = [page.extract_text() for page in reader.pages]
    df = pd.DataFrame({'Content': data})
    csv_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_base_name}.csv")
    excel_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_base_name}.xlsx")
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)
    return csv_path, excel_path

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    output_base_name = os.path.splitext(filename)[0]
    csv_path, excel_path = convert_pdf_to_csv_and_excel(file_path, output_base_name)
    return jsonify({
        'csv_download_link': f'/download/csv/{output_base_name}',
        'excel_download_link': f'/download/excel/{output_base_name}'
    })

@app.route('/download/csv/<filename>', methods=['GET'])
def download_csv(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.csv")
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

@app.route('/download/excel/<filename>', methods=['GET'])
def download_excel(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.xlsx")
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
