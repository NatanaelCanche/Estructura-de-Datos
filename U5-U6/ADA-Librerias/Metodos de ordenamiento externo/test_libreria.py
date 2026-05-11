# test_libreria.py
import ordenamiento_externo as oe

# 1. Probar lógica pura (esto se ve solo en consola)
datos_prueba = [25, 2, 10, 55, 1, 8]
resultado = oe.generar_pasadas_mezcla_directa(datos_prueba)
print("Estado final en consola:", resultado[-1])

# 2. LANZAR LA INTERFAZ (esto abre la ventana de Matplotlib)
# Puedes pasarle datos iniciales o dejarlo vacío para usar los de defecto
oe.iniciar_visualizador()