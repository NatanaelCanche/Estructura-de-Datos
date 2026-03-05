def torre_hanoi(n, origen, destino, auxiliar):
    """
    Función recursiva para resolver la Torre de Hanoi.
    """
    if n == 1:
        print(f"Mover disco 1 de {origen} a {destino}")
        return
    
    # 1. Mover n-1 discos del origen al auxiliar, usando el destino como apoyo
    torre_hanoi(n-1, origen, auxiliar, destino)
    
    # 2. Mover el disco restante (el más grande) del origen al destino
    print(f"Mover disco {n} de {origen} a {destino}")
    
    # 3. Mover los n-1 discos del auxiliar al destino, usando el origen como apoyo
    torre_hanoi(n-1, auxiliar, destino, origen)


def calcular_movimientos_totales(n):
    """Calcula matemáticamente el total de movimientos requeridos."""
    return (2 ** n) - 1


if __name__ == "__main__":
    # --- PRUEBA CON 3 DISCOS (Seguro para tu PC) ---
    discos_prueba = 3
    print(f"--- Resolviendo para {discos_prueba} discos ---")
    torre_hanoi(discos_prueba, 'Torre A', 'Torre C', 'Torre B')
    print("-" * 40)
    
    # --- LA REALIDAD DE LOS 64 DISCOS ---
    discos_reales = 64
    total_movimientos = calcular_movimientos_totales(discos_reales)
    
    print(f"\nSi intentaramos resolver para {discos_reales} discos:")
    print(f"Total de movimientos requeridos: {total_movimientos:,}")
    print("Nota: Si descomentas la siguiente línea, tu script se ejecutará hasta el fin de los tiempos.")
    
    # torre_hanoi(64, 'Torre A', 'Torre C', 'Torre B')