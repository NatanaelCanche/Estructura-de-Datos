class UnionFind:

    def __init__(self, nodos):
        self.padre = {nodo: nodo for nodo in nodos}
        self.rango = {nodo: 0 for nodo in nodos}

    def encontrar(self, nodo):
        if self.padre[nodo] != nodo:
            self.padre[nodo] = self.encontrar(self.padre[nodo])
        return self.padre[nodo]

    def unir(self, nodo1, nodo2):
        raiz1 = self.encontrar(nodo1)
        raiz2 = self.encontrar(nodo2)

        if raiz1 == raiz2:
            return False  # Mismo componente -> ciclo

        # Union por rango
        if self.rango[raiz1] < self.rango[raiz2]:
            self.padre[raiz1] = raiz2
        elif self.rango[raiz1] > self.rango[raiz2]:
            self.padre[raiz2] = raiz1
        else:
            self.padre[raiz2] = raiz1
            self.rango[raiz1] += 1

        return True


def kruskal(nodos, aristas):
    """
    Algoritmo de Kruskal para encontrar el Arbol de Expansion Minima (MST).
    Selecciona las aristas de menor peso sin formar ciclos hasta conectar
    todos los nodos del grafo.

    Args:
        nodos: lista de nodos del grafo
        aristas: lista de tuplas (peso, nodo1, nodo2)

    Returns:
        mst: lista de aristas del arbol de expansion minima
        costo_total: suma total de pesos del MST
    """
    # Ordenar aristas por peso (ascendente)
    aristas_ordenadas = sorted(aristas, key=lambda x: x[0])

    uf = UnionFind(nodos)
    mst = []
    costo_total = 0

    print(f"\nProceso de seleccion de aristas:")
    print(f"  {'Arista':<15} {'Peso':<8} {'Accion'}")
    print("  " + "-" * 40)

    for peso, u, v in aristas_ordenadas:
        if uf.unir(u, v):
            mst.append((peso, u, v))
            costo_total += peso
            print(f"  {u} - {v:<10}  {peso:<8} AGREGADA al MST")
        else:
            print(f"  {u} - {v:<10}  {peso:<8} RECHAZADA (forma ciclo)")

        if len(mst) == len(nodos) - 1:
            break  # MST completo

    return mst, costo_total


# ─── Ejemplo de uso ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    nodos = ['A', 'B', 'C', 'D', 'E', 'F']

    # Lista de aristas: (peso, nodo1, nodo2)
    aristas = [
        (4,  'A', 'B'),
        (2,  'A', 'C'),
        (6,  'A', 'D'),
        (5,  'B', 'C'),
        (3,  'B', 'E'),
        (1,  'C', 'D'),
        (7,  'C', 'E'),
        (8,  'D', 'F'),
        (4,  'E', 'F'),
    ]

    print("=" * 50)
    print("       ALGORITMO DE KRUSKAL")
    print("=" * 50)
    print(f"\nNodos del grafo: {', '.join(nodos)}")
    print(f"Total de aristas: {len(aristas)}")

    mst, costo = kruskal(nodos, aristas)

    print("\n" + "=" * 50)
    print("Arbol de Expansion Minima (MST):")
    print("-" * 50)
    for peso, u, v in mst:
        print(f"  {u} ---- {v}   (peso: {peso})")
    print("-" * 50)
    print(f"  Costo total del MST: {costo}")
    print(f"  Aristas en el MST:   {len(mst)} de {len(nodos)-1} necesarias")
