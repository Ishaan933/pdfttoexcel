from flask import Flask, request, jsonify, send_from_directory, render_template
from tabula import read_pdf
import pandas as pd
import os
import uuid

app = Flask(__name__)

# Define upload and output folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_pdf_to_excel_and_csv(pdf_path, excel_path, csv_path):
    """Convert a PDF file to Excel and CSV formats using Tabula."""
    try:
        # Extract tables from PDF (all pages)
        tables = read_pdf(pdf_path, pages="all", multiple_tables=True, output_format="dataframe", silent=True)
        
        # If no tables were found, raise an error
        if not tables:
            return False, "No tables found in the uploaded PDF file."

        # Combine all tables into a single DataFrame
        combined_data = pd.concat(tables, ignore_index=True)

        # Save to Excel and CSV
        combined_data.to_excel(excel_path, index=False)
        combined_data.to_csv(csv_path, index=False)
        return True, None
    except Exception as e:
        return False, str(e)

@app.route("/")
def index():
    """Serve the drag-and-drop upload page."""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and convert the PDF to Excel and CSV."""
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # Validate file type
    if file and file.filename.endswith(".pdf"):
        try:
            # Generate unique filenames
            unique_id = str(uuid.uuid4())
            input_filename = f"{unique_id}.pdf"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)

            # Save the uploaded PDF
            file.save(input_path)

            # Define paths for output files
            excel_filename = f"{unique_id}.xlsx"
            csv_filename = f"{unique_id}.csv"
            excel_path = os.path.join(OUTPUT_FOLDER, excel_filename)
            csv_path = os.path.join(OUTPUT_FOLDER, csv_filename)

            # Convert PDF to Excel and CSV
            success, error_message = convert_pdf_to_excel_and_csv(input_path, excel_path, csv_path)

            if success:
                return jsonify({
                    "success": True,
                    "message": "File successfully converted!",
                    "download_excel": f"/download/{excel_filename}",
                    "download_csv": f"/download/{csv_filename}"
                }), 200
            else:
                return jsonify({"success": False, "message": error_message}), 500
        except Exception as e:
            return jsonify({"success": False, "message": f"Unexpected error: {str(e)}"}), 500

    return jsonify({"success": False, "message": "Invalid file type. Only PDF files are allowed."}), 400

@app.route("/download/<filename>")
def download_file(filename):
    """Serve a file from the outputs folder for download."""
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    # Set up the app to run with Render-friendly settings
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
