import tkinter as tk
from tkinter import ttk
import points
from points import Point


class Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.listOfPoints = []
        self.title("Calculador de 2 puntos")

        self.configure(bg="#FEEBF6")

        self.frameTitle = tk.Frame(self, bg="#BE5985")
        self.frameTitle.grid(row=0, column=0, sticky="nsew")
        self.lblTitle = tk.Label(
            self.frameTitle,
            text="Buscador de puntos más cercanos",
            font=("Times New Roman", 18, "bold"),
            bg="#BE5985",
            fg="white",
            pady=15,
        )
        self.lblTitle.grid(row=0, column=0, sticky="nsew", padx=20)

        self.frameData = tk.LabelFrame(
            self,
            text=" Coordenadas de los puntos ",
            padx=20,
            pady=10,
            bg="#eeeeee",
            font=("Times New Roman", 12, "bold"),
        )
        self.frameData.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        ttk.Label(self.frameData, text="x").grid(row=0, column=1, padx=10)
        ttk.Label(self.frameData, text="y").grid(row=0, column=2, padx=10)

        self.entries = {}
        for i in range(1, 6):
            ttk.Label(self.frameData, text=f"P{i}").grid(row=i, column=0, sticky="w", pady=5)
            self.entries[f"P{i}x"] = ttk.Entry(self.frameData, width=7)
            self.entries[f"P{i}x"].grid(row=i, column=1, padx=10)
            self.entries[f"P{i}y"] = ttk.Entry(self.frameData, width=7)
            self.entries[f"P{i}y"].grid(row=i, column=2, padx=10)

        style = ttk.Style()
        style.configure("TButton", font=("Times New Roman", 10), padding=6)

        ttk.Button(self.frameData, text="Llenar Random", command=self.generateData).grid(
            row=2, column=3, padx=20, pady=5
        )
        ttk.Button(self.frameData, text="Calcular", command=self.calculateShortDistance).grid(
            row=3, column=3, padx=20, pady=5
        )
        ttk.Button(self.frameData, text="Limpiar", command=self.cleanData).grid(
            row=4, column=3, padx=20, pady=5
        )

        self.frameResult = tk.Frame(self, bg="#FEEBF6")
        self.frameResult.grid(row=2, column=0, pady=20)
        self.lblResult = tk.Label(
            self.frameResult,
            text="",
            font=("Times New Roman", 12),
            fg="#333",
            bg="#EEEEEE",
            padx=20,
            pady=10,
            relief="groove",
            width=60,
            anchor="center",
        )
        self.lblResult.grid(row=0, column=0, pady=10)

        self.after(100, self.centerWindow)

    def centerWindow(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def generateData(self):
        self.cleanData()
        listOfPoints = points.generateListOfPoints(5)
        for i, p in enumerate(listOfPoints, start=1):
            self.entries[f"P{i}x"].insert(0, p.xPos)
            self.entries[f"P{i}y"].insert(0, p.yPos)

    def cleanData(self):
        self.listOfPoints = []
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def calculateShortDistance(self):
        self.listOfPoints = []
        for i in range(1, 6):
            point = Point()
            point.xPos = self.entries[f"P{i}x"].get()
            point.yPos = self.entries[f"P{i}y"].get()
            point.name = f"P{i}"
            if point.xPos.isdigit() and point.yPos.isdigit():
                point.xPos = int(point.xPos)
                point.yPos = int(point.yPos)
                self.listOfPoints.append(point)

        if len(self.listOfPoints) <= 1:
            self.lblResult.config(text="Algo no está bien, intente de nuevo...")
            return
        
        listOfDistances = points.calculateDistance(self.listOfPoints)
        shortDistance = points.findShortDistance(listOfDistances)
        result = f"La distancia más corta es entre {shortDistance[1]} y {shortDistance[2]} con una distancia de: {shortDistance[0]}"
        self.lblResult.config(text=result)

