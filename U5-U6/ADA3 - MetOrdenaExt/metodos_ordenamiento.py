import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import timeit
import random
import threading
from typing import List, Tuple, Callable, Dict, Any

# ==================== ALGORITMOS DE ORDENAMIENTO ====================

def intercalacion(lista: List[int]) -> Tuple[List[int], List[List[int]]]:
    """
    Intercalación (Insertion Sort):
    Toma cada elemento y lo inserta en la posición correcta
    dentro de la parte ya ordenada de la lista.
    """
    pasos: List[List[int]] = []
    arr = lista[:]
    n = len(arr)
    pasos.append(arr[:])
    for i in range(1, n):
        clave = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > clave:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = clave
        pasos.append(arr[:])
    return arr, pasos


def mezcla_directa(lista: List[int]) -> Tuple[List[int], List[List[int]]]:
    """
    Mezcla Directa (Merge Sort):
    Divide la lista en mitades recursivamente y las combina ordenadas.
    """
    pasos: List[List[int]] = []
    arr = lista[:]
    pasos.append(arr[:])

    def merge_sort(start: int, end: int):
        if end - start > 1:
            mid = (start + end) // 2
            merge_sort(start, mid)
            merge_sort(mid, end)
            merge(start, mid, end)

    def merge(start: int, mid: int, end: int):
        left = arr[start:mid]
        right = arr[mid:end]
        i = j = 0
        k = start
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
        pasos.append(arr[:])

    merge_sort(0, len(arr))
    return arr, pasos


def mezcla_equilibrada(lista: List[int]) -> Tuple[List[int], List[List[int]]]:
    """
    Mezcla Equilibrada (Natural Merge Sort):
    Identifica secuencias naturalmente ordenadas (runs) y las mezcla.
    """
    pasos: List[List[int]] = []
    arr = lista[:]
    pasos.append(arr[:])

    def encontrar_runs(array: List[int]) -> List[Tuple[int, int]]:
        runs = []
        i = 0
        n = len(array)
        while i < n:
            j = i + 1
            while j < n and array[j] >= array[j - 1]:
                j += 1
            runs.append((i, j))
            i = j
        return runs

    def merge_runs(r1: Tuple[int, int], r2: Tuple[int, int]):
        start1, end1 = r1
        start2, end2 = r2
        left = arr[start1:end1]
        right = arr[start2:end2]
        i = j = 0
        k = start1
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

    while True:
        runs = encontrar_runs(arr)
        if len(runs) <= 1:
            break
        i = 0
        while i < len(runs) - 1:
            merge_runs(runs[i], runs[i + 1])
            pasos.append(arr[:])
            i += 2

    return arr, pasos

# ==================== VISUALIZACIÓN DE BARRAS ====================

def dibujar_barras_estado(canvas: tk.Canvas, datos: List[int], color: str, titulo: str, offset_x: int, ancho_total: int, max_val: int, pad: int = 20):
    w = canvas.winfo_width() or 700
    h = canvas.winfo_height() or 400
    
    if not datos:
        return

    bw = ancho_total / len(datos) * 0.75
    gap = ancho_total / len(datos)
    max_h = h - pad * 4 - 30

    canvas.create_text(offset_x + ancho_total // 2, pad,
                       text=titulo, fill="#9090b0",
                       font=("Consolas", 9))

    for i, val in enumerate(datos):
        bh = (val / max_val) * max_h if max_val > 0 else 1
        x1 = offset_x + i * gap + gap * 0.125
        y1 = h - pad * 2 - bh
        x2 = x1 + bw
        y2 = h - pad * 2

        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", width=0)
        if len(datos) <= 30:
            canvas.create_text((x1 + x2) / 2, y1 - 8,
                               text=str(val),
                               fill="#e8e8f0", font=("Consolas", 7))

