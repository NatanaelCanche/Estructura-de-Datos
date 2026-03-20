from collections import deque
from urllib.parse import urlparse

class CacheFrecuencia:
    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.cache = deque()
        self.contadores = {}

    def es_url_valida(self, url):
        """Verifica si la cadena tiene un formato básico de URL."""
        try:
            resultado = urlparse(url)
            # Verifica que tenga un esquema (http/https) y un dominio (netloc)
            # O al menos un punto que indique un dominio (ej. google.com)
            return all([resultado.scheme, resultado.netloc]) or ('.' in url and len(url) > 3)
        except:
            return False

    def consultar_pagina(self, url):
        # --- VALIDACIÓN ---
        if not self.es_url_valida(url):
            print(f" [!] Error: '{url}' no parece una dirección web válida. Intenta con 'http://google.com' o 'google.com'.")
            return

        print(f"\n--- Procesando: {url} ---")
        
        # 1. Actualizar frecuencia
        if url in self.contadores:
            self.contadores[url] += 1
            print(f"-> Hit! Frecuencia de '{url}': {self.contadores[url]}")
        else:
            self.contadores[url] = 1
            print(f"-> Miss! Agregando nueva página.")

        # 2. Gestionar espacio en la Bicola
        if url in self.cache:
            self.cache.remove(url)
        elif len(self.cache) >= self.capacidad:
            # Eliminamos la que quedó al final tras el último ordenamiento (la menos frecuente)
            eliminada = self.cache.pop()
            print(f" [!] Caché llena. Eliminando la menos frecuente: {eliminada}")
            if eliminada in self.contadores:
                del self.contadores[eliminada]

        # 3. Insertar y reordenar por visitas (de mayor a menor)
        self.cache.append(url)
        lista_ordenada = sorted(list(self.cache), key=lambda x: self.contadores[x], reverse=True)
        self.cache = deque(lista_ordenada)

        self.mostrar_estado()

    def mostrar_estado(self):
        print("\nEstado actual (Ordenado por Frecuencia):")
        if not self.cache:
            print("  Caché vacía.")
        for i, url in enumerate(self.cache, 1):
            print(f"  {i}. {url} | Visitas: {self.contadores[url]}")


try:
    cap = int(input("Capacidad de la caché: "))
    mi_cache = CacheFrecuencia(cap)

    print("\nInstrucciones: Ingresa URLs. Escribe 'salir' para terminar.")
    
    while True:
        entrada = input("\nURL: ").strip().lower()
        if entrada == 'salir':
            print("Cerrando sistema de caché...")
            break
        mi_cache.consultar_pagina(entrada)
except ValueError:
    print("Error: Debes ingresar un número entero para la capacidad.")