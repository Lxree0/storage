from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cartella base dove verranno salvati i file
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max 50 MB per file

# Definizione delle categorie e delle rispettive sottocartelle
CATEGORIES = {
    'algebra': {'title': 'Algebra e Funzioni Base', 'folder': 'Mate/01_Algebra_e_Funzioni_Base', 'color': 'c-blue'},
    'geometria': {'title': 'Geometria Analitica', 'folder': 'Mate/02_Geometria_Analitica', 'color': 'c-green'},
    'goniometria': {'title': 'Goniometria e Trigonometria', 'folder': 'Mate/03_Goniometria_e_Trigonometria', 'color': 'c-purple'},
    'analisi': {'title': 'Analisi Matematica', 'folder': 'Mate/04_Analisi_Matematica', 'color': 'c-orange'},
    'informatica': {'title': 'Informatica', 'folder': 'Informatica/05_Informatica', 'color': 'c-red'}
}

# Assicurati che le cartelle esistano all'avvio
for cat, data in CATEGORIES.items():
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], data['folder']), exist_ok=True)

@app.route('/')
def index():
    # Conta i file dinamicamente per aggiornare la UI
    counts = {}
    for cat, data in CATEGORIES.items():
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], data['folder'])
        counts[cat] = len([f for f in os.listdir(folder_path) if f.endswith('.pdf')])
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
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], CATEGORIES[category]['folder'], filename)
            file.save(save_path)
            return redirect(url_for('index'))
            
    return render_template('upload.html', categories=CATEGORIES)

@app.route('/api/files')
def get_files():
    # API che fornisce a JavaScript i file attuali nelle cartelle
    file_data = {}
    for cat, data in CATEGORIES.items():
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], data['folder'])
        files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        file_data[cat] = {
            'title': data['title'],
            'folder': f"/files/{cat}/",
            'files': files
        }
    return jsonify(file_data)

@app.route('/files/<category>/<filename>')
def serve_file(category, filename):
    # Route per scaricare o visualizzare i PDF caricati
    if category in CATEGORIES:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], CATEGORIES[category]['folder'])
        return send_from_directory(folder_path, filename)
    return "Not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)