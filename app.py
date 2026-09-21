from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

CATEGORIES = {
    'algebra': {'title': 'Algebra e Funzioni Base', 'folder': 'Mate/01_Algebra_e_Funzioni_Base', 'color': 'c-blue'},
    'geometria': {'title': 'Geometria Analitica', 'folder': 'Mate/02_Geometria_Analitica', 'color': 'c-green'},
    'goniometria': {'title': 'Goniometria e Trigonometria', 'folder': 'Mate/03_Goniometria_e_Trigonometria', 'color': 'c-purple'},
    'analisi': {'title': 'Analisi Matematica', 'folder': 'Mate/04_Analisi_Matematica', 'color': 'c-orange'},
    'informatica': {'title': 'Informatica', 'folder': 'Informatica/05_Informatica', 'color': 'c-red'}
}

def get_blob_files():
    """Recupera la lista di tutti i file presenti su Vercel Blob"""
    token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    if not token:
        return []
    
    headers = {"authorization": f"Bearer {token}"}
    resp = requests.get("https://blob.vercel-storage.com", headers=headers)
    if resp.status_code == 200:
        return resp.json().get('blobs', [])
    return []

@app.route('/')
def index():
    blobs = get_blob_files()
    counts = {}
    for cat, data in CATEGORIES.items():
        folder_path = data['folder']
        count = sum(1 for b in blobs if b['pathname'].startswith(folder_path + '/'))
        counts[cat] = count
    return render_template('index.html', counts=counts)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        category = request.form.get('category')
        
        if file.filename == '' or not category or category not in CATEGORIES:
            return redirect(request.url)
            
        if file and file.filename.lower().endswith('.pdf'):
            token = os.environ.get('BLOB_READ_WRITE_TOKEN')
            if not token:
                return "Errore: Blob non configurato in Vercel.", 500
                
            filename = secure_filename(file.filename)
            blob_pathname = f"{CATEGORIES[category]['folder']}/{filename}"
            
            headers = {
                "authorization": f"Bearer {token}",
                "x-add-random-suffix": "0"
            }
            
            # Invio del file a Vercel Blob
            resp = requests.put(
                f"https://blob.vercel-storage.com/{blob_pathname}",
                data=file.read(),
                headers=headers
            )
            
            if resp.status_code == 200:
                return redirect(url_for('index'))
            else:
                return f"Errore API Blob: {resp.text}", 500
                
    return render_template('upload.html', categories=CATEGORIES)

@app.route('/api/files')
def get_files():
    blobs = get_blob_files()
    file_data = {}
    
    for cat, data in CATEGORIES.items():
        folder_path = data['folder']
        files = [
            b['pathname'].replace(folder_path + '/', '') 
            for b in blobs if b['pathname'].startswith(folder_path + '/')
        ]
        file_data[cat] = {
            'title': data['title'],
            'folder': f"/files/{cat}/",
            'files': files
        }
    return jsonify(file_data)

@app.route('/files/<category>/<path:filename>')
def serve_file(category, filename):
    if category in CATEGORIES:
        expected_path = f"{CATEGORIES[category]['folder']}/{filename}"
        blobs = get_blob_files()
        for b in blobs:
            if b['pathname'] == expected_path:
                return redirect(b['url'])
                
    return "File non trovato", 404

app_handler = app

if __name__ == '__main__':
    app.run(debug=True)