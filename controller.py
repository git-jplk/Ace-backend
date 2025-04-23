import os
import re
import unicodedata
from flask import Flask, request, jsonify
from model import QueryService
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
query_service = QueryService()
def clean_text(text: str) -> str:
    # Normalize unicode (e.g. turn “ﬁ” ligature into “fi”)
    text = unicodedata.normalize('NFKC', text)
    # Remove any non-printable/control chars
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
    # Collapse all whitespace (newlines, tabs, multiple spaces) into single spaces
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()

@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf_raw():
    uploaded_file = request.files.get('pdf_file')
    if not uploaded_file or uploaded_file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 400

    # Read PDF from the in-memory stream
    reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    raw_pages = []
    for page in reader.pages:
        extracted = page.extract_text() or ''
        raw_pages.append(extracted)

    # Join all pages and clean
    full_text = ' '.join(raw_pages)
    clean = clean_text(full_text)

    return jsonify({
        'filename': secure_filename(uploaded_file.filename),
        'num_pages': len(reader.pages),
        'raw_text': clean
    })

@app.route('/evaluate', methods=['GET'])
async def get_company():
    company_name = request.args.get('name')
    if not company_name:
        return jsonify({'error': 'Company name is required'}), 400
    try:
        result = await query_service.query(company_name)
        print(result)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
