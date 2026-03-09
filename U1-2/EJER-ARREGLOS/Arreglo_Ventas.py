# Inicialización del arreglo bidimensional (12 meses x 3 departamentos)
# Se inicializa en 0 para representar una tabla vacía
ventas = [[0 for _ in range(3)] for _ in range(12)]

# Listas de referencia para índices
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
deptos = ["Ropa", "Deportes", "Juguetería"]

def visualizar_tabla():
    """Muestra el arreglo bidimensional en formato de tabla."""
    print(f"\n{'MES':<12} | {'ROPA':<10} | {'DEPORTES':<10} | {'JUGUETERÍA':<10}")
    print("-" * 52)
    for i in range(12):
        print(f"{meses[i]:<12} | {ventas[i][0]:<10} | {ventas[i][1]:<10} | {ventas[i][2]:<10}")
    print("-" * 52)

def insertar_venta(mes, depto, monto):
    """Método para insertar o modificar un elemento en el arreglo."""
    try:
        f = meses.index(mes.capitalize())
        c = deptos.index(depto.capitalize())
        ventas[f][c] = monto
        print(f"✅ Venta insertada: {mes} - {depto}: ${monto}")
    except ValueError:
        print("❌ Error: Mes o Departamento no válido.")

def buscar_venta(mes, depto):
    """Método para buscar un elemento particular en el arreglo."""
    try:
        f = meses.index(mes.capitalize())
        c = deptos.index(depto.capitalize())
        monto = ventas[f][c]
        print(f"🔍 Resultado: La venta en {mes} ({depto}) es de ${monto}")
        return monto
    except ValueError:
        print("❌ Error: Datos de búsqueda no válidos.")

def eliminar_venta(mes, depto):
    """Método para eliminar una venta (resetear a 0) de un departamento."""
    try:
        f = meses.index(mes.capitalize())
        c = deptos.index(depto.capitalize())
        ventas[f][c] = 0
        print(f"🗑️ Registro eliminado: {mes} - {depto} ahora es $0")
    except ValueError:
        print("❌ Error: No se pudo realizar la eliminación.")

# --- MENÚ INTERACTIVO ---
while True:
    print("\n--- MENÚ DE VENTAS ---")
    print("1. Visualizar Tabla")
    print("2. Insertar/Modificar Venta")
    print("3. Buscar Venta")
    print("4. Eliminar Venta")
    print("5. Salir")
    
    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        visualizar_tabla()
    elif opcion == "2":
        m = input("Mes: ")
        d = input("Departamento: ")
        v = float(input("Monto: "))
        insertar_venta(m, d, v)
    elif opcion == "3":
        m = input("Mes a buscar: ")
        d = input("Departamento a buscar: ")
        buscar_venta(m, d)
    elif opcion == "4":
        m = input("Mes a eliminar: ")
        d = input("Departamento a eliminar: ")
        eliminar_venta(m, d)
    elif opcion == "5":
        print("Cerrando programa...")
        break
    else:
        print("Opción inválida.")