INF = float('inf')

def floyd_warshall(matriz_adyacencia, nodos):
    n = len(nodos)

    # Copiar la matriz de adyacencia
    dist = [fila[:] for fila in matriz_adyacencia]

    # Matriz para reconstruccion de caminos
    siguiente = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != INF:
                siguiente[i][j] = j

    # Relajacion con cada nodo k como intermediario
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    siguiente[i][j] = siguiente[i][k]

    return dist, siguiente


def reconstruir_camino(siguiente, i, j):
    if siguiente[i][j] is None:
        return []
    camino = [i]
    while i != j:
        i = siguiente[i][j]
        camino.append(i)
    return camino


def imprimir_matriz(matriz, nodos, titulo):
    n = len(nodos)
    print(f"\n{titulo}")
    print("      " + "  ".join(f"{nodos[j]:>5}" for j in range(n)))
    print("      " + "-------" * n)
    for i in range(n):
        fila = []
        for j in range(n):
            val = matriz[i][j]
            fila.append("  INF" if val == INF else f"{val:>5}")
        print(f"  {nodos[i]} | " + "  ".join(fila))


# ─── Ejemplo de uso ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    nodos = ['A', 'B', 'C', 'D']
    n = len(nodos)
    idx = {v: i for i, v in enumerate(nodos)}

    matriz = [
        [0,   3,  INF,  7],
        [8,   0,   2,  INF],
        [5,  INF,  0,   1],
        [2,  INF, INF,  0]
    ]

    print("=" * 50)
    print("       ALGORITMO DE FLOYD-WARSHALL")
    print("=" * 50)

    imprimir_matriz(matriz, nodos, "Matriz de adyacencia inicial:")

    dist, siguiente = floyd_warshall(matriz, nodos)

    imprimir_matriz(dist, nodos, "Matriz de distancias minimas:")

    print("\nCaminos mas cortos entre todos los pares:")
    print("-" * 50)
    for i in range(n):
        for j in range(n):
            if i != j:
                camino_idx = reconstruir_camino(siguiente, i, j)
                if camino_idx:
                    ruta = " -> ".join(nodos[x] for x in camino_idx)
                else:
                    ruta = "No alcanzable"
                print(f"  {nodos[i]} -> {nodos[j]}: distancia={dist[i][j]}  ruta: {ruta}")
