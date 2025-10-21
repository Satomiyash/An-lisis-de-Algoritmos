import hashlib
import time
import os
import matplotlib.pyplot as plt

BLOCK_SIZE = 1 * 1024 

# --- Algoritmos ---
def calc_sha256_block(path):
    """Algoritmo 1: Calcula SHA256 por bloques de 4 KB"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def calc_sha256_full(path):
    """Algoritmo 2: Calcula SHA256 leyendo todo el archivo de una vez"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

# --- Función para medir tiempo ---
def measure_time(func, path):
    start = time.time()
    func(path)
    end = time.time()
    return end - start

# --- Generar archivos de prueba ---
file_sizes = [1024, 100*1024, 1000*1024, 1024*1024, 10*1024*1024, 100*1024*1024, 1000*1024*1024]  # en bytes
file_names = []

for size in file_sizes:
    filename = f"test_{size}.bin"
    with open(filename, "wb") as f:
        f.write(os.urandom(size))  # archivo con datos aleatorios
    file_names.append(filename)

# --- Medir tiempos ---
times_block = []
times_full = []

for file in file_names:
    times_block.append(measure_time(calc_sha256_block, file))
    times_full.append(measure_time(calc_sha256_full, file))

# --- Graficar ---
plt.plot(file_sizes, times_block, marker='o', label="Por bloques (4KB)")
plt.plot(file_sizes, times_full, marker='x', label="Todo de una vez")
plt.xlabel("Tamaño de archivo (bytes)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("Comparativa temporal de algoritmos SHA256")
plt.legend()
plt.grid(True)
plt.show()

# --- Limpiar archivos de prueba ---
for file in file_names:
    os.remove(file)
