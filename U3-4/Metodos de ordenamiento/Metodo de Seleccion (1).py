import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class OrdenamientoSeleccionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordenamiento por Selección - Organizando Libros")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Datos iniciales (años de publicación de libros)
        self.datos = [2015, 2008, 2020, 2005, 2018, 2010, 2003, 2022, 1999, 2012]
        self.datos_original = self.datos.copy()
        self.paso_actual = 0
        self.historial = []  # Guarda el estado después de cada paso
        self.indice_actual = -1  # Índice que se está comparando
        self.min_index = -1      # Índice del mínimo encontrado
        
        self.generar_historial()
        self.setup_ui()
        self.mostrar_grafico()
    
    def generar_historial(self):
        """Ejecuta el algoritmo de selección y guarda los estados visuales."""
        datos = self.datos_original.copy()
        n = len(datos)
        self.historial = []
        
        # Guardar estado inicial
        self.historial.append({
            'datos': datos.copy(),
            'comparando': -1,
            'minimo': -1,
            'fijo_hasta': -1,
            'mensaje': "Estado inicial: Libros sin ordenar"
        })
        
        for i in range(n):
            min_idx = i
            # Guardar estado antes de buscar el mínimo
            self.historial.append({
                'datos': datos.copy(),
                'comparando': i,
                'minimo': i,
                'fijo_hasta': i-1,
                'mensaje': f"Paso {i+1}: Buscando el libro más antiguo desde posición {i}"
            })
            
            for j in range(i+1, n):
                # Guardar comparación actual
                self.historial.append({
                    'datos': datos.copy(),
                    'comparando': j,
                    'minimo': min_idx,
                    'fijo_hasta': i-1,
                    'mensaje': f"Comparando libro del año {datos[j]} con el año mínimo actual {datos[min_idx]}"
                })
                
                if datos[j] < datos[min_idx]:
                    min_idx = j
                    # Guardar cuando se encuentra un nuevo mínimo
                    self.historial.append({
                        'datos': datos.copy(),
                        'comparando': j,
                        'minimo': min_idx,
                        'fijo_hasta': i-1,
                        'mensaje': f"¡Nuevo libro más antiguo encontrado! Año {datos[min_idx]} en posición {min_idx}"
                    })
            
            if min_idx != i:
                # Intercambiar
                datos[i], datos[min_idx] = datos[min_idx], datos[i]
                # Guardar estado después del intercambio
                self.historial.append({
                    'datos': datos.copy(),
                    'comparando': -1,
                    'minimo': -1,
                    'fijo_hasta': i,
                    'mensaje': f"Intercambio: Libro del año {datos[i]} va a posición {i}, libro del año {datos[min_idx]} va a posición {min_idx}"
                })
            else:
                # Ya estaba en su lugar
                self.historial.append({
                    'datos': datos.copy(),
                    'comparando': -1,
                    'minimo': -1,
                    'fijo_hasta': i,
                    'mensaje': f"El libro en posición {i} ya es el más antiguo de los restantes"
                })
        
        # Estado final
        self.historial.append({
            'datos': datos.copy(),
            'comparando': -1,
            'minimo': -1,
            'fijo_hasta': n-1,
            'mensaje': "¡Ordenamiento completado! Libros ordenados por año de publicación (más antiguo a más reciente)"
        })
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y descripción
        title_label = ttk.Label(main_frame, text="Método de Ordenamiento por Selección", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=5)
        
        desc_text = ("Ejemplo real: Organizar libros en una estantería por año de publicación.\n"
                     "El algoritmo busca el libro más antiguo (año más pequeño) y lo coloca al inicio,\n"
                     "luego busca el siguiente más antiguo entre los restantes, y así sucesivamente.")
        desc_label = ttk.Label(main_frame, text=desc_text, font=("Arial", 10), justify="center")
        desc_label.pack(pady=5)
        
        # Frame para el gráfico
        self.figure = plt.Figure(figsize=(10, 5), dpi=80)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, main_frame)
        self.canvas.get_tk_widget().pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Frame para controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        # Botones de navegación
        self.btn_anterior = ttk.Button(control_frame, text="◀ Anterior", command=self.paso_anterior)
        self.btn_anterior.pack(side=tk.LEFT, padx=5)
        
        self.btn_siguiente = ttk.Button(control_frame, text="Siguiente ▶", command=self.paso_siguiente)
        self.btn_siguiente.pack(side=tk.LEFT, padx=5)
        
        self.btn_inicio = ttk.Button(control_frame, text="⟪ Inicio", command=self.ir_inicio)
        self.btn_inicio.pack(side=tk.LEFT, padx=5)
        
        self.btn_fin = ttk.Button(control_frame, text="Fin ⟫", command=self.ir_fin)
        self.btn_fin.pack(side=tk.LEFT, padx=5)
        
        self.btn_reiniciar = ttk.Button(control_frame, text="Reiniciar", command=self.reiniciar)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5)
        
        # Indicador de paso
        self.step_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.step_label.pack(pady=5)
        
        # Mensaje de estado
        self.message_label = ttk.Label(main_frame, text="", font=("Arial", 10, "italic"), wraplength=800)
        self.message_label.pack(pady=5)
        
        # Actualizar contador de pasos
        self.actualizar_info()
    
    def mostrar_grafico(self):
        """Dibuja el gráfico de barras con colores que indican el estado."""
        self.ax.clear()
        
        estado = self.historial[self.paso_actual]
        datos = estado['datos']
        comparando = estado['comparando']
        minimo = estado['minimo']
        fijo_hasta = estado['fijo_hasta']
        
        indices = np.arange(len(datos))
        colores = []
        
        for i in range(len(datos)):
            if i <= fijo_hasta:
                colores.append('green')  # Ya ordenados
            elif i == minimo:
                colores.append('gold')   # Mínimo encontrado
            elif i == comparando:
                colores.append('orange') # Comparando actual
            else:
                colores.append('skyblue') # Pendiente
        
        bars = self.ax.bar(indices, datos, color=colores, edgecolor='black')
        self.ax.set_xlabel('Posición en la estantería', fontsize=10)
        self.ax.set_ylabel('Año de publicación', fontsize=10)
        self.ax.set_title('Ordenando libros por año (más antiguo → más reciente)', fontsize=12)
        self.ax.set_xticks(indices)
        self.ax.set_xticklabels([f'Estante {i}' for i in indices], rotation=45)
        
        # Agregar valor sobre cada barra
        for bar, valor in zip(bars, datos):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                         f'{int(valor)}', ha='center', va='bottom', fontsize=9)
        
        self.canvas.draw()
    
    def actualizar_info(self):
        """Actualiza los textos de información."""
        total = len(self.historial) - 1
        self.step_label.config(text=f"Paso {self.paso_actual} de {total}")
        
        mensaje = self.historial[self.paso_actual]['mensaje']
        self.message_label.config(text=mensaje)
        
        # Habilitar/deshabilitar botones según el paso
        if self.paso_actual == 0:
            self.btn_anterior.config(state=tk.DISABLED)
            self.btn_inicio.config(state=tk.DISABLED)
        else:
            self.btn_anterior.config(state=tk.NORMAL)
            self.btn_inicio.config(state=tk.NORMAL)
        
        if self.paso_actual >= len(self.historial) - 1:
            self.btn_siguiente.config(state=tk.DISABLED)
            self.btn_fin.config(state=tk.DISABLED)
        else:
            self.btn_siguiente.config(state=tk.NORMAL)
            self.btn_fin.config(state=tk.NORMAL)
    
    def paso_siguiente(self):
        if self.paso_actual < len(self.historial) - 1:
            self.paso_actual += 1
            self.mostrar_grafico()
            self.actualizar_info()
    
    def paso_anterior(self):
        if self.paso_actual > 0:
            self.paso_actual -= 1
            self.mostrar_grafico()
            self.actualizar_info()
    
    def ir_inicio(self):
        self.paso_actual = 0
        self.mostrar_grafico()
        self.actualizar_info()
    
    def ir_fin(self):
        self.paso_actual = len(self.historial) - 1
        self.mostrar_grafico()
        self.actualizar_info()
    
    def reiniciar(self):
        self.paso_actual = 0
        self.mostrar_grafico()
        self.actualizar_info()
        messagebox.showinfo("Reiniciar", "Se ha reiniciado la visualización del algoritmo.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrdenamientoSeleccionApp(root)
    root.mainloop()