"""
╔══════════════════════════════════════════════════════════════════════╗
║        RECORRIDO DE ESTADOS DE MÉXICO — GRAFOS CON COSTOS           ║
║  7 estados del sureste mexicano conectados por carretera (km)       ║
╚══════════════════════════════════════════════════════════════════════╝

Estados elegidos (Sureste / Península de Yucatán + vecinos):
  1. Yucatán        (MID)
  2. Campeche       (CAM)
  3. Quintana Roo   (QRO)
  4. Tabasco        (TAB)
  5. Chiapas        (CHS)
  6. Veracruz       (VER)
  7. Oaxaca         (OAX)

Conexiones (costo = km aprox. por carretera):
  MID ↔ CAM   :  197
  MID ↔ QRO   :  320
  CAM ↔ QRO   :  378
  CAM ↔ TAB   :  444
  TAB ↔ CHS   :  300
  TAB ↔ VER   :  390
  CHS ↔ OAX   :  600
  VER ↔ OAX   :  450
  OAX ↔ CAM   :  950   ← ruta larga de respaldo
  VER ↔ CHS   :  710
"""

import tkinter as tk
from tkinter import ttk
import math
import itertools
from collections import defaultdict

# ══════════════════════════════════════════════════════════════════
#  DATOS DEL GRAFO
# ══════════════════════════════════════════════════════════════════

ESTADOS = {
    "MID": "Yucatán",
    "CAM": "Campeche",
    "QRO": "Quintana Roo",
    "TAB": "Tabasco",
    "CHS": "Chiapas",
    "VER": "Veracruz",
    "OAX": "Oaxaca",
}

# (nodo_a, nodo_b, costo_km)
ARISTAS = [
    ("MID", "CAM", 197),
    ("MID", "QRO", 320),
    ("CAM", "QRO", 378),
    ("CAM", "TAB", 444),
    ("TAB", "CHS", 300),
    ("TAB", "VER", 390),
    ("CHS", "OAX", 600),
    ("VER", "OAX", 450),
    ("OAX", "CAM", 950),
    ("VER", "CHS", 710),
]

# Posiciones en canvas (x, y) — aproximación geográfica
POSICIONES = {
    "MID": (680, 130),
    "CAM": (530, 210),
    "QRO": (720, 260),
    "TAB": (390, 290),
    "CHS": (310, 410),
    "VER": (230, 300),
    "OAX": (200, 430),
}

# ══════════════════════════════════════════════════════════════════
#  MODELO DE GRAFO
# ══════════════════════════════════════════════════════════════════

class GrafoMexico:
    def __init__(self):
        self.nodos = list(ESTADOS.keys())
        self.adyacencia = defaultdict(dict)
        for a, b, costo in ARISTAS:
            self.adyacencia[a][b] = costo
            self.adyacencia[b][a] = costo

    def vecinos(self, nodo):
        return self.adyacencia[nodo]

    def costo(self, a, b):
        return self.adyacencia[a].get(b, None)

    # ── a) Recorrido sin repetir (Hamilton path / DFS exhaustivo) ──
    def recorrer_sin_repetir(self, inicio="MID"):
        """Encuentra TODOS los caminos hamiltonianos desde 'inicio'."""
        resultados = []

        def dfs(actual, visitados, camino, costo_acum):
            visitados.add(actual)
            camino.append(actual)
            if len(visitados) == len(self.nodos):
                resultados.append((list(camino), costo_acum))
            else:
                for vecino, costo in self.adyacencia[actual].items():
                    if vecino not in visitados:
                        dfs(vecino, visitados, camino, costo_acum + costo)
            camino.pop()
            visitados.remove(actual)

        dfs(inicio, set(), [], 0)
        # Ordenar por costo
        resultados.sort(key=lambda x: x[1])
        return resultados

    # ── b) Recorrido repitiendo al menos uno (DFS, máx profundidad) ─
    def recorrer_con_repeticion(self, inicio="MID", max_pasos=9):
        """
        Visita los 7 estados repitiendo al menos uno.
        Se permite revisar nodos ya visitados.  Busca rutas donde:
          - Se visitan todos los nodos (con repetidos)
          - total de pasos > 7  (garantiza al menos 1 repetición)
        Limita la búsqueda a max_pasos para no explotar el espacio.
        """
        resultados = []
        todos = set(self.nodos)

        def dfs(actual, visitados_set, camino, costo_acum, pasos):
            camino.append(actual)
            visitados_set.add(actual)

            if visitados_set == todos and pasos >= 8:   # ≥8 pasos → al menos 1 repetición
                resultados.append((list(camino), costo_acum))
            elif pasos < max_pasos:
                for vecino, costo in self.adyacencia[actual].items():
                    dfs(vecino, set(visitados_set), camino,
                        costo_acum + costo, pasos + 1)

            camino.pop()

        dfs(inicio, set(), [], 0, 1)
        resultados.sort(key=lambda x: x[1])
        # Quitar duplicados exactos de camino
        seen = set()
        unique = []
        for r in resultados:
            key = tuple(r[0])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique[:20]   # top 20 rutas más baratas


