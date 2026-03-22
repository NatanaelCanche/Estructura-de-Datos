from mylinkedlist import MyLinkedList

def ejecutar_prueba():
    
    lista_itm = MyLinkedList()

    print("--- 1. Insertando datos ---")
    lista_itm.insertar_al_final("Cálculo")
    lista_itm.insertar_al_final("Contabilidad")
    lista_itm.insertar_al_inicio("Estructura de Datos")
    print(f"Lista actual: {lista_itm}")
    print(f"Total de materias: {lista_itm.obtener_tamano()}")

    print("\n--- 2. Probando el iterador (ciclo for) ---")
    for materia in lista_itm:
        print(f"Estudiando: {materia}")

    print("\n--- 3. Eliminando un elemento ---")
    lista_itm.eliminar("Contabilidad")
    print(f"Lista después de borrar: {lista_itm}")

    print("\n--- 4. Limpiando la lista ---")
    lista_itm.limpiar_lista()
    print(f"¿La lista está vacía?: {lista_itm.esta_vacia()}")
    print(f"Estado final: {lista_itm}")

if __name__ == "__main__":
    ejecutar_prueba()