def dibujar_barras_comparacion(canvas: tk.Canvas, tiempos: List[float], colores: List[str], nombres: List[str]):
    canvas.delete("all")
    canvas.update_idletasks()
    w = canvas.winfo_width() or 700
    h = canvas.winfo_height() or 160

    if not tiempos or max(tiempos) == 0:
        return

    pad = 20
    n = len(tiempos)
    bw = (w - pad * 2) / n * 0.6
    gap = (w - pad * 2) / n
    max_t = max(tiempos)
    max_h = h - pad * 3

    for i, (t, col, nom) in enumerate(zip(tiempos, colores, nombres)):
        bh = (t / max_t) * max_h if max_t > 0 else 1
        x1 = pad + i * gap + gap * 0.2
        y1 = h - pad * 2 - bh
        x2 = x1 + bw
        y2 = h - pad * 2

        canvas.create_rectangle(x1, y1, x2, y2, fill=col, outline="", width=0)
        canvas.create_text((x1 + x2) / 2, y1 - 10,
                           text=f"{t:.4f}ms", fill=col,
                           font=("Consolas", 8))
        canvas.create_text((x1 + x2) / 2, h - pad + 4,
                           text=nom[:16], fill="#9090b0",
                           font=("Consolas", 7))


# ==================== INTERFAZ GRÁFICA ====================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Métodos de Ordenamiento — Investigación")
        self.geometry("1100x720")
        self.configure(bg="#0f0f1a")
        self.resizable(True, True)

        self.colores: Dict[str, str] = {
            "bg":       "#0f0f1a",
            "panel":    "#1a1a2e",
            "borde":    "#252545",
            "acento":   "#7c5cbf",
            "acento2":  "#5ca8bf",
            "acento3":  "#bf5c8a",
            "texto":    "#e8e8f0",
            "muted":    "#9090b0",
            "verde":    "#5cbf7c",
            "amarillo": "#bfa55c",
            "rojo":     "#bf5c5c",
        }

        self.animating: bool = False

        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        c = self.colores
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background=c["bg"], borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook.Tab", background=c["panel"], foreground=c["muted"], padding=[18, 10], font=("Consolas", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", c["acento"]), ("active", c["borde"])], foreground=[("selected", "#ffffff"), ("active", c["texto"])])
        
        style.configure("TFrame", background=c["bg"])
        style.configure("Inner.TFrame", background=c["panel"])
        
        style.configure("Accion.TButton", background=c["acento"], foreground="#ffffff", font=("Consolas", 10, "bold"), padding=[14, 8], borderwidth=0, relief="flat")
        style.map("Accion.TButton", background=[("active", "#9070df")], foreground=[("disabled", "#a0a0a0")])
        
        style.configure("Animar.TButton", background=c["verde"], foreground="#ffffff", font=("Consolas", 10, "bold"), padding=[14, 8], borderwidth=0, relief="flat")
        style.map("Animar.TButton", background=[("active", "#7ce09c")], foreground=[("disabled", "#a0a0a0")])

        style.configure("Sec.TButton", background=c["borde"], foreground=c["texto"], font=("Consolas", 9), padding=[10, 6], borderwidth=0, relief="flat")
        style.map("Sec.TButton", background=[("active", c["acento"])])

    def _construir_ui(self):
        c = self.colores

        # Cabecera
        cab = tk.Frame(self, bg=c["panel"], pady=14, padx=24)
        cab.pack(fill="x", side="top")

        tk.Label(cab, text="⬡ MÉTODOS DE ORDENAMIENTO", bg=c["panel"], fg=c["acento"], font=("Consolas", 16, "bold")).pack(side="left")
        tk.Label(cab, text="Investigación · Python GUI", bg=c["panel"], fg=c["muted"], font=("Consolas", 9)).pack(side="left", padx=16)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(6, 10))

        self._tab_intercalacion(nb)
        self._tab_mezcla_directa(nb)
        self._tab_mezcla_equilibrada(nb)
        self._tab_comparacion(nb)

    def _crear_tab_algoritmo(self, nb: ttk.Notebook, nombre: str, color_acento: str, funcion: Callable, info: Dict[str, str]):
        c = self.colores
        frame = ttk.Frame(nb)
        nb.add(frame, text=nombre)

        # Panel izquierdo
        izq = tk.Frame(frame, bg=c["panel"], width=320)
        izq.pack(side="left", fill="y", padx=(10, 5), pady=10)
        izq.pack_propagate(False)

        tk.Label(izq, text=nombre, bg=c["panel"], fg=color_acento, font=("Consolas", 13, "bold")).pack(anchor="w", padx=14, pady=(14, 4))
        tk.Label(izq, text=info["subtitulo"], bg=c["panel"], fg=c["muted"], font=("Consolas", 8), wraplength=290, justify="left").pack(anchor="w", padx=14)

        tk.Frame(izq, bg=color_acento, height=2).pack(fill="x", padx=14, pady=8)

        # Entrada de datos
        tk.Label(izq, text="Datos de entrada:", bg=c["panel"], fg=c["texto"], font=("Consolas", 9, "bold")).pack(anchor="w", padx=14, pady=(4, 2))
        
        frame_entrada = tk.Frame(izq, bg=c["panel"])
        frame_entrada.pack(fill="x", padx=14)
        entrada_var = tk.StringVar()
        entrada = tk.Entry(frame_entrada, textvariable=entrada_var, bg=c["borde"], fg=c["texto"], font=("Consolas", 10), insertbackground=c["texto"], relief="flat", highlightbackground=c["borde"], highlightcolor=color_acento, highlightthickness=1)
        entrada.pack(fill="x", pady=(0, 6), ipady=5)

        tk.Label(izq, text="Separa los números con comas", bg=c["panel"], fg=c["muted"], font=("Consolas", 8)).pack(anchor="w", padx=14)

        # Botones rápidos
        def gen_aleatorio():
            if not self.animating: entrada_var.set(",".join(map(str, random.sample(range(1, 100), 10))))

        def gen_ordenado_inv():
            if not self.animating: entrada_var.set(",".join(map(str, range(10, 0, -1))))

        fr_btn = tk.Frame(izq, bg=c["panel"])
        fr_btn.pack(fill="x", padx=14, pady=(6, 0))
        btn_aleatorio = ttk.Button(fr_btn, text="🎲 Aleatorio", style="Sec.TButton", command=gen_aleatorio)
        btn_aleatorio.pack(side="left", padx=(0, 6))
        btn_inverso = ttk.Button(fr_btn, text="↓ Invertido", style="Sec.TButton", command=gen_ordenado_inv)
        btn_inverso.pack(side="left")

        tk.Frame(izq, bg=c["borde"], height=1).pack(fill="x", padx=14, pady=12)

        resultado_var = tk.StringVar(value="—")
        tiempo_var = tk.StringVar(value="—")
        pasos_var = tk.StringVar(value="—")

        # UI Elements that need to be disabled during processing
        controles = [entrada, btn_aleatorio, btn_inverso]
        canvas_ref: List[tk.Canvas] = []
        pasos_cache: List[List[int]] = []

        def parse_input() -> List[int]:
            raw = entrada_var.get().strip()
            if not raw:
                messagebox.showwarning("Entrada vacía", "Ingresa al menos un número.")
                return []
            try:
                lista = [int(x.strip()) for x in raw.split(",") if x.strip()]
            except ValueError:
                messagebox.showerror("Error", "Solo se permiten números enteros.")
                return []
            if len(lista) < 2:
                messagebox.showwarning("Pocos datos", "Ingresa al menos 2 números.")
                return []
            return lista

        def redibujar_base(original: List[int], actual: List[int]):
            canvas = canvas_ref[0]
            canvas.delete("all")
            canvas.update_idletasks()
            w = canvas.winfo_width() or 700
            pad = 20
            mitad = (w - pad * 2) // 2 - 10
            max_val = max(max(original), max(actual)) if original else 1
            dibujar_barras_estado(canvas, original, "#444466", "ESTADO INICIAL", pad, mitad, max_val, pad)
            dibujar_barras_estado(canvas, actual, color_acento, "ESTADO ACTUAL", pad + mitad + 20, mitad, max_val, pad)
            canvas.create_line(pad + mitad + 10, pad, pad + mitad + 10, (canvas.winfo_height() or 400) - pad, fill="#252545", width=1)

        def ejecutar_ordenamiento():
            lista = parse_input()
            if not lista: return

            for c in controles: c.configure(state="disabled")
            btn_ordenar.configure(state="disabled")
            btn_animar.configure(state="disabled")
            
            # Ejecutar en hilo separado para no congelar la UI
            def tarea():
                t0 = time.perf_counter()
                ordenada, pasos = funcion(lista)
                tf = time.perf_counter()
                
                # Actualizar UI (usando after para ser thread-safe)
                self.after(0, lambda: finalizar_ordenamiento(lista, ordenada, pasos, tf - t0))

            threading.Thread(target=tarea, daemon=True).start()
            resultado_var.set("Procesando...")
            tiempo_var.set("...")
            pasos_var.set("...")

        def finalizar_ordenamiento(original: List[int], ordenada: List[int], pasos: List[List[int]], tiempo: float):
            resultado_var.set(" → ".join(map(str, ordenada)))
            tiempo_var.set(f"{tiempo*1000:.4f} ms")
            pasos_var.set(str(len(pasos)-1)) # Excluir el paso 0
            
            pasos_cache.clear()
            pasos_cache.extend(pasos)
            
            redibujar_base(original, ordenada)
            
            for c in controles: c.configure(state="normal")
            btn_ordenar.configure(state="normal")
            btn_animar.configure(state="normal")

        def animar_pasos():
            lista = parse_input()
            if not lista: return
            if not pasos_cache or len(pasos_cache) < 2:
                # Si no hay pasos guardados, calculamos
                ejecutar_ordenamiento()
                return

            self.animating = True
            for c in controles: c.configure(state="disabled")
            btn_ordenar.configure(state="disabled")
            btn_animar.configure(state="disabled")

            original = pasos_cache[0]
            velocidad = 250 if len(lista) <= 20 else 50
            total_pasos = len(pasos_cache)
            
            def frame_animacion(idx: int):
                if idx < total_pasos and self.animating:
                    pasos_var.set(f"Animando {idx}/{total_pasos-1}")
                    redibujar_base(original, pasos_cache[idx])
                    self.after(velocidad, frame_animacion, idx + 1)
                else:
                    self.animating = False
                    for c in controles: c.configure(state="normal")
                    btn_ordenar.configure(state="normal")
                    btn_animar.configure(state="normal")
                    pasos_var.set(str(total_pasos-1))
            
            frame_animacion(0)

        fr_botones = tk.Frame(izq, bg=c["panel"])
        fr_botones.pack(fill="x", padx=14, pady=(0, 10))
        btn_ordenar = ttk.Button(fr_botones, text="▶ ORDENAR", style="Accion.TButton", command=ejecutar_ordenamiento)
        btn_ordenar.pack(side="left", fill="x", expand=True, padx=(0, 4))
        btn_animar = ttk.Button(fr_botones, text="🎬 ANIMAR", style="Animar.TButton", command=animar_pasos)
        btn_animar.pack(side="left", fill="x", expand=True)

        for lbl, var in [("Resultado:", resultado_var), ("Tiempo:", tiempo_var), ("Pasos:", pasos_var)]:
            row = tk.Frame(izq, bg=c["panel"])
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=lbl, bg=c["panel"], fg=c["muted"], font=("Consolas", 8), width=10, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var, bg=c["panel"], fg=color_acento, font=("Consolas", 9, "bold"), wraplength=200, justify="left").pack(side="left")

        tk.Frame(izq, bg=c["borde"], height=1).pack(fill="x", padx=14, pady=10)

        tk.Label(izq, text="Ejemplo Aplicado:", bg=c["panel"], fg=color_acento, font=("Consolas", 10, "bold")).pack(anchor="w", padx=14, pady=(0, 2))
        tk.Label(izq, text=info["ejemplo_texto"], bg=c["panel"], fg=c["muted"], font=("Consolas", 9), wraplength=290, justify="left").pack(anchor="w", padx=14, pady=(0, 6))

        def cargar_ejemplo():
            if not self.animating:
                entrada_var.set(info["ejemplo_datos"])

        btn_ejemplo = ttk.Button(izq, text="📥 Cargar Datos de Ejemplo", style="Sec.TButton", command=cargar_ejemplo)
        btn_ejemplo.pack(anchor="w", padx=14, pady=(0, 14))
        controles.append(btn_ejemplo)

        der = tk.Frame(frame, bg=c["bg"])
        der.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)
        tk.Label(der, text="Visualización  (Estado Inicial → Estado Actual)", bg=c["bg"], fg=c["muted"], font=("Consolas", 9)).pack(anchor="w", padx=4, pady=(4, 4))

        canvas = tk.Canvas(der, bg=c["panel"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas_ref.append(canvas)
        canvas.create_text(350, 200, text="← Ingresa datos y presiona ORDENAR o ANIMAR", fill=c["muted"], font=("Consolas", 11))

        return frame

    def _tab_intercalacion(self, nb: ttk.Notebook):
        info = {
            "subtitulo": "Insertion Sort · O(n²) promedio · O(n) mejor caso",
            "ejemplo_texto": "Ordenamiento de calificaciones: Un maestro tiene calificaciones desordenadas que necesita ordenar para generar un cuadro de honor. Este método inserta cada elemento en su lugar ideal.",
            "ejemplo_datos": "95, 82, 100, 75, 88, 91, 60, 85, 78, 92"
        }
        self._crear_tab_algoritmo(nb, "Intercalación", "#7c5cbf", intercalacion, info)

    def _tab_mezcla_directa(self, nb: ttk.Notebook):
        info = {
            "subtitulo": "Merge Sort clásico · O(n log n) siempre",
            "ejemplo_texto": "Ranking de jugadores: Un torneo necesita clasificar puntajes. Con Mezcla Directa, se dividen los puntajes en mitades y se combinan recursivamente, garantizando un orden rápido.",
            "ejemplo_datos": "1200, 1550, 1100, 1800, 1340, 1450, 1600, 1250"
        }
        self._crear_tab_algoritmo(nb, "Mezcla Directa", "#5ca8bf", mezcla_directa, info)

    def _tab_mezcla_equilibrada(self, nb: ttk.Notebook):
        info = {
            "subtitulo": "Natural Merge Sort · O(n log k) donde k = número de runs",
            "ejemplo_texto": "Fusión de listas de contactos: Una empresa fusiona 3 bases de datos, cada una ya ordenada alfabéticamente por ID. Este método reconoce las secuencias ya ordenadas (runs) y las fusiona eficientemente.",
            "ejemplo_datos": "10, 20, 30, 5, 15, 25, 2, 12, 22"
        }
        self._crear_tab_algoritmo(nb, "Mezcla Equilibrada", "#bf5c8a", mezcla_equilibrada, info)

    def _tab_comparacion(self, nb: ttk.Notebook):
        c = self.colores
        frame = ttk.Frame(nb)
        nb.add(frame, text="Comparación")

        tk.Label(frame, text="Comparación de Rendimiento (Benchmarking)", bg=c["bg"], fg=c["acento"], font=("Consolas", 14, "bold")).pack(pady=(16, 4))
        tk.Label(frame, text="Calcula un promedio sobre múltiples ejecuciones para estabilizar la métrica", bg=c["bg"], fg=c["muted"], font=("Consolas", 9)).pack()
        tk.Frame(frame, bg=c["acento"], height=2).pack(fill="x", padx=20, pady=10)

        ctrl = tk.Frame(frame, bg=c["bg"])
        ctrl.pack(fill="x", padx=20, pady=4)
        tk.Label(ctrl, text="Datos:", bg=c["bg"], fg=c["texto"], font=("Consolas", 10)).pack(side="left")
        
        entrada_var = tk.StringVar()
        ent = tk.Entry(ctrl, textvariable=entrada_var, width=40, bg=c["borde"], fg=c["texto"], font=("Consolas", 10), insertbackground=c["texto"], relief="flat", highlightbackground=c["borde"], highlightcolor=c["acento"], highlightthickness=1)
        ent.pack(side="left", padx=8, ipady=4)

        ttk.Button(ctrl, text="🎲 Generar Aleatorio", style="Sec.TButton", command=lambda: entrada_var.set(",".join(map(str, random.sample(range(1, 1000), 50))))).pack(side="left", padx=4)

        tabla_frame = tk.Frame(frame, bg=c["bg"])
        tabla_frame.pack(fill="x", padx=20, pady=10)

        algos = [
            ("Intercalación", intercalacion, "O(n²)", "Sí"),
            ("Mezcla Directa", mezcla_directa, "O(n log n)", "Sí"),
            ("Mezcla Equilibrada", mezcla_equilibrada, "O(n log k)", "Sí"),
        ]
        colores_alg = [c["acento"], c["acento2"], c["acento3"]]

        hdr = tk.Frame(tabla_frame, bg=c["borde"])
        hdr.pack(fill="x", pady=(0, 2))
        for txt, w in zip(["Algoritmo", "Tiempo Prom. (ms)", "Pasos", "Complejidad"], [180, 150, 80, 160]):
            tk.Label(hdr, text=txt, bg=c["borde"], fg=c["muted"], font=("Consolas", 9, "bold"), width=w//8, anchor="w", padx=10, pady=6).pack(side="left")

        vars_tiempo: List[tk.StringVar] = []
        vars_pasos: List[tk.StringVar] = []

        for i, (nombre, _, comp, _) in enumerate(algos):
            row = tk.Frame(tabla_frame, bg=c["panel"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=nombre, bg=c["panel"], fg=colores_alg[i], font=("Consolas", 10, "bold"), width=180//8, anchor="w", padx=10, pady=8).pack(side="left")
            t_var, p_var = tk.StringVar(value="—"), tk.StringVar(value="—")
            vars_tiempo.append(t_var)
            vars_pasos.append(p_var)
            tk.Label(row, textvariable=t_var, bg=c["panel"], fg=c["texto"], font=("Consolas", 10), width=150//8, anchor="w", padx=10).pack(side="left")
            tk.Label(row, textvariable=p_var, bg=c["panel"], fg=c["texto"], font=("Consolas", 10), width=80//8, anchor="w", padx=10).pack(side="left")
            tk.Label(row, text=comp, bg=c["panel"], fg=c["amarillo"], font=("Consolas", 10), width=160//8, anchor="w", padx=10).pack(side="left")

        ganador_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=ganador_var, bg=c["bg"], fg=c["verde"], font=("Consolas", 11, "bold")).pack(pady=4)
        
        btn_comparar = ttk.Button(frame, text="▶ COMPARAR CON PRECISIÓN", style="Accion.TButton")
        btn_comparar.pack(pady=8)

        tk.Frame(frame, bg=c["borde"], height=1).pack(fill="x", padx=20, pady=4)

        tk.Label(frame, text="Tiempos comparativos (ms)", bg=c["bg"], fg=c["muted"], font=("Consolas", 8)).pack()
        canvas_comp = tk.Canvas(frame, bg=c["panel"], height=160, highlightthickness=0)
        canvas_comp.pack(fill="both", expand=True, padx=20, pady=(4, 14))

        def comparar():
            raw = entrada_var.get().strip()
            if not raw: return
            try: lista = [int(x.strip()) for x in raw.split(",") if x.strip()]
            except ValueError: return
            if len(lista) < 2: return

            btn_comparar.configure(state="disabled")
            ganador_var.set("Procesando Benchmark...")

            def tarea_benchmark():
                tiempos_promedio = []
                num_runs = 50 if len(lista) <= 50 else 10 # Adaptar iteraciones

                for i, (_, func, _, _) in enumerate(algos):
                    # Benchmark puro con timeit (solo la logica pura, ignorando re-crear arrays por overhead de py)
                    def run_func():
                        func(lista[:])
                    
                    t_total = timeit.timeit(run_func, number=num_runs)
                    t_promedio = (t_total / num_runs) * 1000
                    tiempos_promedio.append(t_promedio)
                    
                    # Obtenemos los pasos ejecutando una vez mas
                    _, pasos = func(lista[:])
                    
                    # Actualizar ui
                    self.after(0, lambda idx=i, t=t_promedio, p=len(pasos)-1: [vars_tiempo[idx].set(f"{t:.4f}"), vars_pasos[idx].set(str(p))])

                self.after(0, lambda: finalizar_benchmark(tiempos_promedio))

            def finalizar_benchmark(tiempos: List[float]):
                mejor_idx = tiempos.index(min(tiempos))
                ganador_var.set(f"✓ Más rápido en promedio ({len(lista)} items): {algos[mejor_idx][0]}")
                dibujar_barras_comparacion(canvas_comp, tiempos, colores_alg, [a[0] for a in algos])
                btn_comparar.configure(state="normal")

            threading.Thread(target=tarea_benchmark, daemon=True).start()

        btn_comparar.configure(command=comparar)

if __name__ == "__main__":
    app = App()
    app.mainloop()
