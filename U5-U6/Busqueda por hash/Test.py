from hash_storage import TablaHashLibreria

# 1. Instanciamos nuestra librería con capacidad para 7 slots
diccionario_hash = TablaHashLibreria(capacidad_inicial=7)

print("--- 1. Insertando Elementos ---")
diccionario_hash.insertar("L01", "Sistema de Control Escolar")
diccionario_hash.insertar("L02", "Módulo de Autenticación")
diccionario_hash.insertar("L03", "Base de Datos NoSQL")
# Forzamos cadenas que compartan tipos de datos para validar estabilidad
diccionario_hash.insertar(2026, "Proyecto Desarrollo Web")

print(f"Elementos totales guardados: {diccionario_hash.tamano}")
print(f"Factor de carga actual: {diccionario_hash.obtener_factor_carga():.2f}\n")

print("--- 2. Ejecutando Algoritmo de Búsqueda ---")
# Buscamos una llave existente
busqueda_1 = "L02"
resultado_1 = diccionario_hash.buscar(busqueda_1)
print(f"Buscando '{busqueda_1}': {resultado_1}")

# Buscamos una llave numérica
busqueda_2 = 2026
resultado_2 = diccionario_hash.buscar(busqueda_2)
print(f"Buscando '{busqueda_2}': {resultado_2}")

# Buscamos una llave inexistente
busqueda_3 = "L99"
resultado_3 = diccionario_hash.buscar(busqueda_3)
print(f"Buscando '{busqueda_3}': {resultado_3}\n")

print("--- 3. Eliminación y Verificación ---")
# Eliminamos un elemento y comprobamos que ya no sea accesible
if diccionario_hash.eliminar("L01"):
    print("Elemento 'L01' eliminado con éxito.")

# Intentamos volver a buscar el elemento eliminado
resultado_post = diccionario_hash.buscar("L01")
print(f"Buscando 'L01' post-eliminación: {resultado_post}")
print(f"Elementos totales restantes: {diccionario_hash.tamano}")