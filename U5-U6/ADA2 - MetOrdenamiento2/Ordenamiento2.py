"""
Métodos de Ordenamiento — Interfaz Gráfica
==========================================
Requiere: pip install PyQt5
Ejecutar:  python ordenamiento_gui.py
"""

import sys
import time
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSpinBox, QLineEdit,
    QTextEdit, QFrame, QScrollArea, QSizePolicy, QMessageBox,
    QGraphicsDropShadowEffect, QDialog
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QTimer, QRect
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QLinearGradient,
    QBrush, QPen, QFontDatabase
)


# ═══════════════════════════════════════════════════
#  ALGORITMOS DE ORDENAMIENTO
# ═══════════════════════════════════════════════════

def shell_sort(arr, log, add_step=lambda a, h: None):
    a = arr[:]
    n = len(a)
    gap = n // 2
    log(f"  Iniciando ShellSort  |  gap inicial = {gap}")
    add_step(a, [])
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                add_step(a, [j, j - gap])
                j -= gap
            a[j] = temp
            add_step(a, [j, i])
        log(f"  gap = {gap:>3}  →  {a}")
        gap //= 2
    add_step(a, [])
    return a


def quick_sort(arr, log, add_step=lambda a, h: None):
    a = arr[:]

    def _qs(a, lo, hi):
        if lo < hi:
            pivot = a[hi]
            i = lo - 1
            for j in range(lo, hi):
                add_step(a, [j, hi])
                if a[j] <= pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]
                    add_step(a, [i, j])
            a[i + 1], a[hi] = a[hi], a[i + 1]
            add_step(a, [i + 1, hi])
            pi = i + 1
            log(f"  pivot = {pivot:<4}  →  {a}")
            _qs(a, lo, pi - 1)
            _qs(a, pi + 1, hi)

    log("  Iniciando Quicksort")
    add_step(a, [])
    _qs(a, 0, len(a) - 1)
    add_step(a, [])
    return a


