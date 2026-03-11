import tkinter as tk
from tkinter import ttk, messagebox

class EvaluadorGraficoPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Evaluador de Pilas con Historial")
        self.root.geometry("700x550")
        self.root.configure(bg="#f8f9fa")
        
        self.operadores = {'+', '-', '*', '/', '^'}
        self.pila = []
        self.delay = 1200  
        
        tk.Label(root, text="Expresiones Aritmeticas", font=("Arial", 14, "bold"), bg="#f8f9fa").pack(pady=10)
        
        frame_top = tk.Frame(root, bg="#f8f9fa")
        frame_top.pack(pady=5)
        self.entry_exp = tk.Entry(frame_top, width=35, font=("Arial", 12))
        self.entry_exp.insert(0, "4 5 + 3 *")
        self.entry_exp.pack(side=tk.LEFT, padx=5)
        
        frame_btns = tk.Frame(root, bg="#f8f9fa")
        frame_btns.pack(pady=10)
        tk.Button(frame_btns, text="Evaluar Posfija", command=lambda: self.iniciar("pos"), bg="#d1e7dd").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="Evaluar Prefija", command=lambda: self.iniciar("pre"), bg="#cfe2ff").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="Limpiar", command=self.limpiar, bg="#f8d7da").pack(side=tk.LEFT, padx=5)

        frame_main = tk.Frame(root, bg="#f8f9fa")
        frame_main.pack(pady=10, fill=tk.BOTH, expand=True)


        frame_pila = tk.Frame(frame_main, bg="#f8f9fa")
        frame_pila.pack(side=tk.LEFT, padx=30)
        tk.Label(frame_pila, text="Pila (LIFO)", font=("Arial", 10, "bold"), bg="#f8f9fa").pack()
        self.canvas_pila = tk.Canvas(frame_pila, width=160, height=250, bg="white", highlightthickness=2)
        self.canvas_pila.pack()

        frame_hist = tk.Frame(frame_main, bg="#f8f9fa")
        frame_hist.pack(side=tk.RIGHT, padx=30, fill=tk.BOTH, expand=True)
        tk.Label(frame_hist, text="Historial de Operaciones", font=("Arial", 10, "bold"), bg="#f8f9fa").pack()
        self.historial = tk.Listbox(frame_hist, height=12, width=40, font=("Courier", 9))
        self.historial.pack(pady=5)

        self.lbl_resultado = tk.Label(root, text="Resultado: -", font=("Arial", 12, "bold"), fg="#0d6efd", bg="#f8f9fa")
        self.lbl_resultado.pack(pady=15)

    def dibujar_pila(self):
        self.canvas_pila.delete("all")

        self.canvas_pila.create_line(40, 20, 40, 230, width=3)
        self.canvas_pila.create_line(120, 20, 120, 230, width=3)
        self.canvas_pila.create_line(40, 230, 120, 230, width=3)
        
        for i, elem in enumerate(self.pila):
            y_pos = 200 - (i * 35)
            self.canvas_pila.create_rectangle(45, y_pos, 115, y_pos + 30, fill="#ffca28", outline="black")
            self.canvas_pila.create_text(80, y_pos + 15, text=str(elem), font=("Arial", 9, "bold"))

    def agregar_historial(self, texto):
        self.historial.insert(tk.END, f" {texto}")
        self.historial.see(tk.END) 

    def iniciar(self, tipo):
        self.pila = []
        self.historial.delete(0, tk.END)
        self.lbl_resultado.config(text="Procesando...")
        
        exp = self.entry_exp.get().split()
        if not exp: return
        
        tokens = exp if tipo == "pos" else list(reversed(exp))
        self.agregar_historial(f"--- Iniciando modo {tipo.upper()} ---")
        self.ejecutar_pasos(tokens, tipo)

    def ejecutar_pasos(self, tokens, tipo):
        if not tokens:
            if len(self.pila) == 1:
                final = self.pila[0]
                self.lbl_resultado.config(text=f"Resultado Final: {final}")
                self.agregar_historial(f"FIN: Resultado es {final}")
            return

        token = tokens.pop(0)
        
        if token not in self.operadores:
            val = float(token)
            self.pila.append(val)
            self.agregar_historial(f"PUSH: {val} a la pila")
        else:
            if len(self.pila) >= 2:
                b = self.pila.pop()
                a = self.pila.pop()
                if tipo == "pre": a, b = b, a 
                
                res = self.operar(token, a, b)
                self.agregar_historial(f"POP: {a} y {b}")
                self.agregar_historial(f"CALC: {a} {token} {b} = {res}")
                self.pila.append(res)
                self.agregar_historial(f"PUSH: {res} a la pila")
            else:
                messagebox.showerror("Error", "Expresión inválida")
                return

        self.dibujar_pila()
        self.root.after(self.delay, lambda: self.ejecutar_pasos(tokens, tipo))

    def operar(self, op, a, b):
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a / b
        if op == '^': return a ** b
        return 0

    def limpiar(self):
        self.entry_exp.delete(0, tk.END)
        self.pila = []
        self.historial.delete(0, tk.END)
        self.dibujar_pila()
        self.lbl_resultado.config(text="Resultado: -")

if __name__ == "__main__":
    root = tk.Tk()
    app = EvaluadorGraficoPro(root)
    root.mainloop()