from flask import Flask, request, send_from_directory, jsonify, render_template, redirect, url_for
import os, hashlib, json
from pathlib import Path
from mimetypes import guess_type
import shutil

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = Path(os.path.join(BASE_DIR, "uploads"))
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
SNAPSHOT_FILE = os.path.join(BASE_DIR, "snapshot.json")

BLOCK_SIZE = 4 * 1024  # 4 KB

'''Función que realiza el calculo del hash de los archivos, se implementa DYV, recibe una ruta de un archivo
lo abre en modo lectura y lo va leyendo por bloques fijos de 4 Kb'''

def calc_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def load_snapshot(): #retorna el archivo json en modo lectura
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_snapshot(snapshot): #Abre el archivo json en modo escritura y escribe lo que le pasen
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)

def update_snapshot():#Actualiza el snapshot con hashes nuevos
    snapshot = {}
    for path in UPLOAD_FOLDER.rglob("*"):
        if path.is_file():
            rel_path = path.relative_to(UPLOAD_FOLDER).as_posix()
            snapshot[rel_path] = calc_sha256(path)
    save_snapshot(snapshot)


@app.route("/upload", methods=["POST"]) #Guarda archivos en el servidor y actualiza el snapshot
def upload_file():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    update_snapshot()
    return "Archivo recibido y guardado.", 200

@app.route("/download/<path:filename>", methods=["GET"]) #Permite descargar archivos desde el servidor
def download_file(filename):
    safe_path = filename.replace("\\", "/")
    abs_path = UPLOAD_FOLDER / safe_path
    if not abs_path.exists():
        return f"Archivo no encontrado: {safe_path}", 404
    #Verificar tipos de archivos
    mime_type, _ = guess_type(str(abs_path))
    if mime_type is None:
        if abs_path.suffix.lower() == ".pdf":
            mime_type = "application/pdf"
        elif abs_path.suffix.lower() in [".doc", ".docx"]:
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif abs_path.suffix.lower() in [".xls", ".xlsx"]:
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            mime_type = "application/octet-stream"

    return send_from_directory(
        directory=abs_path.parent,
        path=abs_path.name,
        as_attachment=True,
        mimetype=mime_type,
        download_name=abs_path.name,
        max_age=0
    )

@app.route("/snapshot", methods=["GET"])#Devuelve .json de los archivos en el servidor
def snapshot():
    update_snapshot()
    return jsonify(load_snapshot())

'''Muestra todos los archivos del servidor. Utiliza fueza bruta os.walk recorre todas las carpetas para obtener las rutas y tamaños de 
los archivos que se encuentran en el servidor y genera el .json asociado al servidor'''
@app.route("/")
def index():
    files_info = []
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for f in files:
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            rel_path = os.path.relpath(path, UPLOAD_FOLDER)
            files_info.append({"name": rel_path, "size": round(size / 1024, 2)})
    return render_template("index.html", files=files_info)

@app.route("/upload_web", methods=["POST"])#Sube un archivo desde la web y actualiza el snapshot.
def upload_web():
    file = request.files["file"]
    if file:
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        update_snapshot()
    return redirect(url_for("index"))

@app.route("/upload_folder", methods=["POST"])#Sube carpetas desde la web y actualiza el snapshot.
def upload_folder():
    files = request.files.getlist("files")
    for file in files:
        rel_path = file.filename.replace("\\", "/")
        save_path = os.path.join(UPLOAD_FOLDER, rel_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
    update_snapshot()
    return redirect(url_for("index"))

@app.route("/delete/<path:filename>", methods=["GET", "DELETE"]) #Permite eliminar archivos desde la web y actualiza snapshot
def delete_file(filename):
    file_path = UPLOAD_FOLDER / filename

    if file_path.exists():
        if file_path.is_file():
            file_path.unlink()
        else:
            shutil.rmtree(file_path) 

        update_snapshot()
        return "Deleted", 200

    return "Not Found", 404

@app.route("/download_client")#Descarga el sincronizador desde la web.
def download_client():
    return send_from_directory(".", "client_syncDYV.py", as_attachment=True)


if __name__ == "__main__":
    print("🚀 Servidor de sincronización ejecutándose en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
