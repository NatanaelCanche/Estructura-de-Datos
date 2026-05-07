import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import time
import random
import threading
import re
import zipfile
from typing import Callable, List, Tuple, Optional

# ==================== UTILIDADES DE ARCHIVO ====================

def obtener_hojas_excel(filepath: str) -> dict:
    """Devuelve un diccionario { 'Nombre de Hoja': 'xl/worksheets/sheetX.xml' }"""
    hojas = {}
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            wb_xml = z.read('xl/workbook.xml').decode('utf-8')
            sheets_data = re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb_xml)
            
            rels_xml = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
            rels_data = re.findall(r'<Relationship [^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels_xml)
            rels_dict = {rid: target for rid, target in rels_data}
            
            for nombre, rid in sheets_data:
                target = rels_dict.get(rid)
                if target:
                    if target.startswith('/xl/'): target = target[1:]
                    elif not target.startswith('xl/'): target = 'xl/' + target
                    hojas[nombre] = target
    except Exception as e:
        print(f"Error obteniendo hojas de {filepath}: {e}")
    return hojas

def leer_enteros_archivo(filepath: str, hoja_objetivo: str = None) -> List[int]:
    """Lee todos los enteros de un archivo, independiente de su separador o tipo."""
    if not os.path.exists(filepath):
        return []
        
    _, ext = os.path.splitext(filepath.lower())
    
    numeros = []
    if ext == '.xlsx':
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                # 1. Analizar styles.xml para identificar qué estilos corresponden a Fechas/Horas
                estilos_fecha = set()
                try:
                    if 'xl/styles.xml' in z.namelist():
                        styles_xml = z.read('xl/styles.xml').decode('utf-8')
                        # Extraer bloque de estilos de celdas
                        m_cellxfs = re.search(r'<cellXfs.*?</cellXfs>', styles_xml, re.DOTALL)
                        if m_cellxfs:
                            xfs = re.findall(r'<xf[^>]*numFmtId="(\d+)"[^>]*>', m_cellxfs.group(0))
                            for i, fmt in enumerate(xfs):
                                fmt_id = int(fmt)
                                # IDs 14-22 y 45-47 son fechas/horas estándar. >164 son personalizadas (generalmente fechas)
                                if (14 <= fmt_id <= 22) or (45 <= fmt_id <= 47) or fmt_id >= 164:
                                    estilos_fecha.add(i)
                except Exception as e:
                    print("Advertencia leyendo styles.xml:", e)

                targets = []
                if hoja_objetivo == "TODAS":
                    targets = [f for f in z.namelist() if f.startswith('xl/worksheets/') and f.endswith('.xml')]
                elif hoja_objetivo:
                    targets = [hoja_objetivo]
                else:
                    hojas = [f for f in z.namelist() if f.startswith('xl/worksheets/') and f.endswith('.xml')]
                    if hojas: targets = [hojas[0]]
                
                for target in targets:
                    xml_content = z.read(target)
                    # En Excel, las celdas están en <c> y los valores en <v>
                    celdas = re.findall(b'<c([^>]*)>(.*?)</c>', xml_content)
                    for attrs, inner in celdas:
                        # Ignorar índices de palabras (Strings)
                        if b't="s"' in attrs or b't="str"' in attrs or b't="inlineStr"' in attrs:
                            continue 
                        
                        # Ignorar si es una fecha u hora (usando el índice de estilo)
                        s_match = re.search(b's="(\\d+)"', attrs)
                        if s_match:
                            style_idx = int(s_match.group(1))
                            if style_idx in estilos_fecha:
                                continue # Es una fecha/hora, la ignoramos!

                        # Extraer el valor real numérico
                        v_match = re.search(b'<v>(-?\\d+)</v>', inner)
                        if v_match:
                            numeros.append(int(v_match.group(1)))
            return numeros
        except Exception as e:
            print(f"Error parseando Excel {filepath}: {e}")
            return []
            
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                contenido = f.read()
        except Exception as e:
            print(f"Error leyendo texto {filepath}: {e}")
            return []
            
    # Solo hacer match de números independientes (ignorando letras pegadas como "fecha2023")
    nums = re.findall(r'\b-?\d+\b', contenido)
    return [int(x) for x in nums]

def escribir_enteros_archivo(filepath: str, numeros: List[int], separador: str = "\n"):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(separador.join(map(str, numeros)))
    except Exception as e:
        print(f"Error escribiendo {filepath}: {e}")

def leer_siguiente(f) -> Optional[int]:
    while True:
        line = f.readline()
        if not line: return None
        m = re.search(r'-?\d+', line)
        if m: return int(m.group())

def combinar_archivos(archivo1: str, hoja1: str, archivo2: str, hoja2: str, output_path: str, log_callback: Callable) -> bool:
    log_callback("--- PREPARACIÓN: COMBINANDO ARCHIVOS ---")
    datos1 = leer_enteros_archivo(archivo1, hoja1) if archivo1 and os.path.exists(archivo1) else []
    datos2 = leer_enteros_archivo(archivo2, hoja2) if archivo2 and os.path.exists(archivo2) else []
    
    if archivo1 and os.path.exists(archivo1):
        log_callback(f"Leídos {len(datos1)} elementos de {os.path.basename(archivo1)}")
    if archivo2 and os.path.exists(archivo2):
        log_callback(f"Leídos {len(datos2)} elementos de {os.path.basename(archivo2)}")
    
    totales = datos1 + datos2
    if not totales:
        log_callback("Error: No se encontraron datos para ordenar.")
        return False
        
    escribir_enteros_archivo(output_path, totales)
    log_callback(f"Archivo maestro temporal creado con {len(totales)} elementos.\n")
    return True

# ==================== ALGORITMOS DE ORDENAMIENTO EXTERNO ====================

def intercalacion_externa(arch1: str, hoja1: str, arch2: str, hoja2: str, ext: str, log_callback: Callable):
    maestro = f"resultado_ordenado{ext}"
    if not combinar_archivos(arch1, hoja1, arch2, hoja2, maestro, log_callback): return
    
    datos = leer_enteros_archivo(maestro)
    ordenado_path = f"temp_ordenado{ext}"
    with open(ordenado_path, 'w') as f: pass

    for i, num in enumerate(datos):
        if i % 10 == 0:
            log_callback(f"→ Insertando {num} en archivo temporal...")
        temp_datos = leer_enteros_archivo(ordenado_path)
        pos = 0
        while pos < len(temp_datos) and temp_datos[pos] < num:
            pos += 1
        temp_datos.insert(pos, num)
        escribir_enteros_archivo(ordenado_path, temp_datos)
        time.sleep(0.01)
        
    final = leer_enteros_archivo(ordenado_path)
    escribir_enteros_archivo(maestro, final)
    if os.path.exists(ordenado_path): os.remove(ordenado_path)
    log_callback(f"\n✓ Intercalación completada en: {maestro}")

def mezcla_directa_externa(arch1: str, hoja1: str, arch2: str, hoja2: str, ext: str, log_callback: Callable):
    maestro = f"resultado_ordenado{ext}"
    if not combinar_archivos(arch1, hoja1, arch2, hoja2, maestro, log_callback): return
    
    aux1 = f"aux1{ext}"
    aux2 = f"aux2{ext}"
    total_elementos = len(leer_enteros_archivo(maestro))
    if total_elementos <= 1: return
    
    chunk_size = 1
    pasada = 1
    while chunk_size < total_elementos:
        log_callback(f"\n--- PASADA {pasada} ---")
        log_callback(f"PARTICIÓN (Bloques de {chunk_size}) → {aux1} y {aux2}")
        
        f_in = open(maestro, 'r')
        f1 = open(aux1, 'w')
        f2 = open(aux2, 'w')
        turno = True; leidos = 0
        while True:
            val = leer_siguiente(f_in)
            if val is None: break
            if turno: f1.write(f"{val}\n")
            else: f2.write(f"{val}\n")
            leidos += 1
            if leidos == chunk_size:
                leidos = 0; turno = not turno
        f_in.close(); f1.close(); f2.close()
        time.sleep(0.3)
        
        log_callback(f"FUSIÓN → De regreso a {maestro}")
        f_out = open(maestro, 'w'); f1 = open(aux1, 'r'); f2 = open(aux2, 'r')
        eof1 = False; eof2 = False
        v1 = leer_siguiente(f1); v2 = leer_siguiente(f2)
        if v1 is None: eof1 = True
        if v2 is None: eof2 = True
        
        while not eof1 or not eof2:
            c1 = 0; c2 = 0
            while c1 < chunk_size and not eof1 and c2 < chunk_size and not eof2:
                if v1 <= v2:
                    f_out.write(f"{v1}\n"); v1 = leer_siguiente(f1)
                    if v1 is None: eof1 = True
                    c1 += 1
                else:
                    f_out.write(f"{v2}\n"); v2 = leer_siguiente(f2)
                    if v2 is None: eof2 = True
                    c2 += 1
            while c1 < chunk_size and not eof1:
                f_out.write(f"{v1}\n"); v1 = leer_siguiente(f1)
                if v1 is None: eof1 = True
                c1 += 1
            while c2 < chunk_size and not eof2:
                f_out.write(f"{v2}\n"); v2 = leer_siguiente(f2)
                if v2 is None: eof2 = True
                c2 += 1
        f_out.close(); f1.close(); f2.close()
        time.sleep(0.3)
        chunk_size *= 2; pasada += 1
        
    if os.path.exists(aux1): os.remove(aux1)
    if os.path.exists(aux2): os.remove(aux2)
    log_callback(f"\n✓ Mezcla Directa completada en: {maestro}")

def mezcla_equilibrada_externa(arch1: str, hoja1: str, arch2: str, hoja2: str, ext: str, log_callback: Callable):
    maestro = f"resultado_ordenado{ext}"
    if not combinar_archivos(arch1, hoja1, arch2, hoja2, maestro, log_callback): return
    
    aux1 = f"aux1{ext}"
    aux2 = f"aux2{ext}"
    pasada = 1
    while True:
        log_callback(f"\n--- PASADA {pasada} ---")
        log_callback(f"PARTICIÓN (Secuencias naturales) → {aux1} y {aux2}")
        
        f_in = open(maestro, 'r'); f1 = open(aux1, 'w'); f2 = open(aux2, 'w')
        v_actual = leer_siguiente(f_in)
        if v_actual is None:
            f_in.close(); f1.close(); f2.close(); break
            
        turno = True
        if turno: f1.write(f"{v_actual}\n")
        else: f2.write(f"{v_actual}\n")
        runs_count = 1
        
        while True:
            v_sgte = leer_siguiente(f_in)
            if v_sgte is None: break
            if v_sgte < v_actual:
                turno = not turno; runs_count += 1
            if turno: f1.write(f"{v_sgte}\n")
            else: f2.write(f"{v_sgte}\n")
            v_actual = v_sgte
            
        f_in.close(); f1.close(); f2.close()
        if runs_count <= 1:
            log_callback("¡Archivo ya está ordenado!")
            break
            
        time.sleep(0.3)
        log_callback(f"FUSIÓN → De regreso a {maestro}")
        f_out = open(maestro, 'w'); f1 = open(aux1, 'r'); f2 = open(aux2, 'r')
        eof1 = False; eof2 = False
        v1 = leer_siguiente(f1); v2 = leer_siguiente(f2)
        if v1 is None: eof1 = True
        if v2 is None: eof2 = True
        
        while not eof1 and not eof2:
            while True:
                if v1 <= v2:
                    f_out.write(f"{v1}\n"); ant1 = v1; v1 = leer_siguiente(f1)
                    if v1 is None: eof1 = True
                    if eof1 or v1 < ant1:
                        while not eof2:
                            f_out.write(f"{v2}\n"); ant2 = v2; v2 = leer_siguiente(f2)
                            if v2 is None: eof2 = True
                            if eof2 or v2 < ant2: break
                        break
                else:
                    f_out.write(f"{v2}\n"); ant2 = v2; v2 = leer_siguiente(f2)
                    if v2 is None: eof2 = True
                    if eof2 or v2 < ant2:
                        while not eof1:
                            f_out.write(f"{v1}\n"); ant1 = v1; v1 = leer_siguiente(f1)
                            if v1 is None: eof1 = True
                            if eof1 or v1 < ant1: break
                        break
        while not eof1:
            f_out.write(f"{v1}\n"); v1 = leer_siguiente(f1)
            if v1 is None: eof1 = True
        while not eof2:
            f_out.write(f"{v2}\n"); v2 = leer_siguiente(f2)
            if v2 is None: eof2 = True
            
        f_out.close(); f1.close(); f2.close()
        time.sleep(0.3); pasada += 1
        
    if os.path.exists(aux1): os.remove(aux1)
    if os.path.exists(aux2): os.remove(aux2)
    log_callback(f"\n✓ Mezcla Equilibrada completada en: {maestro}")


# ==================== INTERFAZ GRÁFICA ====================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ordenamiento Externo de 2 Archivos (Merge)")
        self.geometry("1050x780")
        self.configure(bg="#0f0f1a")
        
        self.archivo1 = ""
        self.hoja1 = None
        self.archivo2 = ""
        self.hoja2 = None
        
        self.colores = {
            "bg": "#0f0f1a", "panel": "#1a1a2e", "borde": "#252545", "acento": "#ff6b6b",
            "texto": "#e8e8f0", "muted": "#9090b0", "verde": "#5cbf7c", "azul": "#5ca8bf"
        }
        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        c = self.colores; style = ttk.Style(self); style.theme_use("clam")
        style.configure("TFrame", background=c["bg"]); style.configure("Panel.TFrame", background=c["panel"])
        style.configure("Accion.TButton", background=c["acento"], foreground="#ffffff", font=("Consolas", 10, "bold"), padding=[10, 8], borderwidth=0, relief="flat")
        style.map("Accion.TButton", background=[("active", "#ff8787")], foreground=[("disabled", "#a0a0a0")])
        style.configure("Sec.TButton", background=c["borde"], foreground=c["texto"], font=("Consolas", 9), padding=[8, 6], borderwidth=0, relief="flat")
        style.map("Sec.TButton", background=[("active", c["azul"])])

    def _construir_ui(self):
        c = self.colores
        cab = tk.Frame(self, bg=c["panel"], pady=14, padx=24); cab.pack(fill="x", side="top")
        tk.Label(cab, text="💾 ORDENAMIENTO EXTERNO (FUSIÓN DE ARCHIVOS)", bg=c["panel"], fg=c["acento"], font=("Consolas", 16, "bold")).pack(side="left")
        tk.Label(cab, text="Combina 2 archivos distintos", bg=c["panel"], fg=c["muted"], font=("Consolas", 9)).pack(side="left", padx=16)

        ctrl = tk.Frame(self, bg=c["panel"], pady=10, padx=20); ctrl.pack(fill="x", pady=10)
        
        opt_frame = tk.Frame(ctrl, bg=c["panel"]); opt_frame.pack(fill="x", pady=(0, 15))
        tk.Label(opt_frame, text="Formato de salida esperado:", bg=c["panel"], fg=c["muted"], font=("Consolas", 10)).pack(side="left")
        self.combo_ext = ttk.Combobox(opt_frame, values=[".txt", ".csv", ".dat", ".log"], width=6, state="readonly", font=("Consolas", 10))
        self.combo_ext.set(".txt")
        self.combo_ext.pack(side="left", padx=5)

        row1 = tk.Frame(ctrl, bg=c["panel"]); row1.pack(fill="x", pady=5)
        tk.Label(row1, text="ARCHIVO 1:", bg=c["panel"], fg=c["azul"], font=("Consolas", 10, "bold"), width=12, anchor="w").pack(side="left")
        self.lbl_a1 = tk.Label(row1, text="(Vacío)", bg=c["borde"], fg=c["texto"], font=("Consolas", 10), width=45, anchor="w", padx=10)
        self.lbl_a1.pack(side="left", padx=5)
        ttk.Button(row1, text="📂 Seleccionar", style="Sec.TButton", command=lambda: self.seleccionar_archivo(1)).pack(side="left", padx=5)
        ttk.Button(row1, text="✨ Generar Aleatorio", style="Sec.TButton", command=lambda: self.generar_archivo(1)).pack(side="left", padx=5)
        ttk.Button(row1, text="❌ Quitar", style="Sec.TButton", command=lambda: self.quitar_archivo(1)).pack(side="left", padx=5)

        row2 = tk.Frame(ctrl, bg=c["panel"]); row2.pack(fill="x", pady=5)
        tk.Label(row2, text="ARCHIVO 2:", bg=c["panel"], fg=c["verde"], font=("Consolas", 10, "bold"), width=12, anchor="w").pack(side="left")
        self.lbl_a2 = tk.Label(row2, text="(Vacío)", bg=c["borde"], fg=c["texto"], font=("Consolas", 10), width=45, anchor="w", padx=10)
        self.lbl_a2.pack(side="left", padx=5)
        ttk.Button(row2, text="📂 Seleccionar", style="Sec.TButton", command=lambda: self.seleccionar_archivo(2)).pack(side="left", padx=5)
        ttk.Button(row2, text="✨ Generar Aleatorio", style="Sec.TButton", command=lambda: self.generar_archivo(2)).pack(side="left", padx=5)
        ttk.Button(row2, text="❌ Quitar", style="Sec.TButton", command=lambda: self.quitar_archivo(2)).pack(side="left", padx=5)

        main_frame = tk.Frame(self, bg=c["bg"]); main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        izq = tk.Frame(main_frame, bg=c["bg"], width=420); izq.pack(side="left", fill="y", padx=(0, 10)); izq.pack_propagate(False)
        tk.Label(izq, text="COMBINAR Y ORDENAR", bg=c["bg"], fg=c["acento"], font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0, 10))

        self.btn_int = ttk.Button(izq, text="▶ Intercalación Externa", style="Accion.TButton", command=lambda: self.ejecutar_algoritmo(intercalacion_externa))
        self.btn_int.pack(fill="x", pady=5)
        self.btn_dir = ttk.Button(izq, text="▶ Mezcla Directa Externa", style="Accion.TButton", command=lambda: self.ejecutar_algoritmo(mezcla_directa_externa))
        self.btn_dir.pack(fill="x", pady=5)
        self.btn_eq = ttk.Button(izq, text="▶ Mezcla Equilibrada Externa", style="Accion.TButton", command=lambda: self.ejecutar_algoritmo(mezcla_equilibrada_externa))
        self.btn_eq.pack(fill="x", pady=5)

        tk.Label(izq, text="Log de Operaciones (Disco)", bg=c["bg"], fg=c["muted"], font=("Consolas", 10, "bold")).pack(anchor="w", pady=(20, 5))
        self.log_txt = scrolledtext.ScrolledText(izq, bg=c["panel"], fg=c["verde"], font=("Consolas", 9), relief="flat"); self.log_txt.pack(fill="both", expand=True)

        der = tk.Frame(main_frame, bg=c["panel"]); der.pack(side="right", fill="both", expand=True)
        tk.Label(der, text="CONTENIDO DE ENTRADA (Archivos Originales)", bg=c["panel"], fg=c["azul"], font=("Consolas", 10, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.preview_in = scrolledtext.ScrolledText(der, bg=c["borde"], fg=c["texto"], font=("Consolas", 10), relief="flat", height=6); self.preview_in.pack(fill="x", padx=15, pady=(0, 15))
        tk.Label(der, text="RESULTADO ORDENADO", bg=c["panel"], fg=c["acento"], font=("Consolas", 10, "bold")).pack(anchor="w", padx=15, pady=(0, 5))
        self.preview_out = scrolledtext.ScrolledText(der, bg=c["borde"], fg=c["texto"], font=("Consolas", 11), relief="flat"); self.preview_out.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.actualizar_previews()

    def pedir_hoja_usuario(self, hojas: dict) -> str:
        dlg = tk.Toplevel(self)
        dlg.title("Seleccionar Hoja")
        dlg.geometry("350x160")
        dlg.configure(bg=self.colores["bg"])
        dlg.transient(self)
        dlg.grab_set()
        
        tk.Label(dlg, text="Este archivo Excel contiene múltiples hojas.\n¿De cuál quieres extraer los datos?", bg=self.colores["bg"], fg=self.colores["texto"], font=("Consolas", 10)).pack(pady=15)
        
        nombres = list(hojas.keys())
        opcion_todas = "▶ Extraer de TODAS las hojas combinadas"
        nombres.insert(0, opcion_todas)
        
        combo = ttk.Combobox(dlg, values=nombres, state="readonly", font=("Consolas", 10))
        combo.set(opcion_todas)
        combo.pack(pady=5)
        
        resultado = []
        def confirmar():
            if combo.get() == opcion_todas:
                resultado.append("TODAS")
            else:
                resultado.append(hojas[combo.get()])
            dlg.destroy()
            
        ttk.Button(dlg, text="✔ Cargar Datos", style="Accion.TButton", command=confirmar).pack(pady=15)
        
        self.wait_window(dlg)
        return resultado[0] if resultado else None

    def seleccionar_archivo(self, num: int):
        filepath = filedialog.askopenfilename(title=f"Seleccionar Archivo {num}", filetypes=[("Todos los archivos", "*.*")])
        if not filepath: return
        
        hoja_seleccionada = None
        display_name = os.path.basename(filepath)
        
        if filepath.lower().endswith('.xlsx'):
            hojas = obtener_hojas_excel(filepath)
            if len(hojas) > 1:
                # Mostrar popup para elegir
                hoja_seleccionada = self.pedir_hoja_usuario(hojas)
                if not hoja_seleccionada: return # El usuario canceló el popup
                
                if hoja_seleccionada == "TODAS":
                    display_name += " [Todas las hojas]"
                else:
                    # Buscar el nombre de la hoja para mostrarlo
                    nombre_h = [k for k, v in hojas.items() if v == hoja_seleccionada][0]
                    display_name += f" [{nombre_h}]"
            elif len(hojas) == 1:
                hoja_seleccionada = list(hojas.values())[0]
                nombre_h = list(hojas.keys())[0]
                display_name += f" [{nombre_h}]"

        if num == 1:
            self.archivo1 = filepath
            self.hoja1 = hoja_seleccionada
            self.lbl_a1.config(text=display_name)
        else:
            self.archivo2 = filepath
            self.hoja2 = hoja_seleccionada
            self.lbl_a2.config(text=display_name)
        self.actualizar_previews()

    def generar_archivo(self, num: int):
        ext = self.combo_ext.get()
        filepath = os.path.abspath(f"datos{num}{ext}")
        if num == 1: numeros = random.sample(range(1, 500), 25)
        else: numeros = random.sample(range(500, 1000), 25)
        escribir_enteros_archivo(filepath, numeros)
        
        if num == 1:
            self.archivo1 = filepath
            self.hoja1 = None
            self.lbl_a1.config(text=os.path.basename(filepath))
        else:
            self.archivo2 = filepath
            self.hoja2 = None
            self.lbl_a2.config(text=os.path.basename(filepath))
        self.actualizar_previews()
        messagebox.showinfo("Éxito", f"Se ha generado el archivo:\n{filepath}")

    def quitar_archivo(self, num: int):
        if num == 1:
            self.archivo1 = ""; self.hoja1 = None; self.lbl_a1.config(text="(Vacío)")
        else:
            self.archivo2 = ""; self.hoja2 = None; self.lbl_a2.config(text="(Vacío)")
        self.actualizar_previews()

    def actualizar_previews(self):
        self.preview_in.config(state="normal"); self.preview_in.delete("1.0", tk.END)
        if not self.archivo1 and not self.archivo2:
            self.preview_in.insert("1.0", "No hay archivos seleccionados.")
        else:
            if self.archivo1:
                d1 = leer_enteros_archivo(self.archivo1, self.hoja1)
                self.preview_in.insert(tk.END, f"[{os.path.basename(self.archivo1)}]: {d1}\n\n")
            if self.archivo2:
                d2 = leer_enteros_archivo(self.archivo2, self.hoja2)
                self.preview_in.insert(tk.END, f"[{os.path.basename(self.archivo2)}]: {d2}")
        self.preview_in.config(state="disabled")

        self.preview_out.config(state="normal"); self.preview_out.delete("1.0", tk.END)
        self.preview_out.insert("1.0", "Esperando ejecución de algoritmo..."); self.preview_out.config(state="disabled")

    def mostrar_resultado(self, maestro_path: str):
        self.preview_out.config(state="normal"); self.preview_out.delete("1.0", tk.END)
        if os.path.exists(maestro_path):
            d_out = leer_enteros_archivo(maestro_path)
            self.preview_out.insert("1.0", f"Total ordenados: {len(d_out)}\n\n")
            self.preview_out.insert(tk.END, ", ".join(map(str, d_out)))
        self.preview_out.config(state="disabled")

    def log(self, mensaje):
        self.log_txt.insert(tk.END, mensaje + "\n"); self.log_txt.see(tk.END)

    def ejecutar_algoritmo(self, func: Callable):
        if not self.archivo1 and not self.archivo2:
            messagebox.showwarning("Sin archivos", "Selecciona al menos 1 archivo para ordenar.")
            return

        self.btn_int.config(state="disabled"); self.btn_dir.config(state="disabled"); self.btn_eq.config(state="disabled")
        self.log_txt.delete("1.0", tk.END); self.log(f"Iniciando Combinación y {func.__name__}...")

        def tarea():
            t0 = time.perf_counter(); ext = self.combo_ext.get()
            func(self.archivo1, self.hoja1, self.archivo2, self.hoja2, ext, lambda m: self.after(0, self.log, m))
            tf = time.perf_counter()
            ruta_absoluta = os.path.abspath(f"resultado_ordenado{ext}")
            self.after(0, lambda: self.finalizar_ejecucion(tf - t0, ruta_absoluta))

        threading.Thread(target=tarea, daemon=True).start()

    def finalizar_ejecucion(self, tiempo: float, maestro_path: str):
        self.log(f"\n¡Operación en disco finalizada exitosamente! ({tiempo*1000:.2f} ms)")
        self.log(f"📍 ARCHIVO GUARDADO EN: {maestro_path}")
        self.mostrar_resultado(maestro_path)
        self.btn_int.config(state="normal"); self.btn_dir.config(state="normal"); self.btn_eq.config(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
