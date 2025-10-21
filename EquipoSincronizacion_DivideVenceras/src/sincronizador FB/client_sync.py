import os
import time
import hashlib
import json
import requests
from pathlib import Path

# --- CONFIGURACIÓN ---
SERVER_URL = "http://10.254.2.8:5000"  # Cambia por la IP real del servidor si está en red local
LOCAL_DIR = Path("C:/Users/Satomi/Documents/sync")    # Carpeta local a sincronizar
SNAPSHOT_FILE = LOCAL_DIR / ".snapshot_local.json"
POLL_INTERVAL = 10  # segundos

LOCAL_DIR.mkdir(exist_ok=True)

# --- FUNCIONES AUXILIARES ---
def calc_sha256(path):
    """Calcula el hash SHA256 completo del archivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())  # leer todo el archivo de una vez
    return h.hexdigest()

def load_snapshot():
    if SNAPSHOT_FILE.exists():
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_snapshot(snapshot):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)

def build_local_snapshot():
    snap = {}
    for root, _, files in os.walk(LOCAL_DIR):
        for f in files:
            if f.startswith(".snapshot"):
                continue
            full_path = Path(root) / f
            rel_path = full_path.relative_to(LOCAL_DIR).as_posix()
            st = full_path.stat()
            snap[rel_path] = {
                "size": st.st_size,
                "mtime": st.st_mtime,
                "hash": calc_sha256(full_path)
            }
    return snap

# --- OPERACIONES CON EL SERVIDOR ---
def upload_file(rel_path):
    full_path = LOCAL_DIR / rel_path
    try:
        with open(full_path, "rb") as f:
            r = requests.post(f"{SERVER_URL}/upload", files={"file": (rel_path, f)})
        print(f"⬆️ Subido: {rel_path} ({r.status_code})")
    except Exception as e:
        print(f"⚠️ Error subiendo {rel_path}: {e}")

def download_file(rel_path):
    save_path = LOCAL_DIR / rel_path
    os.makedirs(save_path.parent, exist_ok=True)
    try:
        r = requests.get(f"{SERVER_URL}/download/{rel_path}", stream=True)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"⬇️ Descargado: {rel_path}")
        else:
            print(f"⚠️ Error descargando {rel_path}: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Error descargando {rel_path}: {e}")

def delete_remote_file(rel_path):
    try:
        r = requests.delete(f"{SERVER_URL}/delete/{rel_path}")
        if r.status_code == 200:
            print(f"🗑️ Eliminado en servidor: {rel_path}")
    except Exception as e:
        print(f"⚠️ Error eliminando {rel_path} en servidor: {e}")

# --- SINCRONIZACIÓN ---
def sync():
    # snapshot local y remoto
    local_snap = build_local_snapshot()  # función que devuelve {rel_path: hash}
    try:
        remote_snap = requests.get(f"{SERVER_URL}/snapshot").json()
    except Exception as e:
        print(f"⚠️ No se pudo obtener snapshot remoto: {e}")
        remote_snap = {}

    # cargar snapshot anterior local
    snapshot = load_snapshot()
    new_snapshot = {}

    # 1) Archivos nuevos/modificados localmente
    for rel, local_data in local_snap.items():
        remote_hash = remote_snap.get(rel)
        local_hash = local_data["hash"]

        if remote_hash != local_hash:
            upload_file(rel)
            new_snapshot[rel] = local_hash
        else:
            new_snapshot[rel] = local_hash

    # 2) Archivos eliminados localmente
    for rel in snapshot:
        if rel not in local_snap and rel in remote_snap:
            delete_remote_file(rel)

    # 3) Archivos nuevos/modificados en servidor
    for rel, rhash in remote_snap.items():
        if rel not in new_snapshot:
            download_file(rel)
            new_snapshot[rel] = rhash

    save_snapshot(new_snapshot)
    print("✅ Sincronización completada.\n")

# --- LOOP PRINCIPAL ---
def main():
    print(f"🚀 Sincronizador activo en {LOCAL_DIR.resolve()}")
    try:
        while True:
            sync()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("🛑 Sincronizador detenido.")

if __name__ == "__main__":
    main()