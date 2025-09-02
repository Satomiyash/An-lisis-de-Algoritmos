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

        self.graphicFrame = tk.Frame(self)
        self.graphicFrame.grid(row=2, column=0, sticky='nsew')
        self.graphic = Graphic(self.graphicFrame)
        self.graphic.canvas.grid(row=1, column=1, padx=30, pady=20)
        self.graphic.generar(self.numBarras.get())

        self.upperPanel = tk.Frame(self)
        self.upperPanel.grid(row=0, column=0, sticky='nsew', pady=20, padx=35)
        self.lblEntryNum = tk.Label(self.upperPanel, text="Ingresa el numero de datos: ").grid(
            row=0, column=0, sticky='w')
        self.entryNum = tk.Entry(self.upperPanel, textvariable=self.numBarras).grid(
            row=0, column=1, sticky='w')
        self.delay = tk.Scale(self.upperPanel, from_=0, to=200, orient="horizontal", label="Selecciona la velocidad",
                              variable=self.delayTime).grid(row=0, column=3, ipadx=30, padx=150, sticky='e')

        self.upperPanel2 = tk.Frame(self)
        self.upperPanel2.grid(row=1, column=0, sticky='nsew', padx=35)
        self.select = ttk.Combobox(
            self.upperPanel2, values=self.opciones, state="readonly", textvariable=self.selection)
        self.select.set("Seleccionar ordenamientos")
        self.select.grid(row=0, column=0, sticky='w', ipadx=50)
        self.highlight = tk.Checkbutton(self.upperPanel2, text="Seleccione si desea resaltar", onvalue=True,
                                        offvalue=False, variable=self.isHighlight).grid(row=0, column=1, padx=185, sticky='w')

        self.lowerPanel = tk.Frame(self)
        self.lowerPanel.grid(row=3, column=0, sticky='nsew', pady=10)
        self.generateBtn = tk.Button(self.lowerPanel, text="Generar", command=lambda: self.graphic.generar(
            self.numBarras.get())).grid(row=0, column=0, padx=35, ipadx=50, pady=10, sticky='nsew')
        self.shuffleBtn = tk.Button(self.lowerPanel, text="Mezclar", command=lambda: self.graphic.shuffle(
            )).grid(row=1, column=0, padx=35, ipadx=50, pady=20, sticky='nsew')
        self.sortBtn = tk.Button(self.lowerPanel, text="Ordenar", command=lambda: self.graphic.ordenar(self.selectSort(
            ), self.delayTime, self, self.isHighlight)).grid(row=0, column=1, padx=50, pady=10, ipadx=50, sticky='nsew')
        self.stopBtn = tk.Button(self.lowerPanel, text="Detener", command=lambda: self.graphic.stopIteration(
            )).grid(row=1, column=1, padx=50, ipadx=50, pady=20, sticky='nsew')
        self.pauseBtn = tk.Button(self.lowerPanel, text="Pausar", command=lambda: self.graphic.pauseIteration()).grid(row=0, column=2, padx=50, ipadx=50,pady=10, sticky='nsew')
        self.continueBtn = tk.Button(self.lowerPanel, text="Continuar", command=lambda: self.graphic.continueIteration(self)).grid(row=1, column=2, padx=50, ipadx=50, pady=20, sticky='nsew')

        


    def printN(self):
        print(self.numBarras.get())

    def selectSort(self):
        option = self.select.get()
        if option == "Bubble Sort":
            selection = bubbleSort
        elif option == "Selection Sort":
            selection = selectionSort
        elif option == "Merge Sort":
            selection = mergeSort
        elif option == "Quick Sort":
            selection = quickSort
        return selection