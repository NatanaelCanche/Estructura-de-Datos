class Cola:
    def __init__(self):
        self.items = []

    def encolar(self, elemento):
        self.items.append(elemento)

    def desencolar(self):
        if not self.esta_vacia():
            return self.items.pop(0)
        return 0 

    def esta_vacia(self):
        return len(self.items) == 0

    def mostrar(self):
        return self.items


def sumar_colas_con_proceso(cola_a, cola_b):
    cola_resultado = Cola()
    paso = 1
    
    print("========================================")
    print("   INICIANDO SUMA DE COLAS PASO A PASO")
    print("========================================")
    
    while not cola_a.esta_vacia() or not cola_b.esta_vacia():
        valor_a = cola_a.desencolar()
        valor_b = cola_b.desencolar()
        
        suma = valor_a + valor_b
        
        print(f"Paso {paso}:")
        print(f"  -> Extrayendo {valor_a} (Cola A) y {valor_b} (Cola B)")
        print(f"  -> Sumando: {valor_a} + {valor_b} = {suma}")
        print(f"  -> Insertando {suma} en la Cola Resultado\n")
        
        cola_resultado.encolar(suma)
        paso += 1
        
    print("========================================")
    print("   PROCESO FINALIZADO CON ÉXITO")
    print("========================================\n")
    
    return cola_resultado

if __name__ == "__main__":
    cola1 = Cola()
    cola2 = Cola()

    for num in [3, 4, 2, 8, 12]:
        cola1.encolar(num)

    for num in [6, 2, 9, 11, 3]:
        cola2.encolar(num)

    print(f"Estado inicial Cola A: {cola1.mostrar()}")
    print(f"Estado inicial Cola B: {cola2.mostrar()}\n")

   
    cola_res = sumar_colas_con_proceso(cola1, cola2)

    print(f"Estado final Cola Resultado: {cola_res.mostrar()}")