def torre_hanoi(n, origen, destino, auxiliar):
  
    if n == 1:
        print(f"Mover disco 1 de {origen} a {destino}")
        return
    
  
    torre_hanoi(n-1, origen, auxiliar, destino)
    

    print(f"Mover disco {n} de {origen} a {destino}")
    

    torre_hanoi(n-1, auxiliar, destino, origen)


def calcular_movimientos_totales(n):
    """Calcula matemáticamente el total de movimientos requeridos."""
    return (2 ** n) - 1


if __name__ == "__main__":
    discos_prueba = 3
    print(f"--- Resolviendo para {discos_prueba} discos ---")
    torre_hanoi(discos_prueba, 'Torre A', 'Torre C', 'Torre B')
    print(f"Total de movimientos: {calcular_movimientos_totales(discos_prueba)}")
    print("-" * 40)
    
    