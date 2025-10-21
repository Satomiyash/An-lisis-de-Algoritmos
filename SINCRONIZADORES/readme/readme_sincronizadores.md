# Sincronizador DYV

Servidor y cliente para sincronización automática de archivos entre una carpeta local y un servidor central.

---

## Estructura del proyecto

```
DYV/
├─ server/
│  ├─ app.py               # Servidor Flask
│  ├─ client_sync.py       # Cliente Python para sincronización automática
│  ├─ templates/
│  │  └─ index.html        # Interfaz web
│  └─ uploads/             # Carpeta donde se almacenan los archivos subidos
```

---

## Requisitos

- Python 3.10+
- Flask
- Requests
- Internet o red local para conectar cliente y servidor

Instalar dependencias:

```bash
pip install flask requests
```

---

## Cómo ejecutar

### 1. Servidor

Desde la carpeta `server/`:

```bash
python app.py
```

Accede a la interfaz web en: `http://127.0.0.1:5000`

- Subir archivos o carpetas.
- Descargar archivos.
- Descargar cliente de sincronización (`client_sync.py`).

---

### 2. Cliente (sincronización automática)

En la máquina cliente:

```bash
python client_sync.py
```

- Antes de ejecutar, modifica estas dos líneas en `client_sync.py` para que apunten a tu configuración:
```python
SERVER_URL = "http://<IP_DEL_SERVIDOR>:5000"
LOCAL_DIR = Path("<RUTA_LOCAL_A_SYNC>")
```
- Se sincronizará automáticamente la carpeta local (`LOCAL_DIR`) con el servidor.
- La sincronización ocurre cada `POLL_INTERVAL` segundos (configurable en `client_sync.py`).

---

## Notas

- Los archivos se sincronizan basándose en hash SHA256.
- Archivos eliminados localmente se eliminan en el servidor y viceversa.
- Interfaz web permite operaciones manuales si se prefiere.

