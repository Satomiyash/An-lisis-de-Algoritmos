import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Página principal que lista archivos
@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

# Subir archivo
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for('index'))

# Descargar archivo
@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    else:
        return f"Archivo {filename} no encontrado", 404

# Eliminar archivo
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)
