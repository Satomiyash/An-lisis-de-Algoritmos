import os
import threading
import time
import hashlib
import json
import shutil
import random
import string
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ---------------------- Configuration ----------------------
DEFAULT_LOCAL = Path("local_root")
DEFAULT_REMOTE = Path("remote_root")
SNAPSHOT_FILE = Path(".sync_snapshot_gui.json")
POLL_INTERVAL_DEFAULT = 5  # seconds
HASH_BLOCK = 4 * 1024 * 1024

# ---------------------- Utilities ----------------------
#Calcula el hash por bloques
def calc_sha256(path: Path, block_size=HASH_BLOCK):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(block_size)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None

#Ruta relativa
def relpath(p: Path, root: Path):
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)


# ---------------------- Sync logic (simple brute-force) ----------------------
class BruteSyncWorker(threading.Thread):
    def __init__(self, local_root: Path, remote_root: Path, interval: float, ui_callbacks):
        super().__init__(daemon=True)
        self.local_root = local_root
        self.remote_root = remote_root
        self.interval = interval
        self.ui = ui_callbacks  # dict with methods for UI updates (log, refresh lists, set_status)
        self.stop_event = threading.Event()
        # load snapshot if exists
        if SNAPSHOT_FILE.exists():
            try:
                with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                    self.snapshot = json.load(f)
            except Exception:
                self.snapshot = {}
        else:
            self.snapshot = {}

    def run(self):
        self.ui['log']("Sync worker started.")
        while not self.stop_event.is_set():
            start = time.time()
            try:
                self._sync_cycle()
            except Exception as e:
                self.ui['log'](f"Error in sync cycle: {e}")
            # save snapshot
            try:
                with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.snapshot, f, indent=2)
            except Exception as e:
                self.ui['log'](f"Warning: couldn't save snapshot: {e}")

            elapsed = time.time() - start
            sleep_for = max(0, self.interval - elapsed)
            # wait, but allow early stop
            stop_flag = self.stop_event.wait(timeout=sleep_for)
            if stop_flag:
                break
        self.ui['log']("Sync worker stopped.")

    def stop(self):
        self.stop_event.set()

    #Escaneo local, devuelve el mtime y size de todos los archivos que contiene
    def _scan_local(self):
        out = {}
        for root, _, files in os.walk(self.local_root):
            for fn in files:
                fp = Path(root) / fn
                rel = relpath(fp, self.local_root)
                try:
                    st = fp.stat()
                    out[rel] = {"size": st.st_size, "mtime": st.st_mtime}
                except Exception:
                    continue
        return out

    #Escaneo de la nube, guarda el hash, el mtime y el size
    def _remote_snapshot(self):
        out = {}
        for root, _, files in os.walk(self.remote_root):
            for fn in files:
                fp = Path(root) / fn
                rel = relpath(fp, self.remote_root)
                try:
                    st = fp.stat()
                    out[rel] = {"size": st.st_size, "mtime": st.st_mtime, "hash": None}
                except Exception:
                    continue
        # compute hashes lazily only when needed by sync
        return out

    def _remote_get_hash(self, rel):
        p = self.remote_root / rel
        if p.exists():
            return calc_sha256(p)
        return None

    def _sync_cycle(self):
        self.ui['set_status']("Scanning...")
        local_scan = self._scan_local()
        remote_snap = self._remote_snapshot()
        new_snapshot = {}

        # 1) detect new/modified locally
        for rel, meta in local_scan.items():
            prev = self.snapshot.get(rel)
            needs_hash = False
            if prev is None: 
                needs_hash = True #si no hay nada en el snapshot, necesita calcular el hash
            else:
                if meta['size'] != prev.get('size') or abs(meta['mtime'] - prev.get('mtime', 0)) > 0.5:
                    needs_hash = True #Si el tamaño es distinto, o el tiempo de modificacion es distino, necesita calcular el hash
            if not needs_hash:
                new_snapshot[rel] = {"size": meta['size'], "mtime": meta['mtime'], "hash": prev.get('hash')}
                continue #Si todo esta igual se guarda como estaba, se sale de la iteracion

            # calcular el hash de la ruta local
            local_path = self.local_root / rel
            h = calc_sha256(local_path)
            new_snapshot[rel] = {"size": meta['size'], "mtime": meta['mtime'], "hash": h} #Actualizar el snapshot

            rmeta = remote_snap.get(rel)
            if not rmeta:
                # upload
                self.ui['log'](f"UPLOAD -> {rel}")
                self._remote_put(rel, local_path)
            else:
                r_hash = self._remote_get_hash(rel)
                if r_hash != h:
                    # conflict/simple resolution by mtime
                    if meta['mtime'] >= rmeta['mtime']:
                        self.ui['log'](f"UPLOAD (overwrite remote) -> {rel}")
                        self._remote_put(rel, local_path)
                    else:
                        self.ui['log'](f"CONFLICT: remote newer -> DOWNLOAD {rel}")
                        self._remote_get(rel, local_path)
                        # update hash to remote
                        new_snapshot[rel]['hash'] = r_hash

        # 2) detect deletions locally
        for rel in list(self.snapshot.keys()):
            if rel not in local_scan:
                # deleted locally since last snapshot
                self.ui['log'](f"DELETE_REMOTE -> {rel}")
                self._remote_delete(rel)
                # do not add to new_snapshot

        # 3) detect files in remote not present locally -> download
        for rel, rmeta in remote_snap.items():
            if rel not in new_snapshot and rel not in local_scan:
                self.ui['log'](f"DOWNLOAD -> {rel}")
                self._remote_get(rel, self.local_root / rel)
                # compute hash from saved file
                dst = self.local_root / rel
                try:
                    st = dst.stat()
                    h = calc_sha256(dst)
                    new_snapshot[rel] = {"size": st.st_size, "mtime": st.st_mtime, "hash": h}
                except Exception:
                    pass

        self.snapshot = new_snapshot
        # refresh UI lists
        self.ui['refresh_lists']()
        self.ui['set_status']("Idle")

    # remote operations (simulated using local filesystem)
    def _remote_put(self, rel, local_path: Path):
        dest = self.remote_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(local_path, dest)
        except Exception as e:
            self.ui['log'](f"Error uploading {rel}: {e}")

    def _remote_get(self, rel, local_dest: Path):
        src = self.remote_root / rel
        try:
            local_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, local_dest)
        except Exception as e:
            self.ui['log'](f"Error downloading {rel}: {e}")

    def _remote_delete(self, rel):
        p = self.remote_root / rel
        try:
            if p.exists():
                p.unlink()
        except Exception as e:
            self.ui['log'](f"Error deleting remote {rel}: {e}")


