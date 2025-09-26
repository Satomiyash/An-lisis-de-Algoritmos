import os
import time
import tkinter as tk
from tkinter import filedialog

# Lista global donde guardamos los archivos encontrados
archivos_encontrados = []

def recorrer_carpeta_gui(base_dir):
    """Recorre la carpeta mostrando en GUI cada paso"""
    for root, dirs, files in os.walk(base_dir):
        # Mostrar la carpeta actual
        listbox.insert(tk.END, f"📂 Abriendo carpeta: {root}")
        listbox.yview_moveto(1.0)  # desplazar scroll hacia abajo
        ventana.update()
        time.sleep(0.5)  # pequeña pausa para ver animación

        for archivo in files:
            ruta = os.path.join(root, archivo)
            try:
                stats = os.stat(ruta)
                size = stats.st_size
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime))

                # Guardamos en arreglo
                archivos_encontrados.append({
                    "ruta": ruta,
                    "size": size,
                    "mtime": mtime
                })

                # Mostrar en GUI
                listbox.insert(tk.END, f"   📄 {archivo} | {size} bytes | {mtime}")
                listbox.yview_moveto(1.0)
                ventana.update()
                time.sleep(1)  # pausa breve para ver paso a paso

            except PermissionError:
                listbox.insert(tk.END, f"   ⚠️ {archivo} (sin permiso)")
                ventana.update()
                time.sleep(0.3)


def seleccionar_carpeta():
    """Abre un diálogo para elegir carpeta y la recorre"""
    carpeta = filedialog.askdirectory()
    if carpeta:
        listbox.delete(0, tk.END)  # limpiar lista
        archivos_encontrados.clear()
        recorrer_carpeta_gui(carpeta)
        listbox.insert(tk.END, "✅ Recorrido terminado")


# Ventana principal
ventana = tk.Tk()
ventana.title("Visualizador de Recorrido de Carpetas")
ventana.geometry("700x500")

# Botón para seleccionar carpeta
boton = tk.Button(ventana, text="Seleccionar Carpeta", command=seleccionar_carpeta)
boton.pack(pady=5)

# Listbox para mostrar recorrido
listbox = tk.Listbox(ventana, width=100, height=25)
listbox.pack(pady=10, fill="both", expand=True)

ventana.mainloop()
