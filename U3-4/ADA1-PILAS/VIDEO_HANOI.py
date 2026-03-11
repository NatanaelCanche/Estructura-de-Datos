import tkinter as tk
from tkinter import messagebox
import time

class Pila:
    """Clase Pila básica para gestionar los discos."""
    def __init__(self):
        self.items = []
    def apilar(self, item): self.items.append(item)
    def desapilar(self): return self.items.pop() if not self.esta_vacia() else None
    def esta_vacia(self): return len(self.items) == 0
    def ver_todo(self): return self.items

class HanoiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Torres de Hanoi - Simulación con Pilas")
        
        self.torres = [Pila(), Pila(), Pila()]
        for disco in [3, 2, 1]:
            self.torres[0].apilar(disco)

        self.canvas = tk.Canvas(root, width=600, height=300, bg="white")
        self.canvas.pack(pady=20)
        
        self.btn_resolver = tk.Button(root, text="Resolver Automáticamente", command=self.iniciar_resolucion)
        self.btn_resolver.pack(pady=10)
        
        self.dibujar_escena()

    def dibujar_escena(self):
        """Dibuja las torres y los discos actuales basándose en las Pilas."""
        self.canvas.delete("all")
        nombres = ["Origen", "Auxiliar", "Destino"]
        
        for i in range(3):
            x_base = 100 + (i * 200)
            self.canvas.create_rectangle(x_base-5, 100, x_base+5, 250, fill="gray")
            self.canvas.create_text(x_base, 270, text=nombres[i])
            
            discos = self.torres[i].ver_todo()
            for nivel, tamano in enumerate(discos):
                ancho = tamano * 40
                y = 240 - (nivel * 25)
                color = ["#FF5733", "#33FF57", "#3357FF"][tamano-1]
                self.canvas.create_rectangle(x_base - ancho/2, y, x_base + ancho/2, y + 20, fill=color, outline="black")

    def mover_disco(self, origen, destino):
        """Lógica de pilas: Desapila de uno y apila en otro."""
        disco = self.torres[origen].desapilar()
        self.torres[destino].apilar(disco)
        self.dibujar_escena()
        self.root.update()
        time.sleep(0.8) 

    def resolver_hanoi(self, n, origen, destino, auxiliar):
        """Algoritmo recursivo clásico."""
        if n == 1:
            self.mover_disco(origen, destino)
        else:
            self.resolver_hanoi(n-1, origen, auxiliar, destino)
            self.mover_disco(origen, destino)
            self.resolver_hanoi(n-1, auxiliar, destino, origen)

    def iniciar_resolucion(self):
        self.btn_resolver.config(state="disabled")
        self.resolver_hanoi(3, 0, 2, 1)
        messagebox.showinfo("Éxito", "¡Torres de Hanoi resueltas!")
        self.btn_resolver.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = HanoiGUI(root)
    root.mainloop()