import tkinter as tk
from tkinter import messagebox

class PilaVisual:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador Gráfico de Pila (Stack)")
        self.master.geometry("400x550")
        self.master.configure(bg="#2c3e50")

        # Lógica de la pila
        self.pila = []
        self.capacidad_maxima = 6  # Límite para mostrar el estado "Llena"

        self.crear_interfaz()

    def crear_interfaz(self):
        # Título
        lbl_titulo = tk.Label(self.master, text="Estructura de Datos: Pila", 
                              font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        lbl_titulo.pack(pady=10)

        # Entrada de datos
        frame_entrada = tk.Frame(self.master, bg="#2c3e50")
        frame_entrada.pack(pady=5)
        
        self.entrada_dato = tk.Entry(frame_entrada, font=("Arial", 14), width=10)
        self.entrada_dato.pack(side=tk.LEFT, padx=5)

        # Botones de Operaciones
        frame_botones = tk.Frame(self.master, bg="#2c3e50")
        frame_botones.pack(pady=10)

        btn_push = tk.Button(frame_botones, text="Push (Apilar)", bg="#27ae60", fg="white", 
                             font=("Arial", 10, "bold"), command=self.push)
        btn_push.grid(row=0, column=0, padx=5)

        btn_pop = tk.Button(frame_botones, text="Pop (Desapilar)", bg="#e74c3c", fg="white", 
                            font=("Arial", 10, "bold"), command=self.pop)
        btn_pop.grid(row=0, column=1, padx=5)

        btn_peek = tk.Button(frame_botones, text="Peek (Cima)", bg="#2980b9", fg="white", 
                             font=("Arial", 10, "bold"), command=self.peek)
        btn_peek.grid(row=0, column=2, padx=5)

        # Estado de la Pila
        self.lbl_estado = tk.Label(self.master, text="Estado: Vacía", 
                                   font=("Arial", 12), bg="#2c3e50", fg="#f1c40f")
        self.lbl_estado.pack(pady=5)

        # Canvas para dibujar la pila
        self.canvas = tk.Canvas(self.master, width=200, height=320, bg="#ecf0f1", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(pady=10)
        
        self.dibujar_pila()

    def push(self):
        dato = self.entrada_dato.get()
        if not dato:
            messagebox.showwarning("Advertencia", "Ingresa un dato para apilar.")
            return

        if len(self.pila) >= self.capacidad_maxima:
            messagebox.showerror("Error: Stack Overflow", "La pila está LLENA. No puedes agregar más elementos.")
            return

        self.pila.append(dato)
        self.entrada_dato.delete(0, tk.END)
        self.actualizar_estado()
        self.dibujar_pila()

    def pop(self):
        if not self.pila:
            messagebox.showerror("Error: Stack Underflow", "La pila está VACÍA. No hay nada que quitar.")
            return

        dato_eliminado = self.pila.pop()
        messagebox.showinfo("Pop ejecutado", f"Se ha extraído el elemento: {dato_eliminado}")
        self.actualizar_estado()
        self.dibujar_pila()

    def peek(self):
        if not self.pila:
            messagebox.showinfo("Peek", "La pila está vacía.")
        else:
            cima = self.pila[-1]
            messagebox.showinfo("Peek ejecutado", f"El elemento en la cima es: {cima}")

    def actualizar_estado(self):
        if not self.pila:
            self.lbl_estado.config(text="Estado: Vacía", fg="#f1c40f")
        elif len(self.pila) == self.capacidad_maxima:
            self.lbl_estado.config(text="Estado: Llena (Stack Overflow si agregas más)", fg="#e74c3c")
        else:
            self.lbl_estado.config(text=f"Estado: {len(self.pila)}/{self.capacidad_maxima} elementos", fg="#2ecc71")

    def dibujar_pila(self):
        self.canvas.delete("all")
        
        # Dimensiones de los bloques
        ancho_canvas = 200
        alto_canvas = 320
        alto_bloque = 50
        margen = 10
        
        # Dibujar desde la base hacia arriba
        for i, dato in enumerate(self.pila):
            # Calcular coordenadas (el índice 0 va hasta abajo)
            y2 = alto_canvas - (i * alto_bloque) - margen
            y1 = y2 - alto_bloque + 5 # +5 para dejar un pequeño espacio entre bloques
            x1 = margen
            x2 = ancho_canvas - margen
            
            # Dibujar el rectángulo (el último elemento se pinta de un color distinto para resaltar la cima)
            color_fondo = "#3498db" if i == len(self.pila) - 1 else "#95a5a6"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_fondo, outline="black")
            
            # Dibujar el texto centrado en el bloque
            self.canvas.create_text(ancho_canvas/2, (y1+y2)/2, text=dato, font=("Arial", 12, "bold"), fill="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = PilaVisual(root)
    root.mainloop()