# ---------------------- GUI ----------------------
class BruteSyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute-force Sync Demo")
        self.local_root = DEFAULT_LOCAL
        self.remote_root = DEFAULT_REMOTE
        self.worker = None

        # ensure folders exist
        self.local_root.mkdir(parents=True, exist_ok=True)
        self.remote_root.mkdir(parents=True, exist_ok=True)

        self._build_ui()
        self._refresh_file_lists()

    def _build_ui(self):
        frm_top = ttk.Frame(self.root, padding=6)
        frm_top.pack(fill=tk.BOTH, expand=True)

        # left: local files
        frm_left = ttk.LabelFrame(frm_top, text="Local")
        frm_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.tree_local = ttk.Treeview(frm_left, columns=("size", "mtime"), show="headings")
        self.tree_local.heading("size", text="Name")
        self.tree_local.heading("mtime", text="Size")
        self.tree_local.pack(fill=tk.BOTH, expand=True)

        # center control
        frm_mid = ttk.Frame(frm_top)
        frm_mid.pack(side=tk.LEFT, fill=tk.Y, padx=4)

        ttk.Button(frm_mid, text="Select Local...", command=self._choose_local).pack(fill=tk.X, pady=2)
        ttk.Button(frm_mid, text="Select Remote...", command=self._choose_remote).pack(fill=tk.X, pady=2)
        ttk.Separator(frm_mid).pack(fill=tk.X, pady=4)

        ttk.Label(frm_mid, text="Poll interval (s):").pack()
        self.interval_var = tk.DoubleVar(value=POLL_INTERVAL_DEFAULT)
        ttk.Spinbox(frm_mid, from_=1, to=60, increment=1, textvariable=self.interval_var, width=6).pack()

        self.btn_start = ttk.Button(frm_mid, text="Start Sync", command=self._start_stop)
        self.btn_start.pack(fill=tk.X, pady=6)


        ttk.Separator(frm_mid).pack(fill=tk.X, pady=4)
        ttk.Label(frm_mid, text="Demo actions (local):").pack()
        ttk.Button(frm_mid, text="Create random file", command=self._create_random_file).pack(fill=tk.X, pady=2)
        ttk.Button(frm_mid, text="Modify random file", command=self._modify_random_file).pack(fill=tk.X, pady=2)
        ttk.Button(frm_mid, text="Delete random file", command=self._delete_random_file).pack(fill=tk.X, pady=2)

        # right: remote files
        frm_right = ttk.LabelFrame(frm_top, text="Remote (simulated)")
        frm_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.tree_remote = ttk.Treeview(frm_right, columns=("size", "mtime"), show="headings")
        self.tree_remote.heading("size", text="Name")
        self.tree_remote.heading("mtime", text="Size")
        self.tree_remote.pack(fill=tk.BOTH, expand=True)

        # bottom: log and status
        frm_bottom = ttk.Frame(self.root)
        frm_bottom.pack(fill=tk.BOTH, expand=False)
        self.txt_log = tk.Text(frm_bottom, height=12, wrap=tk.NONE)
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        self.lbl_status = ttk.Label(self.root, text="Status: Idle")
        self.lbl_status.pack(fill=tk.X)

        # toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="Open local folder", command=self._open_local).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Open remote folder", command=self._open_remote).pack(side=tk.LEFT)

    # UI helper callbacks passed to worker
    def ui_callbacks(self):
        return {
            'log': lambda s: self.root.after(0, lambda: self._log(s)),
            'refresh_lists': lambda: self.root.after(0, self._refresh_file_lists),
            'set_status': lambda s: self.root.after(0, lambda: self.lbl_status.config(text=f"Status: {s}"))
        }

    # control actions
    def _start_stop(self):
        if self.worker and self.worker.is_alive():
            # stop
            self.worker.stop()
            self.worker = None
            self.btn_start.config(text="Start Sync")
            self._log("Requested stop of worker...")
        else:
            interval = float(self.interval_var.get())
            self.worker = BruteSyncWorker(self.local_root, self.remote_root, interval, self.ui_callbacks())
            self.worker.start()
            self.btn_start.config(text="Stop Sync")
            self._log(f"Started worker with interval {interval}s")

    def _manual_cycle_once(self):
        # create a temporary worker object to run one cycle using current snapshot file
        tmp_worker = BruteSyncWorker(self.local_root, self.remote_root, self.interval_var.get(), self.ui_callbacks())
        tmp_worker.snapshot = self._load_snapshot_if_any()
        tmp_worker._sync_cycle()
        # save snapshot back
        try:
            with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
                json.dump(tmp_worker.snapshot, f, indent=2)
            # update main snapshot if live worker exists
            if self.worker:
                self.worker.snapshot = tmp_worker.snapshot
        except Exception as e:
            self._log(f"Error saving snapshot: {e}")

    # demo file actions (local)
    def _create_random_file(self):
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '.txt'
        p = self.local_root / name
        p.write_text(f"random demo file {name}\n{time.ctime()}\n")
        self._log(f"Created local file: {name}")
        self._refresh_file_lists()

    def _modify_random_file(self):
        files = list(self.local_root.glob('*'))
        txt_files = [f for f in files if f.is_file()]
        if not txt_files:
            self._log("No local files to modify")
            return
        f = random.choice(txt_files)
        with open(f, 'a', encoding='utf-8') as fh:
            fh.write(f"mod at {time.ctime()}\n")
        os.utime(f, None)
        self._log(f"Modified local file: {f.name}")
        self._refresh_file_lists()

    def _delete_random_file(self):
        files = list(self.local_root.glob('*'))
        txt_files = [f for f in files if f.is_file()]
        if not txt_files:
            self._log("No local files to delete")
            return
        f = random.choice(txt_files)
        try:
            f.unlink()
            self._log(f"Deleted local file: {f.name}")
        except Exception as e:
            self._log(f"Error deleting file: {e}")
        self._refresh_file_lists()

    # folder selection
    def _choose_local(self):
        d = filedialog.askdirectory(title="Choose local folder")
        if d:
            self.local_root = Path(d)
            self._log(f"Set local root: {d}")
            self._refresh_file_lists()

    def _choose_remote(self):
        d = filedialog.askdirectory(title="Choose remote folder")
        if d:
            self.remote_root = Path(d)
            self._log(f"Set remote root: {d}")
            self._refresh_file_lists()

    def _open_local(self):
        try:
            os.startfile(self.local_root)
        except Exception:
            self._log("Can't open folder on this OS")

    def _open_remote(self):
        try:
            os.startfile(self.remote_root)
        except Exception:
            self._log("Can't open folder on this OS")

    # helpers
    def _log(self, s):
        ts = time.strftime('%H:%M:%S')
        self.txt_log.insert('end', f"[{ts}] {s}\n")
        self.txt_log.see('end')

    def _refresh_file_lists(self):
        # local
        for i in self.tree_local.get_children():
            self.tree_local.delete(i)
        for root, _, files in os.walk(self.local_root):
            for fn in files:
                fp = Path(root) / fn
                rel = relpath(fp, self.local_root)
                try:
                    st = fp.stat()
                    self.tree_local.insert('', 'end', values=(rel, st.st_size, time.ctime(st.st_mtime)))
                except Exception:
                    continue
        # remote
        for i in self.tree_remote.get_children():
            self.tree_remote.delete(i)
        for root, _, files in os.walk(self.remote_root):
            for fn in files:
                fp = Path(root) / fn
                rel = relpath(fp, self.remote_root)
                try:
                    st = fp.stat()
                    self.tree_remote.insert('', 'end', values=(rel, st.st_size, time.ctime(st.st_mtime)))
                except Exception:
                    continue

    def _load_snapshot_if_any(self):
        if SNAPSHOT_FILE.exists():
            try:
                with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}


# ---------------------- Main ----------------------

def main():
    root = tk.Tk()
    app = BruteSyncGUI(root)
    root.geometry('1000x600')
    root.mainloop()


if __name__ == '__main__':
    main()
