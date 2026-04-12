import heapq

def dijkstra(grafo, inicio):
    """
    Algoritmo de Dijkstra para encontrar el camino mas corto
    desde un nodo origen hacia todos los demas nodos del grafo.

    Args:
        grafo: diccionario de adyacencia {nodo: [(vecino, peso), ...]}
        inicio: nodo de inicio

    Returns:
        distancias: diccionario con la distancia minima a cada nodo
        predecesores: diccionario para reconstruir el camino
    """
    # Inicializar distancias como infinito para todos los nodos
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    predecesores = {nodo: None for nodo in grafo}

    # Cola de prioridad: (distancia, nodo)
    cola_prioridad = [(0, inicio)]

    visitados = set()

    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        for vecino, peso in grafo[nodo_actual]:
            distancia = distancia_actual + peso

            if distancia < distancias[vecino]:
                distancias[vecino] = distancia
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (distancia, vecino))

    return distancias, predecesores


def reconstruir_camino(predecesores, inicio, fin):
    """Reconstruye el camino desde inicio hasta fin."""
    camino = []
    nodo = fin
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesores[nodo]
    camino.reverse()
    if camino[0] == inicio:
        return camino
    return []


# ─── Ejemplo de uso ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    grafo = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)]
    }

    inicio = 'A'
    distancias, predecesores = dijkstra(grafo, inicio)

    print("=" * 45)
    print("       ALGORITMO DE DIJKSTRA")
    print("=" * 45)
    print(f"Nodo de inicio: {inicio}\n")
    print(f"{'Destino':<10} {'Distancia':<12} {'Camino'}")
    print("-" * 45)

    for nodo in sorted(grafo):
        if nodo != inicio:
            camino = reconstruir_camino(predecesores, inicio, nodo)
            ruta = " -> ".join(camino) if camino else "No alcanzable"
            print(f"{nodo:<10} {distancias[nodo]:<12} {ruta}")
