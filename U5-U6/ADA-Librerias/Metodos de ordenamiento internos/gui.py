"""
gui.py
======
Interfaz gráfica para la librería de métodos de ordenamiento externos.
Requiere que 'metodos_de_ordenamiento_externos.py' esté en la misma carpeta.

Ejecutar:
    python gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import random

# ── Importar la librería de ordenamiento ──────────────────────────────────────
from Metodos_de_ordenamiento_interno import (
    bubble_sort,
    insertion_sort,
    selection_sort,
    shell_sort,
    quick_sort,
    heap_sort,
    radix_sort,
    comparar_algoritmos,
)

ALGORITMOS = {
    "Burbuja":    bubble_sort,
    "Inserción":  insertion_sort,
    "Selección":  selection_sort,
    "Shell Sort": shell_sort,
    "Quick Sort": quick_sort,
    "Heap Sort":  heap_sort,
    "Radix Sort": radix_sort,
}

# ── Paleta de colores ─────────────────────────────────────────────────────────
BG        = "#0f1117"
PANEL     = "#1a1d27"
CARD      = "#22263a"
ACCENT    = "#00e5ff"
ACCENT2   = "#7c4dff"
TEXT      = "#e8eaf6"
TEXT_DIM  = "#6b7394"
SUCCESS   = "#00e676"
WARNING   = "#ffab40"
FONT_MONO = ("Courier New", 11)
FONT_UI   = ("Segoe UI", 11)
FONT_H1   = ("Segoe UI", 16, "bold")
FONT_H2   = ("Segoe UI", 12, "bold")


# ── Aplicación principal ───────────────────────────────────────────────────────
class SortingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Métodos de Ordenamiento Internos")
        self.geometry("860x700")
        self.minsize(760, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._build_header()
        self._build_input_panel()
        self._build_algo_panel()
        self._build_output_panel()
        self._build_benchmark_panel()
        self._build_footer()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG, pady=18)
        hdr.pack(fill="x", padx=30)

        tk.Label(hdr, text="⟨ SORT ⟩", font=("Courier New", 22, "bold"),
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(hdr, text="  Métodos de Ordenamiento Internos",
                 font=FONT_H1, fg=TEXT, bg=BG).pack(side="left", padx=10)

        sep = tk.Frame(self, bg=ACCENT, height=2)
        sep.pack(fill="x", padx=30)

    # ── Panel de entrada ──────────────────────────────────────────────────────
    def _build_input_panel(self):
        frame = tk.LabelFrame(self, text="  Datos de entrada  ", font=FONT_H2,
                              fg=ACCENT, bg=PANEL, bd=1, relief="flat",
                              labelanchor="nw")
        frame.pack(fill="x", padx=30, pady=(20, 8))

        inner = tk.Frame(frame, bg=PANEL, pady=10)
        inner.pack(fill="x", padx=14)

        tk.Label(inner, text="Números (separados por comas):",
                 font=FONT_UI, fg=TEXT_DIM, bg=PANEL).pack(anchor="w")

        entry_row = tk.Frame(inner, bg=PANEL)
        entry_row.pack(fill="x", pady=(4, 0))

        self.entry = tk.Entry(entry_row, font=FONT_MONO, bg=CARD, fg=TEXT,
                              insertbackground=ACCENT, relief="flat",
                              bd=0, highlightthickness=2,
                              highlightcolor=ACCENT, highlightbackground=CARD)
        self.entry.pack(side="left", fill="x", expand=True, ipady=7, ipadx=8)
        self.entry.insert(0, "64, 34, 25, 12, 22, 11, 90, 3, 77, 50")

        btn_random = self._btn(entry_row, "🎲 Aleatorio", self._generar_random,
                               ACCENT2, width=12)
        btn_random.pack(side="left", padx=(8, 0))

        btn_clear = self._btn(entry_row, "✕ Limpiar", self._limpiar_todo,
                              "#444", width=10)
        btn_clear.pack(side="left", padx=(6, 0))

    # ── Panel de algoritmos ───────────────────────────────────────────────────
    def _build_algo_panel(self):
        frame = tk.LabelFrame(self, text="  Algoritmo  ", font=FONT_H2,
                              fg=ACCENT, bg=PANEL, bd=1, relief="flat",
                              labelanchor="nw")
        frame.pack(fill="x", padx=30, pady=8)

        inner = tk.Frame(frame, bg=PANEL, pady=10)
        inner.pack(fill="x", padx=14)

        # Selector de algoritmo
        sel_row = tk.Frame(inner, bg=PANEL)
        sel_row.pack(fill="x")

        tk.Label(sel_row, text="Selecciona un método:",
                 font=FONT_UI, fg=TEXT_DIM, bg=PANEL).pack(side="left")

        self.algo_var = tk.StringVar(value="Quick Sort")
        combo = ttk.Combobox(sel_row, textvariable=self.algo_var,
                             values=list(ALGORITMOS.keys()),
                             state="readonly", font=FONT_UI, width=18)
        combo.pack(side="left", padx=(10, 0))

        # Botón principal
        btn_sort = self._btn(sel_row, "▶  ORDENAR", self._ordenar,
                             ACCENT, fg_color=BG, width=14)
        btn_sort.pack(side="left", padx=(16, 0))

        # Info de complejidad
        self.info_label = tk.Label(inner, text="", font=("Courier New", 10),
                                   fg=ACCENT2, bg=PANEL)
        self.info_label.pack(anchor="w", pady=(8, 0))

        combo.bind("<<ComboboxSelected>>", self._mostrar_info)
        self._mostrar_info()

    # ── Panel de salida ───────────────────────────────────────────────────────
    def _build_output_panel(self):
        frame = tk.LabelFrame(self, text="  Resultado  ", font=FONT_H2,
                              fg=ACCENT, bg=PANEL, bd=1, relief="flat",
                              labelanchor="nw")
        frame.pack(fill="both", expand=True, padx=30, pady=8)

        inner = tk.Frame(frame, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=14, pady=10)

        # Métricas rápidas
        metrics = tk.Frame(inner, bg=PANEL)
        metrics.pack(fill="x", pady=(0, 8))

        self.lbl_tiempo = self._metric_label(metrics, "⏱ Tiempo", "—")
        self.lbl_n      = self._metric_label(metrics, "# Elementos", "—")
        self.lbl_algo   = self._metric_label(metrics, "Algoritmo", "—")

        # Texto de resultado
        txt_frame = tk.Frame(inner, bg=CARD, bd=0)
        txt_frame.pack(fill="both", expand=True)

        self.output = tk.Text(txt_frame, font=FONT_MONO, bg=CARD, fg=SUCCESS,
                              relief="flat", bd=0, wrap="word",
                              state="disabled", padx=10, pady=8,
                              cursor="arrow")
        scroll = tk.Scrollbar(txt_frame, command=self.output.yview,
                              bg=CARD, troughcolor=CARD,
                              activebackground=ACCENT)
        self.output.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.output.pack(fill="both", expand=True)

    # ── Panel de benchmark ────────────────────────────────────────────────────
    def _build_benchmark_panel(self):
        frame = tk.LabelFrame(self, text="  Benchmark (todos los algoritmos)  ",
                              font=FONT_H2, fg=ACCENT, bg=PANEL,
                              bd=1, relief="flat", labelanchor="nw")
        frame.pack(fill="x", padx=30, pady=(8, 12))

        inner = tk.Frame(frame, bg=PANEL, pady=10)
        inner.pack(fill="x", padx=14)

        ctrl = tk.Frame(inner, bg=PANEL)
        ctrl.pack(fill="x")

        tk.Label(ctrl, text="Tamaño:", font=FONT_UI, fg=TEXT_DIM,
                 bg=PANEL).pack(side="left")

        self.bench_n = tk.IntVar(value=1000)
        spin = tk.Spinbox(ctrl, from_=100, to=10000, increment=100,
                          textvariable=self.bench_n, width=7,
                          font=FONT_MONO, bg=CARD, fg=TEXT,
                          buttonbackground=CARD, relief="flat",
                          insertbackground=ACCENT)
        spin.pack(side="left", padx=(6, 0), ipady=4)

        btn_bench = self._btn(ctrl, "⚡ Ejecutar benchmark",
                              self._ejecutar_benchmark, WARNING, fg_color=BG,
                              width=22)
        btn_bench.pack(side="left", padx=(12, 0))

        self.bench_output = tk.Label(inner, text="", font=("Courier New", 10),
                                     fg=TEXT, bg=PANEL, justify="left",
                                     anchor="w")
        self.bench_output.pack(fill="x", pady=(8, 0))

    # ── Footer ────────────────────────────────────────────────────────────────
    def _build_footer(self):
        sep = tk.Frame(self, bg=TEXT_DIM, height=1)
        sep.pack(fill="x", padx=30)
        tk.Label(self, text="metodos_de_ordenamiento_externos.py  •  Python",
                 font=("Courier New", 9), fg=TEXT_DIM, bg=BG,
                 pady=6).pack()

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _ordenar(self):
        texto = self.entry.get().strip()
        if not texto:
            messagebox.showwarning("Sin datos", "Ingresa números separados por comas.")
            return

        try:
            numeros = [int(x.strip()) for x in texto.split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Error", "Solo se permiten números enteros separados por comas.")
            return

        if not numeros:
            return

        nombre = self.algo_var.get()
        funcion = ALGORITMOS[nombre]

        t0 = time.perf_counter()
        resultado = funcion(numeros)
        t1 = time.perf_counter()
        elapsed = (t1 - t0) * 1000  # ms

        self.lbl_tiempo.config(text=f"{elapsed:.4f} ms")
        self.lbl_n.config(text=str(len(numeros)))
        self.lbl_algo.config(text=nombre)

        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", f"Entrada  ({len(numeros)}): {numeros}\n\n")
        self.output.insert("end", f"Resultado({len(resultado)}): {resultado}\n")
        self.output.config(state="disabled")

    def _generar_random(self):
        n = random.randint(8, 20)
        nums = [random.randint(1, 999) for _ in range(n)]
        self.entry.delete(0, "end")
        self.entry.insert(0, ", ".join(map(str, nums)))

    def _limpiar_todo(self):
        self.entry.delete(0, "end")
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")
        self.lbl_tiempo.config(text="—")
        self.lbl_n.config(text="—")
        self.lbl_algo.config(text="—")
        self.bench_output.config(text="")

    def _ejecutar_benchmark(self):
        n = self.bench_n.get()
        self.bench_output.config(text="⏳ Ejecutando...", fg=WARNING)
        self.update()

        tiempos = comparar_algoritmos(n=n)
        ordenados = sorted(tiempos.items(), key=lambda x: x[1])

        lineas = []
        max_t = max(tiempos.values())
        for nombre, t in ordenados:
            barra_len = int((t / max_t) * 20) if max_t > 0 else 0
            barra = "█" * barra_len + "░" * (20 - barra_len)
            lineas.append(f"{nombre:<12}  {barra}  {t*1000:.3f} ms")

        self.bench_output.config(
            text="\n".join(lineas),
            fg=TEXT
        )

    def _mostrar_info(self, event=None):
        info = {
            "Burbuja":    "O(n²) tiempo  |  O(1) espacio  |  Estable",
            "Inserción":  "O(n²) tiempo  |  O(1) espacio  |  Estable",
            "Selección":  "O(n²) tiempo  |  O(1) espacio  |  No estable",
            "Shell Sort": "O(n log² n)   |  O(1) espacio  |  No estable",
            "Quick Sort": "O(n log n)    |  O(log n) esp. |  No estable",
            "Heap Sort":  "O(n log n)    |  O(1) espacio  |  No estable",
            "Radix Sort": "O(nk) tiempo  |  O(n) espacio  |  Estable",
        }
        nombre = self.algo_var.get()
        self.info_label.config(text=f"  ℹ  {info.get(nombre, '')}")

    # ── Helpers de UI ─────────────────────────────────────────────────────────
    def _btn(self, parent, text, command, color, fg_color=TEXT, width=None):
        kwargs = dict(text=text, command=command, font=("Segoe UI", 10, "bold"),
                      bg=color, fg=fg_color, activebackground=color,
                      activeforeground=fg_color, relief="flat", cursor="hand2",
                      padx=12, pady=6, bd=0)
        if width:
            kwargs["width"] = width
        return tk.Button(parent, **kwargs)

    def _metric_label(self, parent, titulo, valor):
        box = tk.Frame(parent, bg=CARD, padx=14, pady=6)
        box.pack(side="left", padx=(0, 10))
        tk.Label(box, text=titulo, font=("Segoe UI", 9),
                 fg=TEXT_DIM, bg=CARD).pack()
        lbl = tk.Label(box, text=valor, font=("Courier New", 12, "bold"),
                       fg=ACCENT, bg=CARD)
        lbl.pack()
        return lbl


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SortingApp()
    app.mainloop()
