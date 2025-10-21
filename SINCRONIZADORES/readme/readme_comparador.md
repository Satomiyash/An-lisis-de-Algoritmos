# Comparativa de Algoritmos SHA256

Este script mide y compara el tiempo que tardan dos métodos de cálculo de hash SHA256:

1. **Por bloques** (lectura de 1 KB por bloque).
2. **Todo de una vez** (lectura completa del archivo).

Luego grafica los resultados.

---

## Requisitos

- Python 3.8+
- matplotlib

Instalar matplotlib:

```bash
pip install matplotlib
```

---

## Cómo ejecutar

1. Guarda el script en un archivo, por ejemplo `sha256_benchmark.py`.
2. Ejecuta:

```bash
python sha256_benchmark.py
```

- El script generará archivos de prueba con tamaños de 1 KB a 1 GB.
- Medirá el tiempo de cada algoritmo sobre cada archivo.
- Mostrará un gráfico comparativo.
- Al finalizar, los archivos de prueba se eliminarán automáticamente.

---

## Notas

- Puedes ajustar el tamaño del bloque modificando la variable `BLOCK_SIZE`.
- Cambia `file_sizes` si deseas probar otros tamaños de archivo.

