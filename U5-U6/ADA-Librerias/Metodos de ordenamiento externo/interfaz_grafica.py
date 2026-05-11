# Estructura-de-Datos/ordenamiento_externo/interfaz_grafica.py

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import RadioButtons, Button, CheckButtons

from .algoritmos_mezcla import (
    ordenar_intercalacion, 
    generar_pasadas_mezcla_directa, 
    generar_pasadas_mezcla_equilibrada
)
from .manejador_archivos import abrir_dialogo_archivo

FONDO      = "#0d1117"
PANEL      = "#161b22"
BORDE      = "#30363d"
ACENTO1    = "#58a6ff"   
ACENTO2    = "#3fb950"   
ACENTO3    = "#f78166"   
DORADO     = "#e3b341"
TEXTO      = "#c9d1d9"
SUBTEXTO   = "#8b949e"
MEZCLA_C   = "#d2a8ff"
ALERTA     = "#ffa657"

plt.rcParams.update({
    "figure.facecolor": FONDO, "axes.facecolor": PANEL, "axes.edgecolor": BORDE,
    "text.color": TEXTO, "axes.labelcolor": TEXTO, "xtick.color": SUBTEXTO,
    "ytick.color": SUBTEXTO, "font.family": "monospace",
})

def dibujar_arreglo(eje, datos, colores, y=0, altura_celda=0.7, etiqueta="", color_titulo=TEXTO, ancho_celda=0.9, tamano_fuente=11):
    n = len(datos)
    fuente_dinamica = tamano_fuente if ancho_celda >= 0.7 else (tamano_fuente - 3)
    
    for i, (valor, color) in enumerate(zip(datos, colores)):
        rectangulo = FancyBboxPatch((i * ancho_celda, y), ancho_celda - 0.05, altura_celda,
                                    boxstyle="round,pad=0.05", fc=color, ec=BORDE, lw=1.2)
        eje.add_patch(rectangulo)
        eje.text(i * ancho_celda + (ancho_celda - 0.05) / 2, y + altura_celda / 2, str(valor),
                 ha="center", va="center", fontsize=fuente_dinamica, fontweight="bold",
                 color=FONDO if color != PANEL else TEXTO)
    if etiqueta:
        eje.text(-0.6, y + altura_celda / 2, etiqueta, ha="right", va="center", fontsize=9, color=color_titulo, fontweight="bold")
    return n

def titulo_seccion(eje, texto, color, tamano_fuente=13):
    eje.set_title(texto, color=color, fontsize=tamano_fuente, fontweight="bold", pad=10, loc="left",
                  path_effects=[pe.withStroke(linewidth=3, foreground=FONDO)])

def calcular_ancho_celda(n: int) -> float:
    if n <= 10: return 0.9
    if n <= 20: return 0.7
    if n <= 40: return 0.5
    return 0.4

def normalizar_datos(datos: list, max_n: int = 40) -> list:
    if len(datos) > max_n: return datos[:max_n]
    return datos


def demo_intercalacion(eje, datos: list):
    lista_a, lista_b, pasos = ordenar_intercalacion(datos)
    fusionados_hasta_ahora = []
    puntero = {"A": 0, "B": 0}
    ancho_celda = calcular_ancho_celda(max(len(lista_a), len(lista_b)))

    def renderizar(cuadro):
        eje.cla(); eje.set_xlim(-1, max(len(lista_a), len(lista_b)) * ancho_celda + 1)
        eje.set_ylim(-1, 5.5); eje.axis("off")
        titulo_seccion(eje, "[1] INTERCALACIÓN  —  Fusión de dos mitades ordenadas", ACENTO1)

        nonlocal fusionados_hasta_ahora
        indice_paso = cuadro % (len(pasos) + 4)
        if indice_paso < len(pasos):
            origen, indice_a, indice_b, _ = pasos[indice_paso]
            puntero["A"] = indice_a; puntero["B"] = indice_b
            fusionados_hasta_ahora = [pasos[k][3] for k in range(indice_paso + 1)]
        elif indice_paso >= len(pasos):
            fusionados_hasta_ahora = [p[3] for p in pasos]

        colores_a = [SUBTEXTO if k < puntero["A"] else ACENTO1 for k in range(len(lista_a))]
        colores_b = [SUBTEXTO if k < puntero["B"] else ACENTO2 for k in range(len(lista_b))]

        dibujar_arreglo(eje, lista_a, colores_a, y=3.2, etiqueta="Mitad A", color_titulo=ACENTO1, ancho_celda=ancho_celda)
        dibujar_arreglo(eje, lista_b, colores_b, y=2.0, etiqueta="Mitad B", color_titulo=ACENTO2, ancho_celda=ancho_celda)

        if indice_paso < len(pasos):
            xi = min(puntero["A"], len(lista_a) - 1) * ancho_celda + ancho_celda / 2
            eje.annotate("", xy=(xi, 3.2), xytext=(xi, 2.0 + 0.7), arrowprops=dict(arrowstyle="<->", color=DORADO, lw=1.5))

        colores_res = [MEZCLA_C] * len(fusionados_hasta_ahora) + [PANEL] * (len(lista_a) + len(lista_b) - len(fusionados_hasta_ahora))
        dibujar_arreglo(eje, fusionados_hasta_ahora + [""] * (len(lista_a) + len(lista_b) - len(fusionados_hasta_ahora)),
                        colores_res, y=0.5, etiqueta="Resultado", color_titulo=MEZCLA_C, ancho_celda=ancho_celda)
        eje.text(0, -0.5, f"Paso {min(indice_paso+1, len(pasos))} / {len(pasos)}  →  fusionados: {len(fusionados_hasta_ahora)}", fontsize=8, color=DORADO)

    return renderizar, len(pasos) + 5

def demo_mezcla_directa(eje, datos: list):
    estados = generar_pasadas_mezcla_directa(datos)
    total_cuadros = (len(estados) + 1) * 8
    ancho_celda = calcular_ancho_celda(len(datos))
    colores_bloque = [ACENTO1, ACENTO2, ACENTO3, DORADO, MEZCLA_C, "#79c0ff", "#56d364", ALERTA]

    def renderizar(cuadro):
        eje.cla(); eje.set_xlim(-1.2, len(datos) * ancho_celda + 0.5)
        eje.set_ylim(-1, len(estados) * 1.5 + 2); eje.axis("off")
        titulo_seccion(eje, "[2] MEZCLA DIRECTA  —  Runs crecientes por pasada", ACENTO2)

        pasada_actual = min(cuadro // 8, len(estados) - 1)
        for p, estado in enumerate(estados[:pasada_actual + 1]):
            y_pos = (len(estados) - p - 1) * 1.4 + 0.2
            cols = [colores_bloque[(k // (2 ** p if p > 0 else 1)) % len(colores_bloque)] for k in range(len(estado))]
            dibujar_arreglo(eje, estado, cols, y=y_pos, etiqueta=f"Pasada {p}" if p > 0 else "Original", color_titulo=ACENTO2, ancho_celda=ancho_celda)

        eje.text(0, -0.6, f"Pasada {pasada_actual}: bloques tamaño {2 ** pasada_actual if pasada_actual > 0 else 1}  →  {len(estados)-1} pasadas", fontsize=8, color=DORADO)

    return renderizar, total_cuadros

def demo_mezcla_equilibrada(eje, datos: list):
    secuencias, pasadas = generar_pasadas_mezcla_equilibrada(datos)
    total_cuadros = len(pasadas) * 10 + 5
    colores_cinta = [ACENTO1, ACENTO3, ACENTO2, DORADO]

    def renderizar(cuadro):
        eje.cla(); eje.set_xlim(-0.5, 14); eje.set_ylim(-1, 7); eje.axis("off")
        titulo_seccion(eje, "[3] MEZCLA EQUILIBRADA  —  k=2 cintas alternas", ACENTO3)

        indice_pasada = min(cuadro // 10, len(pasadas) - 1)
        pasada = pasadas[indice_pasada]

        eje.text(0, 5.6, "CINTAS ENTRADA", fontsize=8, color=SUBTEXTO, fontweight="bold")
        for ci, cinta in enumerate(pasada["entrada"]):
            y_c = 4.5 - ci * 1.3
            eje.text(-0.4, y_c + 0.35, f"C{ci+1}", fontsize=9, color=colores_cinta[ci], fontweight="bold", ha="right")
            x_off = 0
            for run in cinta:
                for val in run:
                    rect = FancyBboxPatch((x_off, y_c), 0.8, 0.65, boxstyle="round,pad=0.04", fc=colores_cinta[ci], ec=BORDE, lw=1)
                    eje.add_patch(rect)
                    eje.text(x_off + 0.4, y_c + 0.325, str(val), ha="center", va="center", fontsize=8, fontweight="bold", color=FONDO)
                    x_off += 0.85
                eje.plot([x_off + 0.05, x_off + 0.05], [y_c, y_c + 0.65], color=BORDE, lw=2, ls="--")
                x_off += 0.35

        eje.annotate("", xy=(5.8, 2.6), xytext=(5.8, 3.5), arrowprops=dict(arrowstyle="-|>", color=DORADO, lw=2))
        eje.text(6.0, 3.0, pasada["etiqueta"], fontsize=9, color=DORADO, fontweight="bold")

        if pasada.get("salida"):
            eje.text(0, 2.4, "CINTAS SALIDA", fontsize=8, color=SUBTEXTO, fontweight="bold")
            for ci, cinta in enumerate(pasada["salida"]):
                y_c = 1.3 - ci * 1.2
                eje.text(-0.4, y_c + 0.35, f"S{ci+1}", fontsize=9, color=MEZCLA_C, fontweight="bold", ha="right")
                x_off = 0
                for run in cinta:
                    for val in run:
                        rect = FancyBboxPatch((x_off, y_c), 0.8, 0.65, boxstyle="round,pad=0.04", fc=MEZCLA_C, ec=BORDE, lw=1)
                        eje.add_patch(rect)
                        eje.text(x_off + 0.4, y_c + 0.325, str(val), ha="center", va="center", fontsize=8, fontweight="bold", color=FONDO)
                        x_off += 0.85
                    x_off += 0.35
        else:
            eje.text(2, 1.5, "← Distribuyendo runs...", fontsize=9, color=SUBTEXTO)
        eje.text(0, -0.7, f"k=2 cintas  |  Paso {indice_pasada+1}/{len(pasadas)}", fontsize=8, color=DORADO)

    return renderizar, total_cuadros

def vista_comparacion(figura, datos: list, seleccionados: list[bool], estado_global):
    figura.clear()
    activos = [i for i, s in enumerate(seleccionados) if s]
    if not activos:
        eje = figura.add_subplot(111, facecolor=PANEL); eje.axis("off")
        eje.text(0.5, 0.5, "Selecciona al menos un método", ha="center", va="center", fontsize=14, color=ALERTA, transform=eje.transAxes)
        figura.canvas.draw_idle(); return

    ejes = [figura.add_subplot(1, len(activos), i + 1, facecolor=PANEL) for i in range(len(activos))]
    for borde in sum([list(a.spines.values()) for a in ejes], []): borde.set_edgecolor(BORDE)

    funciones = [demo_intercalacion, demo_mezcla_directa, demo_mezcla_equilibrada]
    renderizadores = [funciones[idx](eje, datos[:]) for eje, idx in zip(ejes, activos)]

    nombres = ["Intercalación", "Mezcla Directa", "Mezcla Equilibrada"]
    figura.suptitle("COMPARACIÓN:  " + "   vs   ".join(nombres[i] for i in activos),
                 color=DORADO, fontsize=11, fontweight="bold", fontfamily="monospace", path_effects=[pe.withStroke(linewidth=3, foreground=FONDO)])

    estado = {"cuadro": 0, "reproduciendo": True}
    maximos_cuadros = max(mc for _, mc in renderizadores)

    botones = [Button(figura.add_axes([x, 0.02, w, 0.06], facecolor=PANEL), txt, color=PANEL, hovercolor=BORDE) 
               for x, w, txt in [(0.01, 0.08, "◀ Prev"), (0.11, 0.10, "⏸ Pausar"), (0.23, 0.08, "Next ▶"), (0.33, 0.12, "↺ Reiniciar"), (0.80, 0.18, "← Volver")]]
    for btn in botones: btn.label.set_color(TEXTO); btn.label.set_fontfamily("monospace"); btn.label.set_fontsize(8); btn.label.set_fontweight("bold")

    def redibujar():
        for (rf, _), _ in zip(renderizadores, activos): rf(estado["cuadro"])
        figura.canvas.draw_idle()

    def accion(op):
        if op == "prev": estado["reproduciendo"] = False; botones[1].label.set_text("▶ Reanudar"); estado["cuadro"] = max(0, estado["cuadro"] - 1)
        elif op == "play": estado["reproduciendo"] = not estado["reproduciendo"]; botones[1].label.set_text("⏸ Pausar" if estado["reproduciendo"] else "▶ Reanudar")
        elif op == "next": estado["reproduciendo"] = False; botones[1].label.set_text("▶ Reanudar"); estado["cuadro"] = min(estado["cuadro"] + 1, maximos_cuadros - 1)
        elif op == "rst": estado["cuadro"] = 0; estado["reproduciendo"] = True; botones[1].label.set_text("⏸ Pausar")
        elif op == "volver": estado_global["temporizador"].stop(); iniciar_visualizador(datos); return
        redibujar()

    botones[0].on_clicked(lambda _: accion("prev")); botones[1].on_clicked(lambda _: accion("play"))
    botones[2].on_clicked(lambda _: accion("next")); botones[3].on_clicked(lambda _: accion("rst"))
    botones[4].on_clicked(lambda _: accion("volver"))

    def actualizar(_):
        if estado["reproduciendo"]:
            if estado["cuadro"] < maximos_cuadros - 1: estado["cuadro"] += 1; redibujar()
            else: estado["reproduciendo"] = False; botones[1].label.set_text("▶ Reanudar"); figura.canvas.draw_idle()

    temporizador = figura.canvas.new_timer(interval=700); temporizador.add_callback(actualizar, None); temporizador.start()
    estado_global["botones_comp"] = botones; estado_global["temporizador"] = temporizador; redibujar()


def iniciar_visualizador(datos_iniciales=None):
    if datos_iniciales is None:
        datos_iniciales = [45, 12, 67, 23, 89, 34, 56, 78, 91, 5]
    
    datos_archivos = {"1": {"valores": [], "nombre": ""}, "2": {"valores": [], "nombre": ""}}
    datos_actuales = {"valores": datos_iniciales[:], "nombre": "datos por defecto"}

    figura = plt.figure(figsize=(15, 9), facecolor=FONDO)
    figura.canvas.manager.set_window_title("Visualizador de Ordenamiento Externo v3.0 (Numérico)")

    ax_radio = figura.add_axes([0.01, 0.52, 0.17, 0.28], facecolor=PANEL); ax_check = figura.add_axes([0.01, 0.30, 0.17, 0.20], facecolor=PANEL)
    ax_info = figura.add_axes([0.01, 0.10, 0.17, 0.18], facecolor=PANEL); ax_vis = figura.add_axes([0.21, 0.12, 0.77, 0.83], facecolor=PANEL)

    botones = [Button(figura.add_axes([x, 0.02, w, 0.07], facecolor=PANEL), txt, color=c, hovercolor=hc) 
               for x, w, txt, c, hc in [(0.21, 0.07, "◀ Prev", PANEL, BORDE), (0.29, 0.08, "⏸ Pausar", PANEL, BORDE), 
                                        (0.38, 0.07, "Next ▶", PANEL, BORDE), (0.46, 0.08, "↺ Reiniciar", PANEL, BORDE),
                                        (0.56, 0.09, "📂 Arch 1", "#182b40", "#254261"), (0.66, 0.09, "📂 Arch 2", "#1f3a2b", "#2d5a3d"),
                                        (0.77, 0.11, "⚡ Comparar", "#3a1f2b", "#5a2d40")]]
    for i, btn in enumerate(botones): 
        btn.label.set_color([TEXTO, TEXTO, TEXTO, TEXTO, ACENTO1, ACENTO2, ACENTO3][i])
        btn.label.set_fontfamily("monospace"); btn.label.set_fontsize(8); btn.label.set_fontweight("bold")

    for borde in ax_vis.spines.values(): borde.set_edgecolor(BORDE); borde.set_linewidth(1.5)
    for a in (ax_radio, ax_check, ax_info):
        for sp in a.spines.values(): sp.set_edgecolor(BORDE); sp.set_linewidth(1)

    figura.text(0.09, 0.90, "ALGORITMOS\nDE MEZCLA", ha="center", va="top", fontsize=10, fontweight="bold", color=TEXTO, fontfamily="monospace", path_effects=[pe.withStroke(linewidth=3, foreground=FONDO)])

    etiquetas_radio = ["Intercalación", "Mezcla Directa", "Mzcla Equilibrada"]
    colores_btn = [ACENTO1, ACENTO2, ACENTO3]
    radio = RadioButtons(ax_radio, etiquetas_radio, activecolor=DORADO)
    for lbl, col in zip(radio.labels, colores_btn): lbl.set_color(col); lbl.set_fontfamily("monospace"); lbl.set_fontsize(9); lbl.set_fontweight("bold")

    ax_check.axis("off"); ax_check.text(0.05, 0.97, "Comparar (marca varios):", transform=ax_check.transAxes, va="top", fontsize=8, color=SUBTEXTO, fontfamily="monospace")
    check = CheckButtons(figura.add_axes([0.015, 0.30, 0.165, 0.20], facecolor=PANEL), ["Intercalación", "Mezcla Directa", "M. Equilibrada"], [False, False, False])
    for lbl, col in zip(check.labels, colores_btn): lbl.set_color(col); lbl.set_fontfamily("monospace"); lbl.set_fontsize(8); lbl.set_fontweight("bold")

    estado = {"seleccionado": 0, "cuadro": 0, "reproduciendo": True, "renderizador": None, "maximos_cuadros": 1, "temporizador": None}
    funciones_demo = [demo_intercalacion, demo_mezcla_directa, demo_mezcla_equilibrada]

    def actualizar_info(idx):
        ax_info.cla(); ax_info.axis("off"); d = datos_actuales["valores"]; texto_fuente = datos_actuales['nombre']
        if len(texto_fuente) > 25: texto_fuente = texto_fuente[:22] + "..."
        resumen = f"Datos Totales: {len(d)}\nFuente: {texto_fuente}\nTipo: Estricto Numérico\n\n"
        if len(d) > 0: resumen += f"Min: {min(d)}  Max: {max(d)}"
        ax_info.text(0.05, 0.98, resumen, transform=ax_info.transAxes, va="top", fontsize=7.5, color=TEXTO, fontfamily="monospace")
        figura.canvas.draw_idle()

    def cargar_demo(idx):
        datos = normalizar_datos(datos_actuales["valores"]); render_fn, max_f = funciones_demo[idx](ax_vis, datos)
        estado.update({"renderizador": render_fn, "maximos_cuadros": max_f, "cuadro": 0, "seleccionado": idx}); actualizar_info(idx); figura.canvas.draw_idle()

    def accion(op, arg=None):
        if op == "prev": estado["reproduciendo"] = False; botones[1].label.set_text("▶ Reanudar"); estado["cuadro"] = max(0, estado["cuadro"] - 1); estado["renderizador"](estado["cuadro"])
        elif op == "play": estado["reproduciendo"] = not estado["reproduciendo"]; botones[1].label.set_text("⏸ Pausar" if estado["reproduciendo"] else "▶ Reanudar")
        elif op == "next": estado["reproduciendo"] = False; botones[1].label.set_text("▶ Reanudar"); estado["cuadro"] = min(estado["cuadro"] + 1, estado["maximos_cuadros"] - 1); estado["renderizador"](estado["cuadro"])
        elif op == "rst": estado["cuadro"] = 0; estado["reproduciendo"] = True; botones[1].label.set_text("⏸ Pausar"); estado["renderizador"](0)
        elif op == "arch":
            datos, nombre = abrir_dialogo_archivo()
            if datos:
                datos_archivos[arg] = {"valores": datos, "nombre": nombre}
                comb = datos_archivos["1"]["valores"] + datos_archivos["2"]["valores"]
                noms = [f"A{k}:{v['nombre']}" for k, v in datos_archivos.items() if v["valores"]]
                datos_actuales.update({"valores": comb if comb else datos_iniciales[:], "nombre": " + ".join(noms) if comb else "datos iniciales"})
                cargar_demo(estado["seleccionado"])
                ax_vis.text(0.5, 0.02, f"✔ Archivo {arg} cargado (Numérico).", ha="center", va="bottom", fontsize=8, color=ACENTO2, transform=ax_vis.transAxes, fontfamily="monospace")
        elif op == "comp":
            sel = check.get_status()
            estado["temporizador"].stop(); vista_comparacion(figura, normalizar_datos(datos_actuales["valores"]), sel if any(sel) else [True]*3, estado)
            return
        elif op == "rad":
            estado["reproduciendo"] = True; botones[1].label.set_text("⏸ Pausar"); cargar_demo(etiquetas_radio.index(arg))
        figura.canvas.draw_idle()

    botones[0].on_clicked(lambda _: accion("prev")); botones[1].on_clicked(lambda _: accion("play")); botones[2].on_clicked(lambda _: accion("next"))
    botones[3].on_clicked(lambda _: accion("rst")); botones[4].on_clicked(lambda _: accion("arch", "1")); botones[5].on_clicked(lambda _: accion("arch", "2"))
    botones[6].on_clicked(lambda _: accion("comp")); radio.on_clicked(lambda lbl: accion("rad", lbl))

    ax_prog = figura.add_axes([0.21, 0.10, 0.77, 0.02], facecolor=FONDO); ax_prog.axis("off"); texto_progreso = ax_prog.text(0.0, 0.5, "", va="center", fontsize=8, color=SUBTEXTO, fontfamily="monospace")

    def bucle(_):
        if estado["reproduciendo"] and estado["renderizador"]:
            if estado["cuadro"] < estado["maximos_cuadros"] - 1: estado["cuadro"] += 1; estado["renderizador"](estado["cuadro"])
            else: estado["reproduciendo"] = False; botones[1].label.set_text("▶ Reanudar")
            pct = int(estado["cuadro"] / max(estado["maximos_cuadros"] - 1, 1) * 100)
            texto_progreso.set_text(f"[{'█' * (pct // 5) + '░' * (20 - pct // 5)}] {pct:3d}%  cuadro {estado['cuadro']}/{estado['maximos_cuadros']-1}")
            figura.canvas.draw_idle()

    estado["temporizador"] = figura.canvas.new_timer(interval=700); estado["temporizador"].add_callback(bucle, None); estado["temporizador"].start()
    estado["ref"] = [botones, radio, check]
    figura.text(0.09, 0.08, "Formatos Numéricos:\n.txt .csv .json\n.xml .yaml .xlsx\n.xls .npy", ha="center", va="top", fontsize=6.5, color=SUBTEXTO, fontfamily="monospace")
    
    cargar_demo(0)
    plt.show()