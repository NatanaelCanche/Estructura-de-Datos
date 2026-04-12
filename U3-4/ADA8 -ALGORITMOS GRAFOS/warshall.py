def warshall(matriz_adyacencia):
    n = len(matriz_adyacencia)

    # Copiar la matriz de adyacencia como matriz de alcance
    alcance = [fila[:] for fila in matriz_adyacencia]

    # Algoritmo de Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                # Si hay camino de i a k Y de k a j, hay camino de i a j
                alcance[i][j] = alcance[i][j] or (alcance[i][k] and alcance[k][j])

    return alcance


def imprimir_matriz(matriz, nodos, titulo):
    """Imprime la matriz de forma legible."""
    n = len(nodos)
    print(f"\n{titulo}")
    print("     " + "  ".join(f" {v}" for v in nodos))
    print("     " + "---" * n)
    for i in range(n):
        fila = "  ".join(str(int(matriz[i][j])) for j in range(n))
        print(f"  {nodos[i]} | {fila}")


def analizar_conectividad(alcance, nodos):
    """Analiza y reporta la conectividad del grafo."""
    n = len(nodos)
    print("\nAnalisis de conectividad:")
    print("-" * 40)
    for i in range(n):
        alcanzables = [nodos[j] for j in range(n) if alcance[i][j] and i != j]
        if alcanzables:
            print(f"  Desde {nodos[i]} se puede llegar a: {', '.join(alcanzables)}")
        else:
            print(f"  Desde {nodos[i]}: no alcanza ningun otro nodo")

    # Verificar si el grafo es fuertemente conexo
    fuerte = all(alcance[i][j] for i in range(n) for j in range(n) if i != j)
    print(f"\n  Grafo fuertemente conexo: {'Si' if fuerte else 'No'}")


# ─── Ejemplo de uso ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    nodos = ['A', 'B', 'C', 'D']

    # Matriz de adyacencia del grafo dirigido
    # 1 = existe arista directa, 0 = no existe
    matriz = [
        #A  B  C  D
        [0, 1, 0, 0],  # A
        [0, 0, 1, 0],  # B
        [0, 0, 0, 1],  # C
        [0, 0, 0, 0],  # D
    ]

    print("=" * 45)
    print("       ALGORITMO DE WARSHALL")
    print("=" * 45)

    imprimir_matriz(matriz, nodos, "Matriz de adyacencia (grafo original):")

    alcance = warshall(matriz)

    imprimir_matriz(alcance, nodos, "Matriz de clausura transitiva:")

    analizar_conectividad(alcance, nodos)
