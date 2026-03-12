
class Pedido:
    def __init__(self, cantidad, cliente):
        self.cantidad = cantidad
        self.cliente = cliente
        
    def imprimir_info(self):
        print(f"     Cliente: {self.cliente}")
        print(f"     Cantidad: {self.cantidad}")
        print("     ------------")

class Nodo:
    def __init__(self, info):
        self.info = info
        self.siguiente = None

class Cola:
    def __init__(self):
        self.cabeza = None  
        self.final = None   
        self._tamano = 0    

    def tamano(self):
        return self._tamano

    def esta_vacia(self):
        return self._tamano == 0

    def primero(self):
        if self.esta_vacia():
            return None
        return self.cabeza.info

    def encolar(self, info):
        nuevo_nodo = Nodo(info)
        if self.esta_vacia():
            self.cabeza = nuevo_nodo
            self.final = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        self._tamano += 1

    def desencolar(self):
        if self.esta_vacia():
            return None
        info_extraida = self.cabeza.info
        self.cabeza = self.cabeza.siguiente 
        self._tamano -= 1
        if self.esta_vacia():
            self.final = None
        return info_extraida

    def imprimir_estado(self):
        print("\n********* ESTADO DE LA COLA *********")
        if self.esta_vacia():
            print("   [La cola está vacía]")
        else:
            print(f"   Tamaño actual: {self._tamano}")
            actual = self.cabeza
            indice = 1
            while actual is not None:
                print(f"   ** Elemento {indice}")
                if hasattr(actual.info, 'imprimir_info'):
                    actual.info.imprimir_info()
                else:
                    print(actual.info)
                actual = actual.siguiente
                indice += 1
        print("*************************************")

    def obtener_enesimo(self, posicion):
        if posicion < 1 or posicion > self._tamano:
            return None
        actual = self.cabeza
        for _ in range(1, posicion):
            actual = actual.siguiente
        return actual.info


def iniciar_sistema():
    mi_cola = Cola()
    
    while True:
        print("\n=== MENÚ DE GESTIÓN DE PEDIDOS ===")
        print("1. Recibir nuevo pedido (Encolar)")
        print("2. Atender siguiente pedido (Desencolar/Quitar)")
        print("3. Ver estado de la cola")
        print("4. Ver quién es el primero en espera")
        print("5. Buscar pedido por posición")
        print("6. Salir del sistema")
        
        opcion = input("\nElige una opción (1-6): ")
        
        if opcion == '1':
            cliente = input("Ingresa el nombre del cliente: ")
            try:
                cantidad = int(input(f"Ingresa la cantidad de producto para {cliente}: "))
                nuevo_pedido = Pedido(cantidad, cliente)
                mi_cola.encolar(nuevo_pedido)
                print(f" ¡Pedido de {cliente} agregado con éxito a la cola!")
            except ValueError:
                print(" Error: La cantidad debe ser un número entero.")
                
        elif opcion == '2':
            atendido = mi_cola.desencolar()
            if atendido:
                print(f" Se ha atendido y despachado el pedido de: {atendido.cliente}")
            else:
                print(" No hay pedidos en espera para atender.")
                
        elif opcion == '3':
            mi_cola.imprimir_estado()
            
        elif opcion == '4':
            primero = mi_cola.primero()
            if primero:
                print(f"ℹ El siguiente en ser atendido es: {primero.cliente} ({primero.cantidad} unidades).")
            else:
                print(" La cola está vacía.")
                
        elif opcion == '5':
            try:
                pos = int(input("Ingresa el número de posición en la fila que deseas revisar: "))
                encontrado = mi_cola.obtener_enesimo(pos)
                if encontrado:
                    print(f" En la posición {pos} está: {encontrado.cliente} ({encontrado.cantidad} unidades).")
                else:
                    print(" Posición no válida o no hay nadie en ese lugar de la fila.")
            except ValueError:
                print(" Error: Debes ingresar un número entero.")
                
        elif opcion == '6':
            print(" ¡Cerrando el sistema! Hasta luego.")
            break 
            
        else:
            print(" Opción no reconocida. Por favor, elige un número del 1 al 6.")

# Arrancar el programa
if __name__ == "__main__":
    iniciar_sistema()