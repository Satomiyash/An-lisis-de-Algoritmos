from flask import Flask, request, send_from_directory, jsonify, render_template, redirect, url_for
import os, hashlib, json
from pathlib import Path

app = Flask(__name__)

# ---------------- Configuración ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = Path(os.path.join(BASE_DIR, "uploads"))
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
SNAPSHOT_FILE = os.path.join(BASE_DIR, "snapshot.json")

# ---------------- Utilidades ----------------
BLOCK_SIZE = 4 * 1024  # 4 KB

def calc_sha256(path): #calcular hash por bloques
    """Calcula el hash SHA256 por bloques de 4KB."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def load_snapshot(): #Abre el archivo json en modo lectura
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_snapshot(snapshot): #Abre el archivo json en modo escritura y escribe lo que le pasen
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)

def update_snapshot():#Actualiza el snapshot con hashes actuales de los archivos.
    snapshot = {}
    for path in UPLOAD_FOLDER.rglob("*"):
        if path.is_file():
            rel_path = path.relative_to(UPLOAD_FOLDER).as_posix()
            snapshot[rel_path] = calc_sha256(path)
    save_snapshot(snapshot)

# ---------------- API (para cliente Python) ----------------
@app.route("/upload", methods=["POST"]) #Recibe un archivo desde el cliente, lo guarda en el servidor y actualiza el snapshot de hashes.
def upload_file():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    update_snapshot()
    return "Archivo recibido y guardado.", 200

@app.route("/download/<path:filename>", methods=["GET"])#Permite descargar archivos que están en el servidor
def download_file(filename):
    safe_path = filename.replace("\\", "/")
    abs_path = os.path.join(UPLOAD_FOLDER, safe_path)
    if not os.path.exists(abs_path):
        return f"Archivo no encontrado: {safe_path}", 404
    directory = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)
    return send_from_directory(directory, file_name, as_attachment=True)

@app.route("/snapshot", methods=["GET"])#Devuelve un listado completo de archivos y sus hashes SHA256 del servidor.
def snapshot():
    update_snapshot()
    return jsonify(load_snapshot())

# ---------------- Interfaz Web ----------------
@app.route("/")#Muestra una lista de todos los archivos del servidor con su tamaño en una página web.
def index():
    files_info = []
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for f in files:
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            rel_path = os.path.relpath(path, UPLOAD_FOLDER)
            files_info.append({"name": rel_path, "size": round(size / 1024, 2)})
    return render_template("index.html", files=files_info)

@app.route("/upload_web", methods=["POST"])#Permite subir un archivo desde la web y actualiza el snapshot.
def upload_web():
    file = request.files["file"]
    if file:
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        update_snapshot()
    return redirect(url_for("index"))

@app.route("/upload_folder", methods=["POST"])#Permite subir varios archivos simultáneamente desde la web y mantener actualizado el snapshot.
def upload_folder():
    files = request.files.getlist("files")
    for file in files:
        rel_path = file.filename.replace("\\", "/")
        save_path = os.path.join(UPLOAD_FOLDER, rel_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
    update_snapshot()
    return redirect(url_for("index"))

@app.route("/delete/<path:filename>", methods=["DELETE"])#Permite eliminar archivos del servidor y mantener actualizado el snapshot.
def delete_file(filename):
    file_path = UPLOAD_FOLDER / filename
    if file_path.exists():
        file_path.unlink()
        update_snapshot()
        return "Deleted", 200
    return "Not Found", 404

@app.route("/download_client")#Permite descargar un script de cliente necesario para sincronizar archivos con el servidor.
def download_client():
    return send_from_directory(".", "client_sync.py", as_attachment=True)

# ---------------- Main ----------------
if __name__ == "__main__":
    print("🚀 Servidor de sincronización ejecutándose en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
