from flask import Flask, request, jsonify, send_file
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

def convert_pdf_to_csv_and_excel(pdf_path, output_base_name):
    # Read PDF content
    reader = PdfReader(pdf_path)
    data = []
    for page in reader.pages:
        data.append(page.extract_text())

    # Create a DataFrame
    df = pd.DataFrame({'Content': data})

    # Save to CSV and Excel
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

    # Convert PDF to CSV and Excel
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

@app.route('/')
def index():
    return "Welcome to PDF to CSV and Excel Converter API"

if __name__ == '__main__':
    app.run(debug=True)
