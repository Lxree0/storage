from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os

app = Flask(__name__)

# Cartella base dove sono i file (ora di sola lettura su Vercel)
app.config['UPLOAD_FOLDER'] = 'uploads'

CATEGORIES = {
    'algebra': {'title': 'Algebra e Funzioni Base', 'folder': 'Mate/01_Algebra_e_Funzioni_Base', 'color': 'c-blue'},
    'geometria': {'title': 'Geometria Analitica', 'folder': 'Mate/02_Geometria_Analitica', 'color': 'c-green'},
    'goniometria': {'title': 'Goniometria e Trigonometria', 'folder': 'Mate/03_Goniometria_e_Trigonometria', 'color': 'c-purple'},
    'analisi': {'title': 'Analisi Matematica', 'folder': 'Mate/04_Analisi_Matematica', 'color': 'c-orange'},
    'informatica': {'title': 'Informatica', 'folder': 'Informatica/05_Informatica', 'color': 'c-red'}
}

# ABBIAMO RIMOSSO os.makedirs PER EVITARE IL CRASH SU VERCEL

@app.route('/')
def index():
    counts = {}
    for cat, data in CATEGORIES.items():
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], data['folder'])
        # Controllo se la cartella esiste prima di contare i file
        if os.path.exists(folder_path):
            counts[cat] = len([f for f in os.listdir(folder_path) if f.endswith('.pdf')])
        else:
            counts[cat] = 0
    return render_template('index.html', counts=counts)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Poiché Vercel è in sola lettura, disabilitiamo temporaneamente il salvataggio dei file
    # Mostriamo solo un avviso o reindirizziamo
    if request.method == 'POST':
        return "L'upload è disabilitato su Vercel senza un database cloud.", 403
    return render_template('upload.html', categories=CATEGORIES)

@app.route('/api/files')
def get_files():
    file_data = {}
    for cat, data in CATEGORIES.items():
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], data['folder'])
        files = []
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            
        file_data[cat] = {
            'title': data['title'],
            'folder': f"/files/{cat}/",
            'files': files
        }
    return jsonify(file_data)

@app.route('/files/<category>/<filename>')
def serve_file(category, filename):
    if category in CATEGORIES:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], CATEGORIES[category]['folder'])
        if os.path.exists(os.path.join(folder_path, filename)):
            return send_from_directory(folder_path, filename)
    return "File non trovato", 404

# Aggiungi questa variabile per Vercel
app_handler = app

if __name__ == '__main__':
    app.run(debug=True)