# -*- coding: utf-8 -*-
"""
Librería: hash_storage
Descripción: Implementación de una estructura de Tabla Hash con manejo de 
             colisiones mediante encadenamiento separado.
"""

class NodoHash:
    """Clase interna para representar cada par Llave-Valor en la lista enlazada."""
    def __init__(self, llave, valor):
        self.llave = llave
        self.valor = valor
        self.siguiente = None  # Puntero al siguiente nodo en caso de colisión


class TablaHashLibreria:
    def __init__(self, capacidad_inicial=11):
        """
        Inicializa la tabla. Se recomienda usar un número primo para la 
        capacidad inicial para mejorar la distribución de los índices.
        """
        self.capacidad = capacidad_inicial
        self.tamano = 0
        # Inicializamos el arreglo principal con posiciones vacías (None)
        self.buckets = [None] * self.capacidad

    def _funcion_hash(self, llave):
        """
        Función Hash privada. Convierte cualquier llave (int, str, float)
        en un índice válido dentro del rango del arreglo [0, capacidad - 1].
        """
        # abs(hash(llave)) nos da un entero único y positivo respaldado por Python
        return abs(hash(llave)) % self.capacidad

    def insertar(self, llave, valor):
        """Inserta un par llave-valor. Si la llave ya existe, actualiza su valor."""
        indice = self._funcion_hash(llave)
        
        # Caso 1: La casilla está vacía (no hay colisiones aún)
        if self.buckets[indice] is None:
            self.buckets[indice] = NodoHash(llave, valor)
            self.tamano += 1
            return True
        
        # Caso 2: Hay una colisión. Recorremos la lista enlazada en esa casilla
        actual = self.buckets[indice]
        while actual:
            if actual.llave == llave:
                actual.valor = valor  # La llave ya existía, actualizamos el valor
                return True
            if actual.siguiente is None:
                break
            actual = actual.siguiente
            
        # Llegamos al final de la lista enlazada sin encontrar la llave, agregamos el nuevo nodo
        actual.siguiente = NodoHash(llave, valor)
        self.tamano += 1
        return True

    def buscar(self, llave):
        """
        ALGORITMO DE BÚSQUEDA HASH
        Calcula el índice de manera directa en O(1) y busca el valor.
        Retorna el valor si lo encuentra, o None si no existe.
        """
        indice = self._funcion_hash(llave)
        actual = self.buckets[indice]
        
        # Buscamos de forma secuencial únicamente dentro de la sublista de colisión
        while actual:
            if actual.llave == llave:
                return actual.valor  # ¡Elemento encontrado!
            actual = actual.siguiente
            
        return None  # No se encontró la llave en la tabla

    def eliminar(self, llave):
        """Elimina un elemento de la tabla por su llave. Retorna True si se eliminó."""
        indice = self._funcion_hash(llave)
        actual = self.buckets[indice]
        anterior = None
        
        while actual:
            if actual.llave == llave:
                if anterior is None:
                    # El elemento a eliminar era el primero de la lista
                    self.buckets[indice] = actual.siguiente
                else:
                    # Saltamos el nodo actual para desvincularlo de la lista
                    anterior.siguiente = actual.siguiente
                self.tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
            
        return False  # No se encontró el elemento a eliminar

    def obtener_factor_carga(self):
        """Retorna el factor de carga actual (Número de elementos / Capacidad)."""
        return self.tamano / self.capacidad