import tkinter as tk
import algorithms
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Interface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.myList = []
        self.listSize = [100, 1000, 10000, 100000]
        self.listTimeL = [None] * len(self.listSize)
        self.listTimeB = [None] * len(self.listSize)
        self.option = tk.IntVar(value=0)
        self.tempOption = tk.IntVar(value=0)

        self.title("Practica 1")

        self.lblTitle = tk.Label(self, text="Analizador de algoritmos de búsqueda", font=("Times new roman", 28), fg="white", bg="grey")
        self.lblTitle.grid(row=0 ,column=0, sticky="nsew", pady=20)
        self.askSize = tk.Label(self, text="Ingrese la cantidad de elementos que desea en su lista", font=("Times new roman", 12))
        self.askSize.grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.entrySize100=tk.Radiobutton(self, text="100", variable=self.tempOption, value=100)
        self.entrySize100.grid(row=3, column=0, pady=5, padx=100, sticky="w")
        self.entrySize1000=tk.Radiobutton(self, text="1000", variable=self.tempOption, value=1000)
        self.entrySize1000.grid(row=3, column=0, pady=5, padx=200, sticky="w")
        self.entrySize10000=tk.Radiobutton(self, text="10000", variable=self.tempOption, value=10000)
        self.entrySize10000.grid(row=3, column=0, pady=5, padx=300,  sticky="w")
        self.entrySize100000=tk.Radiobutton(self, text="100000", variable=self.tempOption, value=100000)
        self.entrySize100000.grid(row=3, column=0, pady=5, padx=400,  sticky="w")
        self.buttonGenerate=tk.Button(self, text="Generar datos", command=self.fillList)
        self.buttonGenerate.grid(row=4, column=0, sticky="w", padx=10)
        self.lblShowData = tk.Label(self, text="")
        self.lblShowData.grid(row=5, column=0, pady=5, padx=10, sticky="w")
        self.askNum = tk.Label(self, text="Ingrese el elemento que desea en su encontrar", font=("Times new roman", 12))
        self.askNum.grid(row=6, column=0, pady=15, padx=10, sticky="w")
        self.entryNum = tk.Entry(self)
        self.entryNum.grid(row=7, column=0, pady=5,  padx=10, sticky="w")
        self.buttonTimeL=tk.Button(self, text="Busqueda Lineal", command=self.calculateTimeL)
        self.buttonTimeL.grid(row=8, column=0, padx=10, sticky="w")
        self.lblShowTimeL = tk.Label(self, text="")
        self.lblShowTimeL.grid(row=9, column=0, pady=5, padx=10, sticky="w")
        self.lblShowDataL = tk.Label(self, text="")
        self.lblShowDataL.grid(row=10, column=0, pady=5, padx=10, sticky="w")
        self.buttonTimeB=tk.Button(self, text="Busqueda Binaria", command=self.calculateTimeB)
        self.buttonTimeB.grid(row=11, column=0, padx=10, sticky="w")
        self.lblShowTimeB = tk.Label(self, text="")
        self.lblShowTimeB.grid(row=12, column=0, pady=5, padx=10, sticky="w")
        self.lblShowDataB = tk.Label(self, text="")
        self.lblShowDataB.grid(row=13, column=0, pady=5, padx=10, sticky="w")

        self.figure, self.graphic = plt.subplots(figsize=(5, 4))
        self.timeL, = self.graphic.plot(self.listSize, self.listTimeL, marker="*", color="blue", label="Busqueda lineal")
        self.timeB, = self.graphic.plot(self.listSize, self.listTimeB, marker="*", color="green", label="Busqueda binaria")
        self.graphic.set_title("Gráfica de tiempos")
        self.graphic.set_xlabel("Tamaño de la lista")
        self.graphic.set_ylabel("Tiempo (s)")
        self.graphic.grid(True)
        self.graphic.legend()

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=14, column=0, columnspan=2, sticky="nsew")

    def fillList(self):
        self.option.set(self.tempOption.get())
        self.myList = algorithms.generateData(self.option.get())
        self.lblShowData.config(text="Lista creada con exito, el tamaño es " + str(self.option.get()))

    def calculateTimeL(self):
        try:
            search = int(self.entryNum.get())
            timeTotal = 0
            for i in range (5):
                timeStart = time.perf_counter()
                self.lblShowDataL.config(text=algorithms.searchL(self.myList, search))
                timeEnd = time.perf_counter()
                timeTotal += timeEnd -timeStart
            timeTotal = timeTotal/5
            self.listTimeL[self.updateList(self.option.get())] = timeTotal
            self.lblShowTimeL.config(text="El tiempo de la busqueda lineal en promedio de 5 repeticiones es " + str(timeTotal))
            self.updateGraphic()
        except ValueError:
            self.lblShowTimeL.config(text="Algo no esta bien, intente de nuevo")
            self.lblShowDataL.config(text="")

    
    def calculateTimeB(self):
        try:
            search = int(self.entryNum.get())
            timeTotal = 0
            for i in range (5):
                timeStart = time.perf_counter()
                self.lblShowDataB.config(text=algorithms.searchB(self.myList, search))
                timeEnd = time.perf_counter()
                timeTotal += timeEnd -timeStart
            timeTotal = timeTotal/5
            self.listTimeB[self.updateList(self.option.get())] = timeTotal
            self.lblShowTimeB.config(text="El tiempo de la busqueda binaria en promedio de 5 repeticiones es " + str(timeTotal))
            self.updateGraphic()
        except ValueError:
            self.lblShowTimeB.config(text="Algo no esta bien, intente de nuevo")
            self.lblShowDataB.config(text="")


    def updateGraphic(self):
        self.timeL.set_data(self.listSize, self.listTimeL)
        self.timeB.set_data(self.listSize, self.listTimeB)
        self.graphic.relim()
        self.graphic.autoscale_view()
        self.canvas.draw()

    def updateList(self, size):
        for i in range (len(self.listSize)):
            if size == self.listSize[i]:
                return i



