# Practica 1 - ADA

Este proyecto implementa una interfaz en Python con Tkinter que permite generar listas de distintos tamaños y buscar elementos mediante búsqueda lineal y binaria, para medir los tiempos de ejecución de cada una y compararlas gráficamente mediante los resultados obtenidos en función del tamaño de la muestra.

## Requisitos

- Python 3.x
- Librerías externas:
  ```bash
  pip install matplotlib
  ```
- Librerías estándar de Python usadas: `tkinter`, `time`, `random` (no necesitan instalación)

## Ejecución

1. Instalar dependencias:
   ```bash
   pip install matplotlib
   ```

2. Ejecutar el programa:
   ```bash
   python main.py
   ```

3. Usar la interfaz:
   - Seleccionar el tamaño de la lista (100, 1000, 10000 o 100000)
   - Generar la lista
   - Ingresar el número a buscar
   - Hacer la búsqueda lineal y la binaria
   - Ver los tiempos de búsqueda y la gráfica comparativa

## Notas

- Cada búsqueda se realiza 5 veces y se muestra el tiempo promedio.
- La gráfica compara visualmente los tiempos de búsqueda en función del tamaño de la lista.
- El código está desarrollado en Python 3 y requiere que `tkinter` esté disponible (incluido en Python estándar).

## Autor

- Nombre: Satomi Yashima Rodríguez  
- Materia: Análisis de algoritmos
- Fecha: [18/08/2025]