# ══════════════════════════════════════════════════════════════════
#  COLORES Y ESTILOS
# ══════════════════════════════════════════════════════════════════

BG        = "#0b1523"
PANEL     = "#0f2035"
CARD      = "#112845"
ACCENT    = "#f4a261"
ACCENT2   = "#48cae4"
GREEN     = "#06d6a0"
RED       = "#ef476f"
YELLOW    = "#ffd166"
WHITE     = "#e8f4fd"
GRAY      = "#1e3a5f"
NODE_CLR  = "#1a4a7a"
NODE_HL   = "#e76f51"
EDGE_CLR  = "#2c5f8a"
EDGE_HL   = "#48cae4"
PATH_CLR  = "#f4a261"

FONT_T  = ("Georgia", 14, "bold")
FONT_B  = ("Courier New", 11, "bold")
FONT_N  = ("Courier New", 10)
FONT_S  = ("Courier New", 9)

# ══════════════════════════════════════════════════════════════════
#  APLICACIÓN
# ══════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🗺  Recorrido de Estados de México — Grafos")
        self.configure(bg=BG)
        self.geometry("1300x820")
        self.resizable(True, True)

        self.grafo = GrafoMexico()
        self.resultado_a = []   # rutas sin repetir
        self.resultado_b = []   # rutas con repetición
        self.ruta_activa = []   # ruta dibujada en canvas
        self.modo_ruta   = ""

        self._build_ui()
        self._draw_graph()
        self._mostrar_relaciones()

    # ── CONSTRUCCIÓN UI ───────────────────────────────────────────

    def _build_ui(self):
        # ---- TÍTULO ----
        hdr = tk.Frame(self, bg=BG, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text="◈  RECORRIDO DE 7 ESTADOS DE MÉXICO  ◈",
                 font=("Georgia", 16, "bold"), fg=ACCENT, bg=BG).pack()
        tk.Label(hdr,
                 text="Sureste mexicano · Costos en kilómetros por carretera",
                 font=("Courier New", 10), fg=ACCENT2, bg=BG).pack()

        # ---- CUERPO ----
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Canvas del grafo
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(left, bg=BG, bd=0,
                                highlightthickness=1,
                                highlightbackground=ACCENT2)
        self.canvas.pack(fill="both", expand=True)

        # Panel derecho
        right = tk.Frame(body, bg=PANEL, width=420, padx=10, pady=10)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_panel(right)

        # ---- STATUS ----
        bot = tk.Frame(self, bg=GRAY, padx=8, pady=4)
        bot.pack(fill="x")
        self.lbl_status = tk.Label(bot, text="▸ Listo. Usa los botones del panel.",
                                   font=FONT_N, fg=GREEN, bg=GRAY,
                                   anchor="w", wraplength=1200)
        self.lbl_status.pack(fill="x")

    def _build_panel(self, p):
        def section(txt):
            tk.Label(p, text=f"── {txt} ──",
                     font=("Courier New", 10, "bold"),
                     fg=ACCENT2, bg=PANEL).pack(anchor="w", pady=(10, 2))

        def btn(txt, cmd, color=ACCENT):
            tk.Button(p, text=txt, command=cmd,
                      bg=GRAY, fg=color, font=FONT_N,
                      relief="flat", bd=0, padx=6, pady=3,
                      activebackground=ACCENT,
                      activeforeground=BG,
                      cursor="hand2").pack(fill="x", pady=2)

        tk.Label(p, text="🗺 PANEL DE CONTROL",
                 font=FONT_T, fg=ACCENT, bg=PANEL).pack(pady=(0, 4))

        section("Inciso a) Sin repetir nodos")
        btn("▶  Calcular rutas sin repetir", self._calc_sin_repetir, GREEN)
        btn("◀  Ver mejor ruta (mín costo)",  self._ver_mejor_sin_rep, ACCENT2)

        section("Inciso b) Con al menos 1 repetición")
        btn("▶  Calcular rutas con repetición", self._calc_con_rep, YELLOW)
        btn("◀  Ver mejor ruta (mín costo)",    self._ver_mejor_con_rep, ACCENT)

        section("c) Costos totales")
        btn("💰  Mostrar costos",  self._mostrar_costos, ACCENT)

        section("e) Estados y relaciones")
        btn("🔗  Mostrar tabla de relaciones", self._mostrar_relaciones, WHITE)
        btn("↺  Limpiar ruta del grafo",       self._limpiar_ruta, RED)

        # ---- RESULTADOS ----
        tk.Label(p, text="── Resultados ──",
                 font=("Courier New", 10, "bold"),
                 fg=ACCENT2, bg=PANEL).pack(anchor="w", pady=(12, 2))

        frame_txt = tk.Frame(p, bg=PANEL)
        frame_txt.pack(fill="both", expand=True)
        sc = tk.Scrollbar(frame_txt)
        sc.pack(side="right", fill="y")
        self.txt = tk.Text(frame_txt, bg=CARD, fg=WHITE,
                           font=("Courier New", 9),
                           insertbackground=WHITE,
                           selectbackground=ACCENT,
                           yscrollcommand=sc.set,
                           relief="flat", bd=0, wrap="word")
        self.txt.pack(fill="both", expand=True)
        sc.config(command=self.txt.yview)

        # tags de colores
        self.txt.tag_config("hdr",    foreground=ACCENT,  font=("Courier New", 9, "bold"))
        self.txt.tag_config("green",  foreground=GREEN)
        self.txt.tag_config("yellow", foreground=YELLOW)
        self.txt.tag_config("cyan",   foreground=ACCENT2)
        self.txt.tag_config("red",    foreground=RED)
        self.txt.tag_config("white",  foreground=WHITE)

    # ── DIBUJADO DEL GRAFO ────────────────────────────────────────

    R = 26

    def _draw_graph(self, ruta=None):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width() or 860
        H = c.winfo_height() or 700

        # fondo con puntos
        for x in range(0, W, 40):
            for y in range(0, H, 40):
                c.create_oval(x-1, y-1, x+1, y+1, fill="#162840", outline="")

        # construir set de aristas en ruta activa
        ruta_edges = set()
        if ruta and len(ruta) > 1:
            for i in range(len(ruta)-1):
                ruta_edges.add((ruta[i], ruta[i+1]))
                ruta_edges.add((ruta[i+1], ruta[i]))

        # Aristas
        for a, b, costo in ARISTAS:
            x1, y1 = POSICIONES[a]
            x2, y2 = POSICIONES[b]
            en_ruta = (a, b) in ruta_edges or (b, a) in ruta_edges
            clr  = PATH_CLR if en_ruta else EDGE_CLR
            w    = 4 if en_ruta else 2
            c.create_line(x1, y1, x2, y2, fill=clr, width=w)
            # etiqueta de costo
            mx, my = (x1+x2)/2, (y1+y2)/2
            offset_x = 8 if x2 > x1 else -8
            offset_y = -10
            c.create_rectangle(mx+offset_x-18, my+offset_y-8,
                                mx+offset_x+18, my+offset_y+8,
                                fill=CARD, outline=clr, width=1)
            c.create_text(mx+offset_x, my+offset_y,
                          text=str(costo), fill=clr,
                          font=("Courier New", 8, "bold"))

        # Nodos
        for nodo, (x, y) in POSICIONES.items():
            en_ruta_nodo = ruta and nodo in ruta
            fill    = NODE_HL if en_ruta_nodo else NODE_CLR
            outline = PATH_CLR if en_ruta_nodo else ACCENT2
            ow      = 3 if en_ruta_nodo else 2
            c.create_oval(x-self.R, y-self.R, x+self.R, y+self.R,
                          fill=fill, outline=outline, width=ow)
            c.create_text(x, y-5, text=nodo,
                          fill=WHITE, font=("Courier New", 9, "bold"))
            nombre = ESTADOS[nodo].split()[0]  # solo primera palabra
            c.create_text(x, y+9, text=nombre,
                          fill=ACCENT2, font=("Courier New", 7))

        # Leyenda
        c.create_rectangle(10, 10, 200, 80, fill=CARD, outline=ACCENT2, width=1)
        c.create_text(105, 25, text="LEYENDA", fill=ACCENT,
                      font=("Courier New", 9, "bold"))
        c.create_line(20, 40, 60, 40, fill=EDGE_CLR, width=2)
        c.create_text(120, 40, text="Carretera (km)", fill=WHITE,
                      font=("Courier New", 8))
        c.create_line(20, 58, 60, 58, fill=PATH_CLR, width=4)
        c.create_text(115, 58, text="Ruta activa", fill=PATH_CLR,
                      font=("Courier New", 8))

        # Si hay ruta, dibujar orden con flechas numeradas
        if ruta and len(ruta) > 1:
            for i in range(len(ruta)-1):
                a, b = ruta[i], ruta[i+1]
                x1, y1 = POSICIONES[a]
                x2, y2 = POSICIONES[b]
                dx, dy = x2-x1, y2-y1
                dist = math.hypot(dx, dy)
                if dist == 0: continue
                ux, uy = dx/dist, dy/dist
                mx = x1 + dx*0.5
                my = y1 + dy*0.5
                c.create_oval(mx-9, my-9, mx+9, my+9,
                              fill=ACCENT, outline=BG, width=2)
                c.create_text(mx, my, text=str(i+1),
                              fill=BG, font=("Courier New", 8, "bold"))

    def _limpiar_ruta(self):
        self.ruta_activa = []
        self._draw_graph()
        self._status("Ruta limpiada del grafo.", ACCENT2)

    # ── OPERACIONES ───────────────────────────────────────────────

    def _calc_sin_repetir(self):
        self._status("Calculando rutas sin repetir...", YELLOW)
        self.update()
        self.resultado_a = self.grafo.recorrer_sin_repetir("MID")
        self._write_resultados_a()
        self._status(f"✔  {len(self.resultado_a)} rutas hamiltonianas encontradas.", GREEN)

    def _write_resultados_a(self):
        self.txt.delete("1.0", "end")
        t = self.txt
        t.insert("end", "═══ INCISO a) SIN REPETIR NODOS ═══\n", "hdr")
        t.insert("end", f"Inicio: MID (Yucatán) | {len(self.resultado_a)} rutas\n\n", "cyan")
        for i, (camino, costo) in enumerate(self.resultado_a[:10], 1):
            ruta_str = " → ".join(camino)
            t.insert("end", f"#{i:2}  {ruta_str}\n", "green")
            t.insert("end", f"     Costo total: {costo:,} km\n\n", "white")
        if len(self.resultado_a) > 10:
            t.insert("end", f"... y {len(self.resultado_a)-10} rutas más.\n", "yellow")

    def _ver_mejor_sin_rep(self):
        if not self.resultado_a:
            self._calc_sin_repetir()
        if not self.resultado_a:
            self._status("No se encontraron rutas.", RED)
            return
        mejor = self.resultado_a[0]
        self.ruta_activa = mejor[0]
        self._draw_graph(ruta=self.ruta_activa)
        self.txt.delete("1.0", "end")
        t = self.txt
        t.insert("end", "═══ MEJOR RUTA SIN REPETIR ═══\n\n", "hdr")
        ruta_str = " → ".join(mejor[0])
        t.insert("end", f"Ruta: {ruta_str}\n\n", "green")
        t.insert("end", f"Costo total: {mejor[1]:,} km\n\n", "yellow")
        t.insert("end", "Detalle por tramo:\n", "cyan")
        for i in range(len(mejor[0])-1):
            a, b = mejor[0][i], mejor[0][i+1]
            c = self.grafo.costo(a, b)
            t.insert("end", f"  {a} → {b} : {c:,} km\n", "white")
        self._status(f"✔ Mejor ruta sin repetir: {mejor[1]:,} km", GREEN)

    def _calc_con_rep(self):
        self._status("Calculando rutas con repetición...", YELLOW)
        self.update()
        self.resultado_b = self.grafo.recorrer_con_repeticion("MID")
        self._write_resultados_b()
        self._status(f"✔  {len(self.resultado_b)} rutas con repetición encontradas.", GREEN)

    def _write_resultados_b(self):
        self.txt.delete("1.0", "end")
        t = self.txt
        t.insert("end", "═══ INCISO b) CON AL MENOS 1 REPETICIÓN ═══\n", "hdr")
        t.insert("end", f"Inicio: MID (Yucatán) | Top {len(self.resultado_b)}\n\n", "cyan")
        for i, (camino, costo) in enumerate(self.resultado_b[:10], 1):
            ruta_str = " → ".join(camino)
            repetidos = [n for n in set(camino) if camino.count(n) > 1]
            t.insert("end", f"#{i:2}  {ruta_str}\n", "yellow")
            t.insert("end", f"     Repetidos: {repetidos}\n", "red")
            t.insert("end", f"     Costo total: {costo:,} km\n\n", "white")

    def _ver_mejor_con_rep(self):
        if not self.resultado_b:
            self._calc_con_rep()
        if not self.resultado_b:
            self._status("No se encontraron rutas.", RED)
            return
        mejor = self.resultado_b[0]
        self.ruta_activa = mejor[0]
        self._draw_graph(ruta=self.ruta_activa)
        self.txt.delete("1.0", "end")
        t = self.txt
        t.insert("end", "═══ MEJOR RUTA CON REPETICIÓN ═══\n\n", "hdr")
        ruta_str = " → ".join(mejor[0])
        repetidos = [n for n in set(mejor[0]) if mejor[0].count(n) > 1]
        t.insert("end", f"Ruta: {ruta_str}\n\n", "yellow")
        t.insert("end", f"Nodos repetidos: {repetidos}\n\n", "red")
        t.insert("end", f"Costo total: {mejor[1]:,} km\n\n", "yellow")
        t.insert("end", "Detalle por tramo:\n", "cyan")
        for i in range(len(mejor[0])-1):
            a, b = mejor[0][i], mejor[0][i+1]
            c = self.grafo.costo(a, b)
            t.insert("end", f"  {a} → {b} : {c:,} km\n", "white")
        self._status(f"✔ Mejor ruta con repetición: {mejor[1]:,} km", GREEN)

    def _mostrar_costos(self):
        if not self.resultado_a:
            self.resultado_a = self.grafo.recorrer_sin_repetir("MID")
        if not self.resultado_b:
            self.resultado_b = self.grafo.recorrer_con_repeticion("MID")

        self.txt.delete("1.0", "end")
        t = self.txt

        t.insert("end", "═══ INCISO c) COSTOS TOTALES ═══\n\n", "hdr")

        if self.resultado_a:
            mejor_a = self.resultado_a[0]
            t.insert("end", "▸ Inciso a) — Sin repetir nodos:\n", "cyan")
            ruta_a = " → ".join(mejor_a[0])
            t.insert("end", f"  Ruta:  {ruta_a}\n", "green")
            t.insert("end", f"  Costo: {mejor_a[1]:,} km\n\n", "yellow")
        else:
            t.insert("end", "  (Calcular primero inciso a)\n\n", "red")

        if self.resultado_b:
            mejor_b = self.resultado_b[0]
            t.insert("end", "▸ Inciso b) — Con al menos 1 repetición:\n", "cyan")
            ruta_b = " → ".join(mejor_b[0])
            t.insert("end", f"  Ruta:  {ruta_b}\n", "yellow")
            t.insert("end", f"  Costo: {mejor_b[1]:,} km\n\n", "yellow")
        else:
            t.insert("end", "  (Calcular primero inciso b)\n\n", "red")

        if self.resultado_a and self.resultado_b:
            diff = self.resultado_b[0][1] - self.resultado_a[0][1]
            t.insert("end", f"Diferencia de costo (b - a): +{diff:,} km\n", "red")

        self._status("Costos mostrados.", GREEN)

    def _mostrar_relaciones(self):
        self.txt.delete("1.0", "end")
        t = self.txt
        t.insert("end", "═══ INCISO e) ESTADOS Y RELACIONES ═══\n\n", "hdr")

        t.insert("end", "ESTADOS DEL GRAFO:\n", "cyan")
        for cod, nombre in ESTADOS.items():
            t.insert("end", f"  [{cod}]  {nombre}\n", "white")

        t.insert("end", "\nCONEXIONES (ARISTAS):\n", "cyan")
        t.insert("end", f"  {'Origen':<6}  {'Destino':<6}  {'Costo':>6}\n", "yellow")
        t.insert("end", "  " + "─"*24 + "\n", "yellow")
        for a, b, costo in sorted(ARISTAS, key=lambda x: x[2]):
            t.insert("end", f"  {a:<6}  {b:<6}  {costo:>5} km\n", "white")

        t.insert("end", "\nLISTA DE ADYACENCIA:\n", "cyan")
        for nodo in self.grafo.nodos:
            vecinos = self.grafo.vecinos(nodo)
            vec_str = "  ".join([f"{v}({c})" for v, c in sorted(vecinos.items())])
            t.insert("end", f"  {nodo}: {vec_str}\n", "white")

        t.insert("end", f"\nTotal vértices: {len(ESTADOS)}\n", "green")
        t.insert("end", f"Total aristas:  {len(ARISTAS)}\n", "green")

    def _status(self, msg, color=GREEN):
        self.lbl_status.config(text=f"▸ {msg}", fg=color)

    def run(self):
        # Esperar a que el canvas tenga tamaño real
        self.after(100, self._draw_graph)
        self.mainloop()


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.run()
