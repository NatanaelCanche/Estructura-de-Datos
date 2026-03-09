"""
Sistema de Control Escolar - Interfaz Gráfica
Programación Orientada a Objetos en Python
Funcionalidades: Gestión de alumnos, docentes, materias, calificaciones y horarios con persistencia de datos
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont


class Persona:
    """Clase base para Alumno y Docente"""
    
    def __init__(self, id: str, nombre: str, apellido: str, fecha_nacimiento: str, telefono: str):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
    
    def get_nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'fecha_nacimiento': self.fecha_nacimiento,
            'telefono': self.telefono
        }


class Alumno(Persona):
    """Clase Alumno que hereda de Persona"""
    
    def __init__(self, id: str, nombre: str, apellido: str, fecha_nacimiento: str, 
                 telefono: str, matricula: str, grado: str, grupo: str, activo: bool = True):
        super().__init__(id, nombre, apellido, fecha_nacimiento, telefono)
        self.matricula = matricula
        self.grado = grado
        self.grupo = grupo
        self.activo = activo
        self.fecha_alta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_baja = None
    
    def dar_de_baja(self):
        """Dar de baja al alumno"""
        self.activo = False
        self.fecha_baja = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'matricula': self.matricula,
            'grado': self.grado,
            'grupo': self.grupo,
            'activo': self.activo,
            'fecha_alta': self.fecha_alta,
            'fecha_baja': self.fecha_baja
        })
        return data
    
    @staticmethod
    def from_dict(data: Dict) -> 'Alumno':
        alumno = Alumno(
            data['id'],
            data['nombre'],
            data['apellido'],
            data['fecha_nacimiento'],
            data['telefono'],
            data['matricula'],
            data['grado'],
            data['grupo'],
            data['activo']
        )
        alumno.fecha_alta = data.get('fecha_alta', alumno.fecha_alta)
        alumno.fecha_baja = data.get('fecha_baja')
        return alumno


class Docente(Persona):
    """Clase Docente que hereda de Persona"""
    
    def __init__(self, id: str, nombre: str, apellido: str, fecha_nacimiento: str,
                 telefono: str, num_empleado: str, especialidad: str, email: str):
        super().__init__(id, nombre, apellido, fecha_nacimiento, telefono)
        self.num_empleado = num_empleado
        self.especialidad = especialidad
        self.email = email
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'num_empleado': self.num_empleado,
            'especialidad': self.especialidad,
            'email': self.email
        })
        return data
    
    @staticmethod
    def from_dict(data: Dict) -> 'Docente':
        return Docente(
            data['id'],
            data['nombre'],
            data['apellido'],
            data['fecha_nacimiento'],
            data['telefono'],
            data['num_empleado'],
            data['especialidad'],
            data['email']
        )


class Materia:
    """Clase para gestionar materias"""
    
    def __init__(self, id: str, nombre: str, grado: str, descripcion: str = ""):
        self.id = id
        self.nombre = nombre
        self.grado = grado
        self.descripcion = descripcion
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nombre': self.nombre,
            'grado': self.grado,
            'descripcion': self.descripcion
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Materia':
        return Materia(
            data['id'],
            data['nombre'],
            data['grado'],
            data.get('descripcion', '')
        )


class Calificacion:
    """Clase para gestionar calificaciones de alumnos"""
    
    def __init__(self, id: str, matricula_alumno: str, materia_id: str, 
                 semestre: str, calificacion: float, fecha_registro: str = None):
        self.id = id
        self.matricula_alumno = matricula_alumno
        self.materia_id = materia_id
        self.semestre = semestre
        self.calificacion = calificacion
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'matricula_alumno': self.matricula_alumno,
            'materia_id': self.materia_id,
            'semestre': self.semestre,
            'calificacion': self.calificacion,
            'fecha_registro': self.fecha_registro
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Calificacion':
        return Calificacion(
            data['id'],
            data['matricula_alumno'],
            data['materia_id'],
            data['semestre'],
            data['calificacion'],
            data.get('fecha_registro')
        )


class Horario:
    """Clase para gestionar horarios de clases"""
    
    def __init__(self, id: str, materia_id: str, docente_id: str, grado: str, 
                 grupo: str, dia: str, hora_inicio: str, hora_fin: str, aula: str):
        self.id = id
        self.materia_id = materia_id
        self.docente_id = docente_id
        self.grado = grado
        self.grupo = grupo
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula = aula
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'materia_id': self.materia_id,
            'docente_id': self.docente_id,
            'grado': self.grado,
            'grupo': self.grupo,
            'dia': self.dia,
            'hora_inicio': self.hora_inicio,
            'hora_fin': self.hora_fin,
            'aula': self.aula
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Horario':
        return Horario(
            data['id'],
            data['materia_id'],
            data['docente_id'],
            data['grado'],
            data['grupo'],
            data['dia'],
            data['hora_inicio'],
            data['hora_fin'],
            data['aula']
        )


class SistemaControlEscolar:
    """Sistema principal de Control Escolar"""
    
    def __init__(self, archivo_datos: str = "datos_escuela.json"):
        self.archivo_datos = archivo_datos
        self.alumnos: Dict[str, Alumno] = {}
        self.docentes: Dict[str, Docente] = {}
        self.materias: Dict[str, Materia] = {}
        self.calificaciones: Dict[str, Calificacion] = {}
        self.horarios: Dict[str, Horario] = {}
        self.cargar_datos()
    
    def cargar_datos(self):
        """Cargar datos desde archivo JSON"""
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    
                    # Cargar alumnos
                    for alumno_data in datos.get('alumnos', []):
                        alumno = Alumno.from_dict(alumno_data)
                        matricula_str = str(alumno.matricula).strip()
                        self.alumnos[matricula_str] = alumno
                    
                    # Cargar docentes
                    for docente_data in datos.get('docentes', []):
                        docente = Docente.from_dict(docente_data)
                        num_emp_str = str(docente.num_empleado).strip()
                        self.docentes[num_emp_str] = docente
                    
                    # Cargar materias
                    for materia_data in datos.get('materias', []):
                        materia = Materia.from_dict(materia_data)
                        self.materias[materia.id] = materia
                    
                    # Cargar calificaciones
                    for calif_data in datos.get('calificaciones', []):
                        calificacion = Calificacion.from_dict(calif_data)
                        self.calificaciones[calificacion.id] = calificacion
                    
                    # Cargar horarios
                    for horario_data in datos.get('horarios', []):
                        horario = Horario.from_dict(horario_data)
                        self.horarios[horario.id] = horario
                
            except Exception as e:
                print(f"Error al cargar datos: {e}")
    
    def guardar_datos(self):
        """Guardar todos los datos en archivo JSON"""
        datos = {
            'alumnos': [alumno.to_dict() for alumno in self.alumnos.values()],
            'docentes': [docente.to_dict() for docente in self.docentes.values()],
            'materias': [materia.to_dict() for materia in self.materias.values()],
            'calificaciones': [calif.to_dict() for calif in self.calificaciones.values()],
            'horarios': [horario.to_dict() for horario in self.horarios.values()]
        }
        
        try:
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al guardar datos: {e}")
    
    def dar_alta_alumno(self, nombre: str, apellido: str, fecha_nacimiento: str,
                        telefono: str, matricula: str, grado: str, grupo: str):
        """Dar de alta un nuevo alumno"""
        matricula = str(matricula).strip()
        
        if matricula in self.alumnos:
            return False, f"Ya existe un alumno con matrícula {matricula}"
        
        alumno = Alumno(
            id=matricula,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            matricula=matricula,
            grado=grado,
            grupo=grupo
        )
        
        self.alumnos[matricula] = alumno
        self.guardar_datos()
        return True, f"Alumno {alumno.get_nombre_completo()} dado de alta exitosamente"
    
    def dar_baja_alumno(self, matricula: str):
        """Dar de baja a un alumno"""
        matricula = str(matricula).strip()
        
        if matricula not in self.alumnos:
            return False, f"No se encontró alumno con matrícula {matricula}"
        
        alumno = self.alumnos[matricula]
        
        if not alumno.activo:
            return False, f"El alumno {alumno.get_nombre_completo()} ya está dado de baja"
        
        alumno.dar_de_baja()
        self.guardar_datos()
        return True, f"Alumno {alumno.get_nombre_completo()} dado de baja exitosamente"
    
    def agregar_docente(self, nombre: str, apellido: str, fecha_nacimiento: str,
                       telefono: str, num_empleado: str, especialidad: str, email: str):
        """Agregar un nuevo docente"""
        if num_empleado in self.docentes:
            return False, f"Ya existe un docente con número de empleado {num_empleado}"
        
        docente = Docente(
            id=num_empleado,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            num_empleado=num_empleado,
            especialidad=especialidad,
            email=email
        )
        
        self.docentes[num_empleado] = docente
        self.guardar_datos()
        return True, f"Docente {docente.get_nombre_completo()} agregado exitosamente"
    
    def agregar_materia(self, id: str, nombre: str, grado: str, descripcion: str = ""):
        """Agregar una nueva materia"""
        if id in self.materias:
            return False, f"Ya existe una materia con ID {id}"
        
        materia = Materia(id, nombre, grado, descripcion)
        self.materias[id] = materia
        self.guardar_datos()
        return True, f"Materia {nombre} agregada exitosamente"
    
    def registrar_calificacion(self, matricula_alumno: str, materia_id: str, 
                              semestre: str, calificacion: float):
        """Registrar una calificación para un alumno"""
        if matricula_alumno not in self.alumnos:
            return False, f"No existe alumno con matrícula {matricula_alumno}"
        
        if not self.alumnos[matricula_alumno].activo:
            return False, f"El alumno está dado de baja"
        
        if materia_id not in self.materias:
            return False, f"No existe materia con ID {materia_id}"
        
        # Verificar si ya existe una calificación para este alumno, materia y semestre
        for calif in self.calificaciones.values():
            if (calif.matricula_alumno == matricula_alumno and 
                calif.materia_id == materia_id and 
                calif.semestre == semestre):
                return False, f"Ya existe una calificación para este alumno en {semestre}"
        
        # Generar ID único para la calificación
        calif_id = f"{matricula_alumno}_{materia_id}_{semestre}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        calificacion_obj = Calificacion(
            calif_id,
            matricula_alumno,
            materia_id,
            semestre,
            calificacion
        )
        
        self.calificaciones[calif_id] = calificacion_obj
        self.guardar_datos()
        return True, f"Calificación registrada exitosamente"
    
    def agregar_horario(self, id: str, materia_id: str, docente_id: str, grado: str,
                       grupo: str, dia: str, hora_inicio: str, hora_fin: str, aula: str):
        """Agregar un nuevo horario"""
        if id in self.horarios:
            return False, f"Ya existe un horario con ID {id}"
        
        if docente_id not in self.docentes:
            return False, f"No existe docente con número de empleado {docente_id}"
        
        if materia_id not in self.materias:
            return False, f"No existe materia con ID {materia_id}"
        
        horario = Horario(id, materia_id, docente_id, grado, grupo, dia, hora_inicio, hora_fin, aula)
        self.horarios[id] = horario
        self.guardar_datos()
        return True, "Horario agregado exitosamente"
    
    def obtener_calificaciones_alumno(self, matricula: str) -> List[Calificacion]:
        """Obtener todas las calificaciones de un alumno"""
        return [c for c in self.calificaciones.values() if c.matricula_alumno == matricula]
    
    def obtener_promedio_alumno(self, matricula: str) -> float:
        """Calcular el promedio de calificaciones de un alumno"""
        calificaciones = self.obtener_calificaciones_alumno(matricula)
        if not calificaciones:
            return 0.0
        return sum(c.calificacion for c in calificaciones) / len(calificaciones)
    
    def buscar_alumnos(self, termino: str = "", solo_activos: bool = True) -> List[Alumno]:
        """Buscar alumnos por matrícula, nombre o apellido"""
        termino = termino.lower().strip()
        resultados = []
        
        for alumno in self.alumnos.values():
            if solo_activos and not alumno.activo:
                continue
            
            if not termino:
                resultados.append(alumno)
            elif (termino in alumno.matricula.lower() or
                  termino in alumno.nombre.lower() or
                  termino in alumno.apellido.lower() or
                  termino in alumno.get_nombre_completo().lower()):
                resultados.append(alumno)
        
        return resultados
    
    def buscar_docentes(self, termino: str = "") -> List[Docente]:
        """Buscar docentes por número de empleado, nombre, apellido o especialidad"""
        termino = termino.lower().strip()
        resultados = []
        
        for docente in self.docentes.values():
            if not termino:
                resultados.append(docente)
            elif (termino in docente.num_empleado.lower() or
                  termino in docente.nombre.lower() or
                  termino in docente.apellido.lower() or
                  termino in docente.get_nombre_completo().lower() or
                  termino in docente.especialidad.lower() or
                  termino in docente.email.lower()):
                resultados.append(docente)
        
        return resultados
    
    def buscar_materias(self, termino: str = "") -> List[Materia]:
        """Buscar materias por ID, nombre, grado o descripción"""
        termino = termino.lower().strip()
        resultados = []
        
        for materia in self.materias.values():
            if not termino:
                resultados.append(materia)
            elif (termino in materia.id.lower() or
                  termino in materia.nombre.lower() or
                  termino in materia.grado.lower() or
                  termino in materia.descripcion.lower()):
                resultados.append(materia)
        
        return resultados
    
    def obtener_grupos_disponibles(self) -> List[tuple]:
        """Obtener lista de grupos disponibles con grado y grupo"""
        grupos = set()
        for alumno in self.alumnos.values():
            if alumno.activo:
                grupos.add((alumno.grado, alumno.grupo))
        return sorted(list(grupos), key=lambda x: (x[0], x[1]))
    
    def obtener_alumnos_por_grupo(self, grado: str, grupo: str) -> List[Alumno]:
        """Obtener todos los alumnos activos de un grupo específico"""
        return [a for a in self.alumnos.values() 
                if a.activo and a.grado == grado and a.grupo == grupo]
    
    def obtener_horarios_por_grupo(self, grado: str, grupo: str) -> List[Horario]:
        """Obtener todos los horarios de un grupo específico"""
        return [h for h in self.horarios.values() if h.grado == grado and h.grupo == grupo]
    
    def obtener_horarios_por_docente(self, docente_id: str) -> List[Horario]:
        """Obtener todos los horarios de un docente específico"""
        return [h for h in self.horarios.values() if h.docente_id == docente_id]


class SistemaEscolarGUI:
    """Interfaz gráfica del Sistema de Control Escolar"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control Escolar")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        # Sistema de datos
        self.sistema = SistemaControlEscolar()
        
        # Colores del tema
        self.colors = {
            'primary': '#2E3B55',
            'secondary': '#5C7CFA',
            'accent': '#4C6EF5',
            'success': '#51CF66',
            'danger': '#FF6B6B',
            'warning': '#FFA94D',
            'info': '#4ECDC4',
            'background': '#F8F9FA',
            'surface': '#FFFFFF',
            'text': '#212529',
            'text_light': '#6C757D',
            'border': '#DEE2E6',
            'table_header': '#4472C4',
            'table_alt': '#F2F2F2'
        }
        
        # Días de la semana en orden
        self.dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        
        # Configurar estilo
        self.configurar_estilos()
        
        # Configurar ventana principal
        self.root.configure(bg=self.colors['background'])
        
        # Crear interfaz
        self.crear_interfaz()
    
    def configurar_estilos(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para botones
        style.configure('Primary.TButton',
                       background=self.colors['secondary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10,
                       font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', self.colors['accent'])])
        
        # Estilo para frames
        style.configure('Card.TFrame',
                       background=self.colors['surface'],
                       relief='flat')
        
        # Estilo para labels
        style.configure('Title.TLabel',
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Segoe UI', 16, 'bold'),
                       padding=15)
        
        style.configure('Subtitle.TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 12, 'bold'),
                       padding=8)
        
        style.configure('Normal.TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10))
        
        # Estilo para Treeview con líneas divisorias
        style.configure('Treeview',
                       background='white',
                       foreground=self.colors['text'],
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 10))
        style.configure('Treeview.Heading',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Treeview.Heading',
                 background=[('active', self.colors['accent'])])
        style.configure('Treeview', rowheight=35)
        
        # Configurar líneas divisorias en el Treeview
        style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
    
    def crear_interfaz(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(main_container, bg=self.colors['primary'], height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        title_label = ttk.Label(header, 
                               text="🎓 Sistema de Control Escolar",
                               style='Title.TLabel')
        title_label.pack(side='left', padx=20)
        
        # Frame de contenido
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Menú con scrollbar
        left_panel_container = tk.Frame(content_frame, bg=self.colors['background'])
        left_panel_container.pack(side='left', fill='y', padx=(0, 10))
        
        # Canvas para scroll en el menú
        canvas_menu = tk.Canvas(left_panel_container, bg=self.colors['surface'], highlightthickness=0, width=280)
        scrollbar_menu = ttk.Scrollbar(left_panel_container, orient="vertical", command=canvas_menu.yview)
        
        scrollable_menu_frame = ttk.Frame(canvas_menu, style='Card.TFrame')
        scrollable_menu_frame.bind(
            "<Configure>",
            lambda e: canvas_menu.configure(scrollregion=canvas_menu.bbox("all"))
        )
        
        canvas_menu.create_window((0, 0), window=scrollable_menu_frame, anchor="nw")
        canvas_menu.configure(yscrollcommand=scrollbar_menu.set, width=280, height=650)
        
        canvas_menu.pack(side="left", fill="y", expand=False)
        scrollbar_menu.pack(side="right", fill="y")
        
        # Crear menú en el frame desplazable
        self.crear_menu(scrollable_menu_frame)
        
        # Panel derecho - Contenido
        self.right_panel = ttk.Frame(content_frame, style='Card.TFrame')
        self.right_panel.pack(side='right', fill='both', expand=True)
        
        # Configurar scroll del canvas para usar la rueda del ratón
        def _on_mousewheel(event):
            canvas_menu.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas_menu.bind("<MouseWheel>", _on_mousewheel)
        
        # Mostrar pantalla inicial
        self.mostrar_inicio()
    
    def crear_menu(self, parent):
        """Crear menú lateral"""
        menu_title = ttk.Label(parent, 
                              text="Menú Principal",
                              style='Subtitle.TLabel')
        menu_title.pack(fill='x', pady=(10, 20))
        
        # SECCIÓN DASHBOARD
        tk.Label(parent, text="📊 DASHBOARD", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(5, 5))
        
        self.crear_boton_menu(parent, "📊 Dashboard", self.mostrar_inicio)
        
        # SECCIÓN ALUMNOS
        tk.Label(parent, text="👥 ALUMNOS", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        botones_alumnos = [
            ("➕ Alta Alumno", self.mostrar_alta_alumno),
            ("➖ Baja Alumno", self.mostrar_baja_alumno),
            ("👥 Lista Alumnos", self.mostrar_lista_alumnos),
            ("👥 Ver Grupos", self.mostrar_grupos),
        ]
        
        for texto, comando in botones_alumnos:
            self.crear_boton_menu(parent, texto, comando)
        
        # SECCIÓN DOCENTES
        tk.Label(parent, text="👨‍🏫 DOCENTES", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        botones_docentes = [
            ("➕ Agregar Docente", self.mostrar_agregar_docente),
            ("📋 Lista Docentes", self.mostrar_lista_docentes),
        ]
        
        for texto, comando in botones_docentes:
            self.crear_boton_menu(parent, texto, comando)
        
        # SECCIÓN MATERIAS
        tk.Label(parent, text="📚 MATERIAS", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        botones_materias = [
            ("📖 Agregar Materia", self.mostrar_agregar_materia),
            ("📋 Lista Materias", self.mostrar_lista_materias),
        ]
        
        for texto, comando in botones_materias:
            self.crear_boton_menu(parent, texto, comando)
        
        # SECCIÓN CALIFICACIONES - SIMPLIFICADA
        tk.Label(parent, text="📝 CALIFICACIONES", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        botones_calificaciones = [
            ("✏️ Registrar Calificación", self.mostrar_registrar_calificacion),
            ("🔍 Buscar Calificaciones", self.mostrar_ver_calificaciones_con_buscador),
            ("📄 Boletín de Calificaciones", self.mostrar_boletin_alumno),
        ]
        
        for texto, comando in botones_calificaciones:
            self.crear_boton_menu(parent, texto, comando)
        
        # SECCIÓN HORARIOS - SIMPLIFICADA
        tk.Label(parent, text="🕐 HORARIOS", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        botones_horarios = [
            ("➕ Agregar Horario", self.mostrar_agregar_horario),
            ("🔍 Buscar Horarios", self.mostrar_buscar_horarios),
        ]
        
        for texto, comando in botones_horarios:
            self.crear_boton_menu(parent, texto, comando)
        
        # SECCIÓN REPORTES
        tk.Label(parent, text="📊 REPORTES", 
                bg=self.colors['surface'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        botones_reportes = [
            ("📈 Estadísticas Generales", self.mostrar_inicio),
        ]
        
        for texto, comando in botones_reportes:
            self.crear_boton_menu(parent, texto, comando)
    
    def crear_boton_menu(self, parent, texto, comando):
        """Crear botón de menú con estilo"""
        btn = tk.Button(parent,
                      text=texto,
                      command=comando,
                      bg=self.colors['surface'],
                      fg=self.colors['text'],
                      activebackground=self.colors['secondary'],
                      activeforeground='white',
                      relief='flat',
                      font=('Segoe UI', 10),
                      anchor='w',
                      padx=20,
                      pady=8,
                      cursor='hand2',
                      borderwidth=0)
        btn.pack(fill='x', pady=2, padx=15)
        
        # Efecto hover
        btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.colors['secondary'], fg='white'))
        btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.colors['surface'], fg=self.colors['text']))
    
    def limpiar_panel(self):
        """Limpiar el panel derecho"""
        for widget in self.right_panel.winfo_children():
            widget.destroy()
    
    def configurar_treeview_con_lineas(self, tree):
        """Configurar Treeview con líneas divisorias"""
        style = ttk.Style()
        style.configure('Treeview', 
                       borderwidth=1, 
                       relief='solid',
                       font=('Segoe UI', 10))
        style.configure('Treeview.Heading', 
                       borderwidth=1, 
                       relief='solid',
                       font=('Segoe UI', 10, 'bold'))
        tree.configure(show='headings')
        tree.configure(style='Treeview')
    
    def mostrar_inicio(self):
        """Mostrar pantalla de inicio con estadísticas"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="📊 Dashboard",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        stats_container = tk.Frame(self.right_panel, bg=self.colors['surface'])
        stats_container.pack(fill='both', expand=True, padx=30, pady=10)
        
        alumnos_activos = sum(1 for a in self.sistema.alumnos.values() if a.activo)
        total_docentes = len(self.sistema.docentes)
        total_materias = len(self.sistema.materias)
        total_horarios = len(self.sistema.horarios)
        total_calificaciones = len(self.sistema.calificaciones)
        total_grupos = len(self.sistema.obtener_grupos_disponibles())
        
        stats1 = [
            ("👥 Alumnos Activos", alumnos_activos, self.colors['secondary']),
            ("👨‍🏫 Docentes", total_docentes, self.colors['success']),
            ("📚 Materias", total_materias, self.colors['info']),
        ]
        
        for i, (titulo, valor, color) in enumerate(stats1):
            card = tk.Frame(stats_container, bg=color, relief='flat', bd=0)
            card.grid(row=0, column=i, padx=15, pady=20, sticky='nsew')
            stats_container.columnconfigure(i, weight=1)
            
            tk.Label(card,
                    text=titulo,
                    bg=color,
                    fg='white',
                    font=('Segoe UI', 12, 'bold'),
                    pady=15).pack()
            
            tk.Label(card,
                    text=str(valor),
                    bg=color,
                    fg='white',
                    font=('Segoe UI', 36, 'bold'),
                    pady=10).pack()
        
        stats2 = [
            ("📅 Horarios", total_horarios, self.colors['warning']),
            ("📝 Calificaciones", total_calificaciones, self.colors['accent']),
            ("👥 Grupos", total_grupos, self.colors['primary']),
        ]
        
        for i, (titulo, valor, color) in enumerate(stats2):
            card = tk.Frame(stats_container, bg=color, relief='flat', bd=0)
            card.grid(row=1, column=i, padx=15, pady=20, sticky='nsew')
            stats_container.columnconfigure(i, weight=1)
            
            tk.Label(card,
                    text=titulo,
                    bg=color,
                    fg='white',
                    font=('Segoe UI', 12, 'bold'),
                    pady=15).pack()
            
            tk.Label(card,
                    text=str(valor),
                    bg=color,
                    fg='white',
                    font=('Segoe UI', 36, 'bold'),
                    pady=10).pack()
        
        info_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        info_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        welcome_text = """
        Bienvenido al Sistema de Control Escolar
        
        ✨ Gestiona alumnos, docentes, materias, calificaciones y horarios de manera eficiente
        💾 Todos los datos se guardan automáticamente
        📊 Consulta estadísticas y reportes en tiempo real
        🔍 Busca calificaciones de alumnos por nombre o matrícula
        📅 Visualiza horarios en formato de tabla estilo horario escolar
        👥 Consulta grupos y sus horarios
        
        Selecciona una opción del menú para comenzar.
        """
        
        tk.Label(info_frame,
                text=welcome_text,
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 11),
                justify='left').pack(pady=20)
    
    def mostrar_alta_alumno(self):
        """Mostrar formulario para dar de alta un alumno"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="➕ Dar de Alta Alumno",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        form_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        form_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        campos = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Fecha de Nacimiento (DD/MM/AAAA):", "fecha_nac"),
            ("Teléfono:", "telefono"),
            ("Matrícula:", "matricula"),
            ("Grado:", "grado"),
            ("Grupo:", "grupo")
        ]
        
        entries = {}
        
        for i, (label, key) in enumerate(campos):
            tk.Label(form_frame,
                    text=label,
                    bg=self.colors['surface'],
                    fg=self.colors['text'],
                    font=('Segoe UI', 10, 'bold'),
                    anchor='w').grid(row=i, column=0, sticky='w', pady=8, padx=5)
            
            entry = tk.Entry(form_frame,
                           font=('Segoe UI', 10),
                           relief='solid',
                           bd=1,
                           width=40)
            entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            entries[key] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        def guardar():
            datos = {k: v.get().strip() for k, v in entries.items()}
            
            if not all(datos.values()):
                messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos")
                return
            
            exito, mensaje = self.sistema.dar_alta_alumno(
                datos['nombre'],
                datos['apellido'],
                datos['fecha_nac'],
                datos['telefono'],
                datos['matricula'],
                datos['grado'],
                datos['grupo']
            )
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_inicio()
            else:
                messagebox.showerror("Error", mensaje)
        
        btn_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        btn_frame.grid(row=len(campos), column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame,
                 text="💾 Guardar Alumno",
                 command=guardar,
                 bg=self.colors['secondary'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack()
    
    def mostrar_baja_alumno(self):
        """Mostrar formulario para dar de baja un alumno con buscador mejorado"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="➖ Dar de Baja Alumno",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        main_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        search_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(search_frame,
                text="🔍 Buscar alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 11),
                               relief='solid',
                               bd=1,
                               width=40)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Buscar por matrícula, nombre o apellido)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)
        
        table_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        table_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        columns = ('Matrícula', 'Nombre Completo', 'Grado', 'Grupo', 'Teléfono')
        tree = ttk.Treeview(table_frame,
                           columns=columns,
                           show='headings',
                           yscrollcommand=scrollbar.set,
                           height=12)
        
        scrollbar.config(command=tree.yview)
        
        tree.heading('Matrícula', text='Matrícula')
        tree.heading('Nombre Completo', text='Nombre Completo')
        tree.heading('Grado', text='Grado')
        tree.heading('Grupo', text='Grupo')
        tree.heading('Teléfono', text='Teléfono')
        
        tree.column('Matrícula', width=120)
        tree.column('Nombre Completo', width=250)
        tree.column('Grado', width=80)
        tree.column('Grupo', width=80)
        tree.column('Teléfono', width=120)
        
        self.configurar_treeview_con_lineas(tree)
        
        def actualizar_tabla(*args):
            for item in tree.get_children():
                tree.delete(item)
            
            filtro = search_var.get()
            alumnos_filtrados = self.sistema.buscar_alumnos(filtro, solo_activos=True)
            alumnos_filtrados.sort(key=lambda a: a.matricula)
            
            for i, alumno in enumerate(alumnos_filtrados):
                tree.insert('', 'end', values=(
                    alumno.matricula,
                    alumno.get_nombre_completo(),
                    alumno.grado,
                    alumno.grupo,
                    alumno.telefono
                ), tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            
            tree.tag_configure('evenrow', background='#F0F8FF')
            tree.tag_configure('oddrow', background='white')
            
            alumnos_activos = len([a for a in self.sistema.alumnos.values() if a.activo])
            count_label.config(text=f"Mostrando {len(alumnos_filtrados)} de {alumnos_activos} alumnos activos")
        
        search_var.trace('w', actualizar_tabla)
        
        tree.pack(fill='both', expand=True)
        
        bottom_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        count_label = tk.Label(bottom_frame,
                              text="",
                              bg=self.colors['surface'],
                              fg=self.colors['text_light'],
                              font=('Segoe UI', 9))
        count_label.pack(pady=5)
        
        info_frame = tk.Frame(bottom_frame, bg='#FFF3CD', relief='solid', bd=1)
        info_frame.pack(fill='x', pady=5)
        
        tk.Label(info_frame,
                text="ℹ️ Seleccione un alumno de la lista y haga clic en 'Dar de Baja' o haga doble clic en el alumno",
                bg='#FFF3CD',
                fg='#856404',
                font=('Segoe UI', 9)).pack(pady=8)
        
        selected_frame = tk.Frame(bottom_frame, bg=self.colors['surface'])
        selected_frame.pack(fill='x', pady=5)
        
        selected_label = tk.Label(selected_frame,
                                 text="Ningún alumno seleccionado",
                                 bg=self.colors['surface'],
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 10, 'bold'))
        selected_label.pack()
        
        matricula_seleccionada = [None]
        
        def on_select(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                values = item['values']
                matricula_seleccionada[0] = values[0]
                selected_label.config(
                    text=f"Alumno seleccionado: {values[1]} (Matrícula: {values[0]})",
                    fg=self.colors['secondary']
                )
        
        tree.bind('<<TreeviewSelect>>', on_select)
        
        def on_double_click(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                values = item['values']
                if values and len(values) > 0:
                    dar_baja_alumno(values[0])
        
        tree.bind('<Double-1>', on_double_click)
        
        def dar_baja_alumno(matricula):
            if not matricula:
                messagebox.showwarning("Sin selección", "Por favor seleccione un alumno de la lista")
                return
            
            matricula = str(matricula).strip()
            alumno = self.sistema.alumnos.get(matricula)
            
            if not alumno:
                messagebox.showerror("Error", f"No se encontró el alumno con matrícula '{matricula}'")
                return
            
            if not alumno.activo:
                messagebox.showwarning("Alumno ya inactivo", 
                    f"El alumno {alumno.get_nombre_completo()} ya fue dado de baja el {alumno.fecha_baja}.")
                return
            
            respuesta = messagebox.askyesno("Confirmar Baja",
                f"¿Está seguro de dar de baja al alumno?\n\n"
                f"Nombre: {alumno.get_nombre_completo()}\n"
                f"Matrícula: {alumno.matricula}\n"
                f"Grado: {alumno.grado} Grupo: {alumno.grupo}",
                icon='warning')
            
            if respuesta:
                exito, mensaje = self.sistema.dar_baja_alumno(matricula)
                
                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                    self.mostrar_inicio()
                else:
                    messagebox.showerror("Error", mensaje)
        
        btn_frame = tk.Frame(bottom_frame, bg=self.colors['surface'])
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame,
                 text="❌ Dar de Baja al Alumno Seleccionado",
                 command=lambda: dar_baja_alumno(matricula_seleccionada[0]),
                 bg=self.colors['danger'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="🔄 Cancelar",
                 command=self.mostrar_inicio,
                 bg=self.colors['text_light'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack(side='left', padx=5)
        
        actualizar_tabla()
        search_entry.focus()
    
    def mostrar_lista_alumnos(self):
        """Mostrar lista de alumnos en un Treeview"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="👥 Lista de Alumnos",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        search_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        search_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(search_frame,
                text="🔍 Buscar alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 11),
                               relief='solid',
                               bd=1,
                               width=30)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Buscar por matrícula, nombre o apellido)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)
        
        activos_frame = tk.LabelFrame(self.right_panel,
                                      text="✓ ALUMNOS ACTIVOS",
                                      bg=self.colors['surface'],
                                      fg=self.colors['success'],
                                      font=('Segoe UI', 11, 'bold'),
                                      relief='solid',
                                      bd=2)
        activos_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        canvas_activos = tk.Canvas(activos_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar_activos_y = ttk.Scrollbar(activos_frame, orient="vertical", command=canvas_activos.yview)
        scrollbar_activos_x = ttk.Scrollbar(activos_frame, orient="horizontal", command=canvas_activos.xview)
        
        scrollable_frame_activos = ttk.Frame(canvas_activos)
        scrollable_frame_activos.bind("<Configure>", lambda e: canvas_activos.configure(scrollregion=canvas_activos.bbox("all")))
        
        canvas_activos.create_window((0, 0), window=scrollable_frame_activos, anchor="nw")
        canvas_activos.configure(yscrollcommand=scrollbar_activos_y.set, xscrollcommand=scrollbar_activos_x.set)
        
        canvas_activos.pack(side="left", fill="both", expand=True)
        scrollbar_activos_y.pack(side="right", fill="y")
        scrollbar_activos_x.pack(side="bottom", fill="x")
        
        columns = ('Matrícula', 'Nombre', 'Grado', 'Grupo', 'Teléfono', 'Fecha Alta')
        tree_activos = ttk.Treeview(scrollable_frame_activos,
                                    columns=columns,
                                    show='headings',
                                    height=10)
        
        tree_activos.heading('Matrícula', text='Matrícula')
        tree_activos.heading('Nombre', text='Nombre Completo')
        tree_activos.heading('Grado', text='Grado')
        tree_activos.heading('Grupo', text='Grupo')
        tree_activos.heading('Teléfono', text='Teléfono')
        tree_activos.heading('Fecha Alta', text='Fecha Alta')
        
        tree_activos.column('Matrícula', width=120, minwidth=120)
        tree_activos.column('Nombre', width=250, minwidth=200)
        tree_activos.column('Grado', width=80, minwidth=80)
        tree_activos.column('Grupo', width=80, minwidth=80)
        tree_activos.column('Teléfono', width=120, minwidth=120)
        tree_activos.column('Fecha Alta', width=150, minwidth=150)
        
        self.configurar_treeview_con_lineas(tree_activos)
        
        def actualizar_activos(*args):
            for item in tree_activos.get_children():
                tree_activos.delete(item)
            
            filtro = search_var.get()
            alumnos_filtrados = self.sistema.buscar_alumnos(filtro, solo_activos=True)
            alumnos_filtrados.sort(key=lambda a: a.matricula)
            
            for i, alumno in enumerate(alumnos_filtrados):
                tree_activos.insert('', 'end', values=(
                    alumno.matricula,
                    alumno.get_nombre_completo(),
                    alumno.grado,
                    alumno.grupo,
                    alumno.telefono,
                    alumno.fecha_alta
                ), tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            
            tree_activos.tag_configure('evenrow', background='#E8F5E9')
            tree_activos.tag_configure('oddrow', background='white')
            
            count_activos_label.config(text=f"Total: {len(alumnos_filtrados)} alumno(s) activo(s)")
        
        search_var.trace('w', actualizar_activos)
        
        tree_activos.pack(fill='both', expand=True, padx=5, pady=5)
        
        count_activos_label = tk.Label(activos_frame,
                                      text="",
                                      bg=self.colors['surface'],
                                      fg=self.colors['success'],
                                      font=('Segoe UI', 10, 'bold'))
        count_activos_label.pack(pady=5)
        
        inactivos_frame = tk.LabelFrame(self.right_panel,
                                        text="✗ ALUMNOS INACTIVOS (DADOS DE BAJA)",
                                        bg=self.colors['surface'],
                                        fg=self.colors['danger'],
                                        font=('Segoe UI', 11, 'bold'),
                                        relief='solid',
                                        bd=2)
        inactivos_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        canvas_inactivos = tk.Canvas(inactivos_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar_inactivos_y = ttk.Scrollbar(inactivos_frame, orient="vertical", command=canvas_inactivos.yview)
        scrollbar_inactivos_x = ttk.Scrollbar(inactivos_frame, orient="horizontal", command=canvas_inactivos.xview)
        
        scrollable_frame_inactivos = ttk.Frame(canvas_inactivos)
        scrollable_frame_inactivos.bind("<Configure>", lambda e: canvas_inactivos.configure(scrollregion=canvas_inactivos.bbox("all")))
        
        canvas_inactivos.create_window((0, 0), window=scrollable_frame_inactivos, anchor="nw")
        canvas_inactivos.configure(yscrollcommand=scrollbar_inactivos_y.set, xscrollcommand=scrollbar_inactivos_x.set)
        
        canvas_inactivos.pack(side="left", fill="both", expand=True)
        scrollbar_inactivos_y.pack(side="right", fill="y")
        scrollbar_inactivos_x.pack(side="bottom", fill="x")
        
        columns_inactivos = ('Matrícula', 'Nombre', 'Grado', 'Grupo', 'Fecha Baja')
        tree_inactivos = ttk.Treeview(scrollable_frame_inactivos,
                                      columns=columns_inactivos,
                                      show='headings',
                                      height=8)
        
        tree_inactivos.heading('Matrícula', text='Matrícula')
        tree_inactivos.heading('Nombre', text='Nombre Completo')
        tree_inactivos.heading('Grado', text='Grado')
        tree_inactivos.heading('Grupo', text='Grupo')
        tree_inactivos.heading('Fecha Baja', text='Fecha de Baja')
        
        tree_inactivos.column('Matrícula', width=120, minwidth=120)
        tree_inactivos.column('Nombre', width=250, minwidth=200)
        tree_inactivos.column('Grado', width=80, minwidth=80)
        tree_inactivos.column('Grupo', width=80, minwidth=80)
        tree_inactivos.column('Fecha Baja', width=150, minwidth=150)
        
        self.configurar_treeview_con_lineas(tree_inactivos)
        
        count_inactivos = 0
        for alumno in sorted(self.sistema.alumnos.values(), key=lambda a: a.matricula):
            if not alumno.activo:
                tree_inactivos.insert('', 'end', values=(
                    alumno.matricula,
                    alumno.get_nombre_completo(),
                    alumno.grado,
                    alumno.grupo,
                    alumno.fecha_baja if alumno.fecha_baja else "N/A"
                ))
                count_inactivos += 1
        
        for i, item in enumerate(tree_inactivos.get_children()):
            if i % 2 == 0:
                tree_inactivos.item(item, tags=('evenrow',))
        
        tree_inactivos.tag_configure('evenrow', background='#FFEBEE')
        tree_inactivos.tag_configure('oddrow', background='white')
        tree_inactivos.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(inactivos_frame,
                text=f"Total: {count_inactivos} alumno(s) inactivo(s)",
                bg=self.colors['surface'],
                fg=self.colors['danger'],
                font=('Segoe UI', 10, 'bold')).pack(pady=5)
        
        actualizar_activos()
        search_entry.focus()
    
    def mostrar_agregar_docente(self):
        """Mostrar formulario para agregar docente"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="👨‍🏫 Agregar Docente",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        form_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        form_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        campos = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Fecha de Nacimiento (DD/MM/AAAA):", "fecha_nac"),
            ("Teléfono:", "telefono"),
            ("Número de Empleado:", "num_empleado"),
            ("Especialidad:", "especialidad"),
            ("Email:", "email")
        ]
        
        entries = {}
        
        for i, (label, key) in enumerate(campos):
            tk.Label(form_frame,
                    text=label,
                    bg=self.colors['surface'],
                    fg=self.colors['text'],
                    font=('Segoe UI', 10, 'bold'),
                    anchor='w').grid(row=i, column=0, sticky='w', pady=8, padx=5)
            
            entry = tk.Entry(form_frame,
                           font=('Segoe UI', 10),
                           relief='solid',
                           bd=1,
                           width=40)
            entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            entries[key] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        def guardar():
            datos = {k: v.get().strip() for k, v in entries.items()}
            
            if not all(datos.values()):
                messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos")
                return
            
            exito, mensaje = self.sistema.agregar_docente(
                datos['nombre'],
                datos['apellido'],
                datos['fecha_nac'],
                datos['telefono'],
                datos['num_empleado'],
                datos['especialidad'],
                datos['email']
            )
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_inicio()
            else:
                messagebox.showerror("Error", mensaje)
        
        btn_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        btn_frame.grid(row=len(campos), column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame,
                 text="💾 Guardar Docente",
                 command=guardar,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack()
    
    def mostrar_lista_docentes(self):
        """Mostrar lista de docentes con buscador"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="📋 Lista de Docentes",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        search_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        search_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(search_frame,
                text="🔍 Buscar docente:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 11),
                               relief='solid',
                               bd=1,
                               width=40)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Buscar por número, nombre, especialidad o email)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)
        
        table_container = tk.Frame(self.right_panel, bg=self.colors['surface'])
        table_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(table_container, bg=self.colors['surface'], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        columns = ('No. Empleado', 'Nombre', 'Especialidad', 'Email', 'Teléfono')
        tree = ttk.Treeview(scrollable_frame,
                           columns=columns,
                           show='headings',
                           height=20)
        
        tree.heading('No. Empleado', text='No. Empleado')
        tree.heading('Nombre', text='Nombre Completo')
        tree.heading('Especialidad', text='Especialidad')
        tree.heading('Email', text='Email')
        tree.heading('Teléfono', text='Teléfono')
        
        tree.column('No. Empleado', width=120, minwidth=120)
        tree.column('Nombre', width=250, minwidth=200)
        tree.column('Especialidad', width=200, minwidth=150)
        tree.column('Email', width=250, minwidth=200)
        tree.column('Teléfono', width=120, minwidth=120)
        
        self.configurar_treeview_con_lineas(tree)
        
        def actualizar_tabla(*args):
            for item in tree.get_children():
                tree.delete(item)
            
            filtro = search_var.get()
            docentes_filtrados = self.sistema.buscar_docentes(filtro)
            docentes_filtrados.sort(key=lambda d: d.num_empleado)
            
            for i, docente in enumerate(docentes_filtrados):
                tree.insert('', 'end', values=(
                    docente.num_empleado,
                    docente.get_nombre_completo(),
                    docente.especialidad,
                    docente.email,
                    docente.telefono
                ), tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            
            tree.tag_configure('evenrow', background='#F0F8FF')
            tree.tag_configure('oddrow', background='white')
            
            count_label.config(text=f"Mostrando {len(docentes_filtrados)} de {len(self.sistema.docentes)} docentes")
        
        search_var.trace('w', actualizar_tabla)
        
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        count_label = tk.Label(self.right_panel,
                              text="",
                              bg=self.colors['surface'],
                              fg=self.colors['text_light'],
                              font=('Segoe UI', 10))
        count_label.pack(pady=10)
        
        actualizar_tabla()
        search_entry.focus()
    
    def mostrar_agregar_materia(self):
        """Mostrar formulario para agregar materia"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="📖 Agregar Materia",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        form_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        form_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        campos = [
            ("ID de la Materia:", "id"),
            ("Nombre de la Materia:", "nombre"),
            ("Grado:", "grado"),
            ("Descripción:", "descripcion")
        ]
        
        entries = {}
        
        for i, (label, key) in enumerate(campos):
            tk.Label(form_frame,
                    text=label,
                    bg=self.colors['surface'],
                    fg=self.colors['text'],
                    font=('Segoe UI', 10, 'bold'),
                    anchor='w').grid(row=i, column=0, sticky='w', pady=8, padx=5)
            
            if key == "descripcion":
                entry = tk.Text(form_frame,
                              font=('Segoe UI', 10),
                              relief='solid',
                              bd=1,
                              width=40,
                              height=4)
                entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            else:
                entry = tk.Entry(form_frame,
                               font=('Segoe UI', 10),
                               relief='solid',
                               bd=1,
                               width=40)
                entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            
            entries[key] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        def guardar():
            datos = {}
            for key, entry in entries.items():
                if key == "descripcion":
                    datos[key] = entry.get("1.0", tk.END).strip()
                else:
                    datos[key] = entry.get().strip()
            
            if not datos['id'] or not datos['nombre'] or not datos['grado']:
                messagebox.showwarning("Campos vacíos", "Por favor complete ID, Nombre y Grado")
                return
            
            exito, mensaje = self.sistema.agregar_materia(
                datos['id'],
                datos['nombre'],
                datos['grado'],
                datos['descripcion']
            )
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_inicio()
            else:
                messagebox.showerror("Error", mensaje)
        
        btn_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        btn_frame.grid(row=len(campos), column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame,
                 text="💾 Guardar Materia",
                 command=guardar,
                 bg=self.colors['info'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack()
    
    def mostrar_lista_materias(self):
        """Mostrar lista de materias con buscador"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="📋 Lista de Materias",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        search_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        search_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(search_frame,
                text="🔍 Buscar materia:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 11),
                               relief='solid',
                               bd=1,
                               width=40)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Buscar por ID, nombre, grado o descripción)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)
        
        table_container = tk.Frame(self.right_panel, bg=self.colors['surface'])
        table_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(table_container, bg=self.colors['surface'], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        columns = ('ID', 'Nombre', 'Grado', 'Descripción')
        tree = ttk.Treeview(scrollable_frame,
                           columns=columns,
                           show='headings',
                           height=20)
        
        tree.heading('ID', text='ID')
        tree.heading('Nombre', text='Nombre')
        tree.heading('Grado', text='Grado')
        tree.heading('Descripción', text='Descripción')
        
        tree.column('ID', width=120, minwidth=120)
        tree.column('Nombre', width=250, minwidth=200)
        tree.column('Grado', width=80, minwidth=80)
        tree.column('Descripción', width=400, minwidth=300)
        
        self.configurar_treeview_con_lineas(tree)
        
        def actualizar_tabla(*args):
            for item in tree.get_children():
                tree.delete(item)
            
            filtro = search_var.get()
            materias_filtradas = self.sistema.buscar_materias(filtro)
            materias_filtradas.sort(key=lambda m: m.id)
            
            for i, materia in enumerate(materias_filtradas):
                tree.insert('', 'end', values=(
                    materia.id,
                    materia.nombre,
                    materia.grado,
                    materia.descripcion[:100] + "..." if len(materia.descripcion) > 100 else materia.descripcion
                ), tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            
            tree.tag_configure('evenrow', background='#F0F8FF')
            tree.tag_configure('oddrow', background='white')
            
            count_label.config(text=f"Mostrando {len(materias_filtradas)} de {len(self.sistema.materias)} materias")
        
        search_var.trace('w', actualizar_tabla)
        
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        count_label = tk.Label(self.right_panel,
                              text="",
                              bg=self.colors['surface'],
                              fg=self.colors['text_light'],
                              font=('Segoe UI', 10))
        count_label.pack(pady=10)
        
        actualizar_tabla()
        search_entry.focus()
    
    def mostrar_grupos(self):
        """Mostrar lista de grupos con sus alumnos"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="👥 Grupos Escolares",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        grupos = self.sistema.obtener_grupos_disponibles()
        
        if not grupos:
            tk.Label(self.right_panel,
                    text="No hay grupos registrados",
                    bg=self.colors['surface'],
                    fg=self.colors['text_light'],
                    font=('Segoe UI', 12, 'italic')).pack(pady=50)
            return
        
        selector_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        selector_frame.pack(fill='x', padx=40, pady=20)
        
        tk.Label(selector_frame,
                text="Seleccionar Grupo:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        grupo_var = tk.StringVar()
        grupos_list = [f"{grado}° {grupo}" for grado, grupo in grupos]
        grupo_combo = ttk.Combobox(selector_frame,
                                  textvariable=grupo_var,
                                  values=grupos_list,
                                  font=('Segoe UI', 11),
                                  width=30,
                                  state='readonly')
        grupo_combo.pack(side='left', padx=5)
        
        if grupos_list:
            grupo_combo.set(grupos_list[0])
        
        alumnos_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        alumnos_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        def mostrar_alumnos_grupo(*args):
            for widget in alumnos_frame.winfo_children():
                widget.destroy()
            
            if not grupo_var.get():
                return
            
            grupo_text = grupo_var.get()
            grado = grupo_text.split("°")[0]
            grupo = grupo_text.split(" ")[1]
            
            alumnos = self.sistema.obtener_alumnos_por_grupo(grado, grupo)
            
            if not alumnos:
                tk.Label(alumnos_frame,
                        text=f"No hay alumnos en el grupo {grupo_text}",
                        bg=self.colors['surface'],
                        fg=self.colors['text_light'],
                        font=('Segoe UI', 11, 'italic')).pack(pady=30)
                return
            
            tk.Label(alumnos_frame,
                    text=f"Grupo: {grupo_text} - Total: {len(alumnos)} alumnos",
                    bg=self.colors['info'],
                    fg='white',
                    font=('Segoe UI', 12, 'bold'),
                    pady=10).pack(fill='x')
            
            table_container = tk.Frame(alumnos_frame, bg=self.colors['surface'])
            table_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            canvas = tk.Canvas(table_container, bg=self.colors['surface'], highlightthickness=0)
            scrollbar_y = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
            scrollbar_x = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
            
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_y.pack(side="right", fill="y")
            scrollbar_x.pack(side="bottom", fill="x")
            
            columns = ('Matrícula', 'Nombre', 'Teléfono', 'Fecha Alta')
            tree = ttk.Treeview(scrollable_frame,
                               columns=columns,
                               show='headings',
                               height=15)
            
            tree.heading('Matrícula', text='Matrícula')
            tree.heading('Nombre', text='Nombre Completo')
            tree.heading('Teléfono', text='Teléfono')
            tree.heading('Fecha Alta', text='Fecha Alta')
            
            tree.column('Matrícula', width=120, minwidth=120)
            tree.column('Nombre', width=300, minwidth=250)
            tree.column('Teléfono', width=150, minwidth=120)
            tree.column('Fecha Alta', width=180, minwidth=150)
            
            self.configurar_treeview_con_lineas(tree)
            
            alumnos.sort(key=lambda a: a.matricula)
            
            for i, alumno in enumerate(alumnos):
                tree.insert('', 'end', values=(
                    alumno.matricula,
                    alumno.get_nombre_completo(),
                    alumno.telefono,
                    alumno.fecha_alta
                ), tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            
            tree.tag_configure('evenrow', background='#F0F8FF')
            tree.tag_configure('oddrow', background='white')
            
            tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        grupo_var.trace('w', mostrar_alumnos_grupo)
        
        if grupos_list:
            mostrar_alumnos_grupo()
    
    def mostrar_registrar_calificacion(self):
        """Mostrar formulario para registrar calificación con buscador"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="✏️ Registrar Calificación",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        form_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        form_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        search_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        form_frame.columnconfigure(1, weight=1)
        
        tk.Label(search_frame,
                text="🔍 Buscar alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 10),
                               relief='solid',
                               bd=1,
                               width=30)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Escriba para filtrar)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)
        
        tk.Label(form_frame,
                text="Alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=1, column=0, sticky='w', pady=8, padx=5)
        
        alumno_var = tk.StringVar()
        alumno_combo = ttk.Combobox(form_frame,
                                   textvariable=alumno_var,
                                   font=('Segoe UI', 10),
                                   width=40,
                                   state='readonly')
        alumno_combo.grid(row=1, column=1, pady=8, padx=5, sticky='ew')
        
        def actualizar_combo_alumnos(*args):
            filtro = search_var.get()
            alumnos_filtrados = self.sistema.buscar_alumnos(filtro, solo_activos=True)
            alumnos_filtrados.sort(key=lambda a: a.matricula)
            
            alumnos_list = [f"{a.matricula} - {a.get_nombre_completo()} (Grado {a.grado} {a.grupo})" for a in alumnos_filtrados]
            alumno_combo['values'] = alumnos_list
            if alumnos_list:
                alumno_combo.set(alumnos_list[0])
        
        search_var.trace('w', actualizar_combo_alumnos)
        
        tk.Label(form_frame,
                text="Materia:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=2, column=0, sticky='w', pady=8, padx=5)
        
        search_materia_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        search_materia_frame.grid(row=2, column=1, sticky='ew', pady=8, padx=5)
        
        tk.Label(search_materia_frame,
                text="🔍",
                bg=self.colors['surface'],
                fg=self.colors['text']).pack(side='left', padx=(0, 2))
        
        search_materia_var = tk.StringVar()
        search_materia_entry = tk.Entry(search_materia_frame,
                                       textvariable=search_materia_var,
                                       font=('Segoe UI', 10),
                                       relief='solid',
                                       bd=1,
                                       width=20)
        search_materia_entry.pack(side='left', padx=(0, 5))
        
        materia_var = tk.StringVar()
        materia_combo = ttk.Combobox(search_materia_frame,
                                    textvariable=materia_var,
                                    font=('Segoe UI', 10),
                                    width=35,
                                    state='readonly')
        materia_combo.pack(side='left', padx=5)
        
        def actualizar_combo_materias(*args):
            filtro = search_materia_var.get()
            materias_filtradas = self.sistema.buscar_materias(filtro)
            materias_filtradas.sort(key=lambda m: m.id)
            
            materias_list = [f"{m.id} - {m.nombre} (Grado {m.grado})" for m in materias_filtradas]
            materia_combo['values'] = materias_list
            if materias_list:
                materia_combo.set(materias_list[0])
        
        search_materia_var.trace('w', actualizar_combo_materias)
        
        tk.Label(form_frame,
                text="Semestre:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=3, column=0, sticky='w', pady=8, padx=5)
        
        semestre_entry = tk.Entry(form_frame,
                                 font=('Segoe UI', 10),
                                 relief='solid',
                                 bd=1,
                                 width=40)
        semestre_entry.grid(row=3, column=1, pady=8, padx=5, sticky='ew')
        semestre_entry.insert(0, "1er Semestre")
        
        tk.Label(form_frame,
                text="Calificación (0-100):",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=4, column=0, sticky='w', pady=8, padx=5)
        
        calif_entry = tk.Entry(form_frame,
                              font=('Segoe UI', 10),
                              relief='solid',
                              bd=1,
                              width=40)
        calif_entry.grid(row=4, column=1, pady=8, padx=5, sticky='ew')
        
        def guardar():
            if not alumno_var.get():
                messagebox.showwarning("Selección requerida", "Por favor seleccione un alumno")
                return
            
            if not materia_var.get():
                messagebox.showwarning("Selección requerida", "Por favor seleccione una materia")
                return
            
            semestre = semestre_entry.get().strip()
            if not semestre:
                messagebox.showwarning("Campo vacío", "Por favor ingrese el semestre")
                return
            
            try:
                calificacion = float(calif_entry.get().strip())
                if calificacion < 0 or calificacion > 100:
                    messagebox.showwarning("Valor inválido", "La calificación debe estar entre 0 y 100")
                    return
            except ValueError:
                messagebox.showwarning("Valor inválido", "Por favor ingrese un número válido")
                return
            
            matricula = alumno_var.get().split(" - ")[0]
            materia_id = materia_var.get().split(" - ")[0]
            
            exito, mensaje = self.sistema.registrar_calificacion(
                matricula,
                materia_id,
                semestre,
                calificacion
            )
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                semestre_entry.delete(0, tk.END)
                semestre_entry.insert(0, "1er Semestre")
                calif_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)
        
        btn_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame,
                 text="💾 Registrar Calificación",
                 command=guardar,
                 bg=self.colors['warning'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack()
        
        actualizar_combo_alumnos()
        actualizar_combo_materias()
        search_entry.focus()
    
    def mostrar_ver_calificaciones_con_buscador(self):
        """Mostrar buscador de calificaciones por alumno"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="🔍 Buscar Calificaciones por Alumno",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        main_search_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        main_search_frame.pack(fill='x', padx=40, pady=20)
        
        tk.Label(main_search_frame,
                text="🔍 Buscar alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        search_frame = tk.Frame(main_search_frame, bg=self.colors['surface'])
        search_frame.pack(fill='x')
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 11),
                               relief='solid',
                               bd=2,
                               width=50)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Escriba nombre, apellido o matrícula)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 10, 'italic')).pack(side='left', padx=5)
        
        results_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        results_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(results_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(results_frame, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        def buscar_calificaciones():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            termino = search_var.get().strip()
            if not termino:
                tk.Label(scrollable_frame,
                        text="Por favor ingrese un término de búsqueda",
                        bg=self.colors['surface'],
                        fg=self.colors['text_light'],
                        font=('Segoe UI', 12, 'italic')).pack(pady=50)
                return
            
            alumnos_encontrados = self.sistema.buscar_alumnos(termino, solo_activos=True)
            
            if not alumnos_encontrados:
                tk.Label(scrollable_frame,
                        text=f"No se encontraron alumnos con '{termino}'",
                        bg=self.colors['surface'],
                        fg=self.colors['danger'],
                        font=('Segoe UI', 12, 'bold')).pack(pady=50)
                return
            
            for alumno in alumnos_encontrados:
                alumno_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=2)
                alumno_frame.pack(fill='x', pady=10, padx=10)
                
                info_frame = tk.Frame(alumno_frame, bg=self.colors['secondary'])
                info_frame.pack(fill='x')
                
                tk.Label(info_frame,
                        text=f"📘 {alumno.get_nombre_completo()}",
                        bg=self.colors['secondary'],
                        fg='white',
                        font=('Segoe UI', 12, 'bold'),
                        pady=8).pack(side='left', padx=10)
                
                tk.Label(info_frame,
                        text=f"Matrícula: {alumno.matricula} | Grado: {alumno.grado}° | Grupo: {alumno.grupo}",
                        bg=self.colors['secondary'],
                        fg='white',
                        font=('Segoe UI', 10),
                        pady=8).pack(side='right', padx=10)
                
                calificaciones = self.sistema.obtener_calificaciones_alumno(alumno.matricula)
                
                if not calificaciones:
                    tk.Label(alumno_frame,
                            text="No hay calificaciones registradas",
                            bg='white',
                            fg=self.colors['text_light'],
                            font=('Segoe UI', 10, 'italic'),
                            pady=10).pack()
                else:
                    calif_por_materia = {}
                    for calif in calificaciones:
                        if calif.materia_id not in calif_por_materia:
                            calif_por_materia[calif.materia_id] = []
                        calif_por_materia[calif.materia_id].append(calif)
                    
                    table_frame = tk.Frame(alumno_frame, bg='white')
                    table_frame.pack(fill='both', expand=True, padx=10, pady=10)
                    
                    tk.Label(table_frame, text="Materia", bg=self.colors['primary'], fg='white',
                            font=('Segoe UI', 10, 'bold'), width=30, relief='solid', bd=1).grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
                    tk.Label(table_frame, text="Semestre", bg=self.colors['primary'], fg='white',
                            font=('Segoe UI', 10, 'bold'), width=15, relief='solid', bd=1).grid(row=0, column=1, padx=1, pady=1, sticky='nsew')
                    tk.Label(table_frame, text="Calificación", bg=self.colors['primary'], fg='white',
                            font=('Segoe UI', 10, 'bold'), width=15, relief='solid', bd=1).grid(row=0, column=2, padx=1, pady=1, sticky='nsew')
                    tk.Label(table_frame, text="Estado", bg=self.colors['primary'], fg='white',
                            font=('Segoe UI', 10, 'bold'), width=15, relief='solid', bd=1).grid(row=0, column=3, padx=1, pady=1, sticky='nsew')
                    
                    row = 1
                    for materia_id, califs in calif_por_materia.items():
                        materia = self.sistema.materias.get(materia_id)
                        materia_nombre = materia.nombre if materia else materia_id
                        
                        for calif in sorted(califs, key=lambda x: x.semestre):
                            estado = "Aprobado" if calif.calificacion >= 70 else "Reprobado"
                            estado_color = self.colors['success'] if calif.calificacion >= 70 else self.colors['danger']
                            
                            tk.Label(table_frame, text=materia_nombre, bg='white', 
                                    fg=self.colors['text'], font=('Segoe UI', 10), 
                                    width=30, relief='solid', bd=1).grid(row=row, column=0, padx=1, pady=1, sticky='nsew')
                            tk.Label(table_frame, text=calif.semestre, bg='white', 
                                    fg=self.colors['text'], font=('Segoe UI', 10), 
                                    width=15, relief='solid', bd=1).grid(row=row, column=1, padx=1, pady=1, sticky='nsew')
                            tk.Label(table_frame, text=f"{calif.calificacion:.1f}", bg='white', 
                                    fg=self.colors['text'], font=('Segoe UI', 10), 
                                    width=15, relief='solid', bd=1).grid(row=row, column=2, padx=1, pady=1, sticky='nsew')
                            tk.Label(table_frame, text=estado, bg='white', 
                                    fg=estado_color, font=('Segoe UI', 10, 'bold'), 
                                    width=15, relief='solid', bd=1).grid(row=row, column=3, padx=1, pady=1, sticky='nsew')
                            row += 1
                    
                    promedio = self.sistema.obtener_promedio_alumno(alumno.matricula)
                    promedio_frame = tk.Frame(alumno_frame, bg='white')
                    promedio_frame.pack(fill='x', padx=10, pady=5)
                    
                    color_prom = self.colors['success'] if promedio >= 70 else self.colors['danger']
                    tk.Label(promedio_frame,
                            text=f"Promedio General: {promedio:.1f}",
                            bg=color_prom,
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            pady=5).pack()
        
        tk.Button(main_search_frame,
                 text="🔍 Buscar Calificaciones",
                 command=buscar_calificaciones,
                 bg=self.colors['secondary'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack(pady=20)
        
        search_entry.bind('<Return>', lambda e: buscar_calificaciones())
        search_entry.focus()
    
    def mostrar_boletin_alumno(self):
        """Mostrar boletín completo de calificaciones por alumno"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="📈 Boletín de Calificaciones",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        search_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        search_frame.pack(fill='x', padx=40, pady=20)
        
        tk.Label(search_frame,
                text="🔍 Buscar Alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               font=('Segoe UI', 11),
                               relief='solid',
                               bd=1,
                               width=30)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(search_frame,
                text="(Escriba para filtrar alumnos)",
                bg=self.colors['surface'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)
        
        select_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        select_frame.pack(fill='x', padx=40, pady=10)
        
        tk.Label(select_frame,
                text="Seleccionar Alumno:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        alumno_combo_var = tk.StringVar()
        alumno_combo = ttk.Combobox(select_frame,
                                   textvariable=alumno_combo_var,
                                   font=('Segoe UI', 11),
                                   width=50,
                                   state='readonly')
        alumno_combo.pack(side='left', padx=5)
        
        def actualizar_combo(*args):
            filtro = search_var.get()
            alumnos_filtrados = self.sistema.buscar_alumnos(filtro, solo_activos=True)
            alumnos_filtrados.sort(key=lambda a: a.matricula)
            
            alumnos_list = [f"{a.matricula} - {a.get_nombre_completo()} (Grado {a.grado} {a.grupo})" 
                           for a in alumnos_filtrados]
            alumno_combo['values'] = alumnos_list
            if alumnos_list:
                alumno_combo.set(alumnos_list[0])
        
        search_var.trace('w', actualizar_combo)
        
        boletin_container = tk.Frame(self.right_panel, bg='white', relief='solid', bd=2)
        boletin_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(boletin_container, bg='white', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(boletin_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(boletin_container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        def generar_boletin():
            if not alumno_combo_var.get():
                messagebox.showwarning("Selección requerida", "Por favor seleccione un alumno")
                return
            
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            matricula = alumno_combo_var.get().split(" - ")[0]
            alumno = self.sistema.alumnos.get(matricula)
            
            if not alumno:
                return
            
            tk.Label(scrollable_frame,
                    text="BOLETÍN DE CALIFICACIONES",
                    bg=self.colors['primary'],
                    fg='white',
                    font=('Segoe UI', 16, 'bold'),
                    pady=15).pack(fill='x')
            
            info_frame = tk.Frame(scrollable_frame, bg='white')
            info_frame.pack(fill='x', padx=20, pady=15)
            
            info_text = f"""
            Alumno: {alumno.get_nombre_completo()}
            Matrícula: {alumno.matricula}
            Grado: {alumno.grado}°   Grupo: {alumno.grupo}
            Fecha de emisión: {datetime.now().strftime("%d/%m/%Y %H:%M")}
            """
            
            tk.Label(info_frame,
                    text=info_text,
                    bg='white',
                    fg=self.colors['text'],
                    font=('Segoe UI', 11),
                    justify='left').pack(anchor='w')
            
            calificaciones = self.sistema.obtener_calificaciones_alumno(matricula)
            
            if not calificaciones:
                tk.Label(scrollable_frame,
                        text="No hay calificaciones registradas para este alumno",
                        bg='white',
                        fg=self.colors['text_light'],
                        font=('Segoe UI', 12, 'italic')).pack(pady=30)
            else:
                materias_calif = {}
                for calif in calificaciones:
                    if calif.materia_id not in materias_calif:
                        materias_calif[calif.materia_id] = []
                    materias_calif[calif.materia_id].append(calif)
                
                for materia_id, califs in materias_calif.items():
                    materia = self.sistema.materias.get(materia_id)
                    materia_nombre = materia.nombre if materia else materia_id
                    
                    materia_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
                    materia_frame.pack(fill='x', padx=20, pady=5)
                    
                    tk.Label(materia_frame,
                            text=f"📚 {materia_nombre}",
                            bg=self.colors['info'],
                            fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            pady=5).pack(fill='x')
                    
                    calif_subframe = tk.Frame(materia_frame, bg='white')
                    calif_subframe.pack(padx=10, pady=10)
                    
                    tk.Label(calif_subframe, text="Semestre", bg=self.colors['primary'], fg='white', 
                            font=('Segoe UI', 10, 'bold'), width=20, relief='solid', bd=1).grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
                    tk.Label(calif_subframe, text="Calificación", bg=self.colors['primary'], fg='white', 
                            font=('Segoe UI', 10, 'bold'), width=15, relief='solid', bd=1).grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
                    tk.Label(calif_subframe, text="Estado", bg=self.colors['primary'], fg='white', 
                            font=('Segoe UI', 10, 'bold'), width=15, relief='solid', bd=1).grid(row=0, column=2, padx=2, pady=2, sticky='nsew')
                    
                    row = 1
                    for calif in sorted(califs, key=lambda x: x.semestre):
                        calif_text = f"{calif.calificacion:.1f}"
                        estado = "Aprobado" if calif.calificacion >= 70 else "Reprobado"
                        estado_color = self.colors['success'] if calif.calificacion >= 70 else self.colors['danger']
                        
                        tk.Label(calif_subframe, text=calif.semestre, bg='white', 
                                fg=self.colors['text'], font=('Segoe UI', 10), 
                                width=20, relief='solid', bd=1).grid(row=row, column=0, padx=2, pady=2, sticky='nsew')
                        tk.Label(calif_subframe, text=calif_text, bg='white', 
                                fg=self.colors['text'], font=('Segoe UI', 10), 
                                width=15, relief='solid', bd=1).grid(row=row, column=1, padx=2, pady=2, sticky='nsew')
                        tk.Label(calif_subframe, text=estado, bg='white', 
                                fg=estado_color, font=('Segoe UI', 10, 'bold'), 
                                width=15, relief='solid', bd=1).grid(row=row, column=2, padx=2, pady=2, sticky='nsew')
                        row += 1
                    
                    promedio_materia = sum(c.calificacion for c in califs) / len(califs)
                    color_prom = self.colors['success'] if promedio_materia >= 70 else self.colors['danger']
                    
                    tk.Label(materia_frame,
                            text=f"Promedio: {promedio_materia:.1f}",
                            bg=color_prom,
                            fg='white',
                            font=('Segoe UI', 10, 'bold')).pack(pady=5)
                
                promedio = self.sistema.obtener_promedio_alumno(matricula)
                
                promedio_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=2)
                promedio_frame.pack(fill='x', padx=20, pady=15)
                
                color_prom = self.colors['success'] if promedio >= 70 else self.colors['danger']
                estado_general = "APROBADO" if promedio >= 70 else "REPROBADO"
                
                tk.Label(promedio_frame,
                        text=f"PROMEDIO GENERAL: {promedio:.1f}",
                        bg=color_prom,
                        fg='white',
                        font=('Segoe UI', 14, 'bold')).pack(pady=10)
                
                tk.Label(promedio_frame,
                        text=f"ESTADO: {estado_general}",
                        bg=color_prom,
                        fg='white',
                        font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        tk.Button(select_frame,
                 text="📄 Generar Boletín",
                 command=generar_boletin,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=20,
                 pady=8,
                 cursor='hand2').pack(side='left', padx=10)
        
        actualizar_combo()
        search_entry.focus()
    
    def mostrar_agregar_horario(self):
        """Mostrar formulario para agregar horario"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="📅 Agregar Horario",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        form_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        form_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        campos = [
            ("ID del Horario:", "id"),
            ("Materia:", "materia_id"),
            ("Número de Empleado del Docente:", "docente_id"),
            ("Grado:", "grado"),
            ("Grupo:", "grupo"),
            ("Día:", "dia"),
            ("Hora Inicio (HH:MM):", "hora_inicio"),
            ("Hora Fin (HH:MM):", "hora_fin"),
            ("Aula:", "aula")
        ]
        
        entries = {}
        
        for i, (label, key) in enumerate(campos):
            tk.Label(form_frame,
                    text=label,
                    bg=self.colors['surface'],
                    fg=self.colors['text'],
                    font=('Segoe UI', 10, 'bold'),
                    anchor='w').grid(row=i, column=0, sticky='w', pady=8, padx=5)
            
            if key == "dia":
                entry = ttk.Combobox(form_frame,
                                    values=["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"],
                                    font=('Segoe UI', 10),
                                    width=38,
                                    state='readonly')
                entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            elif key == "materia_id":
                entry = ttk.Combobox(form_frame,
                                    values=[f"{m.id} - {m.nombre}" for m in self.sistema.materias.values()],
                                    font=('Segoe UI', 10),
                                    width=38,
                                    state='readonly')
                entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            elif key == "docente_id":
                entry = ttk.Combobox(form_frame,
                                    values=[f"{d.num_empleado} - {d.get_nombre_completo()}" 
                                           for d in self.sistema.docentes.values()],
                                    font=('Segoe UI', 10),
                                    width=38,
                                    state='readonly')
                entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            else:
                entry = tk.Entry(form_frame,
                               font=('Segoe UI', 10),
                               relief='solid',
                               bd=1,
                               width=40)
                entry.grid(row=i, column=1, pady=8, padx=5, sticky='ew')
            
            entries[key] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        def guardar():
            datos = {}
            for key, entry in entries.items():
                if isinstance(entry, ttk.Combobox):
                    value = entry.get().strip()
                    if " - " in value:
                        datos[key] = value.split(" - ")[0]
                    else:
                        datos[key] = value
                else:
                    datos[key] = entry.get().strip()
            
            if not all(datos.values()):
                messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos")
                return
            
            exito, mensaje = self.sistema.agregar_horario(
                datos['id'],
                datos['materia_id'],
                datos['docente_id'],
                datos['grado'],
                datos['grupo'],
                datos['dia'],
                datos['hora_inicio'],
                datos['hora_fin'],
                datos['aula']
            )
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_inicio()
            else:
                messagebox.showerror("Error", mensaje)
        
        btn_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        btn_frame.grid(row=len(campos), column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame,
                 text="💾 Guardar Horario",
                 command=guardar,
                 bg=self.colors['warning'],
                 fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack()
    
    def mostrar_buscar_horarios(self):
        """Mostrar buscador de horarios en formato de tabla estilo horario escolar"""
        self.limpiar_panel()
        
        title = ttk.Label(self.right_panel,
                         text="🔍 Buscar Horarios - Vista de Grupo",
                         style='Subtitle.TLabel')
        title.pack(pady=20)
        
        # Obtener grupos disponibles
        grupos = self.sistema.obtener_grupos_disponibles()
        
        if not grupos:
            tk.Label(self.right_panel,
                    text="No hay grupos registrados para mostrar horarios",
                    bg=self.colors['surface'],
                    fg=self.colors['text_light'],
                    font=('Segoe UI', 12, 'italic')).pack(pady=50)
            return
        
        # Frame para selector de grupo
        selector_frame = tk.Frame(self.right_panel, bg=self.colors['surface'])
        selector_frame.pack(fill='x', padx=40, pady=20)
        
        tk.Label(selector_frame,
                text="Seleccionar Grupo:",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side='left', padx=5)
        
        grupo_var = tk.StringVar()
        grupos_list = [f"{grado}° {grupo}" for grado, grupo in grupos]
        grupo_combo = ttk.Combobox(selector_frame,
                                  textvariable=grupo_var,
                                  values=grupos_list,
                                  font=('Segoe UI', 12),
                                  width=20,
                                  state='readonly')
        grupo_combo.pack(side='left', padx=5)
        
        if grupos_list:
            grupo_combo.set(grupos_list[0])
        
        # Frame de resultados con scrollbars - Tabla estilo horario
        results_container = tk.Frame(self.right_panel, bg=self.colors['surface'])
        results_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Crear canvas con scrollbars para la tabla
        canvas = tk.Canvas(results_container, bg=self.colors['surface'], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(results_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(results_container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        def mostrar_horarios_grupo(*args):
            """Mostrar horarios del grupo en formato tabla estilo horario"""
            # Limpiar frame de resultados
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            if not grupo_var.get():
                return
            
            # Extraer grado y grupo
            grupo_text = grupo_var.get()
            grado = grupo_text.split("°")[0]
            grupo = grupo_text.split(" ")[1]
            
            # Obtener horarios del grupo
            horarios = self.sistema.obtener_horarios_por_grupo(grado, grupo)
            
            # Título del grupo
            tk.Label(scrollable_frame,
                    text=f"HORARIO - GRADO {grado}° GRUPO {grupo}",
                    bg=self.colors['primary'],
                    fg='white',
                    font=('Segoe UI', 14, 'bold'),
                    pady=12).pack(fill='x', padx=5, pady=5)
            
            if not horarios:
                tk.Label(scrollable_frame,
                        text="No hay horarios registrados para este grupo",
                        bg=self.colors['surface'],
                        fg=self.colors['text_light'],
                        font=('Segoe UI', 12, 'italic')).pack(pady=30)
                return
            
            # Crear diccionario para organizar horarios por materia
            horarios_por_materia = {}
            for horario in horarios:
                if horario.materia_id not in horarios_por_materia:
                    horarios_por_materia[horario.materia_id] = []
                horarios_por_materia[horario.materia_id].append(horario)
            
            # Frame principal de la tabla
            tabla_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=2)
            tabla_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # --- ENCABEZADO DE LA TABLA ---
            # Fila 1: CLAVE, MATERIA/DOCENTE, E, y días de la semana
            tk.Label(tabla_frame, text="CLAVE", 
                    bg=self.colors['table_header'], fg='white',
                    font=('Segoe UI', 10, 'bold'), width=15, height=2,
                    relief='solid', bd=1).grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
            
            tk.Label(tabla_frame, text="MATERIA/DOCENTE", 
                    bg=self.colors['table_header'], fg='white',
                    font=('Segoe UI', 10, 'bold'), width=25, height=2,
                    relief='solid', bd=1).grid(row=0, column=1, padx=1, pady=1, sticky='nsew')
            
            tk.Label(tabla_frame, text="Mo/Sp", 
                    bg=self.colors['table_header'], fg='white',
                    font=('Segoe UI', 10, 'bold'), width=8, height=2,
                    relief='solid', bd=1).grid(row=0, column=2, padx=1, pady=1, sticky='nsew')
            
            # Columnas para cada día de la semana
            col_idx = 3
            for dia in self.dias_semana:
                tk.Label(tabla_frame, text=dia, 
                        bg=self.colors['table_header'], fg='white',
                        font=('Segoe UI', 10, 'bold'), width=12, height=2,
                        relief='solid', bd=1).grid(row=0, column=col_idx, padx=1, pady=1, sticky='nsew')
                col_idx += 1
            
            # --- FILAS DE MATERIAS ---
            row_idx = 1
            for materia_id, horarios_materia in horarios_por_materia.items():
                materia = self.sistema.materias.get(materia_id)
                if not materia:
                    continue
                
                # Obtener docente de uno de los horarios (todos deberían tener el mismo docente)
                docente_id = horarios_materia[0].docente_id
                docente = self.sistema.docentes.get(docente_id)
                docente_nombre = docente.get_nombre_completo() if docente else "Sin asignar"
                
                # Información de la materia
                creditos = "05.00"  # Valor por defecto, podrías agregarlo a la clase Materia
                
                # Fila 1: CLAVE y nombre de materia
                tk.Label(tabla_frame, text=materia.id, 
                        bg='white', fg=self.colors['text'],
                        font=('Segoe UI', 9, 'bold'), relief='solid', bd=1,
                        padx=5, pady=5).grid(row=row_idx, column=0, padx=1, pady=1, sticky='nsew')
                
                tk.Label(tabla_frame, text=f"{horarios_materia[0].grupo}  {creditos} {materia.nombre}", 
                        bg='white', fg=self.colors['text'],
                        font=('Segoe UI', 9), relief='solid', bd=1,
                        padx=5, pady=5, anchor='w').grid(row=row_idx, column=1, padx=1, pady=1, sticky='nsew')
                
                tk.Label(tabla_frame, text="E", 
                        bg='white', fg=self.colors['text'],
                        font=('Segoe UI', 9), relief='solid', bd=1,
                        padx=5, pady=5).grid(row=row_idx, column=2, padx=1, pady=1, sticky='nsew')
                
                # Celdas de días de la semana
                col_idx = 3
                for dia in self.dias_semana:
                    horario_dia = next((h for h in horarios_materia if h.dia == dia), None)
                    if horario_dia:
                        # Formato: hora y aula
                        texto = f"{horario_dia.hora_inicio}-{horario_dia.hora_fin[-5:]}\n{horario_dia.aula}"
                        tk.Label(tabla_frame, text=texto, 
                                bg='#E6F3FF', fg=self.colors['text'],
                                font=('Segoe UI', 8), relief='solid', bd=1,
                                padx=3, pady=3).grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky='nsew')
                    else:
                        tk.Label(tabla_frame, text="", 
                                bg='white', relief='solid', bd=1,
                                padx=3, pady=3).grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky='nsew')
                    col_idx += 1
                
                row_idx += 1
                
                # Fila 2: DOCENTE (debajo del nombre de la materia)
                tk.Label(tabla_frame, text="", 
                        bg='white', relief='solid', bd=1,
                        padx=5, pady=5).grid(row=row_idx, column=0, padx=1, pady=1, sticky='nsew')
                
                tk.Label(tabla_frame, text=docente_nombre, 
                        bg='#F5F5F5', fg=self.colors['text'],
                        font=('Segoe UI', 9, 'italic'), relief='solid', bd=1,
                        padx=5, pady=5, anchor='w').grid(row=row_idx, column=1, padx=1, pady=1, sticky='nsew')
                
                tk.Label(tabla_frame, text="", 
                        bg='white', relief='solid', bd=1,
                        padx=5, pady=5).grid(row=row_idx, column=2, padx=1, pady=1, sticky='nsew')
                
                # Celdas de días para la fila del docente (vacías)
                col_idx = 3
                for dia in self.dias_semana:
                    tk.Label(tabla_frame, text="", 
                            bg='white', relief='solid', bd=1,
                            padx=3, pady=3).grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky='nsew')
                    col_idx += 1
                
                row_idx += 1
                # Espacio entre materias
                row_idx += 1
            
            # Configurar pesos de las columnas
            tabla_frame.grid_columnconfigure(0, weight=1)  # CLAVE
            tabla_frame.grid_columnconfigure(1, weight=3)  # MATERIA/DOCENTE
            tabla_frame.grid_columnconfigure(2, weight=1)  # Mo/Sp
            for i in range(3, 10):  # Días de la semana
                tabla_frame.grid_columnconfigure(i, weight=2)
            
            # Total de horarios
            tk.Label(scrollable_frame,
                    text=f"Total de materias: {len(horarios_por_materia)} | Total de horarios: {len(horarios)}",
                    bg=self.colors['surface'],
                    fg=self.colors['text_light'],
                    font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        # Evento de selección de grupo
        grupo_var.trace('w', mostrar_horarios_grupo)
        
        # Mostrar horarios del primer grupo
        if grupos_list:
            mostrar_horarios_grupo()


def main():
    """Función principal"""
    root = tk.Tk()
    app = SistemaEscolarGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()