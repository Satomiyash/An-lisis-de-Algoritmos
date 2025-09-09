import tkinter as tk
from tkinter import ttk
import random
import time
import algorithms


class Graphic():

    def __init__(self, belonging):
        self.ANCHO = 1000
        self.ALTO = 500
        self.VAL_MIN, self.VAL_MAX = 10, 500  # Rango más amplio
        self.canvas = tk.Canvas(
            belonging, width=self.ANCHO, height=self.ALTO, bg="#2c3e50")
        self.data = []
        self.sorting_active = False
        self.current_gen = None
        self.after_id = None
        self.belonging = belonging
        self.isHighlight = False
        self.current_delay = 50
        self.main_interface = belonging.master

        # Colores
        self.COLOR_NORMAL = "#3498db"    # Azul
        self.COLOR_HIGHLIGHT = "#e74c3c"  # Rojo
        self.COLOR_BG = "#2c3e50"        # Fondo oscuro
        self.COLOR_TEXT = "#ecf0f1"      # Texto blanco

        # Definir área reservada para información superior
        self.TOP_MARGIN = 100

    def dibujar_barras(self, activos=None):
        self.canvas.delete("all")
        if not self.data:
            return

        n = len(self.data)
        margen_lateral = 30
        margen_superior = self.TOP_MARGIN
        margen_inferior = 30

        ancho_disp = self.ANCHO - 2 * margen_lateral
        alto_disp = self.ALTO - margen_superior - margen_inferior

        w = ancho_disp / n
        max_val = max(self.data) if self.data else 100

        # Linea de la base de la gráfica
        self.canvas.create_line(
            margen_lateral, self.ALTO - margen_inferior,
            self.ANCHO - margen_lateral, self.ALTO - margen_inferior,
            fill="#7f8c8d", width=3
        )

        for i, v in enumerate(self.data):
            x0 = margen_lateral + i * w
            x1 = x0 + w * 0.70

            # Calcular altura - usar el espacio disponible (restamos el margen superior)
            h = (v / max_val) * alto_disp
            y0 = self.ALTO - margen_inferior - h  # Comenzar desde el margen inferior
            y1 = self.ALTO - margen_inferior

            if self.isHighlight and activos and i in activos:
                color = self.COLOR_HIGHLIGHT  # Rojo para resaltado
            else:
                color = self.COLOR_NORMAL     # Azul para normal

            # Dibujar barra
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=color,
                outline="",
                width=0
            )

            # Mostrar valores
            if w > 15:
                self.canvas.create_text(
                    (x0 + x1) / 2, y0 - 10,  # Texto
                    text=str(v),
                    fill=self.COLOR_TEXT,
                    font=("Arial", 10, "bold"),
                    anchor="center"
                )

        # Información adicional elementos
        self.canvas.create_text(
            margen_lateral + 10, 15,  # Posición en la zona superior
            anchor="nw",
            text=f"📊 Elementos: {len(self.data)}",
            fill=self.COLOR_TEXT,
            font=("Arial", 12, "bold")  # Texto más grande
        )

        # Información de valor máximo
        self.canvas.create_text(
            self.ANCHO - margen_lateral - 10, 15,
            anchor="ne",
            text=f"Max: {max_val}",
            fill=self.COLOR_TEXT,
            font=("Arial", 12, "bold")
        )

        # Información de valor mínimo
        min_val = min(self.data) if self.data else 0
        self.canvas.create_text(
            self.ANCHO - margen_lateral - 10, 40,
            anchor="ne",
            text=f"Min: {min_val}",
            fill=self.COLOR_TEXT,
            font=("Arial", 12, "bold")
        )

        if self.sorting_active:
            self.canvas.create_text(
                self.ANCHO // 2, 15,  # Centrado en la parte superior
                anchor="center",
                text="⏩ ORDENANDO...",
                fill="#f39c12",
                font=("Arial", 14, "bold")
            )

    def set_highlight(self, highlight):
        """Establece el estado de resaltado"""
        self.isHighlight = highlight
        self.dibujar_barras()

    def generar(self, num, isHighlight):
        if self.sorting_active:
            return False

        if not isinstance(num, int):
            num = 30  # Valor por defecto
        random.seed(time.time())
        self.data = []
        for _ in range(num):
            rand_val = random.randint(self.VAL_MIN, self.VAL_MAX)
            self.data.append(rand_val)

        self.set_highlight(isHighlight)
        return True

    def ordenar(self, function, delay, isHighlight):
        if not self.data or self.sorting_active:
            return False

        self.sorting_active = True
        self.set_highlight(isHighlight)
        self.current_delay = delay

        # Crear el generador con la función de callback
        self.current_gen = function(
            self.data,
            lambda activos=None: self.dibujar_barras(activos)
        )

        def paso():
            if not self.sorting_active:
                return

            try:
                next(self.current_gen)
                # Obtener el delay actual en tiempo real
                current_delay = self.main_interface.delayTime.get()
                self.after_id = self.belonging.after(current_delay, paso)
            except StopIteration:
                self.finalizar_ordenamiento()
                # Notificar a la interfaz que terminó
                if hasattr(self.main_interface, 'update_buttons_state'):
                    self.main_interface.update_buttons_state(True)
                if hasattr(self.main_interface, 'update_status'):
                    self.main_interface.update_status(
                        "✅ Ordenamiento completado", "green")

        paso()
        return True

    def finalizar_ordenamiento(self):
        self.sorting_active = False
        self.current_gen = None
        if self.after_id:
            self.belonging.after_cancel(self.after_id)
            self.after_id = None
        # Redibujar todas las barras en color normal
        self.dibujar_barras()

    def detener_ordenamiento(self):
        if self.sorting_active:
            self.finalizar_ordenamiento()
            # Notificar a la interfaz que se detuvo
            if hasattr(self.main_interface, 'update_buttons_state'):
                self.main_interface.update_buttons_state(True)
            if hasattr(self.main_interface, 'update_status'):
                self.main_interface.update_status(
                    "⏹️ Ordenamiento detenido", "orange")

    def shuffle(self, isHighlight):
        if self.sorting_active:
            return False

        random.shuffle(self.data)
        self.set_highlight(isHighlight)
        return True