# Estructura-de-Datos/ordenamiento_externo/algoritmos_mezcla.py

def ordenar_intercalacion(datos):
    """
    Divide los datos en dos mitades, las ordena individualmente y genera el historial de fusión.
    Retorna: mitad_a, mitad_b, historial_pasos
    """
    mitad = len(datos) // 2
    lista_a = sorted(datos[:mitad])
    lista_b = sorted(datos[mitad:])
    pasos = []
    indice_a, indice_b = 0, 0
    
    while indice_a < len(lista_a) and indice_b < len(lista_b):
        if lista_a[indice_a] <= lista_b[indice_b]:
            pasos.append(("A", indice_a, indice_b, lista_a[indice_a]))
            indice_a += 1
        else:
            pasos.append(("B", indice_a, indice_b, lista_b[indice_b]))
            indice_b += 1
            
    while indice_a < len(lista_a):
        pasos.append(("A", indice_a, indice_b, lista_a[indice_a]))
        indice_a += 1
        
    while indice_b < len(lista_b):
        pasos.append(("B", indice_a, indice_b, lista_b[indice_b]))
        indice_b += 1
        
    return lista_a, lista_b, pasos


def generar_pasadas_mezcla_directa(datos):
    """
    Ordena mediante bloques crecientes (potencias de 2).
    Retorna: Una lista con los estados completos del arreglo en cada pasada.
    """
    estados = [datos[:]]
    arreglo = datos[:]
    n = len(arreglo)
    tamano_bloque = 1
    
    while tamano_bloque < n:
        nueva_lista = []
        for izquierda in range(0, n, tamano_bloque * 2):
            medio = min(izquierda + tamano_bloque, n)
            derecha = min(izquierda + tamano_bloque * 2, n)
            
            mitad_izq = arreglo[izquierda:medio]
            mitad_der = arreglo[medio:derecha]
            
            fusionados = []
            i, j = 0, 0
            while i < len(mitad_izq) and j < len(mitad_der):
                if mitad_izq[i] <= mitad_der[j]:
                    fusionados.append(mitad_izq[i])
                    i += 1
                else:
                    fusionados.append(mitad_der[j])
                    j += 1
                    
            fusionados.extend(mitad_izq[i:])
            fusionados.extend(mitad_der[j:])
            nueva_lista.extend(fusionados)
            
        arreglo = nueva_lista
        estados.append(arreglo[:])
        tamano_bloque *= 2
        
    return estados


def generar_pasadas_mezcla_equilibrada(datos, k_cintas=2, tamano_secuencia=2):
    """
    Distribuye los datos en k_cintas alternas y realiza mezclas sucesivas.
    Retorna: secuencias_iniciales, historial_pasadas
    """
    secuencias = [sorted(datos[i:i+tamano_secuencia]) for i in range(0, len(datos), tamano_secuencia)]
    cintas_entrada = [[] for _ in range(k_cintas)]
    
    for indice, secuencia in enumerate(secuencias):
        cintas_entrada[indice % k_cintas].append(secuencia)

    pasadas = [{"entrada": [list(c) for c in cintas_entrada], "salida": None, "etiqueta": "Distribución inicial"}]
    fuente = cintas_entrada
    
    for _ in range(10): # Límite de seguridad
        cintas_salida = [[] for _ in range(k_cintas)]
        longitud_minima = min(len(c) for c in fuente)
        if longitud_minima == 0: 
            break
            
        secuencias_fusionadas = []
        for j in range(longitud_minima):
            combinacion = []
            for cinta in fuente: 
                combinacion.extend(cinta[j])
            combinacion.sort()
            secuencias_fusionadas.append(combinacion)
            
        for indice, secuencia_fusionada in enumerate(secuencias_fusionadas):
            cintas_salida[indice % k_cintas].append(secuencia_fusionada)
            
        pasadas.append({
            "entrada": [list(c) for c in fuente], 
            "salida": [list(c) for c in cintas_salida], 
            "etiqueta": f"Pasada {len(pasadas)}"
        })
        
        fuente = cintas_salida
        if all(len(c) <= 1 for c in fuente): 
            break
            
    return secuencias, pasadas