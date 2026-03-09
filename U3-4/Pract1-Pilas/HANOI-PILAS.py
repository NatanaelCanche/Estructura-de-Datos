import tkinter as tk
from tkinter import messagebox

class PilaExtraccionVisual:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador: Extracción Profunda (Tipo Hanói)")
        self.master.geometry("550x650")
        self.master.configure(bg="#2c3e50")

        # Tenemos DOS pilas ahora. La principal y la temporal.
        self.pila_principal = []
        self.pila_auxiliar = []
        self.capacidad_maxima = 8

        self.crear_interfaz()

    def crear_interfaz(self):
        # Título
        tk.Label(self.master, text="Uso de Pila Auxiliar para Extracción", 
                 font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=10)

        # Controles de Entrada
        frame_entrada = tk.Frame(self.master, bg="#2c3e50")
        frame_entrada.pack(pady=5)
        
        tk.Label(frame_entrada, text="Elemento:", font=("Arial", 12), bg="#2c3e50", fg="white").grid(row=0, column=0, padx=5)
        self.entrada_dato = tk.Entry(frame_entrada, font=("Arial", 14), width=10)
        self.entrada_dato.grid(row=0, column=1, padx=5)

        # Botones Principales
        self.frame_botones = tk.Frame(self.master, bg="#2c3e50")
        self.frame_botones.pack(pady=10)

        self.btn_push = tk.Button(self.frame_botones, text="1. Insertar (Push)", bg="#27ae60", fg="white", 
                                  font=("Arial", 10, "bold"), command=self.push)
        self.btn_push.grid(row=0, column=0, padx=10)

        self.btn_extraer = tk.Button(self.frame_botones, text="2. Extraer Elemento Específico", bg="#e74c3c", fg="white", 
                                     font=("Arial", 10, "bold"), command=self.iniciar_extraccion)
        self.btn_extraer.grid(row=0, column=1, padx=10)

        # Letrero de estado de la animación
        self.lbl_accion = tk.Label(self.master, text="Modo Manual Listo", 
                                   font=("Arial", 12, "italic"), bg="#2c3e50", fg="#f1c40f")
        self.lbl_accion.pack(pady=5)

        # Área de dibujo para las DOS pilas
        frame_canvas = tk.Frame(self.master, bg="#2c3e50")
        frame_canvas.pack(pady=10)

        # Canvas Principal
        tk.Label(frame_canvas, text="Pila Principal", font=("Arial", 12, "bold"), bg="#2c3e50", fg="white").grid(row=0, column=0)
        self.canvas_principal = tk.Canvas(frame_canvas, width=200, height=400, bg="#ecf0f1", relief=tk.SUNKEN, bd=2)
        self.canvas_principal.grid(row=1, column=0, padx=20)

        # Canvas Auxiliar
        tk.Label(frame_canvas, text="Pila Auxiliar (Temporal)", font=("Arial", 12, "bold"), bg="#2c3e50", fg="#bdc3c7").grid(row=0, column=1)
        self.canvas_auxiliar = tk.Canvas(frame_canvas, width=200, height=400, bg="#34495e", relief=tk.SUNKEN, bd=2)
        self.canvas_auxiliar.grid(row=1, column=1, padx=20)

    def push(self):
        dato = self.entrada_dato.get()
        if not dato:
            messagebox.showwarning("Advertencia", "Escribe un dato primero.")
            return

        if len(self.pila_principal) >= self.capacidad_maxima:
            messagebox.showerror("Error", "La pila principal está llena.")
            return

        self.pila_principal.append(dato)
        self.entrada_dato.delete(0, tk.END)
        self.dibujar_pilas()

    def iniciar_extraccion(self):
        objetivo = self.entrada_dato.get()
        
        if not self.pila_principal:
            messagebox.showerror("Error", "La pila está vacía.")
            return
            
        if objetivo not in self.pila_principal:
            messagebox.showerror("Error", f"El elemento '{objetivo}' no existe en la pila.")
            return

        # Bloquear botones durante la animación
        self.btn_push.config(state=tk.DISABLED)
        self.btn_extraer.config(state=tk.DISABLED)
        
        # Iniciar el proceso recursivo visual
        self.lbl_accion.config(text=f"Buscando '{objetivo}'...", fg="#f1c40f")
        self.paso_desapilar(objetivo)

    def paso_desapilar(self, objetivo):
        # Si el elemento en la cima es el que buscamos
        if self.pila_principal[-1] == objetivo:
            extraido = self.pila_principal.pop()
            self.dibujar_pilas()
            self.lbl_accion.config(text=f"¡Elemento '{extraido}' extraído con éxito!", fg="#2ecc71")
            
            # Pausamos 1 segundo para que el usuario vea que desapareció, y empezamos a regresar los datos
            self.master.after(1500, self.paso_restaurar)
            
        # Si no es el que buscamos, lo movemos a la pila auxiliar
        else:
            estorbo = self.pila_principal.pop()
            self.pila_auxiliar.append(estorbo)
            self.lbl_accion.config(text=f"Moviendo '{estorbo}' a la pila auxiliar...", fg="#e67e22")
            self.dibujar_pilas()
            
            # Repetimos la función después de 1 segundo (Animación)
            self.master.after(1000, lambda: self.paso_desapilar(objetivo))

    def paso_restaurar(self):
        # Si hay elementos en la pila auxiliar, los regresamos uno por uno
        if len(self.pila_auxiliar) > 0:
            elemento_recuperado = self.pila_auxiliar.pop()
            self.pila_principal.append(elemento_recuperado)
            self.lbl_accion.config(text=f"Regresando '{elemento_recuperado}' a la pila principal...", fg="#3498db")
            self.dibujar_pilas()
            
            # Repetimos después de 1 segundo
            self.master.after(1000, self.paso_restaurar)
            
        # Cuando la auxiliar queda vacía, terminamos
        else:
            self.lbl_accion.config(text="Proceso terminado. Orden restaurado.", fg="#2ecc71")
            self.entrada_dato.delete(0, tk.END)
            # Reactivar botones
            self.btn_push.config(state=tk.NORMAL)
            self.btn_extraer.config(state=tk.NORMAL)

    def dibujar_pilas(self):
        # Dibujar Pila Principal
        self.canvas_principal.delete("all")
        self._dibujar_canvas(self.canvas_principal, self.pila_principal, color_base="#3498db", color_tope="#9b59b6")
        
        # Dibujar Pila Auxiliar
        self.canvas_auxiliar.delete("all")
        self._dibujar_canvas(self.canvas_auxiliar, self.pila_auxiliar, color_base="#95a5a6", color_tope="#7f8c8d")

    def _dibujar_canvas(self, canvas, lista, color_base, color_tope):
        ancho_canvas = 200
        alto_canvas = 400
        alto_bloque = 45
        margen = 10
        
        for i, dato in enumerate(lista):
            y2 = alto_canvas - (i * alto_bloque) - margen
            y1 = y2 - alto_bloque + 5 
            x1 = margen
            x2 = ancho_canvas - margen
            
            color_fondo = color_tope if i == len(lista) - 1 else color_base
            canvas.create_rectangle(x1, y1, x2, y2, fill=color_fondo, outline="black")
            canvas.create_text(ancho_canvas/2, (y1+y2)/2, text=dato, font=("Arial", 12, "bold"), fill="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = PilaExtraccionVisual(root)
    root.mainloop()