class Nodo:
    """
    Representa un elemento dentro de la Tabla Hash.
    Se utiliza para crear listas enlazadas y resolver las colisiones.
    """
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.siguiente = None  # Apuntador al siguiente nodo en caso de colisión


class TablaHash:
    """
    Estructura principal de la Tabla Hash.
    """
    def __init__(self, capacidad=97):
        # Según el documento, N (la capacidad) debe ser idealmente un número primo.
        self.capacidad = capacidad
        # Iniciamos nuestro arreglo lleno de 'None' (vacío)
        self.tabla = [None] * self.capacidad

    def _funcion_hash_modulo(self, clave):
        """
        Aplica el método de conversión de texto a número y luego la función por módulo.
        """
        # 1. Convertimos la clave a un valor numérico sumando el código ASCII de sus caracteres[cite: 138].
        valor_numerico = 0
        if isinstance(clave, str):
            for caracter in clave:
                valor_numerico += ord(caracter)
        else:
            valor_numerico = int(clave)

        # 2. Aplicamos la función hash por módulo/división[cite: 57, 64].
        # Usamos H(K) = K mod N (sin el +1 porque los índices en Python van de 0 a N-1)
        return valor_numerico % self.capacidad

    def insertar(self, clave, valor):
        """
        Inserta un nuevo par clave-valor en la tabla.
        """
        indice = self._funcion_hash_modulo(clave)
        nuevo_nodo = Nodo(clave, valor)

        # Si la posición está vacía, insertamos directamente
        if self.tabla[indice] is None:
            self.tabla[indice] = nuevo_nodo
            return

        # Si ya hay un elemento, hay una COLISIÓN.
        # Lo resolvemos recorriendo la lista enlazada (encadenamiento).
        actual = self.tabla[indice]
        while actual:
            # Si la clave ya existe, actualizamos su valor
            if actual.clave == clave:
                actual.valor = valor
                return
            # Si llegamos al último nodo, salimos del bucle
            if actual.siguiente is None:
                break
            actual = actual.siguiente

        # Agregamos el nuevo nodo al final de la lista enlazada
        actual.siguiente = nuevo_nodo

    def buscar(self, clave):
        """
        Busca y devuelve el valor asociado a una clave. Retorna None si no existe.
        """
        indice = self._funcion_hash_modulo(clave)
        actual = self.tabla[indice]

        # Recorremos la lista en esa posición para encontrar la clave exacta
        while actual:
            if actual.clave == clave:
                return actual.valor
            actual = actual.siguiente

        return None  # No se encontró la clave

    def eliminar(self, clave):
        """
        Elimina un par clave-valor de la tabla.
        """
        indice = self._funcion_hash_modulo(clave)
        actual = self.tabla[indice]
        previo = None

        while actual:
            if actual.clave == clave:
                # Si es el primer elemento de la lista
                if previo is None:
                    self.tabla[indice] = actual.siguiente
                # Si está en medio o al final de la lista
                else:
                    previo.siguiente = actual.siguiente
                return True # Eliminado con éxito
            
            previo = actual
            actual = actual.siguiente

        return False # La clave no existía

    def mostrar_tabla(self):
        """
        Imprime el estado actual de la tabla en consola para fines de depuración.
        """
        for i in range(self.capacidad):
            elementos = []
            actual = self.tabla[i]
            while actual:
                elementos.append(f"[{actual.clave}: {actual.valor}]")
                actual = actual.siguiente
            
            if elementos:
                print(f"Índice {i}: " + " -> ".join(elementos))

# Prueba de tu código
#mi_tabla = TablaHash(capacidad=10) # Capacidad pequeña para forzar colisiones

# "abc" y "cba" sumarán los mismos ASCII, van a colisionar en el mismo índice
#mi_tabla.insertar("abc", "Primer elemento")
#mi_tabla.insertar("cba", "Segundo elemento (colisión)")
#mi_tabla.insertar("xyz", "Otro elemento")

#print("--- ESTADO DE LA TABLA ---")
#mi_tabla.mostrar_tabla()

#print("\n--- PRUEBA DE BÚSQUEDA ---")
#print("Buscando 'cba':", mi_tabla.buscar("cba"))