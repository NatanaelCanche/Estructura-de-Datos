# mylinkedlist.py

class Nodo:
    """Clase que define la unidad básica de la lista: el Nodo."""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class MyLinkedList:
    """Biblioteca personalizada de Lista Enlazada Simple."""
    
    def __init__(self):
        self.cabeza = None
        self.__tamano = 0  

    def esta_vacia(self):
        """Verifica si la lista no tiene nodos."""
        return self.cabeza is None

    def obtener_tamano(self):
        """Retorna la cantidad de elementos actuales."""
        return self.__tamano

    def insertar_al_inicio(self, dato):
        """Agrega un elemento al principio de la lista. Complejidad: O(1)"""
        nuevo = Nodo(dato)
        nuevo.siguiente = self.cabeza
        self.cabeza = nuevo
        self.__tamano += 1

    def insertar_al_final(self, dato):
        """Agrega un elemento al final de la lista. Complejidad: O(n)"""
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self.__tamano += 1

    def eliminar(self, dato):
        """Busca y elimina la primera aparición de un dato."""
        actual = self.cabeza
        anterior = None
        
        while actual and actual.dato != dato:
            anterior = actual
            actual = actual.siguiente
            
        if actual is None:
            return False  
            
        if anterior is None:
            self.cabeza = actual.siguiente 
        else:
            anterior.siguiente = actual.siguiente 
            
        self.__tamano -= 1
        return True

    def limpiar_lista(self):
        """Vacía la lista completa reseteando la cabeza. Complejidad: O(1)"""
        self.cabeza = None
        self.__tamano = 0

    def __str__(self):
        """Representación visual para usar con print()."""
        nodos = []
        actual = self.cabeza
        while actual:
            nodos.append(f"[{actual.dato}]")
            actual = actual.siguiente
        return " -> ".join(nodos) + " -> None"

    def __iter__(self):
        """Permite usar la lista en ciclos 'for'."""
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente