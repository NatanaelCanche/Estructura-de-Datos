import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
import random

class Arista:
    _contador = 0

    def __init__(self, v, w, objeto=None, dirigida=False):
        Arista._contador += 1
        self.id = Arista._contador
        self.v = v          # vértice origen / extremo 1
        self.w = w          # vértice destino / extremo 2
        self.objeto = objeto
        self.dirigida = dirigida

    def __repr__(self):
        flecha = "→" if self.dirigida else "—"
        return f"e{self.id}({self.v}{flecha}{self.w})"


class Grafo:
    """Implementa TODAS las operaciones de las tres imágenes."""

    def __init__(self):
        self._vertices: dict[int, object] = {}   # id → objeto
        self._aristas:  dict[int, Arista] = {}   # id → Arista
        self._v_counter = 0

    # ── OPERACIONES GENERALES ──────────────────────────────────────

    def numVertices(self):
        return len(self._vertices)

    def numAristas(self):
        return len(self._aristas)

    def vertices(self):
        return list(self._vertices.keys())

    def aristas(self):
        return list(self._aristas.keys())

    def grado(self, v):
        return len(self.aristasIncidentes(v))

    def verticesAdyacentes(self, v):
        adyacentes = []
        for a in self._aristas.values():
            if a.v == v:
                adyacentes.append(a.w)
            elif a.w == v:
                adyacentes.append(a.v)
        return adyacentes

    def aristasIncidentes(self, v):
        return [aid for aid, a in self._aristas.items()
                if a.v == v or a.w == v]

    def verticesFinales(self, e):
        a = self._aristas.get(e)
        if a is None:
            return []
        return [a.v, a.w]

    def opuesto(self, v, e):
        a = self._aristas.get(e)
        if a is None:
            return None
        if a.v == v:
            return a.w
        if a.w == v:
            return a.v
        return None

    def esAdyacente(self, v, w):
        for a in self._aristas.values():
            if (a.v == v and a.w == w) or (a.v == w and a.w == v):
                return True
        return False

    # ── OPERACIONES CON ARISTAS DIRIGIDAS ─────────────────────────

    def aristasDirigidas(self):
        return [aid for aid, a in self._aristas.items() if a.dirigida]

    def aristasNodirigidas(self):
        return [aid for aid, a in self._aristas.items() if not a.dirigida]

    def gradoEnt(self, v):
        return sum(1 for a in self._aristas.values()
                   if a.dirigida and a.w == v)

    def gradoSalida(self, v):
        return sum(1 for a in self._aristas.values()
                   if a.dirigida and a.v == v)

    def aristasIncidentesEnt(self, v):
        return [aid for aid, a in self._aristas.items()
                if a.dirigida and a.w == v]

    def aristasIncidentesSal(self, v):
        return [aid for aid, a in self._aristas.items()
                if a.dirigida and a.v == v]

    def verticesAdyacentesEnt(self, v):
        return [a.v for a in self._aristas.values()
                if a.dirigida and a.w == v]

    def verticesAdyacentesSal(self, v):
        return [a.w for a in self._aristas.values()
                if a.dirigida and a.v == v]

    def destino(self, e):
        a = self._aristas.get(e)
        return a.w if a and a.dirigida else None

    def origen(self, e):
        a = self._aristas.get(e)
        return a.v if a and a.dirigida else None

    def esDirigida(self, e):
        a = self._aristas.get(e)
        return a.dirigida if a else False

    # ── OPERACIONES DE ACTUALIZACIÓN ──────────────────────────────

    def insertaArista(self, v, w, objeto=None):
        a = Arista(v, w, objeto, dirigida=False)
        self._aristas[a.id] = a
        return a.id

    def insertaAristaDirigida(self, v, w, objeto=None):
        a = Arista(v, w, objeto, dirigida=True)
        self._aristas[a.id] = a
        return a.id

    def insertaVertice(self, objeto=None):
        self._v_counter += 1
        vid = self._v_counter
        self._vertices[vid] = objeto
        return vid

    def eliminaVertice(self, v):
        if v not in self._vertices:
            return False
        incidentes = self.aristasIncidentes(v)
        for e in incidentes:
            del self._aristas[e]
        del self._vertices[v]
        return True

    def eliminaArista(self, e):
        if e in self._aristas:
            del self._aristas[e]
            return True
        return False

    def convierteNoDirigida(self, e):
        if e in self._aristas:
            self._aristas[e].dirigida = False
            return True
        return False

    def invierteDir(self, e):
        a = self._aristas.get(e)
        if a and a.dirigida:
            a.v, a.w = a.w, a.v
            return True
        return False

    def asignaDirDesde(self, e, v):
        a = self._aristas.get(e)
        if a:
            w = a.v if a.w == v else a.w
            a.v, a.w, a.dirigida = v, w, True
            return True
        return False

    def asignaDirA(self, e, v):
        a = self._aristas.get(e)
        if a:
            w = a.v if a.w == v else a.w
            a.v, a.w, a.dirigida = w, v, True
            return True
        return False

    def get_objeto_vertice(self, v):
        return self._vertices.get(v, f"V{v}")

    def get_objeto_arista(self, e):
        return self._aristas.get(e)


DARK_BG   = "#0d1b2a"
PANEL_BG  = "#112240"
ACCENT    = "#f4a261"
ACCENT2   = "#4cc9f0"
WHITE     = "#e0e7ff"
GREEN     = "#06d6a0"
RED       = "#ef233c"
GRAY      = "#1e3a5f"
NODE_CLR  = "#264653"
NODE_SEL  = "#e76f51"
EDGE_CLR  = "#4cc9f0"
EDGE_DIR  = "#f4a261"
FONT_MAIN = ("Courier New", 11)
FONT_BOLD = ("Courier New", 12, "bold")
FONT_TTL  = ("Courier New", 15, "bold")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("╠ OPERACIONES DE GRAFOS ╣")
        self.configure(bg=DARK_BG)
        self.geometry("1280x800")
        self.resizable(True, True)

        self.grafo = Grafo()
        self.pos: dict[int, tuple] = {}   # vid → (x, y)
        self.selected_v = None
        self.selected_e = None
        self.dragging   = None
        self.resultado   = ""

        self._build_ui()
        self._init_ejemplo()
        self._redraw()


    def _build_ui(self):
        top = tk.Frame(self, bg=DARK_BG, pady=6)
        top.pack(fill="x")
        tk.Label(top, text="◈ GRAFO TDA — OPERACIONES COMPLETAS ◈",
                 font=FONT_TTL, fg=ACCENT, bg=DARK_BG).pack()

     
        center = tk.Frame(self, bg=DARK_BG)
        center.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        
        self.canvas = tk.Canvas(center, bg=DARK_BG, bd=0,
                                highlightthickness=1,
                                highlightbackground=ACCENT2)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>",        self._on_click)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>",        self._on_right_click)

        
        right = tk.Frame(center, bg=PANEL_BG, width=370,
                         padx=10, pady=8)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_panel(right)


        bot = tk.Frame(self, bg=GRAY, padx=8, pady=4)
        bot.pack(fill="x")
        self.lbl_res = tk.Label(bot, text="▸ Resultado aparecerá aquí",
                                font=FONT_MAIN, fg=GREEN, bg=GRAY,
                                anchor="w", wraplength=1200, justify="left")
        self.lbl_res.pack(fill="x")

    def _build_panel(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",        background=PANEL_BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background=GRAY, foreground=WHITE,
                        font=("Courier New", 10, "bold"), padding=(8, 4))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", DARK_BG)])

        tab1 = tk.Frame(nb, bg=PANEL_BG)
        tab2 = tk.Frame(nb, bg=PANEL_BG)
        tab3 = tk.Frame(nb, bg=PANEL_BG)
        nb.add(tab1, text="🔵 Generales")
        nb.add(tab2, text="🟠 Dirigidas")
        nb.add(tab3, text="🟢 Actualizar")

        self._tab_generales(tab1)
        self._tab_dirigidas(tab2)
        self._tab_actualizar(tab3)

        # instrucciones
        tk.Label(parent, text=(
            "🖱  Clic izq: seleccionar  |  Arrastrar: mover\n"
            "Clic der: deseleccionar / menú"),
            font=("Courier New", 9), fg=ACCENT2, bg=PANEL_BG,
            justify="left").pack(pady=(6, 0))

        # indicadores
        ind = tk.Frame(parent, bg=PANEL_BG)
        ind.pack(fill="x", pady=(4, 0))
        self.lbl_sel_v = tk.Label(ind, text="Vértice sel: —",
                                  font=FONT_MAIN, fg=ACCENT, bg=PANEL_BG)
        self.lbl_sel_v.pack(anchor="w")
        self.lbl_sel_e = tk.Label(ind, text="Arista sel:  —",
                                  font=FONT_MAIN, fg=ACCENT2, bg=PANEL_BG)
        self.lbl_sel_e.pack(anchor="w")

    def _section(self, parent, title):
        tk.Label(parent, text=f"── {title} ──",
                 font=("Courier New", 10, "bold"),
                 fg=ACCENT2, bg=PANEL_BG).pack(anchor="w", pady=(8, 2))

    def _btn(self, parent, text, cmd, color=ACCENT):
        tk.Button(parent, text=text, command=cmd,
                  bg=GRAY, fg=color, font=FONT_MAIN,
                  relief="flat", bd=0, padx=4, pady=2,
                  activebackground=ACCENT, activeforeground=DARK_BG,
                  cursor="hand2").pack(fill="x", pady=1)

    def _tab_generales(self, tab):
        f = tk.Frame(tab, bg=PANEL_BG)
        f.pack(fill="both", expand=True)
        sc = tk.Scrollbar(f); sc.pack(side="right", fill="y")
        inner = tk.Canvas(f, bg=PANEL_BG, yscrollcommand=sc.set, bd=0,
                          highlightthickness=0)
        inner.pack(fill="both", expand=True)
        sc.config(command=inner.yview)
        p = tk.Frame(inner, bg=PANEL_BG)
        inner.create_window((0,0), window=p, anchor="nw")
        p.bind("<Configure>", lambda e: inner.configure(
            scrollregion=inner.bbox("all")))

        self._section(p, "Sin parámetros")
        self._btn(p, "numVertices()",     self._op_numVertices)
        self._btn(p, "numAristas()",      self._op_numAristas)
        self._btn(p, "vertices()",        self._op_vertices)
        self._btn(p, "aristas()",         self._op_aristas)

        self._section(p, "Con vértice seleccionado")
        self._btn(p, "grado(v)",              self._op_grado)
        self._btn(p, "verticesAdyacentes(v)", self._op_verticesAdyacentes)
        self._btn(p, "aristasIncidentes(v)",  self._op_aristasIncidentes)

        self._section(p, "Con arista seleccionada")
        self._btn(p, "verticesFinales(e)",    self._op_verticesFinales)

        self._section(p, "Vértice + arista seleccionados")
        self._btn(p, "opuesto(v, e)",         self._op_opuesto)

        self._section(p, "Dos vértices (pedir 2do)")
        self._btn(p, "esAdyacente(v, w)",     self._op_esAdyacente)

    def _tab_dirigidas(self, tab):
        f = tk.Frame(tab, bg=PANEL_BG)
        f.pack(fill="both", expand=True)
        sc = tk.Scrollbar(f); sc.pack(side="right", fill="y")
        inner = tk.Canvas(f, bg=PANEL_BG, yscrollcommand=sc.set, bd=0,
                          highlightthickness=0)
        inner.pack(fill="both", expand=True)
        sc.config(command=inner.yview)
        p = tk.Frame(inner, bg=PANEL_BG)
        inner.create_window((0,0), window=p, anchor="nw")
        p.bind("<Configure>", lambda e: inner.configure(
            scrollregion=inner.bbox("all")))

        self._section(p, "Listas globales")
        self._btn(p, "aristasDirigidas()",   self._op_aristasDirigidas,   ACCENT)
        self._btn(p, "aristasNodirigidas()", self._op_aristasNodirigidas, ACCENT2)

        self._section(p, "Con vértice seleccionado")
        self._btn(p, "gradoEnt(v)",              self._op_gradoEnt)
        self._btn(p, "gradoSalida(v)",           self._op_gradoSalida)
        self._btn(p, "aristasIncidentesEnt(v)",  self._op_aristasIncidentesEnt)
        self._btn(p, "aristasIncidentesSal(v)",  self._op_aristasIncidentesSal)
        self._btn(p, "verticesAdyacentesEnt(v)", self._op_verticesAdyacentesEnt)
        self._btn(p, "verticesAdyacentesSal(v)", self._op_verticesAdyacentesSal)

        self._section(p, "Con arista seleccionada")
        self._btn(p, "destino(e)",   self._op_destino)
        self._btn(p, "origen(e)",    self._op_origen)
        self._btn(p, "esDirigida(e)",self._op_esDirigida)

    def _tab_actualizar(self, tab):
        f = tk.Frame(tab, bg=PANEL_BG)
        f.pack(fill="both", expand=True)
        sc = tk.Scrollbar(f); sc.pack(side="right", fill="y")
        inner = tk.Canvas(f, bg=PANEL_BG, yscrollcommand=sc.set, bd=0,
                          highlightthickness=0)
        inner.pack(fill="both", expand=True)
        sc.config(command=inner.yview)
        p = tk.Frame(inner, bg=PANEL_BG)
        inner.create_window((0,0), window=p, anchor="nw")
        p.bind("<Configure>", lambda e: inner.configure(
            scrollregion=inner.bbox("all")))

        self._section(p, "Insertar")
        self._btn(p, "insertaVertice(o)",          self._op_insertaVertice,       GREEN)
        self._btn(p, "insertaArista(v, w, o)",     self._op_insertaArista,        GREEN)
        self._btn(p, "insertaAristaDirigida(v,w,o)",self._op_insertaAristaDirigida,GREEN)

        self._section(p, "Eliminar")
        self._btn(p, "eliminaVertice(v)", self._op_eliminaVertice, RED)
        self._btn(p, "eliminaArista(e)",  self._op_eliminaArista,  RED)

        self._section(p, "Modificar dirección")
        self._btn(p, "convierteNoDirigida(e)",   self._op_convierteNoDirigida, ACCENT)
        self._btn(p, "invierteDir(e)",           self._op_invierteDir,         ACCENT)
        self._btn(p, "asignaDirDesde(e, v)",     self._op_asignaDirDesde,      ACCENT2)
        self._btn(p, "asignaDirA(e, v)",         self._op_asignaDirA,          ACCENT2)

        self._section(p, "Herramientas")
        self._btn(p, "⟳ Reiniciar ejemplo", self._reiniciar, WHITE)
        self._btn(p, "⊕ Grafo aleatorio",   self._grafo_random, WHITE)

    # ── EJEMPLO INICIAL ───────────────────────────────────────────

    def _init_ejemplo(self):
        g = self.grafo
        v = [g.insertaVertice(f"V{i}") for i in range(1, 7)]
        g.insertaArista(v[0], v[1], "a")
        g.insertaArista(v[0], v[2], "b")
        g.insertaArista(v[1], v[3], "c")
        g.insertaAristaDirigida(v[2], v[3], "d")
        g.insertaAristaDirigida(v[3], v[4], "e")
        g.insertaArista(v[4], v[5], "f")
        g.insertaAristaDirigida(v[5], v[0], "g")
        g.insertaArista(v[1], v[4], "h")
        self._auto_layout()

    def _auto_layout(self):
        vids = self.grafo.vertices()
        n = len(vids)
        if n == 0:
            return
        cx, cy, r = 400, 340, 220
        for i, vid in enumerate(vids):
            angle = 2 * math.pi * i / n - math.pi / 2
            self.pos[vid] = (cx + r * math.cos(angle),
                             cy + r * math.sin(angle))

    def _reiniciar(self):
        self.grafo = Grafo()
        Arista._contador = 0
        self.pos = {}
        self.selected_v = None
        self.selected_e = None
        self._init_ejemplo()
        self._redraw()
        self._show("Grafo de ejemplo reiniciado.", GREEN)

    def _grafo_random(self):
        self.grafo = Grafo()
        Arista._contador = 0
        self.pos = {}
        self.selected_v = None
        self.selected_e = None
        g = self.grafo
        n = random.randint(4, 8)
        vids = [g.insertaVertice(f"V{i}") for i in range(1, n+1)]
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < 0.4:
                    if random.random() < 0.5:
                        g.insertaAristaDirigida(vids[i], vids[j])
                    else:
                        g.insertaArista(vids[i], vids[j])
        self._auto_layout()
        self._redraw()
        self._show(f"Grafo aleatorio con {n} vértices generado.", GREEN)


    R = 24   # radio de nodo

    def _redraw(self, highlight_v=None, highlight_e=None):
        c = self.canvas
        c.delete("all")

        W, H = c.winfo_width() or 900, c.winfo_height() or 680
        for x in range(0, W, 50):
            c.create_line(x, 0, x, H, fill="#1a3050", width=1)
        for y in range(0, H, 50):
            c.create_line(0, y, W, y, fill="#1a3050", width=1)

    
        for eid, ar in self.grafo._aristas.items():
            if ar.v not in self.pos or ar.w not in self.pos:
                continue
            x1, y1 = self.pos[ar.v]
            x2, y2 = self.pos[ar.w]

            is_hl = (eid == highlight_e or eid == self.selected_e)
            clr = RED if is_hl else (EDGE_DIR if ar.dirigida else EDGE_CLR)
            width = 4 if is_hl else 2

            if ar.dirigida:
                self._draw_arrow(c, x1, y1, x2, y2, clr, width, eid)
            else:
                c.create_line(x1, y1, x2, y2, fill=clr, width=width,
                              tags=f"edge_{eid}")
                
                mx, my = (x1+x2)/2, (y1+y2)/2
                c.create_oval(mx-10, my-10, mx+10, my+10, fill=PANEL_BG,
                              outline=clr, width=1)
                c.create_text(mx, my, text=f"e{eid}", fill=clr,
                              font=("Courier New", 8))


        for vid, (x, y) in self.pos.items():
            is_hl = (vid == highlight_v or vid == self.selected_v)
            fill  = NODE_SEL if is_hl else NODE_CLR
            outline = RED if is_hl else ACCENT2
            ow   = 3 if is_hl else 2
            c.create_oval(x-self.R, y-self.R, x+self.R, y+self.R,
                          fill=fill, outline=outline, width=ow,
                          tags=f"node_{vid}")
            label = str(self.grafo.get_objeto_vertice(vid) or f"V{vid}")
            c.create_text(x, y, text=label,
                          fill=WHITE, font=FONT_BOLD,
                          tags=f"node_{vid}")
            c.create_text(x, y - self.R - 10, text=f"id:{vid}",
                          fill=ACCENT2, font=("Courier New", 8))

        self._update_sel_labels()

    def _draw_arrow(self, c, x1, y1, x2, y2, clr, width, eid):
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        ux, uy = dx/dist, dy/dist
        sx = x1 + ux * self.R
        sy = y1 + uy * self.R
        ex = x2 - ux * (self.R + 10)
        ey = y2 - uy * (self.R + 10)
        c.create_line(sx, sy, ex, ey, fill=clr, width=width,
                      arrow=tk.LAST, arrowshape=(14, 16, 5),
                      tags=f"edge_{eid}")
        mx, my = (sx + ex)/2, (sy + ey)/2
        c.create_oval(mx-10, my-10, mx+10, my+10, fill=PANEL_BG,
                      outline=clr, width=1)
        c.create_text(mx, my, text=f"e{eid}", fill=clr,
                      font=("Courier New", 8))

    def _update_sel_labels(self):
        sv = f"V{self.selected_v}" if self.selected_v else "—"
        se = f"e{self.selected_e}" if self.selected_e else "—"
        self.lbl_sel_v.config(text=f"Vértice sel: {sv}")
        self.lbl_sel_e.config(text=f"Arista sel:  {se}")

    def _show(self, msg, color=GREEN):
        self.lbl_res.config(text=f"▸ {msg}", fg=color)


    def _node_at(self, x, y):
        for vid, (vx, vy) in self.pos.items():
            if math.hypot(x - vx, y - vy) <= self.R:
                return vid
        return None

    def _edge_at(self, x, y):
        for eid, ar in self.grafo._aristas.items():
            if ar.v not in self.pos or ar.w not in self.pos:
                continue
            x1, y1 = self.pos[ar.v]
            x2, y2 = self.pos[ar.w]
            dist = math.hypot(x2-x1, y2-y1)
            if dist == 0:
                continue
            t = ((x-x1)*(x2-x1) + (y-y1)*(y2-y1)) / dist**2
            t = max(0, min(1, t))
            px, py = x1 + t*(x2-x1), y1 + t*(y2-y1)
            if math.hypot(x-px, y-py) < 8:
                return eid
        return None

    def _on_click(self, event):
        vid = self._node_at(event.x, event.y)
        if vid is not None:
            self.selected_v = vid
            self.dragging = vid
            self._redraw()
            return
        eid = self._edge_at(event.x, event.y)
        if eid is not None:
            self.selected_e = eid
            self._redraw()

    def _on_drag(self, event):
        if self.dragging is not None:
            self.pos[self.dragging] = (event.x, event.y)
            self._redraw()

    def _on_release(self, event):
        self.dragging = None

    def _on_right_click(self, event):
        self.selected_v = None
        self.selected_e = None
        self._redraw()
        self._show("Selección limpiada.", ACCENT2)


    def _req_vertex(self):
        if self.selected_v is None:
            self._show("⚠ Selecciona un vértice primero (clic sobre él).", RED)
            return False
        return True

    def _req_edge(self):
        if self.selected_e is None:
            self._show("⚠ Selecciona una arista primero (clic sobre ella).", RED)
            return False
        return True

    def _ask_vertex(self, prompt="ID de vértice:"):
        val = simpledialog.askinteger("Entrada", prompt, parent=self)
        return val

    def _ask_str(self, prompt="Valor:"):
        return simpledialog.askstring("Entrada", prompt, parent=self)

    def _op_numVertices(self):
        r = self.grafo.numVertices()
        self._show(f"numVertices() = {r}", GREEN)

    def _op_numAristas(self):
        r = self.grafo.numAristas()
        self._show(f"numAristas() = {r}", GREEN)

    def _op_vertices(self):
        r = self.grafo.vertices()
        self._show(f"vertices() = {r}", GREEN)
        self._redraw(highlight_v=None)

    def _op_aristas(self):
        r = self.grafo.aristas()
        self._show(f"aristas() = {r}", GREEN)

    def _op_grado(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.grado(v)
        self._show(f"grado(V{v}) = {r}  (aristas incidentes: {self.grafo.aristasIncidentes(v)})", GREEN)
        self._redraw(highlight_v=v)

    def _op_verticesAdyacentes(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.verticesAdyacentes(v)
        self._show(f"verticesAdyacentes(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_aristasIncidentes(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.aristasIncidentes(v)
        self._show(f"aristasIncidentes(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_verticesFinales(self):
        if not self._req_edge(): return
        e = self.selected_e
        r = self.grafo.verticesFinales(e)
        self._show(f"verticesFinales(e{e}) = {r}", GREEN)
        self._redraw(highlight_e=e)

    def _op_opuesto(self):
        if not self._req_vertex() or not self._req_edge(): return
        v, e = self.selected_v, self.selected_e
        r = self.grafo.opuesto(v, e)
        if r is None:
            self._show(f"opuesto(V{v}, e{e}): el vértice no es extremo de esa arista.", RED)
        else:
            self._show(f"opuesto(V{v}, e{e}) = V{r}", GREEN)
            self._redraw(highlight_v=r, highlight_e=e)

    def _op_esAdyacente(self):
        if not self._req_vertex(): return
        v = self.selected_v
        w = self._ask_vertex("ID del segundo vértice w:")
        if w is None: return
        r = self.grafo.esAdyacente(v, w)
        clr = GREEN if r else RED
        self._show(f"esAdyacente(V{v}, V{w}) = {r}", clr)
        self._redraw(highlight_v=v)


    def _op_aristasDirigidas(self):
        r = self.grafo.aristasDirigidas()
        self._show(f"aristasDirigidas() = {r}", ACCENT)

    def _op_aristasNodirigidas(self):
        r = self.grafo.aristasNodirigidas()
        self._show(f"aristasNodirigidas() = {r}", ACCENT2)

    def _op_gradoEnt(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.gradoEnt(v)
        self._show(f"gradoEnt(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_gradoSalida(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.gradoSalida(v)
        self._show(f"gradoSalida(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_aristasIncidentesEnt(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.aristasIncidentesEnt(v)
        self._show(f"aristasIncidentesEnt(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_aristasIncidentesSal(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.aristasIncidentesSal(v)
        self._show(f"aristasIncidentesSal(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_verticesAdyacentesEnt(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.verticesAdyacentesEnt(v)
        self._show(f"verticesAdyacentesEnt(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_verticesAdyacentesSal(self):
        if not self._req_vertex(): return
        v = self.selected_v
        r = self.grafo.verticesAdyacentesSal(v)
        self._show(f"verticesAdyacentesSal(V{v}) = {r}", GREEN)
        self._redraw(highlight_v=v)

    def _op_destino(self):
        if not self._req_edge(): return
        e = self.selected_e
        r = self.grafo.destino(e)
        if r is None:
            self._show(f"destino(e{e}): arista no dirigida o no existe.", RED)
        else:
            self._show(f"destino(e{e}) = V{r}", GREEN)
            self._redraw(highlight_v=r, highlight_e=e)

    def _op_origen(self):
        if not self._req_edge(): return
        e = self.selected_e
        r = self.grafo.origen(e)
        if r is None:
            self._show(f"origen(e{e}): arista no dirigida o no existe.", RED)
        else:
            self._show(f"origen(e{e}) = V{r}", GREEN)
            self._redraw(highlight_v=r, highlight_e=e)

    def _op_esDirigida(self):
        if not self._req_edge(): return
        e = self.selected_e
        r = self.grafo.esDirigida(e)
        clr = GREEN if r else ACCENT2
        self._show(f"esDirigida(e{e}) = {r}", clr)
        self._redraw(highlight_e=e)

    def _op_insertaVertice(self):
        obj = self._ask_str("Objeto/nombre del vértice:")
        if obj is None: return
        vid = self.grafo.insertaVertice(obj)
        W = self.canvas.winfo_width() or 800
        H = self.canvas.winfo_height() or 600
        self.pos[vid] = (random.randint(80, W-80), random.randint(80, H-80))
        self._redraw(highlight_v=vid)
        self._show(f"insertaVertice('{obj}') → id = V{vid}", GREEN)

    def _op_insertaArista(self):
        v = self._ask_vertex("ID vértice origen v:")
        if v is None: return
        w = self._ask_vertex("ID vértice destino w:")
        if w is None: return
        obj = self._ask_str("Objeto de la arista (puede dejarse vacío):")
        eid = self.grafo.insertaArista(v, w, obj)
        self._redraw(highlight_e=eid)
        self._show(f"insertaArista(V{v}, V{w}, '{obj}') → e{eid}", GREEN)

    def _op_insertaAristaDirigida(self):
        v = self._ask_vertex("ID vértice origen v:")
        if v is None: return
        w = self._ask_vertex("ID vértice destino w:")
        if w is None: return
        obj = self._ask_str("Objeto de la arista (puede dejarse vacío):")
        eid = self.grafo.insertaAristaDirigida(v, w, obj)
        self._redraw(highlight_e=eid)
        self._show(f"insertaAristaDirigida(V{v}, V{w}, '{obj}') → e{eid}", GREEN)

    def _op_eliminaVertice(self):
        if not self._req_vertex(): return
        v = self.selected_v
        ok = self.grafo.eliminaVertice(v)
        if ok:
            del self.pos[v]
            self.selected_v = None
        self._redraw()
        self._show(f"eliminaVertice(V{v}) → {'OK' if ok else 'No encontrado'}", GREEN if ok else RED)

    def _op_eliminaArista(self):
        if not self._req_edge(): return
        e = self.selected_e
        ok = self.grafo.eliminaArista(e)
        if ok:
            self.selected_e = None
        self._redraw()
        self._show(f"eliminaArista(e{e}) → {'OK' if ok else 'No encontrado'}", GREEN if ok else RED)

    def _op_convierteNoDirigida(self):
        if not self._req_edge(): return
        e = self.selected_e
        ok = self.grafo.convierteNoDirigida(e)
        self._redraw(highlight_e=e)
        self._show(f"convierteNoDirigida(e{e}) → {'OK' if ok else 'No encontrado'}", GREEN if ok else RED)

    def _op_invierteDir(self):
        if not self._req_edge(): return
        e = self.selected_e
        ok = self.grafo.invierteDir(e)
        self._redraw(highlight_e=e)
        self._show(f"invierteDir(e{e}) → {'OK (dirección invertida)' if ok else 'No es dirigida'}", GREEN if ok else RED)

    def _op_asignaDirDesde(self):
        if not self._req_edge() or not self._req_vertex(): return
        e, v = self.selected_e, self.selected_v
        ok = self.grafo.asignaDirDesde(e, v)
        self._redraw(highlight_e=e, highlight_v=v)
        self._show(f"asignaDirDesde(e{e}, V{v}) → {'OK' if ok else 'Error'}", GREEN if ok else RED)

    def _op_asignaDirA(self):
        if not self._req_edge() or not self._req_vertex(): return
        e, v = self.selected_e, self.selected_v
        ok = self.grafo.asignaDirA(e, v)
        self._redraw(highlight_e=e, highlight_v=v)
        self._show(f"asignaDirA(e{e}, V{v}) → {'OK' if ok else 'Error'}", GREEN if ok else RED)



if __name__ == "__main__":
    app = App()
    app.mainloop()
