from collections import deque

class CacheWebPro:
    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.cache = deque()
        self.contador_visitas = {}

    def registrar_clic(self, url):
        # Actualizar contador global de clics
        self.contador_visitas[url] = self.contador_visitas.get(url, 0) + 1
        
        print(f"\n>>> Has hecho clic en: {url} (Visitas totales: {self.contador_visitas[url]})")
        
        if url in self.cache:
            print(f" Logan: ¡Hit! '{url}' ya estaba en memoria. Movido al frente.")
            self.cache.remove(url)
        else:
            print(f" Logan: ¡Miss! '{url}' no estaba. Cargando en memoria...")
            if len(self.cache) >= self.capacidad:
                eliminada = self.cache.pop()
                print(f" [!] Memoria llena. Expulsando la menos reciente: {eliminada}")
        
        self.cache.appendleft(url)
        self.mostrar_estado()

    def mostrar_estado(self):
        print("-" * 40)
        print(f"ESTADO DE LA CACHÉ (Bicola): {list(self.cache)}")
        # Ordenar para ver quién es el más popular
        ranking = sorted(self.contador_visitas.items(), key=lambda x: x[1], reverse=True)
        print(f"RANKING DE POPULARIDAD: {ranking[:3]} (Top 3)")
        print("-" * 40)

# --- Configuración Inicial ---
sitios_disponibles = [
    "google.com", "youtube.com", "facebook.com", 
    "github.com", "netflix.com", "reddit.com"
]

capacidad_max = 3
mi_cache = CacheWebPro(capacidad_max)

# --- Interfaz de Usuario ---
print(f"--- SIMULADOR DE NAVEGADOR (Caché: {capacidad_max} espacios) ---")

while True:
    print("\nSITIOS WEB DISPONIBLES (Presiona el número para visitar):")
    for i, sitio in enumerate(sitios_disponibles, 1):
        print(f"{i}. {sitio}")
    
    opcion = input("\nSelecciona un sitio (o 's' para salir): ").lower().strip()

    if opcion == 's':
        print("Saliendo del navegador... ¡Adiós!")
        break
    
    if opcion.isdigit():
        indice = int(opcion) - 1
        if 0 <= indice < len(sitios_disponibles):
            url_seleccionada = sitios_disponibles[indice]
            mi_cache.registrar_clic(url_seleccionada)
        else:
            print("Número fuera de rango. Intenta de nuevo.")
    else:
        print("Entrada no válida. Por favor, usa los números del menú.")