def heap_sort(arr, log, add_step=lambda a, h: None):
    a = arr[:]
    n = len(a)

    def _heapify(a, n, i):
        largest = i
        l, r = 2 * i + 1, 2 * i + 2
        add_step(a, [i, l if l<n else i, r if r<n else i])
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            add_step(a, [i, largest])
            _heapify(a, n, largest)

    log("  Iniciando Heapsort")
    add_step(a, [])
    for i in range(n // 2 - 1, -1, -1):
        _heapify(a, n, i)
    log(f"  Max-Heap:  {a}")
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        add_step(a, [0, i])
        _heapify(a, i, 0)
        log(f"  paso {n - i:>3}:  {a}")
    add_step(a, [])
    return a


def radix_sort(arr, log, add_step=lambda a, h: None):
    if any(x < 0 for x in arr):
        raise ValueError("Radix Sort solo admite enteros no negativos (≥ 0).")
    a = arr[:]
    max_val = max(a)
    log("  Iniciando Radix Sort")
    add_step(a, [])
    exp = 1
    while max_val // exp > 0:
        output = [0] * len(a)
        count = [0] * 10
        for num in a:
            count[(num // exp) % 10] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for i in range(len(a) - 1, -1, -1):
            idx = (a[i] // exp) % 10
            output[count[idx] - 1] = a[i]
            count[idx] -= 1
        a = output[:]
        add_step(a, [])
        log(f"  exp = {exp:<6}  →  {a}")
        exp *= 10
    return a


# ═══════════════════════════════════════════════════
#  HILO DE TRABAJO (no bloquea la UI)
# ═══════════════════════════════════════════════════

class SortWorker(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(list, float, list)
    error_signal = pyqtSignal(str)

    def __init__(self, method, numbers):
        super().__init__()
        self.method = method
        self.numbers = numbers

    def run(self):
        logs = []
        steps = []

        def log(msg):
            logs.append(msg)
            self.log_signal.emit(msg)

        def add_step(arr_state, highlight):
            steps.append((list(arr_state), list(highlight)))

        try:
            t0 = time.perf_counter()
            if self.method == "shell":
                result = shell_sort(self.numbers, log, add_step)
            elif self.method == "quick":
                result = quick_sort(self.numbers, log, add_step)
            elif self.method == "heap":
                result = heap_sort(self.numbers, log, add_step)
            else:
                result = radix_sort(self.numbers, log, add_step)
            elapsed = (time.perf_counter() - t0) * 1000
            self.done_signal.emit(result, elapsed, steps)
        except Exception as e:
            self.error_signal.emit(str(e))


# ═══════════════════════════════════════════════════
#  BARRA VISUAL DE NÚMEROS
# ═══════════════════════════════════════════════════

class BarChart(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []
        self.highlight = set()
        self.mode = "bars"
        self.setMinimumHeight(120)

    def set_mode(self, mode):
        self.mode = mode
        self.update()

    def set_data(self, data, highlight=None):
        self.data = data
        self.highlight = set(highlight or [])
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if getattr(self, 'mode', 'bars') == 'tree':
            self._draw_tree(painter)
            return

        w = self.width()
        h = self.height()
        n = len(self.data)
        max_val = max(self.data) if self.data else 1

        gap = 3
        bar_w = max(4, (w - gap * (n + 1)) // n)
        total_w = (bar_w + gap) * n + gap
        x_off = (w - total_w) // 2

        for i, val in enumerate(self.data):
            bar_h = int((val / max_val) * (h - 24))
            x = x_off + gap + i * (bar_w + gap)
            y = h - bar_h - 16

            if i in self.highlight:
                color = QColor("#F59E0B")
            else:
                ratio = i / max(n - 1, 1)
                r = int(30 + ratio * 60)
                g = int(120 + ratio * 40)
                b = int(220 - ratio * 40)
                color = QColor(r, g, b)

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 2, 2)

            if n <= 20 and bar_w >= 16:
                painter.setPen(QColor("#CBD5E1"))
                painter.setFont(QFont("Consolas", 8))
                painter.drawText(x, h - 2, str(val))

    def _draw_tree(self, painter):
        import math
        w = self.width()
        h = self.height()
        n = len(self.data)
        
        levels = math.floor(math.log2(n)) + 1 if n > 0 else 0
        r = 14
        if n > 15: r = 11
        if n > 31: r = 8
        
        v_gap = (h - 2*r - 20) / max(1, levels - 1) if levels > 1 else 0
        
        positions = {}
        
        def get_pos(i, left, right, level):
            if i >= n: return
            x = (left + right) / 2
            y = 10 + r + level * v_gap
            positions[i] = (x, y)
            get_pos(2*i + 1, left, x, level + 1)
            get_pos(2*i + 2, x, right, level + 1)
            
        get_pos(0, 0, w, 0)
        
        painter.setPen(QPen(QColor("#475569"), 2))
        for i in range(n):
            c1 = 2 * i + 1
            c2 = 2 * i + 2
            if c1 < n:
                x1, y1 = positions[i]
                x2, y2 = positions[c1]
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            if c2 < n:
                x1, y1 = positions[i]
                x2, y2 = positions[c2]
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
        font = QFont("Consolas", 8 if r < 12 else 10, QFont.Bold)
        painter.setFont(font)
        
        for i in range(n):
            x, y = positions[i]
            rect = QRect(int(x - r), int(y - r), int(2*r), int(2*r))
            
            val = self.data[i]
            ratio = i / max(n - 1, 1)
            
            if i in self.highlight:
                color = QColor("#F59E0B")
            else:
                rc = int(30 + ratio * 60)
                gc = int(120 + ratio * 40)
                bc = int(220 - ratio * 40)
                color = QColor(rc, gc, bc)
                
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#1E293B"), 2))
            painter.drawEllipse(rect)
            
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(rect, Qt.AlignCenter, str(val))


# ═══════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════

class MainWindow(QMainWindow):
    METHODS = {
        "shell": ("ShellSort",  "O(n log² n)",  "#3B82F6"),
        "quick": ("Quicksort",  "O(n log n)",   "#10B981"),
        "heap":  ("Heapsort",   "O(n log n)",   "#8B5CF6"),
        "radix": ("Radix Sort", "O(nk)",        "#F59E0B"),
    }

    def __init__(self):
        super().__init__()
        self.selected = None
        self.worker = None
        self.setWindowTitle("Métodos de Ordenamiento")
        self.setMinimumSize(860, 750)
        self.resize(880, 800)
        self._apply_theme()
        self._build_ui()

    # ── TEMA ──────────────────────────────────────
    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #0F172A; }
            QWidget { background: #0F172A; color: #E2E8F0; font-family: 'Segoe UI', sans-serif; }
            QLabel  { color: #E2E8F0; }
            QSpinBox, QLineEdit {
                background: #1E293B; border: 1px solid #334155;
                border-radius: 6px; padding: 6px 10px;
                color: #F1F5F9; font-size: 13px; font-family: Consolas;
            }
            QSpinBox:focus, QLineEdit:focus { border-color: #3B82F6; }
            QTextEdit {
                background: #0D1424; border: 1px solid #1E293B;
                border-radius: 8px; color: #94A3B8;
                font-family: Consolas; font-size: 12px; padding: 8px;
            }
            QScrollBar:vertical {
                background: #1E293B; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #334155; border-radius: 4px; min-height: 20px;
            }
            QPushButton {
                background: #1E293B; color: #94A3B8;
                border: 1px solid #334155; border-radius: 8px;
                padding: 8px 18px; font-size: 13px;
            }
            QPushButton:hover { background: #273549; color: #E2E8F0; }
            QPushButton:pressed { background: #1a2535; }
        """)

    # ── UI ────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(28, 16, 28, 16)
        main.setSpacing(12)

        # TÍTULO
        title = QLabel("Métodos de Ordenamiento")
        title.setFont(QFont("Segoe UI Semibold", 22, QFont.Bold))
        title.setStyleSheet("color: #F1F5F9; letter-spacing: 1px;")
        sub = QLabel("ShellSort · Quicksort · Heapsort · Radix Sort")
        sub.setStyleSheet("color: #64748B; font-size: 13px;")
        main.addWidget(title)
        main.addWidget(sub)

        # SELECTOR DE MÉTODO
        main.addWidget(self._section("Método de ordenamiento"))
        method_row = QHBoxLayout()
        method_row.setSpacing(10)
        self.method_btns = {}
        for key, (name, complexity, color) in self.METHODS.items():
            btn = self._method_card(key, name, complexity, color)
            method_row.addWidget(btn)
        main.addLayout(method_row)

        # ENTRADA
        main.addWidget(self._section("Números a ordenar"))
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        lbl_qty = QLabel("Cantidad:")
        lbl_qty.setStyleSheet("color:#94A3B8; font-size:13px;")
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(2, 30)
        self.qty_spin.setValue(8)
        self.qty_spin.setFixedWidth(80)
        self.qty_spin.valueChanged.connect(self._on_qty_change)

        lbl_nums = QLabel("Números (separados por coma o espacio):")
        lbl_nums.setStyleSheet("color:#94A3B8; font-size:13px;")
        self.nums_edit = QLineEdit()
        self.nums_edit.setPlaceholderText("ej:  45, 12, 87, 3, 56, 22, 9, 71")

        btn_random = self._action_btn("🎲  Aleatorio", "#334155")
        btn_random.clicked.connect(self._fill_random)

        input_row.addWidget(lbl_qty)
        input_row.addWidget(self.qty_spin)
        input_row.addSpacing(8)
        input_row.addWidget(lbl_nums)
        input_row.addWidget(self.nums_edit, 1)
        input_row.addWidget(btn_random)
        main.addLayout(input_row)

        # BARRA VISUAL
        self.bar = BarChart()
        self.bar.setFixedHeight(110)
        self.nums_edit.textChanged.connect(self._update_bar)
        main.addWidget(self.bar)

        # BOTONES ACCIÓN
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self.btn_sort = QPushButton("▶  Ordenar")
        self.btn_sort.setStyleSheet("""
            QPushButton { background: #2563EB; color: #EFF6FF;
                border: none; border-radius: 8px; padding: 10px 28px;
                font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: #1D4ED8; }
            QPushButton:pressed { background: #1E40AF; }
            QPushButton:disabled { background: #1E293B; color: #475569; }
        """)
        self.btn_sort.clicked.connect(self._run_sort)

        btn_clear = self._action_btn("🗑  Limpiar", "#1E293B")
        btn_clear.clicked.connect(self._clear_output)

        btn_reset = self._action_btn("↺  Reiniciar", "#1E293B")
        btn_reset.clicked.connect(self._reset)

        self.btn_compare = self._action_btn("📊 Comparar Todos", "#312E81")
        self.btn_compare.clicked.connect(self._run_comparison)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color:#64748B; font-size:12px;")

        action_row.addWidget(self.btn_sort)
        action_row.addWidget(self.btn_compare)
        action_row.addWidget(btn_clear)
        action_row.addWidget(btn_reset)
        action_row.addStretch()
        action_row.addWidget(self.status_lbl)
        main.addLayout(action_row)

        # SALIDA
        main.addWidget(self._section("Resultado y pasos"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(120)
        self.output.setPlaceholderText("Aquí aparecerán los pasos del algoritmo y el resultado final...")
        main.addWidget(self.output, 1)

        # RESULTADO FINAL
        res_row = QHBoxLayout()
        self.result_lbl = QLabel(self)
        self.result_lbl.setFont(QFont("Consolas", 13))
        self.result_lbl.setStyleSheet("""
            color: #34D399; background: #052e16;
            border-radius: 8px; padding: 10px 16px;
            border: 1px solid #065f46;
        """)
        self.result_lbl.setWordWrap(True)
        self.result_lbl.hide()
        res_row.addWidget(self.result_lbl, 1)
        main.addLayout(res_row)

        # Generar números aleatorios al inicio
        self._fill_random()

    # ── WIDGETS HELPER ────────────────────────────
    def _section(self, text):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet("color:#475569; font-size:11px; letter-spacing:1.5px; font-weight:600;")
        return lbl

    def _action_btn(self, text, bg):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{ background:{bg}; color:#94A3B8;
                border:1px solid #334155; border-radius:8px; padding:8px 16px; font-size:13px; }}
            QPushButton:hover {{ color:#E2E8F0; background:#273549; }}
        """)
        return btn

    def _method_card(self, key, name, complexity, color):
        btn = QPushButton(f"{name}\n{complexity}")
        btn.setCheckable(True)
        btn.setFixedHeight(70)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:#1E293B; color:#94A3B8;
                border:1px solid #334155; border-radius:10px;
                font-size:13px; font-family:'Segoe UI';
                text-align:center; padding:8px;
            }}
            QPushButton:hover {{ background:#273549; color:#E2E8F0; border-color:{color}; }}
            QPushButton:checked {{
                background:{color}22; color:{color};
                border:2px solid {color}; font-weight:600;
            }}
        """)
        btn.clicked.connect(lambda _, k=key: self._select_method(k))
        self.method_btns[key] = btn
        return btn

    # ── LÓGICA UI ─────────────────────────────────
    def _select_method(self, key):
        self.selected = key
        for k, b in self.method_btns.items():
            b.setChecked(k == key)
        self.bar.set_mode("tree" if key == "heap" else "bars")

    def _on_qty_change(self, val):
        nums = self._parse_numbers()
        if len(nums) != val:
            self._fill_random()

    def _fill_random(self):
        qty = self.qty_spin.value()
        nums = [random.randint(1, 99) for _ in range(qty)]
        self.nums_edit.setText(", ".join(map(str, nums)))

    def _parse_numbers(self):
        text = self.nums_edit.text().replace(",", " ")
        parts = text.split()
        nums = []
        for p in parts:
            try:
                nums.append(int(p))
            except ValueError:
                pass
        return nums

    def _update_bar(self):
        nums = self._parse_numbers()
        if nums:
            self.bar.set_data(nums)

    def _clear_output(self):
        self.output.clear()
        self.result_lbl.hide()
        self.status_lbl.setText("")

    def _reset(self):
        self._clear_output()
        for b in self.method_btns.values():
            b.setChecked(False)
        self.selected = None
        self.qty_spin.setValue(8)
        self._fill_random()

    # ── ORDENAMIENTO ──────────────────────────────
    def _run_sort(self):
        if not self.selected:
            QMessageBox.warning(self, "Sin método",
                "Por favor selecciona un método de ordenamiento.")
            return

        nums = self._parse_numbers()
        if len(nums) < 2:
            QMessageBox.warning(self, "Pocos números",
                "Ingresa al menos 2 números válidos.")
            return

        self.btn_sort.setEnabled(False)
        self.result_lbl.hide()
        self.output.clear()
        name = self.METHODS[self.selected][0]
        color = self.METHODS[self.selected][2]

        self._log(f"{'─'*50}", "#334155")
        self._log(f"  Método:   {name}", color)
        self._log(f"  Entrada:  {nums}", "#94A3B8")
        self._log(f"{'─'*50}", "#334155")

        self.worker = SortWorker(self.selected, nums)
        self.worker.log_signal.connect(lambda m: self._log(m, "#64748B"))
        self.worker.done_signal.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _log(self, msg, color="#64748B"):
        self.output.setTextColor(QColor(color))
        self.output.append(msg)

    def _on_done(self, result, elapsed, steps):
        self.animation_steps = steps
        self.animation_current = 0
        self.animation_result = result
        self.animation_elapsed = elapsed
        self.animation_name = self.METHODS[self.selected][0]
        self.animation_color = self.METHODS[self.selected][2]
        
        self.status_lbl.setText(f"Animando {len(steps)} pasos...")
        
        delay = 500 if len(steps) < 20 else max(20, int(2000 / max(1, len(steps))))
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate_step)
        self.anim_timer.start(delay)

    def _animate_step(self):
        if self.animation_current < len(self.animation_steps):
            arr, highlight = self.animation_steps[self.animation_current]
            self.bar.set_data(arr, highlight)
            self.animation_current += 1
        else:
            self.anim_timer.stop()
            self._finish_animation()
            
    def _finish_animation(self):
        self._log(f"{'─'*50}", "#334155")
        self._log(f"  Ordenado: {self.animation_result}", self.animation_color)
        self._log(f"  Tiempo:   {self.animation_elapsed:.3f} ms", "#475569")
        self._log(f"{'─'*50}", "#334155")

        self.result_lbl.setText(f"✓  {self.animation_name}  →  {self.animation_result}")
        self.result_lbl.show()
        self.bar.set_data(self.animation_result)
        self.status_lbl.setText(f"Completado en {self.animation_elapsed:.3f} ms")
        self.btn_sort.setEnabled(True)
        if hasattr(self, 'btn_compare'):
            self.btn_compare.setEnabled(True)

    def _run_comparison(self):
        nums = self._parse_numbers()
        if len(nums) < 2:
            QMessageBox.warning(self, "Pocos números", "Ingresa al menos 2 números válidos.")
            return
            
        dialog = ComparativeDialog(nums, self)
        dialog.exec_()

    def _on_error(self, msg):
        self._log(f"\n  ⚠ Error: {msg}", "#F87171")
        self.btn_sort.setEnabled(True)
        if hasattr(self, 'btn_compare'):
            self.btn_compare.setEnabled(True)
        self.status_lbl.setText("Error al ordenar")


# ═══════════════════════════════════════════════════
#  DIÁLOGO COMPARATIVO
# ═══════════════════════════════════════════════════

class ComparisonChart(QWidget):
    def __init__(self, results):
        super().__init__()
        self.results = results
        
    def paintEvent(self, event):
        if not self.results: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        max_time = max(t for t, _ in self.results.values())
        if max_time == 0: max_time = 1
        
        n = len(self.results)
        gap = 40
        bar_w = (w - gap * (n + 1)) // n
        
        x_off = gap
        
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(x_off, h - 30, w - x_off, h - 30)
        
        for i, (name, (time_ms, color_hex)) in enumerate(self.results.items()):
            bar_h = int((time_ms / max_time) * (h - 80))
            x = x_off + i * (bar_w + gap)
            y = h - 30 - bar_h
            
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)
            
            painter.setPen(QColor("#E2E8F0"))
            painter.setFont(QFont("Consolas", 10, QFont.Bold))
            text = f"{time_ms:.4f} ms"
            fm = painter.fontMetrics()
            painter.drawText(x + (bar_w - fm.width(text)) // 2, y - 8, text)
            
            painter.setPen(QColor("#94A3B8"))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(x + (bar_w - fm.width(name)) // 2, h - 10, name)

class ComparativeDialog(QDialog):
    def __init__(self, numbers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparativa de Tiempos")
        self.setMinimumSize(600, 400)
        if parent:
            self.setStyleSheet(parent.styleSheet())
        self.numbers = numbers
        self.results = {}
        self._run_all()
        self._build_ui()
        
    def _run_all(self):
        def dummy_log(msg): pass
        def dummy_step(arr, h): pass
        
        methods = {
            "shell": (shell_sort, "ShellSort", "#3B82F6"),
            "quick": (quick_sort, "Quicksort", "#10B981"),
            "heap":  (heap_sort,  "Heapsort",  "#8B5CF6"),
            "radix": (radix_sort, "Radix Sort", "#F59E0B"),
        }
        
        for key, (func, name, color) in methods.items():
            arr_copy = self.numbers[:]
            t0 = time.perf_counter()
            func(arr_copy, dummy_log, dummy_step)
            elapsed = (time.perf_counter() - t0) * 1000
            self.results[name] = (elapsed, color)
            
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(f"Resultados para {len(self.numbers)} elementos")
        title.setFont(QFont("Segoe UI Semibold", 16))
        layout.addWidget(title)
        
        chart = ComparisonChart(self.results)
        layout.addWidget(chart, 1)


# ═══════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Métodos de Ordenamiento")

    # Fuente base
    app.setFont(QFont("Segoe UI", 11))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())