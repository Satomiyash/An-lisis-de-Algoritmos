import time
import matplotlib.pyplot as plt
import tracemalloc
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def fib_recursivo(n):
    if n <= 1:
        return n
    return fib_recursivo(n - 1) + fib_recursivo(n - 2)

def fib_dinamico(n, memo=None):
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        memo[n] = n
    else:
        memo[n] = fib_dinamico(n - 1, memo) + fib_dinamico(n - 2, memo)
    return memo[n]


def temporalComplexity(function, ns):
    times = []
    for n in ns:
        inicio = time.time()
        function(n)
        times.append(time.time() - inicio) 
    return times

def spaceComplexity(function, ns):
    memory = []
    for n in ns:
        tracemalloc.start()
        function(n)
        _, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory.append(mem_pico / 1024)  # convertir a KB
    return memory


def ejecutar():
    try:
        n_max = int(entry_n.get())
        if n_max < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa un número entero positivo.")
        return

    # Crear lista de valores de n
    ns = list(range(1, n_max + 1))

    # Calcular complejidades
    tiemposR = temporalComplexity(fib_recursivo, ns)
    tiemposD = temporalComplexity(fib_dinamico, ns)
    memoriaR = spaceComplexity(fib_recursivo, ns)
    memoriaD = spaceComplexity(fib_dinamico, ns)

    # Crear figura y subgráficas
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))

    # -------- Gráfica de tiempo --------
    axes[0].plot(ns, tiemposR, 'o-r', label='Recursivo')
    axes[0].plot(ns, tiemposD, 'o-g', label='Dinámico')
    axes[0].set_xlabel("Tamaño de entrada (n)")
    axes[0].set_ylabel("Tiempo (s)")
    axes[0].set_title("Complejidad Temporal")
    axes[0].legend()
    axes[0].grid(True)

    # -------- Gráfica de memoria --------
    axes[1].plot(ns, memoriaR, 'o-r', label='Recursivo')
    axes[1].plot(ns, memoriaD, 'o-g', label='Dinámico')
    axes[1].set_xlabel("Tamaño de entrada (n)")
    axes[1].set_ylabel("Memoria (KB)")
    axes[1].set_title("Complejidad Espacial")
    axes[1].legend()
    axes[1].grid(True)

    fig.tight_layout()

    # Si ya existe un gráfico previo, eliminarlo antes de mostrar el nuevo
    for widget in frame_grafica.winfo_children():
        widget.destroy()

    # Insertar la figura en la GUI
    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------------- INTERFAZ GRÁFICA (Tkinter) ----------------

ventana = tk.Tk()
ventana.title("Análisis de Complejidad de Fibonacci")
ventana.geometry("900x600")
ventana.config(bg="#f0f0f0")

titulo = tk.Label(
    ventana,
    text="Análisis de Complejidad Temporal y Espacial\nFibonacci Recursivo vs Dinámico",
    font=("Arial", 14, "bold"),
    bg="#f0f0f0",
    justify="center"
)
titulo.pack(pady=10)

# Entrada de n
frame_input = tk.Frame(ventana, bg="#f0f0f0")
frame_input.pack(pady=10)

label_n = tk.Label(frame_input, text="Calcular hasta n =", bg="#f0f0f0", font=("Arial", 11))
label_n.pack(side=tk.LEFT, padx=5)

entry_n = ttk.Entry(frame_input, width=10)
entry_n.pack(side=tk.LEFT, padx=5)
entry_n.insert(0, "25")

boton = ttk.Button(ventana, text="Ejecutar y Graficar", command=ejecutar)
boton.pack(pady=10)

# Marco donde se insertarán las gráficas
frame_grafica = tk.Frame(ventana, bg="#ffffff", relief=tk.SUNKEN, borderwidth=2)
frame_grafica.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

ventana.mainloop()

