import math
import tkinter as tk

def calculateDistance(point1, point2):
    return (math.sqrt(((point1.x-point2.x)**2)+((point1.y-point2.y)**2)))

class Points:
    def __init__(self):
        self.x = 0
        self.y = 0

class Interface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.optionX = tk.IntVar(value=0)
        self.optionY = tk.IntVar(value=0)
        self.listOfPointsX = []
        self.listOfPointsY = []
        self.title("Calculador de 2 puntos")
        self.lblTitle = tk.Label(self, text="Buscador de puntos más cercanos", font=("Times new roman", 28), fg="white", bg="grey")
        self.lblTitle.grid(row=0 ,column=0, sticky="nsew", pady=20)

        self.lblP1 = tk.Label(self, text="P1")
        self.lblP1.grid(row=1 ,column=0, sticky="nsew", pady=20)
        self.entryP1x = tk.Entry(self, variable=self.optionX).grid(row=1, column=1)
        self.entryP1y = tk.Entry(self, variable=self.optionY).grid(row=1, column=2)
        self.listOfPoints.append(self.optionX.get())
        self.listOfPoints.append(self.optionY.get())

        self.lblP2 = tk.Label(self, text="P2")
        self.lblP2.grid(row=2 ,column=0, sticky="nsew", pady=20)
        self.entryP2x = tk.Entry(self, variable=self.optionX).grid(row=2, column=1)
        self.entryP2y = tk.Entry(self, variable=self.optionY).grid(row=2, column=2)
        self.listOfPoints.append(self.optionX.get())
        self.listOfPoints.append(self.optionY.get())
        
        self.lblP3 = tk.Label(self, text="P3")
        self.lblP3.grid(row=3 ,column=0, sticky="nsew", pady=20)
        self.entryP3x = tk.Entry(self, variable=self.optionX).grid(row=3, column=1)
        self.entryP3y = tk.Entry(self, variable=self.optionY).grid(row=3, column=2)
        self.listOfPoints.append(self.optionX.get())
        self.listOfPoints.append(self.optionY.get())

        self.lblP4 = tk.Label(self, text="P1")
        self.lblP4.grid(row=4 ,column=0, sticky="nsew", pady=20)
        self.entryP4x = tk.Entry(self, variable=self.optionX).grid(row=4, column=1)
        self.entryP4y = tk.Entry(self, variable=self.optionY).grid(row=4, column=2)
        self.listOfPoints.append(self.optionX.get())
        self.listOfPoints.append(self.optionY.get())

        self.lblP5 = tk.Label(self, text="P1")
        self.lblP5.grid(row=5 ,column=0, sticky="nsew", pady=20)
        self.entryP5x = tk.Entry(self, variable=self.optionX).grid(row=5, column=1)
        self.entryP5y = tk.Entry(self, variable=self.optionY).grid(row=5, column=2)
        self.listOfPoints.append(self.optionX.get())
        self.listOfPoints.append(self.optionY.get())





