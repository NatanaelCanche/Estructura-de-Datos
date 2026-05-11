"""
Librería de algoritmos de ordenamiento en Python.

Algoritmos incluidos:
    - Burbuja      (Bubble Sort)
    - Inserción    (Insertion Sort)
    - Selección    (Selection Sort)
    - Shell Sort
    - Quick Sort
    - Heap Sort
    - Radix Sort

Cada función recibe una lista y devuelve una NUEVA lista ordenada
(la lista original no se modifica), salvo que se indique lo contrario.

Uso rápido
----------
    from sorting_lib import bubble_sort, quick_sort

    datos = [64, 25, 12, 22, 11]
    print(quick_sort(datos))   # [11, 12, 22, 25, 64]
"""

from __future__ import annotations
from typing import List


# ─────────────────────────────────────────────
# 1. Burbuja (Bubble Sort)  O(n²)
# ─────────────────────────────────────────────

def bubble_sort(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante el algoritmo de Burbuja.

    Complejidad temporal: O(n²) promedio y peor caso, O(n) mejor caso.
    Complejidad espacial: O(1) auxiliar.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> bubble_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    lista = arr[:]                      # copia para no mutar el original
    n = len(lista)
    for i in range(n - 1):
        intercambiado = False
        for j in range(n - 1 - i):     # los últimos i elementos ya están en su lugar
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
                intercambiado = True
        if not intercambiado:           # optimización: salir si ya está ordenado
            break
    return lista


# ─────────────────────────────────────────────
# 2. Inserción (Insertion Sort)  O(n²)
# ─────────────────────────────────────────────

def insertion_sort(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante el algoritmo de Inserción.

    Construye la porción ordenada elemento a elemento, insertando
    cada nuevo elemento en la posición correcta.

    Complejidad temporal: O(n²) promedio y peor caso, O(n) mejor caso.
    Complejidad espacial: O(1) auxiliar.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> insertion_sort([12, 11, 13, 5, 6])
        [5, 6, 11, 12, 13]
    """
    lista = arr[:]
    for i in range(1, len(lista)):
        clave = lista[i]
        j = i - 1
        while j >= 0 and lista[j] > clave:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = clave
    return lista


# ─────────────────────────────────────────────
# 3. Selección (Selection Sort)  O(n²)
# ─────────────────────────────────────────────

def selection_sort(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante el algoritmo de Selección.

    En cada pasada busca el mínimo del subarreglo no ordenado y lo
    coloca al inicio de dicho subarreglo.

    Complejidad temporal: O(n²) en todos los casos.
    Complejidad espacial: O(1) auxiliar.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> selection_sort([64, 25, 12, 22, 11])
        [11, 12, 22, 25, 64]
    """
    lista = arr[:]
    n = len(lista)
    for i in range(n - 1):
        idx_min = i
        for j in range(i + 1, n):
            if lista[j] < lista[idx_min]:
                idx_min = j
        lista[i], lista[idx_min] = lista[idx_min], lista[i]
    return lista


# ─────────────────────────────────────────────
# 4. Shell Sort  O(n log² n) promedio
# ─────────────────────────────────────────────

def shell_sort(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante Shell Sort.

    Generalización de Inserción que permite intercambiar elementos
    lejanos reduciendo progresivamente el intervalo (gap) hasta 1.
    Usa la secuencia de Knuth: h = 3h + 1.

    Complejidad temporal: O(n log² n) con la secuencia de Knuth.
    Complejidad espacial: O(1) auxiliar.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> shell_sort([12, 34, 54, 2, 3])
        [2, 3, 12, 34, 54]
    """
    lista = arr[:]
    n = len(lista)

    # calcular el gap inicial según la secuencia de Knuth
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1

    while gap >= 1:
        for i in range(gap, n):
            temp = lista[i]
            j = i
            while j >= gap and lista[j - gap] > temp:
                lista[j] = lista[j - gap]
                j -= gap
            lista[j] = temp
        gap //= 3
    return lista


# ─────────────────────────────────────────────
# 5. Quick Sort  O(n log n) promedio
# ─────────────────────────────────────────────

def quick_sort(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante Quick Sort (versión funcional).

    Elige el elemento central como pivote y divide la lista en tres
    particiones: menores, iguales y mayores al pivote.

    Complejidad temporal: O(n log n) promedio, O(n²) peor caso.
    Complejidad espacial: O(log n) por la pila de recursión.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> quick_sort([10, 7, 8, 9, 1, 5])
        [1, 5, 7, 8, 9, 10]
    """
    if len(arr) <= 1:
        return arr[:]

    pivote = arr[len(arr) // 2]
    menores  = [x for x in arr if x <  pivote]
    iguales  = [x for x in arr if x == pivote]
    mayores  = [x for x in arr if x >  pivote]

    return quick_sort(menores) + iguales + quick_sort(mayores)


def _quick_sort_inplace(arr: List[int | float], bajo: int, alto: int) -> None:
    """Versión in-place de Quick Sort (uso interno)."""
    if bajo < alto:
        idx_pivote = _particionar(arr, bajo, alto)
        _quick_sort_inplace(arr, bajo, idx_pivote - 1)
        _quick_sort_inplace(arr, idx_pivote + 1, alto)


def _particionar(arr: List[int | float], bajo: int, alto: int) -> int:
    """Particiona arr alrededor del último elemento (pivote)."""
    pivote = arr[alto]
    i = bajo - 1
    for j in range(bajo, alto):
        if arr[j] <= pivote:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[alto] = arr[alto], arr[i + 1]
    return i + 1


def quick_sort_inplace(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante Quick Sort in-place.

    Variante que trabaja sobre una copia y usa particionamiento de
    Lomuto con el último elemento como pivote.

    Complejidad temporal: O(n log n) promedio, O(n²) peor caso.
    Complejidad espacial: O(log n) por la pila de recursión.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista ordenada de menor a mayor.
    """
    lista = arr[:]
    _quick_sort_inplace(lista, 0, len(lista) - 1)
    return lista


# ─────────────────────────────────────────────
# 6. Heap Sort  O(n log n)
# ─────────────────────────────────────────────

def _heapificar(arr: List[int | float], n: int, raiz: int) -> None:
    """Mantiene la propiedad de max-heap desde el nodo 'raiz'."""
    mayor = raiz
    izq   = 2 * raiz + 1
    der   = 2 * raiz + 2

    if izq < n and arr[izq] > arr[mayor]:
        mayor = izq
    if der < n and arr[der] > arr[mayor]:
        mayor = der

    if mayor != raiz:
        arr[raiz], arr[mayor] = arr[mayor], arr[raiz]
        _heapificar(arr, n, mayor)


def heap_sort(arr: List[int | float]) -> List[int | float]:
    """
    Ordena una lista mediante Heap Sort.

    Construye un max-heap y extrae repetidamente el elemento mayor,
    colocándolo al final del arreglo.

    Complejidad temporal: O(n log n) en todos los casos.
    Complejidad espacial: O(1) auxiliar.

    Args:
        arr: Lista de números a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> heap_sort([12, 11, 13, 5, 6, 7])
        [5, 6, 7, 11, 12, 13]
    """
    lista = arr[:]
    n = len(lista)

    # construir max-heap
    for i in range(n // 2 - 1, -1, -1):
        _heapificar(lista, n, i)

    # extraer elementos del heap uno a uno
    for i in range(n - 1, 0, -1):
        lista[0], lista[i] = lista[i], lista[0]   # mover la raíz al final
        _heapificar(lista, i, 0)

    return lista


# ─────────────────────────────────────────────
# 7. Radix Sort  O(nk)
# ─────────────────────────────────────────────

def _counting_sort_por_digito(arr: List[int], exp: int) -> List[int]:
    """Counting sort estable usado como subrutina de Radix Sort."""
    n = len(arr)
    salida  = [0] * n
    conteo  = [0] * 10

    for num in arr:
        indice = (num // exp) % 10
        conteo[indice] += 1

    for i in range(1, 10):
        conteo[i] += conteo[i - 1]

    for i in range(n - 1, -1, -1):
        indice = (arr[i] // exp) % 10
        salida[conteo[indice] - 1] = arr[i]
        conteo[indice] -= 1

    return salida


def radix_sort(arr: List[int]) -> List[int]:
    """
    Ordena una lista de enteros no negativos mediante Radix Sort (LSD).

    Aplica Counting Sort por cada dígito, desde el menos significativo
    hasta el más significativo.

    Complejidad temporal: O(nk), donde k = número de dígitos del máximo.
    Complejidad espacial: O(n + k).

    Nota: Solo funciona con enteros ≥ 0.
          Para negativos, separa, ordena los valores absolutos y combina.

    Args:
        arr: Lista de enteros no negativos a ordenar.

    Returns:
        Nueva lista con los elementos ordenados de menor a mayor.

    Ejemplo:
        >>> radix_sort([170, 45, 75, 90, 802, 24, 2, 66])
        [2, 24, 45, 66, 75, 90, 170, 802]
    """
    if not arr:
        return []

    lista = arr[:]
    maximo = max(lista)

    exp = 1
    while maximo // exp > 0:
        lista = _counting_sort_por_digito(lista, exp)
        exp *= 10

    return lista


# ─────────────────────────────────────────────
# Utilidades de comparación y benchmark
# ─────────────────────────────────────────────

import time
import random

ALGORITMOS = {
    "Burbuja":    bubble_sort,
    "Inserción":  insertion_sort,
    "Selección":  selection_sort,
    "Shell Sort": shell_sort,
    "Quick Sort": quick_sort,
    "Heap Sort":  heap_sort,
    "Radix Sort": radix_sort,
}


def comparar_algoritmos(
    datos: List[int | float] | None = None,
    n: int = 1000,
    semilla: int = 42,
) -> dict[str, float]:
    """
    Ejecuta todos los algoritmos sobre los mismos datos y devuelve
    el tiempo de ejecución de cada uno en segundos.

    Args:
        datos:  Lista a ordenar. Si es None se genera una aleatoria.
        n:      Tamaño de la lista aleatoria (ignorado si datos != None).
        semilla: Semilla para reproducibilidad.

    Returns:
        Diccionario {nombre_algoritmo: tiempo_en_segundos}.

    Ejemplo:
        >>> tiempos = comparar_algoritmos(n=500)
        >>> for nombre, t in tiempos.items():
        ...     print(f"{nombre:12s}: {t:.6f} s")
    """
    if datos is None:
        random.seed(semilla)
        datos = [random.randint(0, 10_000) for _ in range(n)]

    resultados: dict[str, float] = {}
    for nombre, funcion in ALGORITMOS.items():
        inicio = time.perf_counter()
        funcion(datos)
        fin = time.perf_counter()
        resultados[nombre] = round(fin - inicio, 6)

    return resultados


# ─────────────────────────────────────────────
# Demo rápida al ejecutar como script
# ─────────────────────────────────────────────

if __name__ == "__main__":
    datos_prueba = [64, 34, 25, 12, 22, 11, 90, 170, 45, 75, 802, 2, 66]

    print("=" * 55)
    print("  Librería de Algoritmos de Ordenamiento  ")
    print("=" * 55)
    print(f"\nDatos originales: {datos_prueba}\n")

    for nombre, funcion in ALGORITMOS.items():
        resultado = funcion(datos_prueba)
        print(f"  {nombre:<12}: {resultado}")

    print("\n" + "─" * 55)
    print("  Benchmark con 2 000 números aleatorios")
    print("─" * 55)

    tiempos = comparar_algoritmos(n=2000)
    ordenados = sorted(tiempos.items(), key=lambda x: x[1])
    for nombre, t in ordenados:
        barra = "█" * int(t * 5000)
        print(f"  {nombre:<12}: {t:.6f} s  {barra}")