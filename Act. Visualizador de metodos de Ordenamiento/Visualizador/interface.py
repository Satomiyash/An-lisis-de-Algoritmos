import tkinter as tk
from tkinter import ttk
from graphic import Graphic
from algorithms import bubbleSort, selectionSort, mergeSort, quickSort


class Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.opciones = ["Bubble Sort",
                         "Selection Sort", "Merge Sort", "Quick Sort"]
        self.numBarras = tk.IntVar(value=40)
        self.selection = tk.StringVar(value="Selection Sort")
        self.isHighlight = tk.IntVar(value=False)
        self.delayTime = tk.IntVar(value=50)

        self.title("Visualizador de metodos de Ordenamiento")
        self.geometry("1020x700")

        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Panel superior (número de datos y velocidad)
        self.upperPanel = tk.Frame(self)
        self.upperPanel.grid(row=0, column=0, sticky='ew', pady=5, padx=10)
        self.upperPanel.grid_columnconfigure(1, weight=1)

        # Entrada de número de datos
        tk.Label(self.upperPanel, text="Número de datos:").grid(
            row=0, column=0, sticky='w', padx=5)
        self.entryNum = tk.Entry(
            self.upperPanel, textvariable=self.numBarras, width=10)
        self.entryNum.grid(row=0, column=1, sticky='w', padx=5)

        # Control de velocidad (ahora con command para actualizar en tiempo real)
        tk.Label(self.upperPanel, text="Velocidad:").grid(
            row=0, column=2, sticky='w', padx=20)
        self.delayScale = tk.Scale(self.upperPanel, from_=1, to=200, orient="horizontal",
                                   variable=self.delayTime, showvalue=True, length=150,
                                   command=self.update_delay)
        self.delayScale.grid(row=0, column=3, sticky='w', padx=5)

        # Segundo panel superior (algoritmo, resaltado y estado)
        self.upperPanel2 = tk.Frame(self)
        self.upperPanel2.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        self.upperPanel2.grid_columnconfigure(3, weight=1)

        # Selección de algoritmo
        tk.Label(self.upperPanel2, text="Algoritmo:").grid(
            row=0, column=0, sticky='w', padx=5)
        self.select = ttk.Combobox(self.upperPanel2, values=self.opciones, state="readonly",
                                   textvariable=self.selection, width=15)
        self.select.grid(row=0, column=1, sticky='w', padx=5)
        self.select.set("Selection Sort")

        # Checkbox de resaltado
        self.highlightCheck = tk.Checkbutton(self.upperPanel2, text="Resaltar elementos",
                                             variable=self.isHighlight, command=self.toggle_highlight)
        self.highlightCheck.grid(row=0, column=2, sticky='w', padx=20)

        # Label de estado
        self.statusLabel = tk.Label(self.upperPanel2, text="Listo", fg="green")
        self.statusLabel.grid(row=0, column=3, sticky='e', padx=10)

        # Frame para el gráfico
        self.graphicFrame = tk.Frame(self)
        self.graphicFrame.grid(
            row=2, column=0, sticky='nsew', padx=10, pady=10)
        self.graphicFrame.grid_columnconfigure(0, weight=1)
        self.graphicFrame.grid_rowconfigure(0, weight=1)

        # Inicializar el gráfico
        self.graphic = Graphic(self.graphicFrame)
        self.graphic.canvas.grid(row=0, column=0, sticky='nsew')
        self.graphic.generar(self.numBarras.get(), self.isHighlight.get())

        # Panel inferior (botones)
        self.lowerPanel = tk.Frame(self)
        self.lowerPanel.grid(row=3, column=0, sticky='ew', pady=10, padx=10)

        # Botones
        self.generateBtn = tk.Button(
            self.lowerPanel, text="Generar", command=self.generate_data, width=12)
        self.generateBtn.grid(row=0, column=0, padx=5)

        self.sortBtn = tk.Button(
            self.lowerPanel, text="Ordenar", command=self.start_sorting, width=12)
        self.sortBtn.grid(row=0, column=1, padx=5)

        self.stopBtn = tk.Button(self.lowerPanel, text="Detener", command=self.stop_sorting,
                                 state=tk.DISABLED, width=12)
        self.stopBtn.grid(row=0, column=2, padx=5)

        self.shuffleBtn = tk.Button(
            self.lowerPanel, text="Mezclar", command=self.shuffle_data, width=12)
        self.shuffleBtn.grid(row=0, column=3, padx=5)

        # Centrar botones
        for i in range(4):
            self.lowerPanel.grid_columnconfigure(i, weight=1)

    def update_delay(self, value):
        """Se llama cuando se cambia el scale de velocidad"""
        # Esta función se ejecuta automáticamente cuando se mueve el scale
        pass  # No necesita hacer nada, solo actualiza la variable delayTime

    def generate_data(self):
        try:
            num = int(self.numBarras.get())
            if num < 5:
                num = 5
            elif num > 200:
                num = 200
            self.numBarras.set(num)

            if self.graphic.generar(num, bool(self.isHighlight.get())):
                self.update_status("Datos generados", "green")
            else:
                self.update_status(
                    "No se puede generar durante ordenamiento", "red")
        except ValueError:
            self.update_status("Número inválido", "red")

    def start_sorting(self):
        algorithm = self.selectSort()
        if algorithm and self.graphic.ordenar(algorithm, self.delayTime.get(), bool(self.isHighlight.get())):
            self.update_buttons_state(False)
            self.update_status("Ordenando...", "blue")
        else:
            self.update_status("No se puede ordenar", "red")

    def stop_sorting(self):
        self.graphic.detener_ordenamiento()
        self.update_buttons_state(True)
        self.update_status("Ordenamiento detenido", "orange")

    def shuffle_data(self):
        if self.graphic.shuffle(bool(self.isHighlight.get())):
            self.update_status("Datos mezclados", "green")
        else:
            self.update_status(
                "No se puede mezclar durante ordenamiento", "red")

    def toggle_highlight(self):
        self.graphic.set_highlight(bool(self.isHighlight.get()))

    def update_buttons_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.generateBtn.config(state=state)
        self.sortBtn.config(state=state)
        self.shuffleBtn.config(state=state)
        self.stopBtn.config(state=tk.NORMAL if not enabled else tk.DISABLED)

    def update_status(self, message, color):
        self.statusLabel.config(text=message, fg=color)

    def selectSort(self):
        option = self.select.get()
        if option == "Bubble Sort":
            return bubbleSort
        elif option == "Selection Sort":
            return selectionSort
        elif option == "Merge Sort":
            return mergeSort
        elif option == "Quick Sort":
            return quickSort
        return None