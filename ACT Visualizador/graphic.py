import tkinter as tk
from tkinter import ttk
import random
import time
import algorithms

class Graphic():

    def __init__(self, belonging):
        self.ANCHO = 800
        self.ALTO = 300
        self.VAL_MIN, self.VAL_MAX = 5, 100
        self.canvas = tk.Canvas(belonging, width=self.ANCHO, height=self.ALTO, bg="white")
        self.data = []
        self.execute = False
        self.pause = False
        self.gen = None
        self.paso = None
        self.highlight = tk.IntVar(value=False)
        self.delay = tk.IntVar(value=0)


    def dibujar_barras(self, canvas, activos=None):
        if not self.highlight.get():
            activos=None
        self.canvas.delete("all")
        if not self.data: return
        n = len(self.data)
        margen = 10
        ancho_disp = self.ANCHO - 2 * margen
        alto_disp = self.ALTO - 2 * margen
        w = ancho_disp / n
        esc = alto_disp / max(self.data)
        for i, v in enumerate(self.data):
            x0 = margen + i * w
            x1 = x0 + w * 0.9
            h = v * esc
            y0 = self.ALTO - margen - h
            y1 = self.ALTO - margen
            color = "#4e79a7"
            if activos and i in activos:
                color = "#f28e2b"
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
        canvas.create_text(6, 6, anchor="nw", text=f"n={len(self.data)}", fill="#666")


    def generar(self, num):
        if self.execute: 
            return
        if not isinstance(num, int):
            num = 20
        random.seed(time.time())
        self.data = [random.randint(self.VAL_MIN, self.VAL_MAX) for _ in range(num)]
        self.dibujar_barras(self.canvas)

    def ordenar(self, function, delayVar, belonging, highlightVar):
        if self.execute: 
            return
        if self.pause:
            return
        if not self.data:
            return
        self.delay = delayVar
        self.highlight = highlightVar
        self.gen = function(
            self.data,
            lambda activos=None: self.dibujar_barras(self.canvas, activos)
        )
        self.execute = True
        def paso():
            if self.pause:
                return
            try:
                next(self.gen)
                belonging.after(self.delay.get(), paso)
            except StopIteration:
                self.execute = False
                pass

        self.paso = paso
        paso()
    

    def stopIteration(self):
        self.execute = False
        self.canvas.delete("all")
        self.dibujar_barras(self.canvas)
        self.paso = None
        self.gen = None

    def continueIteration(self, belonging):
        if self.pause and hasattr(self, "gen"):
            self.pause = False
        if hasattr(self, "paso"):
            belonging.after(self.delay.get(), self.paso)

    def pauseIteration(self):
        self.pause = True
        self.canvas.delete("all")
        self.dibujar_barras(self.canvas)

    def shuffle(self):
        if self.execute: 
            return
        random.shuffle(self.data)
        self.dibujar_barras(self.canvas)
        
