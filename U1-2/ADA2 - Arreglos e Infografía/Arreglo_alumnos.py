import random

def main():
    # --- 1. CONFIGURACIÓN ---
    FILAS_ALUMNOS = 500
    COLUMNAS_MATERIAS = 6
    
    matriz = []

    # Llenamos la matriz (Internamente sigue siendo 0 a 499)
    for i in range(FILAS_ALUMNOS):
        calificaciones = [random.randint(60, 100) for _ in range(COLUMNAS_MATERIAS)]
        matriz.append(calificaciones)

    # --- 2. IMPRESIÓN DE LA TABLA (Visualización AJUSTADA +1) ---
    print("\n--- TABLA DE CALIFICACIONES (500 Alumnos) ---\n")
    
    header = f"{'ALUMNO':<12} |"
    # Ajuste visual: mostramos m + 1 para ver Materia 1 a 6
    for m in range(COLUMNAS_MATERIAS):
        header += f" {'MAT ' + str(m + 1):<7} |"
    
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    # Imprimimos los 500 alumnos
    for i in range(FILAS_ALUMNOS):
        # Ajuste visual: mostramos i + 1 para ver Alumno 1 a 500
        numero_visual_alumno = i + 1
        fila_str = f"{'Alumno ' + str(numero_visual_alumno):<12} |"
        
        for nota in matriz[i]:
            fila_str += f" {nota:<7} |"
        print(fila_str)

    print("-" * len(header)) 

    # --- 3. BÚSQUEDA INTERACTIVA (Ajustada a lógica humana) ---
    print("\n" + "="*40)
    print("       BÚSQUEDA DE CALIFICACIONES")
    print("="*40)

    try:
        # Ahora el usuario ingresa del 1 al 500
        input_alumno = int(input(f"Ingrese el número del Alumno (1 - {FILAS_ALUMNOS}): "))
        input_materia = int(input(f"Ingrese el número de la Materia (1 - {COLUMNAS_MATERIAS}): "))

        # Ajuste interno: Restamos 1 para que la computadora entienda
        # Si usuario escribe 500 -> indice 499
        idx_alumno = input_alumno - 1
        idx_materia = input_materia - 1

        # Validamos índices reales (0 a 499)
        if (0 <= idx_alumno < FILAS_ALUMNOS) and (0 <= idx_materia < COLUMNAS_MATERIAS):
            
            nota_encontrada = matriz[idx_alumno][idx_materia]
            
            print(f"\n✅ RESULTADO:")
            # Mostramos los datos tal cual los ingresó el usuario (estilo humano)
            print(f"El Alumno {input_alumno} tiene una nota de {nota_encontrada} en la Materia {input_materia}.")
            
        else:
            print(f"\n❌ ERROR: Fuera de rango.")
            print(f"   Alumno debe ser entre 1 y {FILAS_ALUMNOS}")
            print(f"   Materia debe ser entre 1 y {COLUMNAS_MATERIAS}")

    except ValueError:
        print("\n❌ ERROR: Por favor, ingrese solamente números enteros.")

if __name__ == "__main__":
    main()