import os
import time
import hashlib
import json
import shutil
import threading
from pathlib import Path
from queue import Queue, Empty
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, DirCreatedEvent, DirDeletedEvent, FileMovedEvent, FileDeletedEvent, FileCreatedEvent, FileModifiedEvent, FileMovedEvent

# --- rutas / configuración ---
LOCAL_ROOT = Path("C:/ADA/ACT código-Divide y vencerás/server/local_root")
REMOTE_ROOT = Path("C:/ADA/ACT código-Divide y vencerás/server/uploads")
SNAPSHOT_FILE = Path(".sync_snapshot.json")

# tiempo durante el cual ignoramos eventos provocados por nuestras propias copias (segundos)
SUPPRESS_EXPIRY = 1.5

# --- utilidades ---
def calc_sha256(path, block_size=4*1024*1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(block_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def relpath(p, root):
    return str(Path(p).relative_to(root))

def load_snapshot():
    if not SNAPSHOT_FILE.exists():
        return {}
    try:
        return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_snapshot(snapshot):
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

def ensure_parent(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

# --- "nube" simulada ops (local copy) ---
def remote_put(relpath_str, local_path):
    dest = REMOTE_ROOT / relpath_str
    ensure_parent(dest)
    shutil.copy2(local_path, dest)
    # actualizar mtime a la misma (shutil.copy2 ya copia metadata)
    print(f"[UPLOAD] {relpath_str}")
    return dest

def remote_delete(relpath_str):
    p = REMOTE_ROOT / relpath_str
    if p.exists():
        p.unlink()
        print(f"[REMOTE DELETE] {relpath_str}")

def remote_exists(relpath_str):
    return (REMOTE_ROOT / relpath_str).exists()

def remote_get(relpath_str, dst_path):
    src = REMOTE_ROOT / relpath_str
    ensure_parent(dst_path)
    shutil.copy2(src, dst_path)
    print(f"[DOWNLOAD] {relpath_str} -> {dst_path}")

def compute_remote_meta(rel):
    p = REMOTE_ROOT / rel
    if not p.exists():
        return None
    return {"size": p.stat().st_size, "mtime": p.stat().st_mtime, "hash": calc_sha256(p)}

# --- scan utilities (on-demand) ---
def scan_local():
    result = {}
    for root, _, files in os.walk(LOCAL_ROOT):
        for fn in files:
            fp = Path(root) / fn
            rel = relpath(fp, LOCAL_ROOT)
            st = fp.stat()
            result[rel] = {"size": st.st_size, "mtime": st.st_mtime}
    return result

def remote_list_snapshot():
    out = {}
    for root, _, files in os.walk(REMOTE_ROOT):
        for fn in files:
            fp = Path(root) / fn
            rel = relpath(fp, REMOTE_ROOT)
            out[rel] = {
                "size": fp.stat().st_size,
                "mtime": fp.stat().st_mtime,
                "hash": calc_sha256(fp)
            }
    return out

# --- suppression set to avoid handling events we triggered ourselves ---
class Suppressor:
    def __init__(self):
        self._d = {}  # path_str -> expiry_time
        self._lock = threading.Lock()

    def add(self, path_str):
        with self._lock:
            self._d[path_str] = time.time() + SUPPRESS_EXPIRY

    def contains(self, path_str):
        now = time.time()
        with self._lock:
            # drop expired
            to_del = [p for p, exp in self._d.items() if exp < now]
            for p in to_del:
                del self._d[p]
            return path_str in self._d

suppressor = Suppressor()

# --- event queue + worker ---
event_q = Queue()

def enqueue_event(ev_type, src_path, dest_path=None, is_dir=False, origin="local"):
    """
    ev_type: 'created', 'modified', 'deleted', 'moved'
    origin: 'local' or 'remote' (indicates which side generated the FS event)
    """
    event_q.put({
        "type": ev_type,
        "src": src_path,
        "dst": dest_path,
        "is_dir": is_dir,
        "origin": origin,
        "time": time.time()
    })

def worker_loop(snapshot):
    """
    worker processes events and applies sync logic.
    snapshot is a dict rel -> {size, mtime, hash}
    """
    while True:
        try:
            ev = event_q.get(timeout=1.0)
        except Empty:
            continue
        try:
            handle_event(ev, snapshot)
        except Exception as e:
            print("Error handling event:", e)
        finally:
            event_q.task_done()

# --- core event handling logic ---
snapshot_lock = threading.Lock()

def handle_event(ev, snapshot):
    ev_type = ev["type"]
    origin = ev["origin"]
    src = Path(ev["src"])
    dst = Path(ev["dst"]) if ev["dst"] else None

    # map paths to relative paths depending on origin
    if origin == "local":
        # event happened in local; map to rel from LOCAL_ROOT
        try:
            rel = relpath(src, LOCAL_ROOT)
        except Exception:
            # not under local root (dir events or temporary) -> ignore
            return
    else:
        try:
            rel = relpath(src, REMOTE_ROOT)
        except Exception:
            return

    # ignore if suppressed (we triggered the change ourselves recently)
    if suppressor.contains(str(src)):
        #print(f"[IGNORED SUPPRESS] {ev_type} {rel} (origin={origin})")
        return

    # handle types
    if ev_type in ("created", "modified"):
        if origin == "local":
            local_path = LOCAL_ROOT / rel
            if not local_path.exists():
                return
            # calcular hash
            try:
                h = calc_sha256(local_path)
            except Exception:
                return
            st = local_path.stat()
            with snapshot_lock:
                snapshot[rel] = {"size": st.st_size, "mtime": st.st_mtime, "hash": h}
                save_snapshot(snapshot)
            # comparar con remote
            rmeta = compute_remote_meta(rel)
            if not rmeta:
                # subir
                dest = remote_put(rel, local_path)
                suppressor.add(str(dest))
            else:
                if h != rmeta.get("hash"):
                    # conflicto por mtime
                    if st.st_mtime >= rmeta["mtime"]:
                        dest = remote_put(rel, local_path)
                        suppressor.add(str(dest))
                    else:
                        # remote más reciente -> descargar
                        print(f"[CONFLICT] remote más reciente para {rel}, restaurando local")
                        dst_local = LOCAL_ROOT / rel
                        ensure_parent(dst_local)
                        shutil.copy2(REMOTE_ROOT / rel, dst_local)
                        suppressor.add(str(dst_local))
                        # actualizar snapshot con hash remoto
                        with snapshot_lock:
                            snapshot[rel] = {"size": dst_local.stat().st_size, "mtime": dst_local.stat().st_mtime, "hash": rmeta.get("hash")}
                            save_snapshot(snapshot)
        else:
            # origen remote: descargar si no existe o local es más viejo
            remote_path = REMOTE_ROOT / rel
            if not remote_path.exists():
                return
            rmeta = compute_remote_meta(rel)
            local_path = LOCAL_ROOT / rel
            if not local_path.exists():
                ensure_parent(local_path)
                shutil.copy2(remote_path, local_path)
                suppressor.add(str(local_path))
                with snapshot_lock:
                    snapshot[rel] = {"size": local_path.stat().st_size, "mtime": local_path.stat().st_mtime, "hash": rmeta.get("hash")}
                    save_snapshot(snapshot)
                print(f"[NEW IN REMOTE] descargado {rel}")
            else:
                # existe local -> verificar hashes
                try:
                    h_local = calc_sha256(local_path)
                except Exception:
                    return
                if h_local != rmeta.get("hash"):
                    # comparar mtime
                    if rmeta["mtime"] >= local_path.stat().st_mtime:
                        shutil.copy2(remote_path, local_path)
                        suppressor.add(str(local_path))
                        with snapshot_lock:
                            snapshot[rel] = {"size": local_path.stat().st_size, "mtime": local_path.stat().st_mtime, "hash": rmeta.get("hash")}
                            save_snapshot(snapshot)
                        print(f"[REMOTE NEWER] sobrescrito local: {rel}")
                    else:
                        # local más nuevo -> subir local
                        dest = remote_put(rel, local_path)
                        suppressor.add(str(dest))
                        with snapshot_lock:
                            snapshot[rel] = {"size": local_path.stat().st_size, "mtime": local_path.stat().st_mtime, "hash": h_local}
                            save_snapshot(snapshot)

    elif ev_type == "deleted":
        if origin == "local":
            # eliminar en remote si existe
            rpath = REMOTE_ROOT / rel
            if rpath.exists():
                remote_delete(rel)
                suppressor.add(str(rpath))
            with snapshot_lock:
                if rel in snapshot:
                    del snapshot[rel]
                    save_snapshot(snapshot)
        else:
            # remote deletion -> eliminar local
            lpath = LOCAL_ROOT / rel
            if lpath.exists():
                try:
                    lpath.unlink()
                    suppressor.add(str(lpath))
                    print(f"[REMOTE DELETE -> LOCAL DELETE] {rel}")
                except Exception:
                    pass
            with snapshot_lock:
                if rel in snapshot:
                    del snapshot[rel]
                    save_snapshot(snapshot)

    elif ev_type == "moved":
        # moved events provide src and dst
        if dst is None:
            return
        if origin == "local":
            try:
                rel_src = relpath(src, LOCAL_ROOT)
                rel_dst = relpath(dst, LOCAL_ROOT)
            except Exception:
                return
            # handle move: if exists on remote as src, move remote file too
            remote_src = REMOTE_ROOT / rel_src
            remote_dst = REMOTE_ROOT / rel_dst
            if remote_src.exists():
                ensure_parent(remote_dst)
                shutil.move(remote_src, remote_dst)
                suppressor.add(str(remote_dst))
                print(f"[REMOTE MOVE] {rel_src} -> {rel_dst}")
            # update snapshot
            with snapshot_lock:
                if rel_src in snapshot:
                    snapshot[rel_dst] = snapshot.pop(rel_src)
                    save_snapshot(snapshot)
        else:
            # origin remote
            try:
                rel_src = relpath(src, REMOTE_ROOT)
                rel_dst = relpath(dst, REMOTE_ROOT)
            except Exception:
                return
            local_src = LOCAL_ROOT / rel_src
            local_dst = LOCAL_ROOT / rel_dst
            if local_src.exists():
                ensure_parent(local_dst)
                shutil.move(local_src, local_dst)
                suppressor.add(str(local_dst))
                print(f"[LOCAL MOVE] {rel_src} -> {rel_dst}")
            with snapshot_lock:
                if rel_src in snapshot:
                    snapshot[rel_dst] = snapshot.pop(rel_src)
                    save_snapshot(snapshot)

# --- watchdog handlers para cada raíz ---
class GenericHandler(FileSystemEventHandler):
    def __init__(self, origin):
        super().__init__()
        self.origin = origin  # 'local' or 'remote'

    def on_created(self, event):
        # ignore directory creation for file sync logic (but we allow file events)
        if event.is_directory:
            return
        enqueue_event("created", event.src_path, origin=self.origin)

    def on_modified(self, event):
        if event.is_directory:
            return
        enqueue_event("modified", event.src_path, origin=self.origin)

    def on_deleted(self, event):
        if event.is_directory:
            return
        enqueue_event("deleted", event.src_path, origin=self.origin)

    def on_moved(self, event):
        if event.is_directory:
            # directories moves could be large; ignore or treat as best-effort
            return
        enqueue_event("moved", event.src_path, dest_path=event.dest_path, origin=self.origin)

# monkey-patch a small adapter so enqueue_event signature matches usage above
def enqueue_event(ev_type, src_path, dest_path=None, is_dir=False, origin="local"):
    event_q.put({
        "type": ev_type,
        "src": src_path,
        "dst": dest_path,
        "is_dir": is_dir,
        "origin": origin,
        "time": time.time()
    })

# --- main ---
def main():
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    REMOTE_ROOT.mkdir(parents=True, exist_ok=True)

    snapshot = load_snapshot()

    # initial full scan to align snapshot with disk (optional: could compute hashes lazily)
    # We'll compute hashes only for existing snapshot entries missing hash
    # Force a quick reconciliation: if file exists in local but not snapshot, add and upload
    print("Haciendo reconciliación inicial (scan rápido)...")
    local_scan = scan_local()
    remote_scan = remote_list_snapshot()

    # Reconcile local -> remote for missing files
    for rel, meta in local_scan.items():
        if rel not in snapshot:
            lp = LOCAL_ROOT / rel
            try:
                h = calc_sha256(lp)
            except Exception:
                continue
            snapshot[rel] = {"size": meta["size"], "mtime": meta["mtime"], "hash": h}
            # if not in remote or different, upload
            rmeta = remote_scan.get(rel)
            if not rmeta or rmeta.get("hash") != h:
                dest = remote_put(rel, lp)
                suppressor.add(str(dest))

    # Reconcile remote-only files -> download
    for rel, rmeta in remote_scan.items():
        if rel not in local_scan:
            src = REMOTE_ROOT / rel
            dst = LOCAL_ROOT / rel
            ensure_parent(dst)
            shutil.copy2(src, dst)
            suppressor.add(str(dst))
            snapshot[rel] = {"size": dst.stat().st_size, "mtime": dst.stat().st_mtime, "hash": rmeta.get("hash")}
            print(f"[INIT DOWNLOAD] {rel}")

    save_snapshot(snapshot)
    print("Sincronizador con watchers iniciado. Ctrl+C para salir.")

    # arrancar worker thread
    worker = threading.Thread(target=worker_loop, args=(snapshot,), daemon=True)
    worker.start()

    # crear observadores
    obs_local = Observer()
    obs_remote = Observer()

    handler_local = GenericHandler("local")
    handler_remote = GenericHandler("remote")

    obs_local.schedule(handler_local, str(LOCAL_ROOT), recursive=True)
    obs_remote.schedule(handler_remote, str(REMOTE_ROOT), recursive=True)

    obs_local.start()
    obs_remote.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Saliendo... deteniendo observers.")
        obs_local.stop()
        obs_remote.stop()
        obs_local.join()
        obs_remote.join()

if __name__ == "__main__":
    main()
