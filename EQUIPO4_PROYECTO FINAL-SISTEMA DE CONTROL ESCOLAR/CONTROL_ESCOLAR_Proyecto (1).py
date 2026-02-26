"""
Sistema de Control Escolar - Versión 2.0 Completa
Mejoras implementadas:
- Módulo 1: Autenticación con roles (Admin, Docente, Estudiante), mostrar/ocultar contraseña,
            validación de contraseña segura, registro de usuarios
- Módulo 2: Catálogo de Alumnos CRUD completo con fotografía, dirección, lugar de nacimiento,
            último grado, carrera, grupo, estatus. Permisos por rol.
- Módulo 3: Catálogo de Docentes con tipo de contrato, baja temporal, materias que imparte
- Módulo 4: Catálogos Unificados (Alumnos, Docentes, Materias, Grupos, Carreras, Aulas)
- Módulo 5: Gestión de Materias y cambio de grupo
- Módulo 6: Gestión de Carreras con materias, grupos y docentes asociados
- Módulo 7: Horarios con validación de cruces, catálogo de aulas
- Módulo 8: UX mejorada con desplegables, confirmaciones, filtros
- Módulo 9: Edición integrada en las vistas de listado
- Módulo 10: Gestión de usuarios unificada, registro mejorado y ventanas emergentes de detalle
"""

import json
import os
import re
import base64
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

PIL_DISPONIBLE = False
try:
    from PIL import Image, ImageTk  # type: ignore
    PIL_DISPONIBLE = True
except Exception:
    PIL_DISPONIBLE = False

# ===========================
# CONSTANTES GLOBALES
# ===========================

ROLES = ['Administración', 'Docente', 'Estudiante']

TIPOS_CONTRATO = ['Permanente', 'Temporal', 'Invitado', 'Suplente', 'Jubilado', 'Despedido']

CARRERAS = {
    'S':  'Sistemas Computacionales',
    'I':  'Industrial',
    'E':  'Electrónica',
    'M':  'Mecatrónica',
    'G':  'Gestión Empresarial',
    'C':  'Contador Público',
    'A':  'Administración',
    'D':  'Derecho',
}

DIAS_SEMANA = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO']

HORAS_DISPONIBLES = [
    '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
    '10:00', '10:30', '11:00', '11:30', '12:00', '12:30',
    '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
    '16:00', '16:30', '17:00', '17:30', '18:00', '18:30',
    '19:00', '19:30', '20:00', '20:30', '21:00',
]

SEMESTRES = [str(i) for i in range(1, 10)]
GRUPOS_LETRAS = ['A', 'B', 'C', 'D', 'E', 'F']

# ===========================
# CONSTANTES DE SEGURIDAD
# ===========================
PASSWORD_ADMIN_DOCENTE = "Tecnm20271886"  

# ===========================
# UTILIDADES
# ===========================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def validar_password(password: str) -> tuple:
    """Valida que la contraseña cumpla los requisitos de seguridad."""
    errores = []
    if len(password) < 8:
        errores.append("• Mínimo 8 caracteres")
    if not re.search(r'[A-Z]', password):
        errores.append("• Al menos una letra mayúscula")
    if not re.search(r'[a-z]', password):
        errores.append("• Al menos una letra minúscula")
    if not re.search(r'\d', password):
        errores.append("• Al menos un número")
    return len(errores) == 0, errores

def imagen_a_base64(ruta: str) -> str:
    """Convierte una imagen a string base64."""
    try:
        with open(ruta, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except:
        return ''

def base64_a_imagen(data: str, size=(80, 80)):
    """Convierte base64 a PhotoImage de tkinter."""
    if not data or not PIL_DISPONIBLE:
        return None
    try:
        import io
        img_bytes = base64.b64decode(data)
        img = Image.open(io.BytesIO(img_bytes))
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# ===========================
# MODELOS DE DATOS
# ===========================

class Usuario:
    def __init__(self, matricula_o_id, nombre, password_hash, rol, email=''):
        self.id = matricula_o_id
        self.nombre = nombre
        self.password_hash = password_hash
        self.rol = rol  # 'Administración', 'Docente', 'Estudiante'
        self.email = email
        self.activo = True

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'password_hash': self.password_hash,
            'rol': self.rol,
            'email': self.email,
            'activo': self.activo,
        }

    @staticmethod
    def from_dict(data):
        u = Usuario(data['id'], data['nombre'], data['password_hash'], data['rol'], data.get('email', ''))
        u.activo = data.get('activo', True)
        return u


class Aula:
    def __init__(self, id, numero_salon, edificio, capacidad):
        self.id = id
        self.numero_salon = numero_salon
        self.edificio = edificio
        self.capacidad = int(capacidad)

    def __str__(self):
        return f"{self.numero_salon} - {self.edificio} (Cap. {self.capacidad})"

    def to_dict(self):
        return {
            'id': self.id,
            'numero_salon': self.numero_salon,
            'edificio': self.edificio,
            'capacidad': self.capacidad,
        }

    @staticmethod
    def from_dict(data):
        return Aula(data['id'], data['numero_salon'], data['edificio'], data['capacidad'])


class Carrera:
    def __init__(self, codigo, nombre, descripcion=''):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion

    def to_dict(self):
        return {'codigo': self.codigo, 'nombre': self.nombre, 'descripcion': self.descripcion}

    @staticmethod
    def from_dict(data):
        return Carrera(data['codigo'], data['nombre'], data.get('descripcion', ''))


class Alumno:
    def __init__(self, id, nombre, apellido, fecha_nacimiento, telefono,
                 matricula, grado, grupo, activo=True,
                 direccion='', lugar_nacimiento='', ultimo_grado_estudios='',
                 foto_base64='', email=''):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.matricula = matricula
        self.grado = grado          # Código completo ej: "3SA"
        self.grupo = grupo          # Solo la letra ej: "A"
        self.activo = activo
        # Campos extendidos (Módulo 2)
        self.direccion = direccion
        self.lugar_nacimiento = lugar_nacimiento
        self.ultimo_grado_estudios = ultimo_grado_estudios
        self.foto_base64 = foto_base64
        self.email = email
        # Fechas
        self.fecha_alta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_baja = None
        self.motivo_baja = None

    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def dar_de_baja(self, motivo=''):
        self.activo = False
        self.fecha_baja = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.motivo_baja = motivo

    def reactivar(self):
        self.activo = True
        self.fecha_baja = None
        self.motivo_baja = None

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'apellido': self.apellido,
            'fecha_nacimiento': self.fecha_nacimiento, 'telefono': self.telefono,
            'matricula': self.matricula, 'grado': self.grado, 'grupo': self.grupo,
            'activo': self.activo, 'direccion': self.direccion,
            'lugar_nacimiento': self.lugar_nacimiento,
            'ultimo_grado_estudios': self.ultimo_grado_estudios,
            'foto_base64': self.foto_base64, 'email': self.email,
            'fecha_alta': self.fecha_alta, 'fecha_baja': self.fecha_baja,
            'motivo_baja': self.motivo_baja,
        }

    @staticmethod
    def from_dict(data):
        a = Alumno(
            data['id'], data['nombre'], data['apellido'],
            data['fecha_nacimiento'], data['telefono'],
            data['matricula'], data['grado'], data['grupo'], data['activo'],
            data.get('direccion', ''), data.get('lugar_nacimiento', ''),
            data.get('ultimo_grado_estudios', ''), data.get('foto_base64', ''),
            data.get('email', ''),
        )
        a.fecha_alta = data.get('fecha_alta', a.fecha_alta)
        a.fecha_baja = data.get('fecha_baja')
        a.motivo_baja = data.get('motivo_baja')
        return a


class Docente:
    def __init__(self, id, nombre, apellido, fecha_nacimiento, telefono,
                 num_empleado, especialidad, email,
                 tipo_contrato='Permanente', direccion='',
                 lugar_nacimiento='', ultimo_grado_estudios='', foto_base64='',
                 activo=True, baja_temporal=False):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.num_empleado = num_empleado
        self.especialidad = especialidad
        self.email = email
        # Campos extendidos (Módulo 3)
        self.tipo_contrato = tipo_contrato
        self.direccion = direccion
        self.lugar_nacimiento = lugar_nacimiento
        self.ultimo_grado_estudios = ultimo_grado_estudios
        self.foto_base64 = foto_base64
        self.activo = activo
        self.baja_temporal = baja_temporal

    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'apellido': self.apellido,
            'fecha_nacimiento': self.fecha_nacimiento, 'telefono': self.telefono,
            'num_empleado': self.num_empleado, 'especialidad': self.especialidad,
            'email': self.email, 'tipo_contrato': self.tipo_contrato,
            'direccion': self.direccion, 'lugar_nacimiento': self.lugar_nacimiento,
            'ultimo_grado_estudios': self.ultimo_grado_estudios,
            'foto_base64': self.foto_base64, 'activo': self.activo,
            'baja_temporal': self.baja_temporal,
        }

    @staticmethod
    def from_dict(data):
        return Docente(
            data['id'], data['nombre'], data['apellido'],
            data['fecha_nacimiento'], data['telefono'],
            data['num_empleado'], data['especialidad'], data['email'],
            data.get('tipo_contrato', 'Permanente'), data.get('direccion', ''),
            data.get('lugar_nacimiento', ''), data.get('ultimo_grado_estudios', ''),
            data.get('foto_base64', ''), data.get('activo', True),
            data.get('baja_temporal', False),
        )


class Materia:
    def __init__(self, id, nombre, grado, descripcion='', carrera_codigo='', creditos=0):
        self.id = id
        self.nombre = nombre
        self.grado = grado
        self.descripcion = descripcion
        self.carrera_codigo = carrera_codigo
        self.creditos = creditos

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'grado': self.grado,
            'descripcion': self.descripcion, 'carrera_codigo': self.carrera_codigo,
            'creditos': self.creditos,
        }

    @staticmethod
    def from_dict(data):
        return Materia(
            data['id'], data['nombre'], data['grado'],
            data.get('descripcion', ''), data.get('carrera_codigo', ''),
            data.get('creditos', 0),
        )


class SolicitudCambioGrupo:
    def __init__(self, id, matricula_alumno, grupo_actual, grupo_solicitado, motivo='', estado='Pendiente'):
        self.id = id
        self.matricula_alumno = matricula_alumno
        self.grupo_actual = grupo_actual
        self.grupo_solicitado = grupo_solicitado
        self.motivo = motivo
        self.estado = estado  # Pendiente, Aprobada, Rechazada
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'id': self.id, 'matricula_alumno': self.matricula_alumno,
            'grupo_actual': self.grupo_actual, 'grupo_solicitado': self.grupo_solicitado,
            'motivo': self.motivo, 'estado': self.estado, 'fecha': self.fecha,
        }

    @staticmethod
    def from_dict(data):
        s = SolicitudCambioGrupo(
            data['id'], data['matricula_alumno'], data['grupo_actual'],
            data['grupo_solicitado'], data.get('motivo', ''), data.get('estado', 'Pendiente')
        )
        s.fecha = data.get('fecha', s.fecha)
        return s


class Calificacion:
    def __init__(self, id, matricula_alumno, materia_id, semestre, calificacion, fecha_registro=None):
        self.id = id
        self.matricula_alumno = matricula_alumno
        self.materia_id = materia_id
        self.semestre = semestre
        self.calificacion = calificacion
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'id': self.id, 'matricula_alumno': self.matricula_alumno,
            'materia_id': self.materia_id, 'semestre': self.semestre,
            'calificacion': self.calificacion, 'fecha_registro': self.fecha_registro,
        }

    @staticmethod
    def from_dict(data):
        return Calificacion(
            data['id'], data['matricula_alumno'], data['materia_id'],
            data['semestre'], data['calificacion'], data.get('fecha_registro'),
        )


class Horario:
    def __init__(self, id, materia_id, docente_id, grado, grupo,
                 dia, hora_inicio, hora_fin, aula_id):
        self.id = id
        self.materia_id = materia_id
        self.docente_id = docente_id
        self.grado = grado
        self.grupo = grupo
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula_id = aula_id  # ahora referencia al ID del aula

    def to_dict(self):
        return {
            'id': self.id, 'materia_id': self.materia_id, 'docente_id': self.docente_id,
            'grado': self.grado, 'grupo': self.grupo, 'dia': self.dia,
            'hora_inicio': self.hora_inicio, 'hora_fin': self.hora_fin, 'aula_id': self.aula_id,
        }

    @staticmethod
    def from_dict(data):
        return Horario(
            data['id'], data['materia_id'], data['docente_id'], data['grado'],
            data['grupo'], data['dia'], data['hora_inicio'], data['hora_fin'],
            data.get('aula_id', data.get('aula', '')),
        )


# ===========================
# SISTEMA PRINCIPAL
# ===========================

class SistemaControlEscolar:

    ARCHIVO_DATOS = "datos_escuela.json"
    ARCHIVO_HISTORIAL = "historial_cambios.json"
    ARCHIVO_USUARIOS = "usuarios.json"

    def __init__(self):
        self.alumnos: Dict[str, Alumno] = {}
        self.docentes: Dict[str, Docente] = {}
        self.materias: Dict[str, Materia] = {}
        self.calificaciones: Dict[str, Calificacion] = {}
        self.horarios: Dict[str, Horario] = {}
        self.aulas: Dict[str, Aula] = {}
        self.carreras: Dict[str, Carrera] = {}
        self.usuarios: Dict[str, Usuario] = {}
        self.solicitudes_grupo: Dict[str, SolicitudCambioGrupo] = {}
        self.historial: List[Dict] = []
        self.usuario_actual: Optional[Usuario] = None
        self._cargar_todo()
        self._inicializar_datos_default()

    # ---------- Inicialización ----------

    def _inicializar_datos_default(self):
        """Crea datos iniciales si no existen."""
        # Admin por defecto
        if not self.usuarios:
            admin_hash = hash_password('Admin123!')
            admin = Usuario('admin', 'Administrador', admin_hash, 'Administración', 'admin@escuela.mx')
            self.usuarios['admin'] = admin
            self._guardar_usuarios()

        # Carreras por defecto
        if not self.carreras:
            for codigo, nombre in CARRERAS.items():
                self.carreras[codigo] = Carrera(codigo, nombre)
            self._guardar_datos()

        # Aulas por defecto
        if not self.aulas:
            for i in range(1, 6):
                a = Aula(f"A{i:02d}", f"Salon {i}", "Edificio A", 30)
                self.aulas[a.id] = a
            for i in range(1, 4):
                a = Aula(f"B{i:02d}", f"Salon {i}", "Edificio B", 40)
                self.aulas[a.id] = a
            self._guardar_datos()

    # ---------- Persistencia ----------

    def _cargar_todo(self):
        self._cargar_datos()
        self._cargar_historial()
        self._cargar_usuarios()

    def _cargar_usuarios(self):
        if os.path.exists(self.ARCHIVO_USUARIOS):
            try:
                with open(self.ARCHIVO_USUARIOS, 'r', encoding='utf-8') as f:
                    for d in json.load(f):
                        u = Usuario.from_dict(d)
                        self.usuarios[u.id] = u
            except:
                pass

    def _guardar_usuarios(self):
        try:
            with open(self.ARCHIVO_USUARIOS, 'w', encoding='utf-8') as f:
                json.dump([u.to_dict() for u in self.usuarios.values()], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando usuarios: {e}")

    def _cargar_datos(self):
        if not os.path.exists(self.ARCHIVO_DATOS):
            return
        try:
            with open(self.ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            for d in datos.get('alumnos', []):
                a = Alumno.from_dict(d)
                self.alumnos[a.matricula] = a
            for d in datos.get('docentes', []):
                doc = Docente.from_dict(d)
                self.docentes[doc.num_empleado] = doc
            for d in datos.get('materias', []):
                m = Materia.from_dict(d)
                self.materias[m.id] = m
            for d in datos.get('calificaciones', []):
                c = Calificacion.from_dict(d)
                self.calificaciones[c.id] = c
            for d in datos.get('horarios', []):
                h = Horario.from_dict(d)
                self.horarios[h.id] = h
            for d in datos.get('aulas', []):
                au = Aula.from_dict(d)
                self.aulas[au.id] = au
            for d in datos.get('carreras', []):
                ca = Carrera.from_dict(d)
                self.carreras[ca.codigo] = ca
            for d in datos.get('solicitudes_grupo', []):
                s = SolicitudCambioGrupo.from_dict(d)
                self.solicitudes_grupo[s.id] = s
        except Exception as e:
            print(f"Error cargando datos: {e}")

    def _guardar_datos(self):
        datos = {
            'alumnos': [a.to_dict() for a in self.alumnos.values()],
            'docentes': [d.to_dict() for d in self.docentes.values()],
            'materias': [m.to_dict() for m in self.materias.values()],
            'calificaciones': [c.to_dict() for c in self.calificaciones.values()],
            'horarios': [h.to_dict() for h in self.horarios.values()],
            'aulas': [a.to_dict() for a in self.aulas.values()],
            'carreras': [c.to_dict() for c in self.carreras.values()],
            'solicitudes_grupo': [s.to_dict() for s in self.solicitudes_grupo.values()],
        }
        try:
            with open(self.ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando datos: {e}")

    def _cargar_historial(self):
        if os.path.exists(self.ARCHIVO_HISTORIAL):
            try:
                with open(self.ARCHIVO_HISTORIAL, 'r', encoding='utf-8') as f:
                    self.historial = json.load(f)
            except:
                self.historial = []

    def _guardar_historial(self):
        try:
            with open(self.ARCHIVO_HISTORIAL, 'w', encoding='utf-8') as f:
                json.dump(self.historial, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def registrar_cambio(self, tipo, descripcion, datos=None):
        cambio = {
            'id': len(self.historial) + 1,
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'usuario': self.usuario_actual.id if self.usuario_actual else 'Sistema',
            'rol': self.usuario_actual.rol if self.usuario_actual else 'Sistema',
            'tipo': tipo,
            'descripcion': descripcion,
            'datos': datos or {},
        }
        self.historial.append(cambio)
        self._guardar_historial()

    # ---------- Auth ----------

    def login(self, user_id, password, rol_seleccionado):
        u = self.usuarios.get(user_id)
        if not u:
            return False, "Usuario no encontrado"
        if not u.activo:
            return False, "Usuario desactivado"
        if u.password_hash != hash_password(password):
            return False, "Contraseña incorrecta"
        if u.rol != rol_seleccionado:
            return False, f"No tienes el rol '{rol_seleccionado}'"
        self.usuario_actual = u
        return True, "Login exitoso"

    def registrar_usuario(self, user_id, nombre, apellido, password, rol, email='',
                          fecha_nacimiento='', telefono='', especialidad=''):
        """Registra un nuevo usuario y crea automáticamente su perfil si es Estudiante o Docente."""
        if user_id in self.usuarios:
            return False, f"El ID '{user_id}' ya está registrado"
        ok, errores = validar_password(password)
        if not ok:
            return False, "Contraseña no segura:\n" + "\n".join(errores)
        
        # Crear usuario base
        nombre_completo = f"{nombre} {apellido}".strip()
        u = Usuario(user_id, nombre_completo, hash_password(password), rol, email)
        self.usuarios[user_id] = u
        self._guardar_usuarios()
        
        # Si es estudiante, crear alumno automáticamente
        if rol == 'Estudiante':
            # Verificar que no exista ya un alumno con esa matrícula
            if user_id in self.alumnos:
                # Si existe, no creamos duplicado, pero el usuario ya se guardó
                pass
            else:
                ok_alumno, msg_alumno = self.dar_alta_alumno(
                    nombre=nombre,
                    apellido=apellido,
                    fecha_nacimiento=fecha_nacimiento,
                    telefono=telefono,
                    matricula=user_id,
                    grado='',  # Se asignará después
                    grupo='',
                    direccion='',
                    lugar_nacimiento='',
                    ultimo_grado='',
                    foto_base64='',
                    email=email
                )
                if not ok_alumno:
                    # Si falla, eliminamos el usuario para mantener consistencia
                    del self.usuarios[user_id]
                    self._guardar_usuarios()
                    return False, f"Error al crear perfil de alumno: {msg_alumno}"
        
        # Si es docente, crear docente automáticamente
        elif rol == 'Docente':
            if user_id in self.docentes:
                pass
            else:
                ok_docente, msg_docente = self.agregar_docente(
                    nombre=nombre,
                    apellido=apellido,
                    fecha_nacimiento=fecha_nacimiento,
                    telefono=telefono,
                    num_empleado=user_id,
                    especialidad=especialidad,
                    email=email,
                    tipo_contrato='Permanente',
                    direccion='',
                    lugar_nacimiento='',
                    ultimo_grado='',
                    foto_base64=''
                )
                if not ok_docente:
                    del self.usuarios[user_id]
                    self._guardar_usuarios()
                    return False, f"Error al crear perfil de docente: {msg_docente}"
        
        self.registrar_cambio('REGISTRO_USUARIO', f"Registro de usuario: {nombre_completo} ({rol})")
        return True, f"Usuario '{user_id}' registrado exitosamente"

    def cambiar_password(self, user_id, nueva_password):
        u = self.usuarios.get(user_id)
        if not u:
            return False, "Usuario no encontrado"
        ok, errores = validar_password(nueva_password)
        if not ok:
            return False, "Contraseña no segura:\n" + "\n".join(errores)
        u.password_hash = hash_password(nueva_password)
        self._guardar_usuarios()
        self.registrar_cambio('CAMBIO_PASSWORD', f"Cambio de contraseña para {user_id}")
        return True, "Contraseña actualizada"

    # ---------- Helpers ----------

    def get_rol(self):
        return self.usuario_actual.rol if self.usuario_actual else None

    def es_admin(self):
        return self.get_rol() == 'Administración'

    def es_docente(self):
        return self.get_rol() == 'Docente'

    def es_estudiante(self):
        return self.get_rol() == 'Estudiante'

    @staticmethod
    def parsear_grupo_completo(grupo_completo):
        if not grupo_completo or len(grupo_completo) < 3:
            return None, None, None
        return grupo_completo[0], grupo_completo[1], grupo_completo[2]

    @staticmethod
    def construir_grupo_completo(semestre, carrera_codigo, grupo):
        return f"{semestre}{carrera_codigo}{grupo}"

    def get_nombre_carrera(self, codigo):
        c = self.carreras.get(codigo)
        return c.nombre if c else CARRERAS.get(codigo, 'Desconocida')

    def get_aulas_lista(self):
        return [f"{a.id} - {a}" for a in sorted(self.aulas.values(), key=lambda x: x.id)]

    def get_materias_lista(self):
        return [f"{m.id} - {m.nombre}" for m in sorted(self.materias.values(), key=lambda x: x.nombre)]

    def get_docentes_lista(self):
        return [f"{d.num_empleado} - {d.get_nombre_completo()} | {d.especialidad}"
                for d in sorted(self.docentes.values(), key=lambda x: x.apellido)]

    def get_materias_docente_grado(self, num_empleado, grado):
        """Retorna lista 'ID - Nombre' de materias que imparte un docente en un grado específico."""
        ids = {h.materia_id for h in self.horarios.values()
               if h.docente_id == num_empleado and h.grado == grado}
        mats = [self.materias[mid] for mid in ids if mid in self.materias]
        return [f"{m.id} - {m.nombre}" for m in sorted(mats, key=lambda x: x.nombre)] or ['(Sin materias asignadas)']

    def get_grupos_lista(self):
        grupos = set()
        for a in self.alumnos.values():
            if a.activo:
                grupos.add(a.grado)
        return sorted(grupos)

    # ---------- Alumnos ----------

    def dar_alta_alumno(self, nombre, apellido, fecha_nacimiento, telefono,
                        matricula, grado, grupo,
                        direccion='', lugar_nacimiento='', ultimo_grado='',
                        foto_base64='', email=''):
        matricula = str(matricula).strip()
        if matricula in self.alumnos:
            return False, f"Ya existe un alumno con matrícula {matricula}"
        a = Alumno(matricula, nombre, apellido, fecha_nacimiento, telefono,
                   matricula, grado, grupo, True,
                   direccion, lugar_nacimiento, ultimo_grado, foto_base64, email)
        self.alumnos[matricula] = a
        self._guardar_datos()
        self.registrar_cambio('ALTA_ALUMNO', f"Alta de alumno: {a.get_nombre_completo()} ({matricula})")
        return True, f"Alumno {a.get_nombre_completo()} dado de alta"

    def editar_alumno(self, matricula, nombre, apellido, fecha_nacimiento, telefono,
                      grado, grupo, direccion='', lugar_nacimiento='',
                      ultimo_grado='', foto_base64=None, email=''):
        matricula = str(matricula).strip()
        a = self.alumnos.get(matricula)
        if not a:
            return False, "Alumno no encontrado"
        if not a.activo and not self.es_admin():
            return False, "Solo Administración puede editar alumnos dados de baja"
        a.nombre = nombre
        a.apellido = apellido
        a.fecha_nacimiento = fecha_nacimiento
        a.telefono = telefono
        a.grado = grado
        a.grupo = grupo
        a.direccion = direccion
        a.lugar_nacimiento = lugar_nacimiento
        a.ultimo_grado_estudios = ultimo_grado
        a.email = email
        if foto_base64 is not None:
            a.foto_base64 = foto_base64
        self._guardar_datos()
        self.registrar_cambio('EDITAR_ALUMNO', f"Edición de alumno: {a.get_nombre_completo()} ({matricula})")
        return True, f"Alumno {a.get_nombre_completo()} actualizado"

    def dar_baja_alumno(self, matricula, motivo=''):
        a = self.alumnos.get(str(matricula).strip())
        if not a:
            return False, "Alumno no encontrado"
        if not a.activo:
            return False, "El alumno ya está dado de baja"
        a.dar_de_baja(motivo)
        self._guardar_datos()
        self.registrar_cambio('BAJA_ALUMNO', f"Baja: {a.get_nombre_completo()}. Motivo: {motivo}")
        return True, f"Alumno {a.get_nombre_completo()} dado de baja"

    def reactivar_alumno(self, matricula):
        a = self.alumnos.get(str(matricula).strip())
        if not a:
            return False, "Alumno no encontrado"
        if a.activo:
            return False, "El alumno ya está activo"
        a.reactivar()
        self._guardar_datos()
        self.registrar_cambio('REACTIVAR_ALUMNO', f"Reactivación: {a.get_nombre_completo()}")
        return True, f"Alumno {a.get_nombre_completo()} reactivado"

    def cambiar_grupo_alumno(self, matricula, nuevo_grado, nuevo_grupo):
        a = self.alumnos.get(str(matricula).strip())
        if not a:
            return False, "Alumno no encontrado"
        if not a.activo:
            return False, "No se puede cambiar grupo a un alumno dado de baja"
        anterior = a.grado
        a.grado = nuevo_grado
        a.grupo = nuevo_grupo
        self._guardar_datos()
        self.registrar_cambio('CAMBIO_GRUPO', f"{a.get_nombre_completo()}: {anterior} → {nuevo_grado}")
        return True, f"Grupo cambiado de {anterior} a {nuevo_grado}"

    def solicitar_cambio_grupo(self, matricula, grupo_solicitado, motivo=''):
        a = self.alumnos.get(str(matricula).strip())
        if not a:
            return False, "Alumno no encontrado"
        sol_id = f"SOL_{matricula}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        s = SolicitudCambioGrupo(sol_id, matricula, a.grado, grupo_solicitado, motivo)
        self.solicitudes_grupo[sol_id] = s
        self._guardar_datos()
        self.registrar_cambio('SOLICITUD_GRUPO', f"Solicitud cambio grupo: {a.get_nombre_completo()}")
        return True, "Solicitud enviada"

    def resolver_solicitud_grupo(self, sol_id, accion):
        s = self.solicitudes_grupo.get(sol_id)
        if not s:
            return False, "Solicitud no encontrada"
        s.estado = accion  # 'Aprobada' o 'Rechazada'
        if accion == 'Aprobada':
            sem, car_cod, grp_letra = self.parsear_grupo_completo(s.grupo_solicitado)
            if sem:
                self.cambiar_grupo_alumno(s.matricula_alumno, s.grupo_solicitado, grp_letra or '')
        self._guardar_datos()
        return True, f"Solicitud {accion}"

    def buscar_alumnos(self, termino='', solo_activos=True):
        t = termino.lower().strip()
        return [a for a in self.alumnos.values()
                if (not solo_activos or a.activo) and
                   (not t or t in a.matricula.lower() or t in a.nombre.lower() or
                    t in a.apellido.lower() or t in a.get_nombre_completo().lower())]

    def buscar_alumnos_inactivos(self, termino=''):
        t = termino.lower().strip()
        return [a for a in self.alumnos.values()
                if not a.activo and
                   (not t or t in a.matricula.lower() or t in a.get_nombre_completo().lower())]

    def buscar_alumnos_por_grupo(self, grupo_completo):
        """Busca alumnos por código de grupo completo (ej: '3SA')"""
        t = grupo_completo.lower().strip()
        return [a for a in self.alumnos.values() if a.activo and a.grado.lower() == t]

    # ---------- Docentes ----------

    def agregar_docente(self, nombre, apellido, fecha_nacimiento, telefono,
                        num_empleado, especialidad, email,
                        tipo_contrato='Permanente', direccion='',
                        lugar_nacimiento='', ultimo_grado='', foto_base64=''):
        if num_empleado in self.docentes:
            return False, f"Ya existe docente con número {num_empleado}"
        d = Docente(num_empleado, nombre, apellido, fecha_nacimiento, telefono,
                    num_empleado, especialidad, email, tipo_contrato,
                    direccion, lugar_nacimiento, ultimo_grado, foto_base64)
        self.docentes[num_empleado] = d
        self._guardar_datos()
        self.registrar_cambio('ALTA_DOCENTE', f"Alta docente: {d.get_nombre_completo()} ({num_empleado})")
        return True, f"Docente {d.get_nombre_completo()} agregado"

    def editar_docente(self, num_empleado, nombre, apellido, fecha_nacimiento,
                       telefono, especialidad, email, tipo_contrato='Permanente',
                       direccion='', lugar_nacimiento='', ultimo_grado='', foto_base64=None):
        d = self.docentes.get(str(num_empleado).strip())
        if not d:
            return False, "Docente no encontrado"
        d.nombre = nombre
        d.apellido = apellido
        d.fecha_nacimiento = fecha_nacimiento
        d.telefono = telefono
        d.especialidad = especialidad
        d.email = email
        d.tipo_contrato = tipo_contrato
        d.direccion = direccion
        d.lugar_nacimiento = lugar_nacimiento
        d.ultimo_grado_estudios = ultimo_grado
        if foto_base64 is not None:
            d.foto_base64 = foto_base64
        self._guardar_datos()
        self.registrar_cambio('EDITAR_DOCENTE', f"Edición docente: {d.get_nombre_completo()} ({num_empleado})")
        return True, f"Docente {d.get_nombre_completo()} actualizado"

    def baja_temporal_docente(self, num_empleado):
        d = self.docentes.get(str(num_empleado).strip())
        if not d:
            return False, "Docente no encontrado"
        d.baja_temporal = True
        d.activo = False
        self._guardar_datos()
        self.registrar_cambio('BAJA_TEMPORAL_DOCENTE', f"Baja temporal: {d.get_nombre_completo()}")
        return True, f"Docente {d.get_nombre_completo()} dado de baja temporal"

    def reactivar_docente(self, num_empleado):
        d = self.docentes.get(str(num_empleado).strip())
        if not d:
            return False, "Docente no encontrado"
        d.baja_temporal = False
        d.activo = True
        self._guardar_datos()
        self.registrar_cambio('REACTIVAR_DOCENTE', f"Reactivación: {d.get_nombre_completo()}")
        return True, f"Docente {d.get_nombre_completo()} reactivado"

    def buscar_docentes(self, termino=''):
        t = termino.lower().strip()
        return [d for d in self.docentes.values()
                if not t or t in d.num_empleado.lower() or
                   t in d.get_nombre_completo().lower() or
                   t in d.especialidad.lower() or t in d.email.lower()]

    def get_materias_docente(self, num_empleado):
        """Retorna los horarios/materias que imparte un docente."""
        return [h for h in self.horarios.values() if h.docente_id == num_empleado]

    def get_grupos_del_docente(self, num_empleado):
        """Retorna el conjunto de (grado, grupo) que imparte un docente.
        Se usa para filtrar vistas cuando el usuario logueado es Docente."""
        grupos = set()
        for h in self.horarios.values():
            if h.docente_id == num_empleado:
                grupos.add((h.grado, h.grupo))
        return grupos

    def get_grados_del_docente(self, num_empleado):
        """Retorna el conjunto de strings 'grado' (ej: '3SA') que imparte un docente."""
        return {h.grado for h in self.horarios.values() if h.docente_id == num_empleado}

    # ---------- Materias ----------

    def agregar_materia(self, id, nombre, grado, descripcion='', carrera_codigo='', creditos=0):
        if id in self.materias:
            return False, f"Ya existe materia con ID {id}"
        m = Materia(id, nombre, grado, descripcion, carrera_codigo, creditos)
        self.materias[id] = m
        self._guardar_datos()
        self.registrar_cambio('ALTA_MATERIA', f"Alta materia: {nombre} ({id})")
        return True, f"Materia '{nombre}' agregada"

    def editar_materia(self, id, nombre, grado, descripcion='', carrera_codigo='', creditos=0):
        m = self.materias.get(id)
        if not m:
            return False, "Materia no encontrada"
        m.nombre = nombre
        m.grado = grado
        m.descripcion = descripcion
        m.carrera_codigo = carrera_codigo
        m.creditos = creditos
        self._guardar_datos()
        self.registrar_cambio('EDITAR_MATERIA', f"Edición materia: {nombre} ({id})")
        return True, f"Materia '{nombre}' actualizada"

    def eliminar_materia(self, id):
        if id not in self.materias:
            return False, "Materia no encontrada"
        nombre = self.materias[id].nombre
        del self.materias[id]
        self._guardar_datos()
        self.registrar_cambio('ELIMINAR_MATERIA', f"Eliminación materia: {nombre} ({id})")
        return True, f"Materia '{nombre}' eliminada"

    def buscar_materias(self, termino=''):
        t = termino.lower().strip()
        return [m for m in self.materias.values()
                if not t or t in m.id.lower() or t in m.nombre.lower() or t in m.grado.lower()]

    # ---------- Aulas ----------

    def agregar_aula(self, id, numero_salon, edificio, capacidad):
        if id in self.aulas:
            return False, f"Ya existe aula con ID {id}"
        a = Aula(id, numero_salon, edificio, capacidad)
        self.aulas[id] = a
        self._guardar_datos()
        self.registrar_cambio('ALTA_AULA', f"Alta aula: {numero_salon} ({id})")
        return True, f"Aula '{numero_salon}' agregada"

    def editar_aula(self, id, numero_salon, edificio, capacidad):
        a = self.aulas.get(id)
        if not a:
            return False, "Aula no encontrada"
        a.numero_salon = numero_salon
        a.edificio = edificio
        a.capacidad = int(capacidad)
        self._guardar_datos()
        self.registrar_cambio('EDITAR_AULA', f"Edición aula: {numero_salon} ({id})")
        return True, f"Aula '{numero_salon}' actualizada"

    def eliminar_aula(self, id):
        if id not in self.aulas:
            return False, "Aula no encontrada"
        nombre = str(self.aulas[id])
        del self.aulas[id]
        self._guardar_datos()
        self.registrar_cambio('ELIMINAR_AULA', f"Eliminación aula: {id}")
        return True, f"Aula eliminada"

    # ---------- Carreras ----------

    def agregar_carrera(self, codigo, nombre, descripcion=''):
        if codigo in self.carreras:
            return False, f"Ya existe carrera con código {codigo}"
        c = Carrera(codigo, nombre, descripcion)
        self.carreras[codigo] = c
        self._guardar_datos()
        self.registrar_cambio('ALTA_CARRERA', f"Alta carrera: {nombre} ({codigo})")
        return True, f"Carrera '{nombre}' agregada"

    def editar_carrera(self, codigo, nombre, descripcion=''):
        c = self.carreras.get(codigo)
        if not c:
            return False, "Carrera no encontrada"
        c.nombre = nombre
        c.descripcion = descripcion
        self._guardar_datos()
        self.registrar_cambio('EDITAR_CARRERA', f"Edición carrera: {nombre} ({codigo})")
        return True, f"Carrera '{nombre}' actualizada"

    def eliminar_carrera(self, codigo):
        if codigo not in self.carreras:
            return False, "Carrera no encontrada"
        nombre = self.carreras[codigo].nombre
        del self.carreras[codigo]
        self._guardar_datos()
        self.registrar_cambio('ELIMINAR_CARRERA', f"Eliminación carrera: {nombre} ({codigo})")
        return True, f"Carrera '{nombre}' eliminada"

    # ---------- Horarios ----------

    def validar_cruce_horario(self, docente_id, aula_id, dia, hora_inicio, hora_fin,
                               excluir_id=None):
        """
        Valida que no haya cruce de docente ni aula.
        Retorna lista de strings con los conflictos encontrados.
        Un traslape existe cuando los rangos se solapan, es decir:
            inicio_nuevo < fin_existente  AND  fin_nuevo > inicio_existente
        """
        conflictos = []
        for h in self.horarios.values():
            if h.id == excluir_id:
                continue
            if h.dia != dia:
                continue

            # ── Detección de traslape ──────────────────────────────────────
            # Dos rangos [A,B) y [C,D) se solapan si A < D y B > C
            hay_traslape = (hora_inicio < h.hora_fin) and (hora_fin > h.hora_inicio)
            if not hay_traslape:
                continue

            # ── Conflicto de DOCENTE ───────────────────────────────────────
            if h.docente_id == docente_id:
                d = self.docentes.get(docente_id)
                mat = self.materias.get(h.materia_id)
                nombre_doc = d.get_nombre_completo() if d else docente_id
                nombre_mat = mat.nombre if mat else h.materia_id
                conflictos.append(
                    f"👨‍🏫 El docente '{nombre_doc}' ya tiene clase\n"
                    f"   Materia: {nombre_mat}\n"
                    f"   Horario ocupado: {dia} {h.hora_inicio}–{h.hora_fin}\n"
                    f"   Grupo: {h.grado}"
                )

            # ── Conflicto de AULA ──────────────────────────────────────────
            if h.aula_id == aula_id:
                a = self.aulas.get(aula_id)
                mat = self.materias.get(h.materia_id)
                nombre_aula = str(a) if a else aula_id
                nombre_mat = mat.nombre if mat else h.materia_id
                conflictos.append(
                    f"🏫 El aula '{nombre_aula}' ya está ocupada\n"
                    f"   Materia: {nombre_mat}\n"
                    f"   Horario ocupado: {dia} {h.hora_inicio}–{h.hora_fin}\n"
                    f"   Grupo: {h.grado}"
                )

        return conflictos

    def agregar_horario(self, id, materia_id, docente_id, grado, grupo,
                        dia, hora_inicio, hora_fin, aula_id):
        if id in self.horarios:
            return False, f"Ya existe horario con ID {id}"
        if docente_id not in self.docentes:
            return False, "Docente no encontrado"
        if materia_id not in self.materias:
            return False, "Materia no encontrada"
        if aula_id not in self.aulas:
            return False, "Aula no encontrada"
        conflictos = self.validar_cruce_horario(docente_id, aula_id, dia, hora_inicio, hora_fin)
        if conflictos:
            return False, "Conflicto de horario:\n" + "\n".join(conflictos)
        h = Horario(id, materia_id, docente_id, grado, grupo, dia, hora_inicio, hora_fin, aula_id)
        self.horarios[id] = h
        self._guardar_datos()
        self.registrar_cambio('ALTA_HORARIO', f"Alta horario ID: {id}")
        return True, "Horario agregado"

    def editar_horario(self, id, materia_id, docente_id, grado, grupo,
                       dia, hora_inicio, hora_fin, aula_id):
        if id not in self.horarios:
            return False, "Horario no encontrado"
        conflictos = self.validar_cruce_horario(docente_id, aula_id, dia, hora_inicio, hora_fin, excluir_id=id)
        if conflictos:
            return False, "Conflicto de horario:\n" + "\n".join(conflictos)
        h = self.horarios[id]
        h.materia_id = materia_id
        h.docente_id = docente_id
        h.grado = grado
        h.grupo = grupo
        h.dia = dia
        h.hora_inicio = hora_inicio
        h.hora_fin = hora_fin
        h.aula_id = aula_id
        self._guardar_datos()
        self.registrar_cambio('EDITAR_HORARIO', f"Edición horario ID: {id}")
        return True, "Horario actualizado"

    def eliminar_horario(self, id):
        if id not in self.horarios:
            return False, "Horario no encontrado"
        del self.horarios[id]
        self._guardar_datos()
        self.registrar_cambio('ELIMINAR_HORARIO', f"Eliminación horario ID: {id}")
        return True, "Horario eliminado"

    # ---------- Calificaciones ----------

    def registrar_calificacion(self, matricula, materia_id, semestre, calificacion):
        if matricula not in self.alumnos:
            return False, "Alumno no encontrado"
        if not self.alumnos[matricula].activo:
            return False, "El alumno está dado de baja"
        if materia_id not in self.materias:
            return False, "Materia no encontrada"
        for c in self.calificaciones.values():
            if c.matricula_alumno == matricula and c.materia_id == materia_id and c.semestre == semestre:
                return False, "Ya existe calificación para ese semestre"
        cid = f"{matricula}_{materia_id}_{semestre}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        c = Calificacion(cid, matricula, materia_id, semestre, calificacion)
        self.calificaciones[cid] = c
        self._guardar_datos()
        self.registrar_cambio('CALIFICACION', f"Calificación: {matricula} - {materia_id}: {calificacion}")
        return True, "Calificación registrada"

    def editar_calificacion(self, cal_id, nueva):
        c = self.calificaciones.get(cal_id)
        if not c:
            return False, "Calificación no encontrada"
        vieja = c.calificacion
        c.calificacion = nueva
        self._guardar_datos()
        self.registrar_cambio('EDITAR_CALIFICACION', f"Calificación {cal_id}: {vieja} → {nueva}")
        return True, "Calificación actualizada"

    def obtener_calificaciones_alumno(self, matricula):
        return [c for c in self.calificaciones.values() if c.matricula_alumno == matricula]

    def obtener_promedio_alumno(self, matricula):
        cals = self.obtener_calificaciones_alumno(matricula)
        return sum(c.calificacion for c in cals) / len(cals) if cals else 0.0

    def obtener_grupos_disponibles(self):
        grupos = set()
        for a in self.alumnos.values():
            if a.activo:
                grupos.add((a.grado, a.grupo))
        return sorted(grupos)

    def obtener_alumnos_por_grupo(self, grado, grupo):
        return [a for a in self.alumnos.values() if a.activo and a.grado == grado and a.grupo == grupo]

    def obtener_horarios_por_grupo(self, grado, grupo):
        """Retorna los horarios para un grupo específico."""
        return [h for h in self.horarios.values() if h.grado == grado and h.grupo == grupo]


# ===========================
# INTERFAZ GRÁFICA
# ===========================

class SistemaEscolarGUI:

    TEMAS = {
        'claro': {
            'primary': '#1E3A8A', 'secondary': '#3B82F6', 'accent': '#60A5FA',
            'success': '#10B981', 'danger': '#EF4444', 'warning': '#F59E0B',
            'info': '#06B6D4', 'background': '#F1F5F9', 'surface': '#FFFFFF',
            'text': '#111827', 'text_light': '#6B7280', 'border': '#E5E7EB',
            'table_header': '#1E40AF', 'table_alt': '#F3F4F6',
            'hover': '#DBEAFE', 'entry_bg': '#FFFFFF', 'entry_fg': '#111827',
        },
        'oscuro': {
            'primary': '#1E293B', 'secondary': '#3B82F6', 'accent': '#60A5FA',
            'success': '#10B981', 'danger': '#EF4444', 'warning': '#F59E0B',
            'info': '#06B6D4', 'background': '#0F172A', 'surface': '#1E293B',
            'text': '#F1F5F9', 'text_light': '#94A3B8', 'border': '#334155',
            'table_header': '#1E40AF', 'table_alt': '#1E293B',
            'hover': '#334155', 'entry_bg': '#334155', 'entry_fg': '#F1F5F9',
        },
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control Escolar v2.0")
        self.root.geometry("1400x820")
        self.sistema = SistemaControlEscolar()
        self.modo_oscuro = False
        self.colors = self.TEMAS['claro']
        self._vista_actual = None
        self._foto_refs = []  # evitar GC de imágenes
        self.mostrar_seleccion_rol()

    def c(self, key):
        return self.colors[key]

    # ===========================
    # UTILIDADES UI
    # ===========================

    def configurar_estilos(self):
        s = ttk.Style()
        s.theme_use('clam')
        c = self.colors
        s.configure('Treeview', background=c['surface'], foreground=c['text'],
                    fieldbackground=c['surface'], font=('Segoe UI', 10), rowheight=32)
        s.configure('Treeview.Heading', background=c['primary'], foreground='white',
                    font=('Segoe UI', 10, 'bold'))
        s.map('Treeview.Heading', background=[('active', c['accent'])])
        s.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        s.configure('TNotebook', background=c['background'])
        s.configure('TNotebook.Tab', background=c['surface'], foreground=c['text'],
                    font=('Segoe UI', 10), padding=[12, 6])
        s.map('TNotebook.Tab', background=[('selected', c['secondary'])],
              foreground=[('selected', 'white')])

    def bind_scroll(self, widget):
        def _s(e): widget.yview_scroll(int(-1 * (e.delta / 120)), "units")
        widget.bind('<Enter>', lambda e: widget.bind_all('<MouseWheel>', _s))
        widget.bind('<Leave>', lambda e: widget.unbind_all('<MouseWheel>'))

    def bind_scroll_tree(self, tree):
        tree.bind('<MouseWheel>', lambda e: tree.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def scroll_frame(self, parent):
        """Crea un frame scrollable y retorna el frame interior."""
        c = self.colors
        canvas = tk.Canvas(parent, bg=c['surface'], highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        frame = tk.Frame(canvas, bg=c['surface'])
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        win = canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        self.bind_scroll(canvas)
        return frame

    def limpiar_panel(self):
        for w in self.right_panel.winfo_children():
            w.destroy()
        self._foto_refs.clear()

    def titulo_panel(self, texto):
        c = self.colors
        tk.Label(self.right_panel, text=texto, bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 14, 'bold'), anchor='w', padx=10, pady=8).pack(fill='x')
        tk.Frame(self.right_panel, bg=c['secondary'], height=2).pack(fill='x', padx=10)

    def tabla(self, parent, cols, anchos, height=14):
        f = tk.Frame(parent, bg=self.c('surface'))
        f.pack(fill='both', expand=True, padx=10, pady=5)
        sby = ttk.Scrollbar(f)
        sby.pack(side='right', fill='y')
        sbx = ttk.Scrollbar(f, orient='horizontal')
        sbx.pack(side='bottom', fill='x')
        tree = ttk.Treeview(f, columns=cols, show='headings',
                            yscrollcommand=sby.set, xscrollcommand=sbx.set, height=height)
        sby.config(command=tree.yview)
        sbx.config(command=tree.xview)
        for col, ancho in zip(cols, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, minwidth=50)
        tree.pack(fill='both', expand=True)
        self.bind_scroll_tree(tree)
        self._colorear(tree)
        return tree

    def _colorear(self, tree, par='#EFF6FF', impar='white'):
        c = self.colors
        if self.modo_oscuro:
            par, impar = '#1E3A5F', c['surface']
        tree.tag_configure('par', background=par)
        tree.tag_configure('impar', background=impar)

    def insertar(self, tree, filas):
        for item in tree.get_children():
            tree.delete(item)
        for i, fila in enumerate(filas):
            tree.insert('', 'end', values=fila, tags=('par' if i % 2 == 0 else 'impar',))

    def busqueda_bar(self, parent, label='🔍 Buscar:', placeholder=''):
        c = self.colors
        f = tk.Frame(parent, bg=c['surface'])
        f.pack(fill='x', padx=10, pady=5)
        tk.Label(f, text=label, bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        var = tk.StringVar()
        e = tk.Entry(f, textvariable=var, font=('Segoe UI', 10), relief='solid', bd=1,
                     width=35, bg=c['entry_bg'], fg=c['entry_fg'], insertbackground=c['entry_fg'])
        e.pack(side='left', padx=5, ipady=3)
        if placeholder:
            tk.Label(f, text=placeholder, bg=c['surface'], fg=c['text_light'],
                     font=('Segoe UI', 8, 'italic')).pack(side='left')
        return var, e

    def info_box(self, parent, texto, tipo='info'):
        colores = {
            'info':    ('#EFF6FF', '#1E40AF'),
            'warn':    ('#FFFBEB', '#92400E'),
            'success': ('#ECFDF5', '#065F46'),
            'error':   ('#FEF2F2', '#991B1B'),
        }
        bg, fg = colores.get(tipo, colores['info'])
        if self.modo_oscuro:
            bg, fg = '#1E3A5F', '#93C5FD'
        f = tk.Frame(parent, bg=bg, relief='solid', bd=1)
        f.pack(fill='x', padx=10, pady=3)
        tk.Label(f, text=texto, bg=bg, fg=fg, font=('Segoe UI', 9),
                 justify='left', wraplength=750, padx=10, pady=6).pack(fill='x')

    def btn(self, parent, texto, comando, color=None, **kwargs):
        c = self.colors
        color = color or c['secondary']
        b = tk.Button(parent, text=texto, command=comando,
                      bg=color, fg='white', relief='flat', cursor='hand2',
                      font=('Segoe UI', 10, 'bold'), **kwargs)
        b.bind('<Enter>', lambda e: b.config(bg=self._darken(color)))
        b.bind('<Leave>', lambda e: b.config(bg=color))
        return b

    def _darken(self, hex_color):
        """Oscurece un color hex ligeramente."""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color

    def entry(self, parent, var=None, **kwargs):
        c = self.colors
        e = tk.Entry(parent, font=('Segoe UI', 10), relief='solid', bd=1,
                     bg=c['entry_bg'], fg=c['entry_fg'],
                     insertbackground=c['entry_fg'], **kwargs)
        if var:
            e.config(textvariable=var)
        return e

    def combo(self, parent, opciones, var=None, width=35, **kwargs):
        c = ttk.Combobox(parent, values=opciones, font=('Segoe UI', 10),
                          width=width, state='readonly', **kwargs)
        if var:
            c.config(textvariable=var)
        if opciones:
            c.current(0)
        return c

    def campo_form(self, parent, row, label, tipo='entry', opciones=None,
                   valor='', width=38, colspan=1):
        c = self.colors
        tk.Label(parent, text=label, bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold'), anchor='w').grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        if tipo == 'entry':
            w = tk.Entry(parent, font=('Segoe UI', 10), relief='solid', bd=1,
                         width=width, bg=c['entry_bg'], fg=c['entry_fg'],
                         insertbackground=c['entry_fg'])
            if valor:
                w.insert(0, valor)
        elif tipo == 'combo':
            w = ttk.Combobox(parent, values=opciones or [], font=('Segoe UI', 10),
                             width=width - 2, state='readonly')
            if opciones and valor in opciones:
                w.set(valor)
            elif opciones:
                w.current(0)
        elif tipo == 'text':
            w = tk.Text(parent, font=('Segoe UI', 10), relief='solid', bd=1,
                        width=width, height=3, bg=self.c('entry_bg'), fg=self.c('entry_fg'))
            if valor:
                w.insert('1.0', valor)
        w.grid(row=row, column=1, pady=5, padx=5, sticky='ew',
               columnspan=colspan)
        return w

    def boton_foto(self, parent, row, key, entries):
        """Widget para seleccionar foto."""
        c = self.colors
        tk.Label(parent, text="Fotografía:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold'), anchor='w').grid(
            row=row, column=0, sticky='nw', pady=5, padx=5)
        frame = tk.Frame(parent, bg=c['surface'])
        frame.grid(row=row, column=1, sticky='w', pady=5, padx=5)

        foto_label = tk.Label(frame, text="Sin foto", bg=c['surface'],
                              fg=c['text_light'], font=('Segoe UI', 9))
        foto_label.pack(side='left', padx=5)
        entries[f'{key}_label'] = foto_label
        entries[key] = ''  # base64

        def seleccionar():
            ruta = filedialog.askopenfilename(
                title="Seleccionar fotografía",
                filetypes=[('Imágenes', '*.jpg *.jpeg *.png *.bmp'), ('Todos', '*.*')]
            )
            if ruta:
                b64 = imagen_a_base64(ruta)
                entries[key] = b64
                foto_label.config(text=f"✓ {os.path.basename(ruta)}", fg=c['success'])

        self.btn(frame, "📷 Seleccionar Foto", seleccionar,
                 color=c['info'], padx=8, pady=3).pack(side='left')

    # ===========================
    # SELECCIÓN DE ROL INICIAL
    # ===========================

    def mostrar_seleccion_rol(self):
        """Pantalla inicial con 3 opciones: Administración, Docente, Estudiante"""
        for w in self.root.winfo_children():
            w.destroy()
        self.root.geometry("520x500")
        self.root.resizable(False, False)
        self.root.configure(bg='#0F172A')

        main = tk.Frame(self.root, bg='#0F172A')
        main.pack(fill='both', expand=True)

        card = tk.Frame(main, bg='#1E293B')
        card.place(relx=0.5, rely=0.5, anchor='center', width=440, height=400)

        tk.Label(card, text="🎓", bg='#1E293B', fg='white',
                 font=('Segoe UI', 48)).pack(pady=(25, 5))
        tk.Label(card, text="Sistema de Control Escolar", bg='#1E293B', fg='white',
                 font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card, text="Selecciona tu rol para continuar", bg='#1E293B', fg='#94A3B8',
                 font=('Segoe UI', 11)).pack(pady=(10, 20))

        def seleccionar_rol(rol):
            # Si es Admin o Docente, pedir contraseña de acceso
            if rol in ['Administración', 'Docente']:
                self.mostrar_verificacion_acceso(rol)
            else:
                # Estudiante va directo al login
                self.mostrar_login(rol)

        # Botones para cada rol
        btn_admin = tk.Button(card, text="👨‍💼 Administración", 
                              command=lambda: seleccionar_rol('Administración'),
                              bg='#1E3A8A', fg='white', font=('Segoe UI', 12, 'bold'),
                              relief='flat', cursor='hand2', height=2)
        btn_admin.pack(fill='x', padx=40, pady=8)

        btn_docente = tk.Button(card, text="👨‍🏫 Docente",
                                command=lambda: seleccionar_rol('Docente'),
                                bg='#3B82F6', fg='white', font=('Segoe UI', 12, 'bold'),
                                relief='flat', cursor='hand2', height=2)
        btn_docente.pack(fill='x', padx=40, pady=8)

        btn_estudiante = tk.Button(card, text="👨‍🎓 Estudiante",
                                   command=lambda: seleccionar_rol('Estudiante'),
                                   bg='#10B981', fg='white', font=('Segoe UI', 12, 'bold'),
                                   relief='flat', cursor='hand2', height=2)
        btn_estudiante.pack(fill='x', padx=40, pady=8)

        # Efectos hover
        for btn in [btn_admin, btn_docente, btn_estudiante]:
            original_color = btn.cget('bg')
            btn.bind('<Enter>', lambda e, color=original_color: e.widget.config(bg=self._darken(color)))
            btn.bind('<Leave>', lambda e, color=original_color: e.widget.config(bg=color))

    def mostrar_verificacion_acceso(self, rol):
        """Ventana para verificar contraseña de acceso para Admin/Docente"""
        win = tk.Toplevel(self.root)
        win.title(f"Verificación de Acceso - {rol}")
        win.geometry("380x250")
        win.configure(bg='#1E293B')
        win.grab_set()
        win.transient(self.root)

        tk.Label(win, text="🔐", bg='#1E293B', fg='white',
                 font=('Segoe UI', 32)).pack(pady=(20, 5))
        tk.Label(win, text=f"Acceso para {rol}", bg='#1E293B', fg='white',
                 font=('Segoe UI', 14, 'bold')).pack()
        tk.Label(win, text="Ingresa la contraseña de acceso", bg='#1E293B', fg='#94A3B8',
                 font=('Segoe UI', 10)).pack(pady=5)

        pw_var = tk.StringVar()
        pw_entry = tk.Entry(win, textvariable=pw_var, font=('Segoe UI', 11), 
                           bg='#334155', fg='white', show='●',
                           insertbackground='white', relief='flat', bd=8)
        pw_entry.pack(fill='x', padx=40, pady=10, ipady=5)

        msg = tk.Label(win, text='', bg='#1E293B', fg='#EF4444', font=('Segoe UI', 9))
        msg.pack()

        def verificar():
            if pw_var.get() == PASSWORD_ADMIN_DOCENTE:
                win.destroy()
                self.mostrar_login(rol)
            else:
                msg.config(text="❌ Contraseña incorrecta")
                pw_entry.delete(0, 'end')
                pw_entry.focus()

        def cancelar():
            win.destroy()
            self.mostrar_seleccion_rol()

        btn_frame = tk.Frame(win, bg='#1E293B')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="✅ Continuar", command=verificar,
                  bg='#3B82F6', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', cursor='hand2', padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ Cancelar", command=cancelar,
                  bg='#EF4444', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', cursor='hand2', padx=15, pady=5).pack(side='left', padx=5)

        pw_entry.focus()
        pw_entry.bind('<Return>', lambda e: verificar())

    # ===========================
    # LOGIN
    # ===========================

    def mostrar_login(self, rol_seleccionado):
        """
        Muestra el panel de login con el rol ya pre-seleccionado.
        Ya no muestra el selector de roles.
        """
        self.rol_actual_login = rol_seleccionado  # Guardamos el rol para el registro
        
        for w in self.root.winfo_children():
            w.destroy()
        self.root.geometry("520x550")
        self.root.resizable(False, False)
        self.root.configure(bg='#0F172A')

        main = tk.Frame(self.root, bg='#0F172A')
        main.pack(fill='both', expand=True)

        card = tk.Frame(main, bg='#1E293B')
        card.place(relx=0.5, rely=0.5, anchor='center', width=440, height=500)

        tk.Label(card, text="🎓", bg='#1E293B', fg='white',
                 font=('Segoe UI', 36)).pack(pady=(25, 3))
        tk.Label(card, text="Control Escolar", bg='#1E293B', fg='white',
                 font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card, text=f"Iniciando sesión como {rol_seleccionado}", bg='#1E293B', fg='#94A3B8',
                 font=('Segoe UI', 10, 'bold')).pack(pady=(0, 15))

        # Mostrar el rol seleccionado
        rol_label = tk.Label(card, text=f"Rol: {rol_seleccionado}", bg='#1E293B', fg='#60A5FA',
                            font=('Segoe UI', 11, 'bold'))
        rol_label.pack(pady=5)

        def lbl(txt): tk.Label(card, text=txt, bg='#1E293B', fg='#CBD5E1',
                                font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill='x', padx=35)

        def inp(show=None):
            e = tk.Entry(card, font=('Segoe UI', 11), bg='#334155', fg='white',
                         insertbackground='white', relief='flat', bd=8)
            if show:
                e.config(show=show)
            e.pack(fill='x', padx=35, pady=(2, 8), ipady=5)
            return e

        lbl("ID de Usuario / Matrícula")
        id_entry = inp()

        # Password con botón mostrar/ocultar
        lbl("Contraseña")
        pw_frame = tk.Frame(card, bg='#1E293B')
        pw_frame.pack(fill='x', padx=35, pady=(2, 8))
        pw_entry = tk.Entry(pw_frame, font=('Segoe UI', 11), bg='#334155', fg='white',
                            insertbackground='white', relief='flat', bd=8, show='●')
        pw_entry.pack(side='left', fill='both', expand=True, ipady=5)
        mostrar_pw = [False]

        def toggle_pw():
            mostrar_pw[0] = not mostrar_pw[0]
            pw_entry.config(show='' if mostrar_pw[0] else '●')
            ojo_btn.config(text='🙈' if mostrar_pw[0] else '👁')

        ojo_btn = tk.Button(pw_frame, text='👁', command=toggle_pw,
                            bg='#334155', fg='white', relief='flat', font=('Segoe UI', 12),
                            cursor='hand2', bd=0, padx=8)
        ojo_btn.pack(side='right')

        msg = tk.Label(card, text='', bg='#1E293B', fg='#EF4444', font=('Segoe UI', 9))
        msg.pack()

        def intentar_login(e=None):
            ok, mensaje = self.sistema.login(id_entry.get().strip(), pw_entry.get(), rol_seleccionado)
            if ok:
                self.iniciar_sistema()
            else:
                msg.config(text=f"❌ {mensaje}")
                pw_entry.delete(0, 'end')

        btn_login = tk.Button(card, text="Iniciar Sesión", command=intentar_login,
                              bg='#3B82F6', fg='white', font=('Segoe UI', 11, 'bold'),
                              relief='flat', cursor='hand2')
        btn_login.pack(fill='x', padx=35, pady=(5, 5), ipady=9)
        btn_login.bind('<Enter>', lambda e: btn_login.config(bg='#2563EB'))
        btn_login.bind('<Leave>', lambda e: btn_login.config(bg='#3B82F6'))

        # Botón de registro - solo visible para Administración
        if rol_seleccionado == 'Administración':
            tk.Button(card, text="Registrar nuevo usuario",
                      command=lambda: self.mostrar_registro_usuario(rol_seleccionado),
                      bg='#1E293B', fg='#60A5FA', relief='flat',
                      font=('Segoe UI', 9, 'underline'), cursor='hand2').pack()

        # Botón para volver a selección de rol
        tk.Button(card, text="⬅ Cambiar rol", command=self.mostrar_seleccion_rol,
                  bg='#1E293B', fg='#94A3B8', relief='flat',
                  font=('Segoe UI', 9), cursor='hand2').pack(pady=5)

        id_entry.focus()
        pw_entry.bind('<Return>', intentar_login)
        id_entry.bind('<Return>', lambda e: pw_entry.focus())

    def mostrar_registro_usuario(self, rol_seleccionado):
        """
        Ventana emergente para registrar nuevo usuario.
        El rol ya viene pre-seleccionado según cómo se inició sesión.
        """
        win = tk.Toplevel(self.root)
        win.title("Registro de Usuario")
        win.geometry("480x700")
        win.configure(bg='#1E293B')
        win.grab_set()

        # Scroll por si muchos campos
        canvas = tk.Canvas(win, bg='#1E293B', highlightthickness=0)
        sb = ttk.Scrollbar(win, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        self.bind_scroll(canvas)

        frame = tk.Frame(canvas, bg='#1E293B')
        win_id = canvas.create_window((0, 0), window=frame, anchor='nw')
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width - 4))

        tk.Label(frame, text=f"📝 Registrar Usuario ({rol_seleccionado})", 
                 bg='#1E293B', fg='white',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(20, 10))

        form = tk.Frame(frame, bg='#1E293B')
        form.pack(padx=30, fill='x')

        def lbl(txt):
            tk.Label(form, text=txt, bg='#1E293B', fg='#CBD5E1',
                     font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill='x', pady=(5, 0))

        def inp(show=None):
            e = tk.Entry(form, font=('Segoe UI', 10), bg='#334155', fg='white',
                         insertbackground='white', relief='flat', bd=6)
            if show:
                e.config(show=show)
            e.pack(fill='x', pady=(2, 0), ipady=4)
            return e

        lbl("ID de Usuario (matrícula o número empleado): *")
        id_e = inp()
        lbl("Nombre(s): *")
        nombre_e = inp()
        lbl("Apellido(s): *")
        apellido_e = inp()
        lbl("Email:")
        email_e = inp()
        lbl("Contraseña (mínimo 8 chars, mayúscula, número): *")
        pw_e = inp('●')
        lbl("Confirmar Contraseña: *")
        pw2_e = inp('●')

        # Mostrar el rol (no editable)
        lbl("Rol:")
        rol_label = tk.Label(form, text=rol_seleccionado, bg='#334155', fg='white',
                            font=('Segoe UI', 10, 'bold'), relief='flat', bd=6,
                            anchor='w', padx=8, pady=4)
        rol_label.pack(fill='x', pady=(2, 10), ipady=2)

        # Campos adicionales según rol (opcionales)
        lbl("Fecha de Nacimiento (opcional, DD/MM/AAAA):")
        fecha_e = inp()
        lbl("Teléfono (opcional):")
        telefono_e = inp()
        
        # Para docentes: especialidad
        especialidad_frame = tk.Frame(form, bg='#1E293B')
        especialidad_frame.pack(fill='x', pady=3)
        tk.Label(especialidad_frame, text="Especialidad (solo Docentes):", bg='#1E293B', fg='#CBD5E1',
                 font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill='x')
        especialidad_e = tk.Entry(especialidad_frame, font=('Segoe UI', 10), bg='#334155', fg='white',
                                  insertbackground='white', relief='flat', bd=6)
        especialidad_e.pack(fill='x', ipady=4)

        msg = tk.Label(frame, text='', bg='#1E293B', fg='#EF4444',
                       font=('Segoe UI', 9), wraplength=400)
        msg.pack(pady=3)

        def registrar():
            # Validar campos obligatorios
            if pw_e.get() != pw2_e.get():
                msg.config(text="❌ Las contraseñas no coinciden")
                return
            id_ = id_e.get().strip()
            nombre = nombre_e.get().strip()
            apellido = apellido_e.get().strip()
            if not id_ or not nombre or not apellido:
                msg.config(text="❌ ID, nombre y apellido son obligatorios")
                return
            email = email_e.get().strip()
            fecha = fecha_e.get().strip()
            telefono = telefono_e.get().strip()
            especialidad = especialidad_e.get().strip() if rol_seleccionado == 'Docente' else ''

            ok, texto = self.sistema.registrar_usuario(
                user_id=id_,
                nombre=nombre,
                apellido=apellido,
                password=pw_e.get(),
                rol=rol_seleccionado,  # Usamos el rol seleccionado
                email=email,
                fecha_nacimiento=fecha,
                telefono=telefono,
                especialidad=especialidad
            )
            if ok:
                messagebox.showinfo("Éxito", texto, parent=win)
                win.destroy()
            else:
                msg.config(text=f"❌ {texto}")

        tk.Button(frame, text="✅ Registrar", command=registrar,
                  bg='#10B981', fg='white', font=('Segoe UI', 11, 'bold'),
                  relief='flat', cursor='hand2').pack(pady=10, padx=30, fill='x', ipady=8)

    def mostrar_cambiar_password(self, user_id=None):
        """
        Ventana para cambiar contraseña.
        Si user_id es None, se cambia la del usuario actual.
        Si se proporciona, debe ser admin para cambiar la de otro.
        """
        if user_id and not self.sistema.es_admin():
            messagebox.showerror("Permiso denegado", "Solo administradores pueden cambiar contraseñas de otros usuarios.")
            return
        
        target_user = self.sistema.usuarios.get(user_id) if user_id else self.sistema.usuario_actual
        if not target_user:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Cambiar Contraseña de {target_user.nombre}")
        win.geometry("380x300")
        win.configure(bg='#1E293B')
        win.grab_set()

        tk.Label(win, text="🔑 Cambiar Contraseña", bg='#1E293B', fg='white',
                 font=('Segoe UI', 13, 'bold')).pack(pady=(20, 10))

        form = tk.Frame(win, bg='#1E293B')
        form.pack(padx=30, fill='x')

        def lbl(t): tk.Label(form, text=t, bg='#1E293B', fg='#CBD5E1',
                              font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill='x', pady=(5,0))
        def inp(s=None):
            e = tk.Entry(form, font=('Segoe UI', 10), bg='#334155', fg='white',
                         insertbackground='white', relief='flat', bd=6)
            if s: e.config(show=s)
            e.pack(fill='x', pady=(2,0), ipady=4)
            return e

        lbl("Nueva Contraseña:")
        pw1 = inp('●')
        lbl("Confirmar Contraseña:")
        pw2 = inp('●')

        msg = tk.Label(win, text='', bg='#1E293B', fg='#EF4444', font=('Segoe UI', 9), wraplength=340)
        msg.pack(pady=3)

        def guardar():
            if pw1.get() != pw2.get():
                msg.config(text="❌ Las contraseñas no coinciden")
                return
            ok, texto = self.sistema.cambiar_password(target_user.id, pw1.get())
            if ok:
                messagebox.showinfo("Éxito", texto, parent=win)
                win.destroy()
            else:
                msg.config(text=f"❌ {texto}")

        tk.Button(win, text="💾 Guardar", command=guardar,
                  bg='#3B82F6', fg='white', font=('Segoe UI', 11, 'bold'),
                  relief='flat', cursor='hand2').pack(pady=12, padx=30, fill='x', ipady=8)

    # ===========================
    # SISTEMA PRINCIPAL
    # ===========================

    def iniciar_sistema(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.geometry("1400x820")
        self.root.resizable(True, True)
        self.configurar_estilos()
        self.root.configure(bg=self.c('background'))
        self._construir_interfaz()

    def toggle_tema(self):
        self.modo_oscuro = not self.modo_oscuro
        self.colors = self.TEMAS['oscuro' if self.modo_oscuro else 'claro']
        v = self._vista_actual
        for w in self.root.winfo_children():
            w.destroy()
        self.configurar_estilos()
        self.root.configure(bg=self.c('background'))
        self._construir_interfaz(v)

    def _construir_interfaz(self, vista=None):
        c = self.colors
        main = tk.Frame(self.root, bg=c['background'])
        main.pack(fill='both', expand=True)

        # Header
        hdr = tk.Frame(main, bg=c['primary'], height=60)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🎓 Sistema de Control Escolar v2.0",
                 bg=c['primary'], fg='white', font=('Segoe UI', 14, 'bold')).pack(side='left', padx=20)

        rframe = tk.Frame(hdr, bg=c['primary'])
        rframe.pack(side='right', padx=12)

        u = self.sistema.usuario_actual
        tk.Label(rframe, text=f"👤 {u.nombre} · {u.rol}",
                 bg=c['primary'], fg='#94A3B8', font=('Segoe UI', 9)).pack(side='right', padx=10)

        for txt, cmd, col in [
            ("🔑 Contraseña", lambda: self.mostrar_cambiar_password(), c['info']),
            ("☀️" if self.modo_oscuro else "🌙 Oscuro", self.toggle_tema, c['secondary']),
            ("📋 Historial", self.mostrar_historial, c['warning']),
            ("🚪 Salir", self.cerrar_sesion, c['danger']),
        ]:
            b = tk.Button(rframe, text=txt, command=cmd, bg=col, fg='white',
                          font=('Segoe UI', 9), relief='flat', cursor='hand2', padx=8, pady=5)
            b.pack(side='right', padx=3)

        # Body
        body = tk.Frame(main, bg=c['background'])
        body.pack(fill='both', expand=True, padx=8, pady=8)

        # Menú lateral
        lc = tk.Frame(body, bg=c['background'])
        lc.pack(side='left', fill='y')
        mc = tk.Canvas(lc, bg=c['surface'], highlightthickness=0, width=220)
        msb = ttk.Scrollbar(lc, orient='vertical', command=mc.yview)
        mf = tk.Frame(mc, bg=c['surface'])
        mf.bind('<Configure>', lambda e: mc.configure(scrollregion=mc.bbox('all')))
        mc.create_window((0, 0), window=mf, anchor='nw')
        mc.configure(yscrollcommand=msb.set, height=740)
        mc.pack(side='left', fill='y')
        msb.pack(side='right', fill='y')
        self.bind_scroll(mc)
        self._construir_menu(mf)

        # Panel derecho
        self.right_panel = tk.Frame(body, bg=c['surface'])
        self.right_panel.pack(side='right', fill='both', expand=True, padx=(8, 0))

        if vista:
            self._vista_actual = vista
            vista()
        else:
            if self.sistema.es_estudiante():
                self.mostrar_informacion_alumno()
            else:
                self.mostrar_dashboard()

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
            self.sistema.usuario_actual = None
            self.mostrar_seleccion_rol()  # Volver a la pantalla de selección de rol

    def _construir_menu(self, parent):
        c = self.colors
        rol = self.sistema.get_rol()

        def sec(txt):
            tk.Label(parent, text=txt, bg=c['surface'], fg=c['secondary'],
                     font=('Segoe UI', 8, 'bold'), anchor='w', padx=12, pady=3).pack(fill='x')
            tk.Frame(parent, bg=c['border'], height=1).pack(fill='x', padx=8)

        def btn(txt, cmd):
            def _cmd():
                self._vista_actual = cmd
                cmd()
            b = tk.Button(parent, text=txt, command=_cmd, bg=c['surface'], fg=c['text'],
                          activebackground=c['secondary'], activeforeground='white',
                          relief='flat', font=('Segoe UI', 9), anchor='w',
                          padx=18, pady=7, cursor='hand2', bd=0)
            b.pack(fill='x', padx=6, pady=1)
            b.bind('<Enter>', lambda e: b.config(bg=c['hover'], fg=c['secondary']))
            b.bind('<Leave>', lambda e: b.config(bg=c['surface'], fg=c['text']))

        # Dashboard solo para Administración y Docentes
        if rol in ('Administración', 'Docente'):
            sec("📊 GENERAL")
            btn("📊 Dashboard", self.mostrar_dashboard)

        # Sección de Información del Alumno para estudiantes
        if rol == 'Estudiante':
            sec("👤 MI PERFIL")
            btn("ℹ️ Mi Información", self.mostrar_informacion_alumno)

        if rol in ('Administración', 'Docente', 'Estudiante'):
            sec("👥 ALUMNOS")
        if rol == 'Administración':
            # Eliminados los botones de alta de alumno y docente
            # Se mantienen las opciones de gestión (baja, reactivar, cambiar grupo, solicitudes)
            btn("➖ Baja Alumno", self.mostrar_baja_alumno)
            btn("🔄 Reactivar Alumno", self.mostrar_reactivar_alumno)
            btn("↔ Cambiar Grupo", self.mostrar_cambiar_grupo)
            btn("📋 Solicitudes Grupo", self.mostrar_solicitudes_grupo)
        
        # Solo mostrar lista de alumnos a Administración y Docentes
        if rol in ('Administración', 'Docente'):
            btn("👥 Lista Alumnos", self.mostrar_lista_alumnos)
        
        # Cambiar nombre de "Ver Grupos" a "Ver mi Grupo" para estudiantes
        if rol == 'Estudiante':
            btn("👥 Ver mi Grupo", self.mostrar_mi_grupo)
        else:
            btn("🏫 Ver Grupos", self.mostrar_grupos)

        if rol == 'Estudiante':
            btn("🙋 Solicitar Cambio Grupo", self.mostrar_solicitar_grupo)

        if rol in ('Administración', 'Docente'):
            sec("👨‍🏫 DOCENTES")
            if rol == 'Administración':
                # Eliminado el botón de agregar docente
                btn("⏸ Baja Temporal Docente", self.mostrar_baja_temporal_docente)
            btn("📋 Lista Docentes", self.mostrar_lista_docentes)

        sec("📚 ACADÉMICO")
        if rol == 'Administración':
            btn("📖 Materias", self.mostrar_lista_materias)
            btn("🏛 Carreras", self.mostrar_lista_carreras)
            btn("🏫 Aulas", self.mostrar_lista_aulas)
        if rol in ('Administración', 'Docente'):
            btn("✏️ Registrar Calificación", self.mostrar_registrar_calificacion)
        
        # Para estudiantes, mostrar solo sus calificaciones con botón de boletín
        if rol == 'Estudiante':
            btn("🔍 Mis Calificaciones", self.mostrar_mis_calificaciones)
        else:
            btn("🔍 Ver Calificaciones", self.mostrar_ver_calificaciones)
            btn("📄 Boletín Alumno", self.mostrar_boletin_alumno)

        sec("🕐 HORARIOS")
        if rol == 'Administración':
            btn("➕ Agregar Horario", self.mostrar_agregar_horario)
        
        # Para estudiantes, mostrar solo horarios de su grupo
        if rol == 'Estudiante':
            btn("🔍 Ver mi Horario", self.mostrar_mi_horario)
        else:
            btn("🔍 Ver Horarios", self.mostrar_buscar_horarios)

        if rol == 'Administración':
            sec("⚙️ SISTEMA")
            btn("👥 Usuarios del Sistema", self.mostrar_lista_usuarios)
            btn("📋 Historial de Cambios", self.mostrar_historial)

    # ===========================
    # DASHBOARD
    # ===========================

    def mostrar_dashboard(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("📊 Dashboard")

        sf = self.scroll_frame(self.right_panel)
        s = self.sistema

        activos = sum(1 for a in s.alumnos.values() if a.activo)
        inactivos = sum(1 for a in s.alumnos.values() if not a.activo)
        solicitudes = sum(1 for x in s.solicitudes_grupo.values() if x.estado == 'Pendiente')

        stats = [
            ("👥 Alumnos Activos",  activos,                 c['secondary']),
            ("⚠ Dados de Baja",    inactivos,                c['danger']),
            ("👨‍🏫 Docentes",         len(s.docentes),          c['success']),
            ("📚 Materias",          len(s.materias),          c['info']),
            ("🕐 Horarios",          len(s.horarios),          c['warning']),
            ("📝 Calificaciones",    len(s.calificaciones),    c['accent']),
            ("🏛 Carreras",          len(s.carreras),          c['primary']),
            ("🏫 Aulas",             len(s.aulas),             '#7C3AED'),
            ("🔄 Solic. Pendientes", solicitudes,              '#DB2777'),
        ]

        grid = tk.Frame(sf, bg=c['surface'])
        grid.pack(padx=15, pady=12)
        for i, (titulo, valor, color) in enumerate(stats):
            card = tk.Frame(grid, bg=color, width=185, height=100)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky='nsew')
            card.pack_propagate(False)
            tk.Label(card, text=titulo, bg=color, fg='white',
                     font=('Segoe UI', 10, 'bold'), wraplength=170).pack(pady=(14, 2))
            tk.Label(card, text=str(valor), bg=color, fg='white',
                     font=('Segoe UI', 26, 'bold')).pack()

        tk.Label(sf, text="🕐 Últimas Actividades", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 11, 'bold'), anchor='w', padx=18).pack(fill='x', pady=(10, 2))
        for cambio in reversed(s.historial[-8:]):
            f = tk.Frame(sf, bg=c['surface'])
            f.pack(fill='x', padx=18, pady=1)
            tk.Label(f, text=f"• [{cambio['tipo']}] {cambio['fecha']} — {cambio['descripcion']}",
                     bg=c['surface'], fg=c['text_light'],
                     font=('Segoe UI', 9), anchor='w', wraplength=950).pack(fill='x')

    # ===========================
    # INFORMACIÓN DEL ALUMNO
    # ===========================

    def mostrar_informacion_alumno(self):
        """Muestra la información completa del alumno con opción de editar datos personales."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("ℹ️ Mi Información Personal")
        
        uid = self.sistema.usuario_actual.id
        al = self.sistema.alumnos.get(uid)
        
        if not al:
            self.info_box(self.right_panel, 
                         "Tu cuenta de estudiante no está asociada a un alumno registrado.\n"
                         "Por favor contacta al administrador.", 'error')
            return
        
        # Variable de control para modo edición
        modo_edicion = [False]
        
        def construir_vista():
            # Limpiar el panel pero mantener el título
            for widget in self.right_panel.winfo_children():
                if widget != self.right_panel.winfo_children()[0]:  # Mantener el título
                    widget.destroy()
            
            sf = self.scroll_frame(self.right_panel)
            
            # Frame principal con borde y sombra
            main_frame = tk.Frame(sf, bg=c['surface'], relief='solid', bd=1)
            main_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            # Cabecera con foto y nombre
            header = tk.Frame(main_frame, bg=c['primary'], height=120)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            # Frame para la foto
            foto_frame = tk.Frame(header, bg=c['primary'], width=100, height=100)
            foto_frame.pack(side='left', padx=20, pady=10)
            foto_frame.pack_propagate(False)
            
            # Mostrar foto si existe
            foto_label = tk.Label(foto_frame, bg=c['primary'], text="📷", 
                                  font=('Segoe UI', 40), fg='white')
            foto_label.pack(expand=True)
            
            if al.foto_base64 and PIL_DISPONIBLE:
                try:
                    img = base64_a_imagen(al.foto_base64, (90, 90))
                    if img:
                        self._foto_refs.append(img)
                        foto_label.config(image=img, text='')
                except:
                    pass
            
            # Nombre y matrícula
            info_header = tk.Frame(header, bg=c['primary'])
            info_header.pack(side='left', fill='both', expand=True, padx=10, pady=15)
            
            tk.Label(info_header, text=al.get_nombre_completo(), 
                    bg=c['primary'], fg='white', font=('Segoe UI', 18, 'bold')).pack(anchor='w')
            tk.Label(info_header, text=f"Matrícula: {al.matricula}", 
                    bg=c['primary'], fg='#E2E8F0', font=('Segoe UI', 11)).pack(anchor='w')
            
            # Estado del alumno
            estado_color = c['success'] if al.activo else c['danger']
            estado_texto = "ACTIVO" if al.activo else "INACTIVO"
            tk.Label(info_header, text=estado_texto, bg=c['primary'], fg=estado_color,
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(5, 0))
            
            # Contenedor para los datos
            datos_frame = tk.Frame(main_frame, bg=c['surface'])
            datos_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Crear un grid para organizar la información
            for i in range(6):
                datos_frame.grid_columnconfigure(i % 2, weight=1)
            
            # Variables para los campos editables
            entries = {}
            
            # Información personal (sección 1)
            tk.Label(datos_frame, text="📋 INFORMACIÓN PERSONAL", 
                    bg=c['surface'], fg=c['secondary'], font=('Segoe UI', 11, 'bold')).grid(
                row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
            
            campos_personales = [
                ("Nombre:", al.nombre, 1, 0, 'nombre'),
                ("Apellido:", al.apellido, 1, 1, 'apellido'),
                ("Fecha Nacimiento:", al.fecha_nacimiento, 2, 0, 'fecha_nac'),
                ("Teléfono:", al.telefono, 2, 1, 'telefono'),
                ("Email:", al.email, 3, 0, 'email'),
                ("Lugar de Nacimiento:", al.lugar_nacimiento, 3, 1, 'lugar_nac'),
                ("Último Grado Estudios:", al.ultimo_grado_estudios or "", 4, 0, 'ultimo_grado'),
            ]
            
            for texto, valor, fila, col, key in campos_personales:
                tk.Label(datos_frame, text=texto, bg=c['surface'], fg=c['text_light'],
                        font=('Segoe UI', 9)).grid(row=fila, column=col*2, sticky='w', pady=3, padx=(0, 5))
                
                if modo_edicion[0]:
                    entry = tk.Entry(datos_frame, font=('Segoe UI', 10), relief='solid', bd=1,
                                    width=25, bg=c['entry_bg'], fg=c['entry_fg'])
                    entry.insert(0, valor)
                    entry.grid(row=fila, column=col*2+1, sticky='w', pady=3, padx=(0, 20))
                    entries[key] = entry
                else:
                    tk.Label(datos_frame, text=valor or "—", bg=c['surface'], fg=c['text'],
                            font=('Segoe UI', 10, 'bold')).grid(row=fila, column=col*2+1, sticky='w', pady=3, padx=(0, 20))
            
            # Línea separadora
            tk.Frame(datos_frame, bg=c['border'], height=1).grid(row=5, column=0, columnspan=4, sticky='ew', pady=15)
            
            # Información académica (sección 2)
            sm, cc, grp = self.sistema.parsear_grupo_completo(al.grado)
            cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
            
            tk.Label(datos_frame, text="🎓 INFORMACIÓN ACADÉMICA", 
                    bg=c['surface'], fg=c['secondary'], font=('Segoe UI', 11, 'bold')).grid(
                row=6, column=0, columnspan=2, sticky='w', pady=(0, 10))
            
            campos_academicos = [
                ("Grupo:", f"{al.grado} ({sm}° Semestre)" if sm else al.grado, 7, 0),
                ("Carrera:", cn, 7, 1),
                ("Fecha de Alta:", al.fecha_alta, 8, 0),
            ]
            
            if not al.activo:
                campos_academicos.append(("Fecha de Baja:", al.fecha_baja or "—", 9, 0))
                campos_academicos.append(("Motivo de Baja:", al.motivo_baja or "—", 9, 1))
            
            for texto, valor, fila, col in campos_academicos:
                tk.Label(datos_frame, text=texto, bg=c['surface'], fg=c['text_light'],
                        font=('Segoe UI', 9)).grid(row=fila, column=col*2, sticky='w', pady=3, padx=(0, 5))
                tk.Label(datos_frame, text=valor, bg=c['surface'], fg=c['text'],
                        font=('Segoe UI', 10, 'bold')).grid(row=fila, column=col*2+1, sticky='w', pady=3, padx=(0, 20))
            
            # Dirección (sección 3)
            if al.direccion or modo_edicion[0]:
                row_actual = 10
                if al.direccion or modo_edicion[0]:
                    tk.Frame(datos_frame, bg=c['border'], height=1).grid(row=row_actual, column=0, columnspan=4, sticky='ew', pady=15)
                    row_actual += 1
                    tk.Label(datos_frame, text="🏠 DIRECCIÓN", 
                            bg=c['surface'], fg=c['secondary'], font=('Segoe UI', 11, 'bold')).grid(
                        row=row_actual, column=0, columnspan=2, sticky='w', pady=(0, 10))
                    row_actual += 1
                    
                    if modo_edicion[0]:
                        tk.Label(datos_frame, text="Dirección:", bg=c['surface'], fg=c['text_light'],
                                font=('Segoe UI', 9)).grid(row=row_actual, column=0, sticky='w', pady=3)
                        entry_dir = tk.Entry(datos_frame, font=('Segoe UI', 10), relief='solid', bd=1,
                                           width=40, bg=c['entry_bg'], fg=c['entry_fg'])
                        entry_dir.insert(0, al.direccion or "")
                        entry_dir.grid(row=row_actual, column=1, columnspan=2, sticky='w', pady=3)
                        entries['direccion'] = entry_dir
                    else:
                        tk.Label(datos_frame, text="Dirección:", bg=c['surface'], fg=c['text_light'],
                                font=('Segoe UI', 9)).grid(row=row_actual, column=0, sticky='w', pady=3)
                        tk.Label(datos_frame, text=al.direccion, bg=c['surface'], fg=c['text'],
                                font=('Segoe UI', 10, 'bold')).grid(row=row_actual, column=1, columnspan=2, sticky='w', pady=3)
            
            # Botones de acción
            btn_frame = tk.Frame(main_frame, bg=c['surface'])
            btn_frame.pack(fill='x', padx=20, pady=20)
            
            def guardar_cambios():
                # Recopilar datos modificados
                nuevos_datos = {}
                for key, entry in entries.items():
                    nuevos_datos[key] = entry.get().strip()
                
                # Validar campos obligatorios
                if not nuevos_datos.get('nombre') or not nuevos_datos.get('apellido'):
                    messagebox.showwarning("Campos obligatorios", 
                                          "Nombre y Apellido no pueden estar vacíos.")
                    return
                
                # Actualizar datos del alumno
                ok, msg = self.sistema.editar_alumno(
                    al.matricula,
                    nuevos_datos.get('nombre', al.nombre),
                    nuevos_datos.get('apellido', al.apellido),
                    nuevos_datos.get('fecha_nac', al.fecha_nacimiento),
                    nuevos_datos.get('telefono', al.telefono),
                    al.grado,  # No permitir cambiar grupo
                    al.grupo,  # No permitir cambiar grupo
                    nuevos_datos.get('direccion', al.direccion),
                    nuevos_datos.get('lugar_nac', al.lugar_nacimiento),
                    nuevos_datos.get('ultimo_grado', al.ultimo_grado_estudios),
                    None,  # No cambiar foto por ahora
                    nuevos_datos.get('email', al.email)
                )
                
                if ok:
                    messagebox.showinfo("✅ Éxito", "Tus datos han sido actualizados correctamente.")
                    modo_edicion[0] = False
                    # Actualizar el objeto alumno
                    al.nombre = nuevos_datos.get('nombre', al.nombre)
                    al.apellido = nuevos_datos.get('apellido', al.apellido)
                    al.fecha_nacimiento = nuevos_datos.get('fecha_nac', al.fecha_nacimiento)
                    al.telefono = nuevos_datos.get('telefono', al.telefono)
                    al.email = nuevos_datos.get('email', al.email)
                    al.direccion = nuevos_datos.get('direccion', al.direccion)
                    al.lugar_nacimiento = nuevos_datos.get('lugar_nac', al.lugar_nacimiento)
                    al.ultimo_grado_estudios = nuevos_datos.get('ultimo_grado', al.ultimo_grado_estudios)
                    # Recargar la vista
                    construir_vista()
                else:
                    messagebox.showerror("❌ Error", msg)
            
            def toggle_edicion():
                modo_edicion[0] = not modo_edicion[0]
                construir_vista()
            
            if modo_edicion[0]:
                self.btn(btn_frame, "💾 Guardar Cambios", guardar_cambios,
                        color=c['success'], padx=20, pady=8).pack(side='left', padx=5)
                self.btn(btn_frame, "❌ Cancelar", toggle_edicion,
                        color=c['danger'], padx=20, pady=8).pack(side='left', padx=5)
            else:
                self.btn(btn_frame, "✏️ Editar Datos Personales", toggle_edicion,
                        color=c['secondary'], padx=20, pady=8).pack(side='left', padx=5)
                
                # Botón para cambiar foto (siempre visible)
                def cambiar_foto():
                    ruta = filedialog.askopenfilename(
                        title="Seleccionar fotografía",
                        filetypes=[('Imágenes', '*.jpg *.jpeg *.png *.bmp'), ('Todos', '*.*')]
                    )
                    if ruta:
                        b64 = imagen_a_base64(ruta)
                        ok, msg = self.sistema.editar_alumno(
                            al.matricula, al.nombre, al.apellido,
                            al.fecha_nacimiento, al.telefono,
                            al.grado, al.grupo,
                            al.direccion, al.lugar_nacimiento,
                            al.ultimo_grado_estudios,
                            b64, al.email
                        )
                        if ok:
                            messagebox.showinfo("✅ Éxito", "Foto actualizada correctamente.")
                            al.foto_base64 = b64
                            construir_vista()
                        else:
                            messagebox.showerror("❌ Error", msg)
                
                self.btn(btn_frame, "📷 Cambiar Foto", cambiar_foto,
                        color=c['info'], padx=20, pady=8).pack(side='left', padx=5)
        
        # Construir la vista inicial
        construir_vista()

    # ===========================
    # ALUMNOS
    # ===========================

    def mostrar_alta_alumno(self):
        # Esta función ya no se usa porque se eliminó del menú, pero se mantiene por si acaso.
        pass

    def mostrar_baja_alumno(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("➖ Dar de Baja Alumno")
        sf = self.scroll_frame(self.right_panel)

        top = tk.Frame(sf, bg=c['surface'])
        top.pack(fill='x')
        sv, se = self.busqueda_bar(top, placeholder="(matrícula o nombre)")
        self.info_box(top, "Solo Administración puede gestionar bajas. Seleccione un alumno activo.", 'warn')

        cols = ('Matrícula', 'Nombre', 'Carrera', 'Grupo', 'Teléfono')
        tree = self.tabla(sf, cols, [120, 230, 210, 60, 120], height=12)
        sel_lbl = tk.Label(sf, text="Ningún alumno seleccionado", bg=c['surface'],
                           fg=c['text_light'], font=('Segoe UI', 9))
        sel_lbl.pack()

        mf = tk.Frame(sf, bg=c['surface'])
        mf.pack(fill='x', padx=10, pady=3)
        tk.Label(mf, text="Motivo de baja:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        mot_e = self.entry(mf, width=45)
        mot_e.insert(0, "Sin especificar")
        mot_e.pack(side='left', padx=5, ipady=3)

        sel = [None]

        def cargar(*a):
            alumnos = sorted(self.sistema.buscar_alumnos(sv.get(), solo_activos=True),
                             key=lambda x: x.matricula)
            filas = []
            for al in alumnos:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
                filas.append((al.matricula, al.get_nombre_completo(), cn, al.grupo, al.telefono))
            self.insertar(tree, filas)

        def on_sel(e):
            s = tree.selection()
            if s:
                v = tree.item(s[0])['values']
                sel[0] = v[0]
                sel_lbl.config(text=f"✓ Seleccionado: {v[1]} ({v[0]})", fg=c['secondary'])

        def dar_baja():
            if not sel[0]:
                messagebox.showwarning("Sin selección", "Seleccione un alumno")
                return
            al = self.sistema.alumnos.get(str(sel[0]))
            motivo = mot_e.get().strip()
            if messagebox.askyesno("Confirmar baja", f"¿Dar de baja a {al.get_nombre_completo()}?\nMotivo: {motivo}"):
                ok, msg = self.sistema.dar_baja_alumno(str(sel[0]), motivo)
                messagebox.showinfo("Resultado", msg)
                if ok:
                    self.mostrar_dashboard()

        tree.bind('<<TreeviewSelect>>', on_sel)
        tree.bind('<Double-1>', lambda e: dar_baja())
        sv.trace('w', cargar)
        self.btn(sf, "❌ Dar de Baja al Seleccionado", dar_baja,
                 color=c['danger'], padx=20, pady=8).pack(pady=8)
        cargar()
        se.focus()

    def mostrar_reactivar_alumno(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🔄 Reactivar Alumno")
        sf = self.scroll_frame(self.right_panel)

        top = tk.Frame(sf, bg=c['surface'])
        top.pack(fill='x')
        sv, se = self.busqueda_bar(top, placeholder="(matrícula o nombre)")
        self.info_box(top, "Lista de alumnos dados de baja. Seleccione y presione 'Reactivar'.", 'warn')

        cols = ('Matrícula', 'Nombre', 'Carrera', 'Grupo', 'Fecha Baja', 'Motivo')
        tree = self.tabla(sf, cols, [120, 200, 180, 60, 150, 200], height=12)
        sel = [None]
        sel_lbl = tk.Label(sf, text="Ninguno seleccionado", bg=c['surface'],
                           fg=c['text_light'], font=('Segoe UI', 9))
        sel_lbl.pack()

        def cargar(*a):
            alumnos = sorted(self.sistema.buscar_alumnos_inactivos(sv.get()), key=lambda x: x.matricula)
            filas = []
            for al in alumnos:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
                filas.append((al.matricula, al.get_nombre_completo(), cn, al.grupo,
                               al.fecha_baja or 'N/A', al.motivo_baja or 'N/A'))
            self.insertar(tree, filas)

        def on_sel(e):
            s = tree.selection()
            if s:
                v = tree.item(s[0])['values']
                sel[0] = v[0]
                sel_lbl.config(text=f"✓ Seleccionado: {v[1]} ({v[0]})", fg=c['success'])

        def reactivar():
            if not sel[0]:
                messagebox.showwarning("Sin selección", "Seleccione un alumno")
                return
            al = self.sistema.alumnos.get(str(sel[0]))
            if messagebox.askyesno("Confirmar", f"¿Reactivar a {al.get_nombre_completo()}?"):
                ok, msg = self.sistema.reactivar_alumno(str(sel[0]))
                messagebox.showinfo("Resultado", msg)
                if ok:
                    self.mostrar_dashboard()

        tree.bind('<<TreeviewSelect>>', on_sel)
        tree.bind('<Double-1>', lambda e: reactivar())
        sv.trace('w', cargar)
        self.btn(sf, "✅ Reactivar Seleccionado", reactivar,
                 color=c['success'], padx=20, pady=8).pack(pady=8)
        cargar()
        se.focus()

    def mostrar_cambiar_grupo(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("↔ Cambiar Grupo de Alumno")
        sf = self.scroll_frame(self.right_panel)
        self.info_box(sf, "Administración puede cambiar el grupo de cualquier alumno activo.", 'info')

        sv, se = self.busqueda_bar(sf, placeholder="(matrícula o nombre)")
        cols = ('Matrícula', 'Nombre', 'Grupo Actual', 'Carrera')
        tree = self.tabla(sf, cols, [120, 230, 120, 220], height=10)
        sel = [None]
        sel_lbl = tk.Label(sf, text="Seleccione un alumno", bg=c['surface'],
                           fg=c['text_light'], font=('Segoe UI', 9))
        sel_lbl.pack()

        def cargar(*a):
            alumnos = sorted(self.sistema.buscar_alumnos(sv.get(), solo_activos=True),
                             key=lambda x: x.apellido)
            filas = []
            for al in alumnos:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
                filas.append((al.matricula, al.get_nombre_completo(), al.grado, cn))
            self.insertar(tree, filas)

        def on_sel(e):
            s = tree.selection()
            if s:
                v = tree.item(s[0])['values']
                sel[0] = v[0]
                sel_lbl.config(text=f"✓ {v[1]} — Grupo actual: {v[2]}", fg=c['secondary'])

        sv.trace('w', cargar)
        tree.bind('<<TreeviewSelect>>', on_sel)

        # Form nuevo grupo
        form = tk.Frame(sf, bg=c['surface'])
        form.pack(padx=20, pady=8, fill='x')
        form.columnconfigure(1, weight=1)

        carreras_opts = [f"{k} - {v}" for k, v in CARRERAS.items()]
        sem_w  = self.campo_form(form, 0, "Nuevo Semestre:", 'combo', SEMESTRES)
        car_w  = self.campo_form(form, 1, "Nueva Carrera:", 'combo', carreras_opts)
        grp_w  = self.campo_form(form, 2, "Nuevo Grupo:", 'combo', GRUPOS_LETRAS)
        prev   = tk.Label(form, text="Nuevo código: —", bg=c['surface'], fg=c['secondary'],
                          font=('Segoe UI', 11, 'bold'))
        prev.grid(row=3, column=0, columnspan=2, pady=5)

        def upd(*a):
            s = sem_w.get(); car = car_w.get(); g = grp_w.get()
            if s and car and g:
                cod = car.split(' - ')[0]
                prev.config(text=f"Nuevo código: {s}{cod}{g}", fg=c['success'])

        for w in [sem_w, car_w, grp_w]:
            w.bind('<<ComboboxSelected>>', upd)

        def cambiar():
            if not sel[0]:
                messagebox.showwarning("Sin selección", "Seleccione un alumno")
                return
            s = sem_w.get(); car = car_w.get(); g = grp_w.get()
            if not all([s, car, g]):
                messagebox.showwarning("Incompleto", "Complete el nuevo grupo")
                return
            cod = car.split(' - ')[0]
            nuevo_grado = self.sistema.construir_grupo_completo(s, cod, g)
            al = self.sistema.alumnos.get(str(sel[0]))
            if messagebox.askyesno("Confirmar", f"¿Cambiar grupo de {al.get_nombre_completo()}\na {nuevo_grado}?"):
                ok, msg = self.sistema.cambiar_grupo_alumno(str(sel[0]), nuevo_grado, g)
                messagebox.showinfo("Resultado", msg)
                if ok:
                    cargar()

        self.btn(form, "↔ Cambiar Grupo", cambiar, color=c['warning'],
                 padx=20, pady=8).grid(row=4, column=0, columnspan=2, pady=10)
        cargar()
        se.focus()

    def mostrar_solicitar_grupo(self):
        """Para estudiantes: solicitar cambio de grupo."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🙋 Solicitar Cambio de Grupo")
        sf = self.scroll_frame(self.right_panel)
        uid = self.sistema.usuario_actual.id
        al = self.sistema.alumnos.get(uid)
        if not al:
            self.info_box(sf, "Tu cuenta de estudiante no está asociada a un alumno registrado.", 'error')
            return
        sm, cc, grp = self.sistema.parsear_grupo_completo(al.grado)
        self.info_box(sf, f"Alumno: {al.get_nombre_completo()} | Grupo actual: {al.grado}", 'info')
        form = tk.Frame(sf, bg=c['surface'])
        form.pack(padx=25, pady=10, fill='x')
        form.columnconfigure(1, weight=1)
        carreras_opts = [f"{k} - {v}" for k, v in CARRERAS.items()]
        sem_w = self.campo_form(form, 0, "Semestre Solicitado:", 'combo', SEMESTRES)
        car_w = self.campo_form(form, 1, "Carrera Solicitada:", 'combo', carreras_opts)
        grp_w = self.campo_form(form, 2, "Grupo Solicitado:", 'combo', GRUPOS_LETRAS)
        mot_w = self.campo_form(form, 3, "Motivo:", 'entry')

        def solicitar():
            s = sem_w.get(); car = car_w.get(); g = grp_w.get(); mot = mot_w.get().strip()
            if not all([s, car, g]):
                messagebox.showwarning("Incompleto", "Complete todos los campos")
                return
            cod = car.split(' - ')[0]
            nuevo = self.sistema.construir_grupo_completo(s, cod, g)
            ok, msg = self.sistema.solicitar_cambio_grupo(uid, nuevo, mot)
            if ok:
                messagebox.showinfo("✅ Solicitud enviada", msg)
            else:
                messagebox.showerror("Error", msg)

        self.btn(form, "📤 Enviar Solicitud", solicitar, color=c['secondary'],
                 padx=20, pady=8).grid(row=4, column=0, columnspan=2, pady=12)

    def mostrar_solicitudes_grupo(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("📋 Solicitudes de Cambio de Grupo")
        sf = self.scroll_frame(self.right_panel)
        self.info_box(sf, "Apruebe o rechace las solicitudes de cambio de grupo de los estudiantes.", 'info')

        cols = ('ID', 'Alumno', 'Grupo Actual', 'Grupo Solicitado', 'Motivo', 'Fecha', 'Estado')
        tree = self.tabla(sf, cols, [140, 200, 120, 140, 160, 150, 90], height=14)
        sel = [None]

        def cargar():
            filas = []
            for s in sorted(self.sistema.solicitudes_grupo.values(), key=lambda x: x.fecha, reverse=True):
                al = self.sistema.alumnos.get(s.matricula_alumno)
                nombre = al.get_nombre_completo() if al else s.matricula_alumno
                filas.append((s.id, nombre, s.grupo_actual, s.grupo_solicitado,
                               s.motivo, s.fecha, s.estado))
            self.insertar(tree, filas)

        def on_sel(e):
            s = tree.selection()
            if s:
                sel[0] = tree.item(s[0])['values'][0]

        tree.bind('<<TreeviewSelect>>', on_sel)

        bf = tk.Frame(sf, bg=c['surface'])
        bf.pack(pady=8)

        def resolver(accion):
            if not sel[0]:
                messagebox.showwarning("Sin selección", "Seleccione una solicitud")
                return
            ok, msg = self.sistema.resolver_solicitud_grupo(sel[0], accion)
            messagebox.showinfo("Resultado", msg)
            cargar()

        self.btn(bf, "✅ Aprobar", lambda: resolver('Aprobada'),
                 color=c['success'], padx=20, pady=8).pack(side='left', padx=8)
        self.btn(bf, "❌ Rechazar", lambda: resolver('Rechazada'),
                 color=c['danger'], padx=20, pady=8).pack(side='left', padx=8)
        cargar()

    def mostrar_lista_alumnos(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("👥 Lista de Alumnos")

        # Determinar filtro de grupos si es docente
        grados_docente = None
        if self.sistema.es_docente():
            uid = self.sistema.usuario_actual.id
            grados_docente = self.sistema.get_grados_del_docente(uid)
            if grados_docente:
                grupos_str = ", ".join(sorted(grados_docente))
                tk.Label(self.right_panel,
                         text=f"📌 Mostrando solo alumnos de tus grupos: {grupos_str}",
                         bg=c['surface'], fg=c['secondary'],
                         font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=12, pady=(4, 0))
            else:
                tk.Label(self.right_panel,
                         text="⚠ No tienes grupos asignados en los horarios.",
                         bg=c['surface'], fg=c['warning'],
                         font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=12, pady=(4, 0))

        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x')

        # ── Barra de búsqueda ──────────────────────────────────────────────
        sv, se = self.busqueda_bar(top)

        # ── Radio buttons: criterio de búsqueda/orden ──────────────────────
        criterio_var = tk.StringVar(value='nombre')
        rf = tk.Frame(top, bg=c['surface'])
        rf.pack(fill='x', padx=10, pady=(0, 4))
        tk.Label(rf, text="Buscar/ordenar por:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 9)).pack(side='left', padx=5)
        for txt, val in [("Nombre", 'nombre'), ("Matrícula", 'matricula'), ("Grupo", 'grupo')]:
            tk.Radiobutton(rf, text=txt, variable=criterio_var, value=val,
                           bg=c['surface'], fg=c['text'], selectcolor=c['surface'],
                           font=('Segoe UI', 9)).pack(side='left', padx=6)

        # Botones de acción
        action_frame = tk.Frame(top, bg=c['surface'])
        action_frame.pack(fill='x', padx=10, pady=5)
        
        if self.sistema.es_admin():
            self.btn(action_frame, "✏️ Editar Seleccionado", 
                    lambda: self._editar_alumno_seleccionado(tree_act), 
                    color=c['warning'], padx=10, pady=5).pack(side='left', padx=5)

        nb = ttk.Notebook(self.right_panel)
        nb.pack(fill='both', expand=True, padx=10, pady=5)

        ta = tk.Frame(nb, bg=c['surface'])
        nb.add(ta, text="✓ Activos")
        cols = ('Matrícula', 'Nombre', 'Email', 'Código', 'Carrera', 'Grupo', 'Teléfono', 'F. Alta')
        tree_act = self.tabla(ta, cols, [110, 190, 180, 70, 190, 55, 110, 140], height=14)

        ti = tk.Frame(nb, bg=c['surface'])
        nb.add(ti, text="✗ Dados de Baja")
        cols2 = ('Matrícula', 'Nombre', 'Código', 'Carrera', 'Grupo', 'F. Baja', 'Motivo')
        tree_in = self.tabla(ti, cols2, [110, 190, 70, 190, 55, 140, 190], height=14)

        cnt = tk.Label(self.right_panel, text="", bg=c['surface'], fg=c['text_light'],
                       font=('Segoe UI', 9))
        cnt.pack()

        def cargar(*a):
            t = sv.get().strip().lower()
            crit = criterio_var.get()

            # --- activos ---
            act = list(self.sistema.alumnos.values())
            act = [al for al in act if al.activo]
            if grados_docente is not None:
                act = [al for al in act if al.grado in grados_docente]
            # filtrar por criterio
            if t:
                if crit == 'matricula':
                    act = [al for al in act if t in al.matricula.lower()]
                elif crit == 'grupo':
                    act = [al for al in act if t in al.grado.lower() or t in al.grupo.lower()]
                else:  # nombre
                    act = [al for al in act if t in al.nombre.lower() or
                           t in al.apellido.lower() or t in al.get_nombre_completo().lower()]
            # ordenar por criterio
            if crit == 'matricula':
                act.sort(key=lambda x: x.matricula)
            elif crit == 'grupo':
                act.sort(key=lambda x: (x.grado, x.apellido))
            else:
                act.sort(key=lambda x: x.apellido)

            filas_a = []
            for al in act:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else 'N/A'
                filas_a.append((al.matricula, al.get_nombre_completo(), al.email,
                                 al.grado, cn, al.grupo, al.telefono, al.fecha_alta))
            self.insertar(tree_act, filas_a)

            # --- inactivos ---
            inact = list(self.sistema.alumnos.values())
            inact = [al for al in inact if not al.activo]
            if grados_docente is not None:
                inact = [al for al in inact if al.grado in grados_docente]
            if t:
                if crit == 'matricula':
                    inact = [al for al in inact if t in al.matricula.lower()]
                elif crit == 'grupo':
                    inact = [al for al in inact if t in al.grado.lower() or t in al.grupo.lower()]
                else:
                    inact = [al for al in inact if t in al.nombre.lower() or
                             t in al.apellido.lower() or t in al.get_nombre_completo().lower()]
            inact.sort(key=lambda x: x.apellido)

            filas_i = []
            for al in inact:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else 'N/A'
                filas_i.append((al.matricula, al.get_nombre_completo(), al.grado,
                                 cn, al.grupo, al.fecha_baja or 'N/A', al.motivo_baja or 'N/A'))
            self.insertar(tree_in, filas_i)
            cnt.config(text=f"Activos: {len(filas_a)} | Dados de baja: {len(filas_i)}")

        # Doble clic para ver detalles
        def on_doble_click_act(e):
            sel = tree_act.selection()
            if sel:
                matricula = tree_act.item(sel[0])['values'][0]
                self.mostrar_detalle_alumno(matricula)

        def on_doble_click_in(e):
            sel = tree_in.selection()
            if sel:
                matricula = tree_in.item(sel[0])['values'][0]
                self.mostrar_detalle_alumno(matricula)

        tree_act.bind('<Double-1>', on_doble_click_act)
        tree_in.bind('<Double-1>', on_doble_click_in)

        sv.trace('w', cargar)
        criterio_var.trace('w', cargar)
        cargar()
        se.focus()

    def _editar_alumno_seleccionado(self, tree):
        """Abre el formulario de edición para el alumno seleccionado."""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Por favor seleccione un alumno de la lista")
            return
        matricula = tree.item(sel[0])['values'][0]
        self.mostrar_editar_alumno_con_id(matricula)

    def mostrar_editar_alumno_con_id(self, matricula=None):
        """Muestra el formulario de edición de alumno, opcionalmente con un ID pre-seleccionado."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("✏️ Editar Alumno")
        sf = self.scroll_frame(self.right_panel)

        if matricula:
            al = self.sistema.alumnos.get(str(matricula))
            if al:
                self._poblar_form_editar_alumno(sf, al)
                return

        # Si no hay matrícula, mostrar buscador
        sv, se = self.busqueda_bar(sf, placeholder="(matrícula o nombre)")
        cols = ('Matrícula', 'Nombre', 'Grado', 'Grupo')
        tree = self.tabla(sf, cols, [120, 240, 100, 60], height=10)

        def cargar(*a):
            alumnos = sorted(self.sistema.buscar_alumnos(sv.get(), False), key=lambda x: x.apellido)
            filas = [(al.matricula, al.get_nombre_completo(), al.grado, al.grupo) for al in alumnos]
            self.insertar(tree, filas)

        def on_sel(e):
            s = tree.selection()
            if s:
                mat = tree.item(s[0])['values'][0]
                al = self.sistema.alumnos.get(str(mat))
                if al:
                    # Limpiar el área y mostrar el formulario
                    for w in sf.winfo_children():
                        w.destroy()
                    self._poblar_form_editar_alumno(sf, al)

        tree.bind('<<TreeviewSelect>>', on_sel)
        sv.trace('w', cargar)
        cargar()
        se.focus()

    def _poblar_form_editar_alumno(self, parent, al):
        """Construye el formulario de edición para un alumno específico."""
        c = self.colors
        rol = self.sistema.get_rol()
        
        form = tk.Frame(parent, bg=c['surface'])
        form.pack(padx=25, pady=10, fill='x')
        form.columnconfigure(1, weight=1)

        entries = {}
        sm, cc, grp = self.sistema.parsear_grupo_completo(al.grado)
        carreras_opts = [f"{k} - {v}" for k, v in CARRERAS.items()]
        car_match = next((o for o in carreras_opts if o.startswith(cc + ' - ')), carreras_opts[0]) if cc else carreras_opts[0]

        # Campos editables según rol
        campos_editables = ['nombre', 'apellido', 'email', 'telefono', 'direccion'] if rol == 'Estudiante' else None

        defs = [
            (0, "Nombre:", 'entry', None, al.nombre, 'nombre'),
            (1, "Apellido:", 'entry', None, al.apellido, 'apellido'),
            (2, "Email:", 'entry', None, al.email, 'email'),
            (3, "Teléfono:", 'entry', None, al.telefono, 'telefono'),
            (4, "Lugar de Nacimiento:", 'entry', None, al.lugar_nacimiento, 'lugar_nac'),
            (5, "Dirección:", 'entry', None, al.direccion, 'direccion'),
            (6, "Fecha Nacimiento:", 'entry', None, al.fecha_nacimiento, 'fecha_nac'),
            (7, "Semestre:", 'combo', SEMESTRES, sm or '', 'semestre'),
            (8, "Carrera:", 'combo', carreras_opts, car_match, 'carrera'),
            (9, "Grupo:", 'combo', GRUPOS_LETRAS, grp or al.grupo, 'grupo'),
        ]

        for row, lbl, tipo, opts, valor, key in defs:
            w = self.campo_form(form, row, lbl, tipo, opts, valor)
            if campos_editables and key not in campos_editables:
                w.config(state='disabled')
            entries[key] = w

        self.boton_foto(form, 10, 'foto', entries)
        if al.foto_base64:
            entries['foto'] = al.foto_base64
            entries.get('foto_label', {}).config(text="✓ Foto existente")

        def guardar():
            def gv(k): return entries[k].get().strip() if hasattr(entries[k], 'get') else entries.get(k, '')
            sem_v = gv('semestre')
            car_v = gv('carrera')
            grp_v = gv('grupo')
            car_cod = car_v.split(' - ')[0] if ' - ' in car_v else cc or ''
            grado_n = self.sistema.construir_grupo_completo(sem_v, car_cod, grp_v) if sem_v else al.grado
            
            ok, msg = self.sistema.editar_alumno(
                al.matricula, gv('nombre'), gv('apellido'), gv('fecha_nac'),
                gv('telefono'), grado_n, grp_v,
                gv('direccion'), gv('lugar_nac'), al.ultimo_grado_estudios,
                entries.get('foto'), gv('email')
            )
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
                self.mostrar_lista_alumnos()
            else:
                messagebox.showerror("❌ Error", msg)

        self.btn(form, "💾 Guardar Cambios", guardar, color=c['warning'],
                 padx=22, pady=9).grid(row=11, column=0, columnspan=2, pady=12)

    def mostrar_grupos(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🏫 Ver Grupos")
        sf = self.scroll_frame(self.right_panel)

        # Si es docente, filtrar solo los grupos en los que tiene horarios asignados
        if self.sistema.es_docente():
            uid = self.sistema.usuario_actual.id
            grupos_docente = self.sistema.get_grupos_del_docente(uid)
            grupos = [(g, gr) for (g, gr) in self.sistema.obtener_grupos_disponibles()
                      if (g, gr) in grupos_docente]
            if not grupos:
                tk.Label(sf, text="No tienes grupos asignados en los horarios.", bg=c['surface'],
                         fg=c['text_light'], font=('Segoe UI', 11)).pack(pady=30)
                return
        else:
            grupos = self.sistema.obtener_grupos_disponibles()
            if not grupos:
                tk.Label(sf, text="No hay grupos con alumnos activos.", bg=c['surface'],
                         fg=c['text_light'], font=('Segoe UI', 11)).pack(pady=30)
                return

        for grado, grupo in grupos:
            sm, cc, grp = self.sistema.parsear_grupo_completo(grado)
            t = (f"Grupo {grado} | {sm}° Semestre — {self.sistema.get_nombre_carrera(cc)} — Grupo {grp}"
                 if sm else f"Grado: {grado} — Grupo: {grupo}")
            sec = tk.LabelFrame(sf, text=t, bg=c['surface'], fg=c['secondary'],
                                font=('Segoe UI', 10, 'bold'), relief='solid', bd=1)
            sec.pack(fill='x', padx=12, pady=4)
            alumnos = sorted(self.sistema.obtener_alumnos_por_grupo(grado, grupo),
                             key=lambda a: a.apellido)
            for i, al in enumerate(alumnos):
                bg = c['table_alt'] if i % 2 == 0 else c['surface']
                row = tk.Frame(sec, bg=bg)
                row.pack(fill='x')
                tk.Label(row, text=f"  {i+1}. {al.get_nombre_completo()} ({al.matricula})",
                         bg=bg, fg=c['text'], font=('Segoe UI', 9), anchor='w').pack(
                    side='left', padx=10, pady=3)
                tk.Label(row, text=f"📞 {al.telefono}",
                         bg=bg, fg=c['text_light'], font=('Segoe UI', 9)).pack(side='right', padx=10)
            tk.Label(sec, text=f"Total: {len(alumnos)} alumno(s)", bg=c['surface'],
                     fg=c['text_light'], font=('Segoe UI', 9, 'italic')).pack(anchor='e', padx=8, pady=2)

    def mostrar_mi_grupo(self):
        """Para estudiantes: mostrar solo su grupo."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("👥 Mi Grupo")
        sf = self.scroll_frame(self.right_panel)
        
        uid = self.sistema.usuario_actual.id
        al = self.sistema.alumnos.get(uid)
        
        if not al:
            self.info_box(sf, "Tu cuenta de estudiante no está asociada a un alumno registrado.", 'error')
            return
        
        grado = al.grado
        grupo = al.grupo
        sm, cc, grp = self.sistema.parsear_grupo_completo(grado)
        
        t = (f"Mi Grupo: {grado} | {sm}° Semestre — {self.sistema.get_nombre_carrera(cc)} — Grupo {grp}"
             if sm else f"Grupo: {grado} — Grupo: {grupo}")
        
        tk.Label(sf, text=t, bg=c['surface'], fg=c['secondary'],
                 font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        alumnos = sorted(self.sistema.obtener_alumnos_por_grupo(grado, grupo),
                         key=lambda a: a.apellido)
        
        if not alumnos:
            tk.Label(sf, text="No hay otros alumnos en tu grupo.", bg=c['surface'],
                     fg=c['text_light'], font=('Segoe UI', 10)).pack(pady=20)
            return
        
        tk.Label(sf, text=f"Compañeros de grupo ({len(alumnos)} alumnos):", 
                 bg=c['surface'], fg=c['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=12, pady=(10, 5))
        
        for i, alum in enumerate(alumnos):
            bg = c['table_alt'] if i % 2 == 0 else c['surface']
            row = tk.Frame(sf, bg=bg)
            row.pack(fill='x', padx=12, pady=1)
            tk.Label(row, text=f"  {i+1}. {alum.get_nombre_completo()}",
                     bg=bg, fg=c['text'], font=('Segoe UI', 9), anchor='w').pack(side='left', padx=10, pady=3)
            if alum.matricula == uid:
                tk.Label(row, text="(Tú)", bg=bg, fg=c['secondary'], 
                         font=('Segoe UI', 9, 'italic')).pack(side='left', padx=5)

    # ===========================
    # DOCENTES
    # ===========================

    def _form_docente(self, titulo, doc_actual=None):
        """Formulario reutilizable para alta/edición de docentes."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel(titulo)
        sf = self.scroll_frame(self.right_panel)

        form = tk.Frame(sf, bg=c['surface'])
        form.pack(padx=25, pady=10, fill='x')
        form.columnconfigure(1, weight=1)

        entries = {}
        d = doc_actual

        campos = [
            (0, "Nombre:", 'entry', None, d.nombre if d else ''),
            (1, "Apellido:", 'entry', None, d.apellido if d else ''),
            (2, "Número de Empleado:", 'entry', None, d.num_empleado if d else ''),
            (3, "Email:", 'entry', None, d.email if d else ''),
            (4, "Fecha Nacimiento (DD/MM/AAAA):", 'entry', None, d.fecha_nacimiento if d else ''),
            (5, "Teléfono:", 'entry', None, d.telefono if d else ''),
            (6, "Especialidad:", 'entry', None, d.especialidad if d else ''),
            (7, "Lugar de Nacimiento:", 'entry', None, d.lugar_nacimiento if d else ''),
            (8, "Dirección:", 'entry', None, d.direccion if d else ''),
            (9, "Último Grado de Estudios:", 'combo',
             ['Licenciatura', 'Especialidad', 'Maestría', 'Doctorado'],
             d.ultimo_grado_estudios if d else ''),
            (10, "Tipo de Contrato:", 'combo', TIPOS_CONTRATO,
             d.tipo_contrato if d else 'Permanente'),
        ]
        keys = ['nombre', 'apellido', 'num_empleado', 'email', 'fecha_nac', 'telefono',
                'especialidad', 'lugar_nac', 'direccion', 'ultimo_grado', 'tipo_contrato']

        for (row, label, tipo, opts, valor), key in zip(campos, keys):
            entries[key] = self.campo_form(form, row, label, tipo, opts, valor)

        if d and d.num_empleado:
            entries['num_empleado'].config(state='disabled')

        self.boton_foto(form, 11, 'foto', entries)
        if d and d.foto_base64:
            entries['foto'] = d.foto_base64
            entries.get('foto_label', type('', (), {'config': lambda **k: None})()).config(text="✓ Foto existente")
        return form, entries

    def mostrar_agregar_docente(self):
        # Esta función ya no se usa porque se eliminó del menú, pero se mantiene por si acaso.
        pass

    def mostrar_lista_docentes(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("📋 Lista de Docentes")
        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x')
        sv, se = self.busqueda_bar(top)

        # Botones de acción
        action_frame = tk.Frame(top, bg=c['surface'])
        action_frame.pack(fill='x', padx=10, pady=5)
        
        if self.sistema.es_admin():
            self.btn(action_frame, "✏️ Editar Seleccionado", 
                    lambda: self._editar_docente_seleccionado(tree_act), 
                    color=c['warning'], padx=10, pady=5).pack(side='left', padx=5)

        nb = ttk.Notebook(self.right_panel)
        nb.pack(fill='both', expand=True, padx=10, pady=5)

        ta = tk.Frame(nb, bg=c['surface'])
        nb.add(ta, text="✓ Activos")
        cols = ('No. Emp.', 'Nombre', 'Especialidad', 'Contrato', 'Email', 'Teléfono')
        tree_act = self.tabla(ta, cols, [90, 200, 190, 110, 200, 110], height=14)

        tb = tk.Frame(nb, bg=c['surface'])
        nb.add(tb, text="⏸ Baja Temporal")
        tree_bt = self.tabla(tb, cols, [90, 200, 190, 110, 200, 110], height=14)

        cnt = tk.Label(self.right_panel, text="", bg=c['surface'], fg=c['text_light'],
                       font=('Segoe UI', 9))
        cnt.pack()

        def cargar(*a):
            activos, baja_t = [], []
            for d in sorted(self.sistema.buscar_docentes(sv.get()), key=lambda x: x.apellido):
                fila = (d.num_empleado, d.get_nombre_completo(), d.especialidad,
                        d.tipo_contrato, d.email, d.telefono)
                if d.baja_temporal:
                    baja_t.append(fila)
                else:
                    activos.append(fila)
            self.insertar(tree_act, activos)
            self.insertar(tree_bt, baja_t)
            cnt.config(text=f"Activos: {len(activos)} | Baja temporal: {len(baja_t)}")

        # Doble clic para ver detalles
        def on_doble_click_act(e):
            sel = tree_act.selection()
            if sel:
                num_emp = tree_act.item(sel[0])['values'][0]
                self.mostrar_detalle_docente(num_emp)

        def on_doble_click_bt(e):
            sel = tree_bt.selection()
            if sel:
                num_emp = tree_bt.item(sel[0])['values'][0]
                self.mostrar_detalle_docente(num_emp)

        tree_act.bind('<Double-1>', on_doble_click_act)
        tree_bt.bind('<Double-1>', on_doble_click_bt)

        sv.trace('w', cargar)
        cargar()
        se.focus()

    def _editar_docente_seleccionado(self, tree):
        """Abre el formulario de edición para el docente seleccionado."""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Por favor seleccione un docente de la lista")
            return
        num_emp = tree.item(sel[0])['values'][0]
        self.mostrar_editar_docente_con_id(num_emp)

    def mostrar_editar_docente_con_id(self, num_empleado=None):
        """Muestra el formulario de edición de docente, opcionalmente con un ID pre-seleccionado."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("✏️ Editar Docente")
        sf = self.scroll_frame(self.right_panel)

        if num_empleado:
            doc = self.sistema.docentes.get(str(num_empleado))
            if doc:
                self._poblar_form_editar_docente(sf, doc)
                return

        # Si no hay num_empleado, mostrar buscador
        sv, se = self.busqueda_bar(sf, placeholder="(nombre o número de empleado)")
        cols = ('No. Emp.', 'Nombre', 'Especialidad', 'Contrato')
        tree = self.tabla(sf, cols, [100, 230, 200, 110], height=10)

        def cargar(*a):
            docs = sorted(self.sistema.buscar_docentes(sv.get()), key=lambda x: x.apellido)
            filas = [(d.num_empleado, d.get_nombre_completo(), d.especialidad, d.tipo_contrato) for d in docs]
            self.insertar(tree, filas)

        def on_sel(e):
            s = tree.selection()
            if s:
                num = tree.item(s[0])['values'][0]
                doc = self.sistema.docentes.get(str(num))
                if doc:
                    # Limpiar el área y mostrar el formulario
                    for w in sf.winfo_children():
                        w.destroy()
                    self._poblar_form_editar_docente(sf, doc)

        tree.bind('<<TreeviewSelect>>', on_sel)
        sv.trace('w', cargar)
        cargar()
        se.focus()

    def _poblar_form_editar_docente(self, parent, doc):
        """Construye el formulario de edición para un docente específico."""
        c = self.colors
        
        form = tk.Frame(parent, bg=c['surface'])
        form.pack(padx=25, pady=10, fill='x')
        form.columnconfigure(1, weight=1)

        entries = {}
        defs = [
            (0, "Nombre:", 'entry', None, doc.nombre, 'nombre'),
            (1, "Apellido:", 'entry', None, doc.apellido, 'apellido'),
            (2, "Email:", 'entry', None, doc.email, 'email'),
            (3, "Teléfono:", 'entry', None, doc.telefono, 'telefono'),
            (4, "Especialidad:", 'entry', None, doc.especialidad, 'especialidad'),
            (5, "Lugar Nacimiento:", 'entry', None, doc.lugar_nacimiento, 'lugar_nac'),
            (6, "Dirección:", 'entry', None, doc.direccion, 'direccion'),
            (7, "Fecha Nacimiento:", 'entry', None, doc.fecha_nacimiento, 'fecha_nac'),
            (8, "Último Grado:", 'combo', ['Licenciatura', 'Especialidad', 'Maestría', 'Doctorado'],
             doc.ultimo_grado_estudios, 'ultimo_grado'),
            (9, "Tipo de Contrato:", 'combo', TIPOS_CONTRATO, doc.tipo_contrato, 'tipo_contrato'),
        ]

        for row, lbl, tipo, opts, valor, key in defs:
            entries[key] = self.campo_form(form, row, lbl, tipo, opts, valor)

        self.boton_foto(form, 10, 'foto', entries)
        if doc.foto_base64:
            entries['foto'] = doc.foto_base64
            entries.get('foto_label', {}).config(text="✓ Foto existente")

        def guardar():
            def gv(k): return entries[k].get().strip() if hasattr(entries[k], 'get') else ''
            ok, msg = self.sistema.editar_docente(
                doc.num_empleado, gv('nombre'), gv('apellido'), gv('fecha_nac'),
                gv('telefono'), gv('especialidad'), gv('email'),
                gv('tipo_contrato'), gv('direccion'), gv('lugar_nac'),
                gv('ultimo_grado'), entries.get('foto')
            )
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
                self.mostrar_lista_docentes()
            else:
                messagebox.showerror("❌ Error", msg)

        self.btn(form, "💾 Guardar Cambios", guardar, color=c['warning'],
                 padx=22, pady=9).grid(row=11, column=0, columnspan=2, pady=12)

    def mostrar_baja_temporal_docente(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("⏸ Baja Temporal / Reactivar Docente")
        sf = self.scroll_frame(self.right_panel)
        self.info_box(sf, "Baja temporal: el registro no se elimina. El docente puede reactivarse después.", 'warn')

        sv, se = self.busqueda_bar(sf)

        nb = ttk.Notebook(sf)
        nb.pack(fill='both', expand=True, padx=8, pady=5)

        ta = tk.Frame(nb, bg=c['surface'])
        nb.add(ta, text="✓ Activos")
        cols = ('No. Emp.', 'Nombre', 'Especialidad', 'Contrato')
        t_act = self.tabla(ta, cols, [100, 220, 200, 120], height=10)

        tb = tk.Frame(nb, bg=c['surface'])
        nb.add(tb, text="⏸ En Baja Temporal")
        t_bt = self.tabla(tb, cols, [100, 220, 200, 120], height=10)

        sel_a = [None]
        sel_b = [None]

        def cargar(*a):
            activos, baja_t = [], []
            for d in sorted(self.sistema.buscar_docentes(sv.get()), key=lambda x: x.apellido):
                fila = (d.num_empleado, d.get_nombre_completo(), d.especialidad, d.tipo_contrato)
                if d.baja_temporal:
                    baja_t.append(fila)
                else:
                    activos.append(fila)
            self.insertar(t_act, activos)
            self.insertar(t_bt, baja_t)

        t_act.bind('<<TreeviewSelect>>', lambda e: sel_a.__setitem__(0, t_act.item(t_act.selection()[0])['values'][0] if t_act.selection() else None))
        t_bt.bind('<<TreeviewSelect>>', lambda e: sel_b.__setitem__(0, t_bt.item(t_bt.selection()[0])['values'][0] if t_bt.selection() else None))
        sv.trace('w', cargar)

        bf = tk.Frame(sf, bg=c['surface'])
        bf.pack(pady=8)

        def baja_temp():
            if not sel_a[0]:
                messagebox.showwarning("Sin selección", "Seleccione un docente activo")
                return
            d = self.sistema.docentes.get(str(sel_a[0]))
            if messagebox.askyesno("Confirmar", f"¿Dar baja temporal a {d.get_nombre_completo()}?"):
                ok, msg = self.sistema.baja_temporal_docente(str(sel_a[0]))
                messagebox.showinfo("Resultado", msg)
                cargar()

        def reactivar():
            if not sel_b[0]:
                messagebox.showwarning("Sin selección", "Seleccione un docente en baja temporal")
                return
            d = self.sistema.docentes.get(str(sel_b[0]))
            if messagebox.askyesno("Confirmar", f"¿Reactivar a {d.get_nombre_completo()}?"):
                ok, msg = self.sistema.reactivar_docente(str(sel_b[0]))
                messagebox.showinfo("Resultado", msg)
                cargar()

        self.btn(bf, "⏸ Dar Baja Temporal", baja_temp, color=c['warning'],
                 padx=16, pady=7).pack(side='left', padx=8)
        self.btn(bf, "✅ Reactivar Docente", reactivar, color=c['success'],
                 padx=16, pady=7).pack(side='left', padx=8)
        cargar()
        se.focus()

    # ===========================
    # CATÁLOGOS: MATERIAS, CARRERAS, AULAS
    # ===========================

    def _cat_crud(self, titulo, cols, anchos, cargar_fn, form_fn, agregar_fn, editar_fn, eliminar_fn):
        """Patrón genérico CRUD para catálogos."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel(titulo)
        sf = self.scroll_frame(self.right_panel)

        sv, se = self.busqueda_bar(sf)
        tree = self.tabla(sf, cols, anchos, height=12)
        sel = [None]

        def on_sel(e):
            s = tree.selection()
            if s:
                sel[0] = tree.item(s[0])['values']

        tree.bind('<<TreeviewSelect>>', on_sel)

        def recargar(*a):
            self.insertar(tree, cargar_fn(sv.get()))

        sv.trace('w', recargar)

        bf = tk.Frame(sf, bg=c['surface'])
        bf.pack(pady=6)

        def agregar():
            def callback(datos):
                ok, msg = agregar_fn(*datos)
                if ok:
                    messagebox.showinfo("✅ Éxito", msg)
                    recargar()
                else:
                    messagebox.showerror("❌ Error", msg)
            form_fn(None, callback)

        def editar():
            if not sel[0]:
                messagebox.showwarning("Sin selección", "Seleccione un registro")
                return
            def callback(datos):
                ok, msg = editar_fn(*datos)
                if ok:
                    messagebox.showinfo("✅ Éxito", msg)
                    recargar()
                else:
                    messagebox.showerror("❌ Error", msg)
            form_fn(sel[0], callback)

        def eliminar():
            if not sel[0]:
                messagebox.showwarning("Sin selección", "Seleccione un registro")
                return
            if messagebox.askyesno("Confirmar eliminación",
                                   f"¿Eliminar '{sel[0][1] if len(sel[0]) > 1 else sel[0][0]}'?\nEsta acción no se puede deshacer."):
                ok, msg = eliminar_fn(sel[0][0])
                if ok:
                    messagebox.showinfo("✅ Éxito", msg)
                    recargar()
                else:
                    messagebox.showerror("❌ Error", msg)

        self.btn(bf, "➕ Agregar", agregar, color=c['success'], padx=14, pady=7).pack(side='left', padx=6)
        self.btn(bf, "✏️ Editar", editar, color=c['warning'], padx=14, pady=7).pack(side='left', padx=6)
        self.btn(bf, "🗑 Eliminar", eliminar, color=c['danger'], padx=14, pady=7).pack(side='left', padx=6)

        recargar()
        se.focus()

    # --- Materias ---
    def mostrar_lista_materias(self):
        c = self.colors

        def cargar(t=''):
            mats = sorted(self.sistema.buscar_materias(t), key=lambda m: m.nombre)
            return [(m.id, m.nombre, m.grado, self.sistema.get_nombre_carrera(m.carrera_codigo),
                     m.creditos, m.descripcion) for m in mats]

        def form(datos, callback):
            win = tk.Toplevel(self.root)
            win.title("Materia")
            win.geometry("400x380")
            win.configure(bg=c['surface'])
            win.grab_set()
            tk.Label(win, text="📖 Materia", bg=c['surface'], fg=c['text'],
                     font=('Segoe UI', 13, 'bold')).pack(pady=(15, 5))
            f = tk.Frame(win, bg=c['surface'])
            f.pack(padx=25, fill='x')
            f.columnconfigure(1, weight=1)
            id_w  = self.campo_form(f, 0, "ID:",    valor=datos[0] if datos else '')
            nom_w = self.campo_form(f, 1, "Nombre:", valor=datos[1] if datos else '')
            grd_w = self.campo_form(f, 2, "Semestre:", 'combo', SEMESTRES,
                                    valor=datos[2] if datos else '')
            car_opts = [f"{k} - {v}" for k, v in CARRERAS.items()]
            car_w  = self.campo_form(f, 3, "Carrera:", 'combo', car_opts)
            if datos and len(datos) > 3:
                for opt in car_opts:
                    if opt.split(' - ')[1].strip() == str(datos[3]).strip():
                        car_w.set(opt)
                        break
            cre_w = self.campo_form(f, 4, "Créditos:", valor=str(datos[4]) if datos else '0')
            desc_w = self.campo_form(f, 5, "Descripción:", valor=datos[5] if datos and len(datos) > 5 else '')
            if datos:
                id_w.config(state='disabled')

            def ok():
                id_ = id_w.get().strip()
                nom = nom_w.get().strip()
                grd = grd_w.get()
                car_sel = car_w.get()
                cre = cre_w.get().strip()
                if not id_ or not nom:
                    messagebox.showwarning("Campos", "ID y Nombre son obligatorios", parent=win)
                    return
                car_cod = car_sel.split(' - ')[0] if ' - ' in car_sel else ''
                try: cr = int(cre) if cre else 0
                except: cr = 0
                callback((id_, nom, grd, desc_w.get().strip(), car_cod, cr))
                win.destroy()

            self.btn(f, "💾 Guardar", ok, color=c['secondary'],
                     padx=18, pady=8).grid(row=6, column=0, columnspan=2, pady=12)

        self._cat_crud(
            "📖 Catálogo de Materias",
            ('ID', 'Nombre', 'Semestre', 'Carrera', 'Créditos', 'Descripción'),
            [90, 210, 80, 180, 70, 220],
            cargar, form,
            lambda *a: self.sistema.agregar_materia(*a),
            lambda *a: self.sistema.editar_materia(*a),
            lambda id: self.sistema.eliminar_materia(id),
        )

    # --- Carreras ---
    def mostrar_lista_carreras(self):
        c = self.colors

        def cargar(t=''):
            return [(ca.codigo, ca.nombre, ca.descripcion) for ca in
                    sorted(self.sistema.carreras.values(), key=lambda x: x.nombre)
                    if not t or t.lower() in ca.nombre.lower() or t.lower() in ca.codigo.lower()]

        def form(datos, callback):
            win = tk.Toplevel(self.root)
            win.title("Carrera")
            win.geometry("380x260")
            win.configure(bg=c['surface'])
            win.grab_set()
            tk.Label(win, text="🏛 Carrera", bg=c['surface'], fg=c['text'],
                     font=('Segoe UI', 13, 'bold')).pack(pady=(15, 5))
            f = tk.Frame(win, bg=c['surface'])
            f.pack(padx=25, fill='x')
            f.columnconfigure(1, weight=1)
            cod_w = self.campo_form(f, 0, "Código (1 letra):", valor=datos[0] if datos else '')
            nom_w = self.campo_form(f, 1, "Nombre:", valor=datos[1] if datos else '')
            desc_w = self.campo_form(f, 2, "Descripción:", valor=datos[2] if datos else '')
            if datos:
                cod_w.config(state='disabled')

            def ok():
                cod = cod_w.get().strip().upper()
                nom = nom_w.get().strip()
                if not cod or not nom:
                    messagebox.showwarning("Campos", "Código y Nombre son obligatorios", parent=win)
                    return
                callback((cod, nom, desc_w.get().strip()))
                win.destroy()

            self.btn(f, "💾 Guardar", ok, color=c['secondary'],
                     padx=18, pady=8).grid(row=3, column=0, columnspan=2, pady=12)

        self._cat_crud(
            "🏛 Catálogo de Carreras",
            ('Código', 'Nombre', 'Descripción'),
            [80, 260, 320],
            cargar, form,
            lambda *a: self.sistema.agregar_carrera(*a),
            lambda *a: self.sistema.editar_carrera(*a),
            lambda cod: self.sistema.eliminar_carrera(cod),
        )

    # --- Aulas ---
    def mostrar_lista_aulas(self):
        c = self.colors

        def cargar(t=''):
            return [(a.id, a.numero_salon, a.edificio, a.capacidad) for a in
                    sorted(self.sistema.aulas.values(), key=lambda x: x.id)
                    if not t or t.lower() in a.numero_salon.lower() or
                    t.lower() in a.edificio.lower() or t.lower() in a.id.lower()]

        def form(datos, callback):
            win = tk.Toplevel(self.root)
            win.title("Aula")
            win.geometry("360x280")
            win.configure(bg=c['surface'])
            win.grab_set()
            tk.Label(win, text="🏫 Aula", bg=c['surface'], fg=c['text'],
                     font=('Segoe UI', 13, 'bold')).pack(pady=(15, 5))
            f = tk.Frame(win, bg=c['surface'])
            f.pack(padx=25, fill='x')
            f.columnconfigure(1, weight=1)
            id_w  = self.campo_form(f, 0, "ID (ej: A01):", valor=datos[0] if datos else '')
            sal_w = self.campo_form(f, 1, "Número de Salón:", valor=datos[1] if datos else '')
            edi_w = self.campo_form(f, 2, "Edificio:", valor=datos[2] if datos else '')
            cap_w = self.campo_form(f, 3, "Capacidad:", valor=str(datos[3]) if datos else '30')
            if datos:
                id_w.config(state='disabled')

            def ok():
                id_ = id_w.get().strip()
                sal = sal_w.get().strip()
                edi = edi_w.get().strip()
                cap = cap_w.get().strip()
                if not all([id_, sal, edi, cap]):
                    messagebox.showwarning("Campos", "Complete todos los campos", parent=win)
                    return
                try: cap = int(cap)
                except: messagebox.showerror("Error", "Capacidad debe ser número", parent=win); return
                callback((id_, sal, edi, cap))
                win.destroy()

            self.btn(f, "💾 Guardar", ok, color=c['secondary'],
                     padx=18, pady=8).grid(row=4, column=0, columnspan=2, pady=12)

        self._cat_crud(
            "🏫 Catálogo de Aulas",
            ('ID', 'Salón', 'Edificio', 'Capacidad'),
            [80, 160, 200, 90],
            cargar, form,
            lambda *a: self.sistema.agregar_aula(*a),
            lambda *a: self.sistema.editar_aula(*a),
            lambda id: self.sistema.eliminar_aula(id),
        )

    # ===========================
    # HORARIOS
    # ===========================

    def _form_horario_win(self, h=None):
        """Ventana popup para agregar/editar horario con validación en tiempo real."""
        c = self.colors
        win = tk.Toplevel(self.root)
        win.title("Nuevo Horario" if not h else f"Editar Horario {h.id}")
        win.geometry("480x640")
        win.configure(bg=c['surface'])
        win.grab_set()
        win.resizable(False, True)

        # Título
        tk.Label(win, text="🕐 " + ("Nuevo Horario" if not h else f"Editar: {h.id}"),
                 bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 13, 'bold')).pack(pady=(15, 5))

        # Scrollable interior
        canvas = tk.Canvas(win, bg=c['surface'], highlightthickness=0)
        sb = ttk.Scrollbar(win, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        self.bind_scroll(canvas)

        f = tk.Frame(canvas, bg=c['surface'])
        win_id = canvas.create_window((0, 0), window=f, anchor='nw')
        f.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width - 4))
        f.columnconfigure(1, weight=1)

        mats  = self.sistema.get_materias_lista()  or ['(Sin materias)']
        docs  = self.sistema.get_docentes_lista()  or ['(Sin docentes)']
        aulas = self.sistema.get_aulas_lista()     or ['(Sin aulas)']
        carreras_opts = [f"{k} - {v}" for k, v in CARRERAS.items()]

        # ── Campos del formulario ──────────────────────────────────────────
        id_w  = self.campo_form(f, 0, "ID del Horario:",
                                valor=h.id if h else f"H{len(self.sistema.horarios)+1:04d}")
        mat_w = self.campo_form(f, 1, "Materia:", 'combo', mats)
        doc_w = self.campo_form(f, 2, "Docente:", 'combo', docs)

        # Separador visual
        sep1 = tk.Frame(f, bg=c['border'], height=1)
        sep1.grid(row=3, column=0, columnspan=2, sticky='ew', padx=8, pady=(8, 2))
        tk.Label(f, text="Grupo que recibirá la clase",
                 bg=c['surface'], fg=c['text_light'],
                 font=('Segoe UI', 8, 'italic')).grid(row=4, column=0, columnspan=2)

        sem_w = self.campo_form(f, 5, "Semestre:", 'combo', SEMESTRES)
        car_w = self.campo_form(f, 6, "Carrera:",  'combo', carreras_opts)
        grp_w = self.campo_form(f, 7, "Grupo:",    'combo', GRUPOS_LETRAS)

        prev_lbl = tk.Label(f, text="Código de grupo: —", bg=c['surface'],
                            fg=c['secondary'], font=('Segoe UI', 10, 'bold'))
        prev_lbl.grid(row=8, column=0, columnspan=2, pady=(2, 4))

        def upd_prev(*_):
            s = sem_w.get(); car = car_w.get(); g = grp_w.get()
            if s and car and g:
                cod = car.split(' - ')[0]
                prev_lbl.config(text=f"Código de grupo: {s}{cod}{g}", fg=c['success'])
            else:
                prev_lbl.config(text="Código de grupo: —", fg=c['text_light'])

        for w in [sem_w, car_w, grp_w]:
            w.bind('<<ComboboxSelected>>', upd_prev)

        sep2 = tk.Frame(f, bg=c['border'], height=1)
        sep2.grid(row=9, column=0, columnspan=2, sticky='ew', padx=8, pady=(4, 2))
        tk.Label(f, text="Horario y lugar",
                 bg=c['surface'], fg=c['text_light'],
                 font=('Segoe UI', 8, 'italic')).grid(row=10, column=0, columnspan=2)

        dia_w  = self.campo_form(f, 11, "Día:",         'combo', DIAS_SEMANA)
        hi_w   = self.campo_form(f, 12, "Hora Inicio:", 'combo', HORAS_DISPONIBLES)
        hf_w   = self.campo_form(f, 13, "Hora Fin:",    'combo', HORAS_DISPONIBLES)
        aula_w = self.campo_form(f, 14, "Aula:",        'combo', aulas)

        # ── Panel de advertencia en tiempo real ────────────────────────────
        aviso_frame = tk.Frame(f, bg='#FEF2F2', relief='solid', bd=1)
        aviso_frame.grid(row=15, column=0, columnspan=2, sticky='ew', padx=8, pady=4)
        aviso_frame.grid_remove()   # oculto por defecto
        aviso_icono = tk.Label(aviso_frame, text="🚫", bg='#FEF2F2',
                               font=('Segoe UI', 18))
        aviso_icono.pack(side='left', padx=(10, 4), pady=8)
        aviso_texto = tk.Label(aviso_frame, text='', bg='#FEF2F2', fg='#991B1B',
                               font=('Segoe UI', 9, 'bold'), justify='left',
                               wraplength=360, anchor='w')
        aviso_texto.pack(side='left', fill='x', expand=True, pady=8, padx=(0, 10))

        def _revisar_conflictos(*_):
            """Se llama cada vez que cambia día, hora inicio, hora fin, aula o docente."""
            dia  = dia_w.get()
            hi   = hi_w.get()
            hf   = hf_w.get()
            aula = aula_w.get()
            doc  = doc_w.get()

            # Necesita al menos día, ambas horas, aula y docente para validar
            if not all([dia, hi, hf, aula, doc]):
                aviso_frame.grid_remove()
                return

            # Primero verificar que hora fin > hora inicio
            if hi >= hf:
                aviso_texto.config(text="La hora de fin debe ser posterior a la hora de inicio.")
                aviso_frame.grid()
                return

            doc_id  = doc.split(' - ')[0]
            aula_id = aula.split(' - ')[0]
            conflictos = self.sistema.validar_cruce_horario(
                doc_id, aula_id, dia, hi, hf,
                excluir_id=h.id if h else None
            )

            if conflictos:
                # Construir mensaje legible
                lineas = []
                for conf in conflictos:
                    lineas.append(conf)
                aviso_texto.config(text="\n\n".join(lineas))
                aviso_frame.grid()
            else:
                aviso_frame.grid_remove()

        # Disparar revisión al cambiar cualquier campo relevante
        for w in [dia_w, hi_w, hf_w, aula_w, doc_w]:
            w.bind('<<ComboboxSelected>>', _revisar_conflictos)

        # ── Pre-llenar en modo edición ─────────────────────────────────────
        if h:
            id_w.config(state='disabled')
            for w2, val in [(mat_w, h.materia_id), (doc_w, h.docente_id),
                            (dia_w, h.dia), (hi_w, h.hora_inicio), (hf_w, h.hora_fin)]:
                for opt in w2.cget('values'):
                    if str(opt).startswith(str(val)):
                        w2.set(opt); break
            for opt in aulas:
                if opt.startswith(h.aula_id):
                    aula_w.set(opt); break
            sm, cc, grp_letra = self.sistema.parsear_grupo_completo(h.grado)
            if sm:
                sem_w.set(sm)
                for opt in carreras_opts:
                    if opt.startswith(cc):
                        car_w.set(opt); break
                grp_w.set(grp_letra or '')
            upd_prev()
            _revisar_conflictos()

        # ── Botón guardar ──────────────────────────────────────────────────
        result = [None]

        def guardar():
            id_  = id_w.get().strip()
            mat  = mat_w.get();  doc  = doc_w.get()
            dia  = dia_w.get();  hi   = hi_w.get()
            hf   = hf_w.get();  aula = aula_w.get()
            s    = sem_w.get(); car  = car_w.get(); g = grp_w.get()

            # 1) Campos obligatorios
            faltantes = [nombre for nombre, val in [
                ("ID", id_), ("Materia", mat), ("Docente", doc),
                ("Día", dia), ("Hora Inicio", hi), ("Hora Fin", hf),
                ("Aula", aula), ("Semestre", s), ("Carrera", car), ("Grupo", g)
            ] if not val]
            if faltantes:
                messagebox.showwarning(
                    "Campos incompletos",
                    "Completa los siguientes campos:\n• " + "\n• ".join(faltantes),
                    parent=win)
                return

            # 2) Hora válida
            if hi >= hf:
                messagebox.showwarning(
                    "Hora inválida",
                    "La hora de fin debe ser posterior a la hora de inicio.",
                    parent=win)
                return

            mat_id  = mat.split(' - ')[0]
            doc_id  = doc.split(' - ')[0]
            aula_id = aula.split(' - ')[0]
            car_cod = car.split(' - ')[0]
            grado   = self.sistema.construir_grupo_completo(s, car_cod, g)

            # 3) Verificar conflictos finales antes de guardar
            conflictos = self.sistema.validar_cruce_horario(
                doc_id, aula_id, dia, hi, hf,
                excluir_id=h.id if h else None
            )
            if conflictos:
                messagebox.showerror(
                    "🚫  Horario no disponible",
                    "No se puede guardar porque hay conflictos:\n\n" +
                    "\n\n".join(conflictos),
                    parent=win)
                return

            result[0] = (id_, mat_id, doc_id, grado, g, dia, hi, hf, aula_id)
            win.destroy()

        self.btn(f, "💾 Guardar Horario", guardar, color=c['secondary'],
                 padx=20, pady=9).grid(row=16, column=0, columnspan=2, pady=14)

        win.wait_window()
        return result[0]

    def mostrar_agregar_horario(self):
        datos = self._form_horario_win()
        if datos:
            ok, msg = self.sistema.agregar_horario(*datos)
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
            else:
                messagebox.showerror("❌ Error", msg)

    def mostrar_buscar_horarios(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🔍 Ver Horarios")
        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x')

        # Determinar filtro de grupos si es docente
        grados_docente = None
        if self.sistema.es_docente():
            uid = self.sistema.usuario_actual.id
            grados_docente = self.sistema.get_grados_del_docente(uid)
            grupos_str = ", ".join(sorted(grados_docente)) if grados_docente else "ninguno"
            tk.Label(top, text=f"📌 Mostrando horarios de tus grupos: {grupos_str}",
                     bg=c['surface'], fg=c['secondary'],
                     font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=12, pady=(4, 0))

        sv, se = self.busqueda_bar(top, label="🔍 Filtrar:")

        # Botones de acción
        action_frame = tk.Frame(top, bg=c['surface'])
        action_frame.pack(fill='x', padx=10, pady=5)
        
        if self.sistema.es_admin():
            self.btn(action_frame, "✏️ Editar Seleccionado", 
                    lambda: self._editar_horario_seleccionado(tree), 
                    color=c['warning'], padx=10, pady=5).pack(side='left', padx=5)
            self.btn(action_frame, "🗑️ Eliminar Seleccionado",
                    lambda: self._eliminar_horario_seleccionado(tree, cargar),
                    color=c['danger'], padx=10, pady=5).pack(side='left', padx=5)

        modo_var = tk.StringVar(value='grupo')
        mf = tk.Frame(top, bg=c['surface'])
        mf.pack(fill='x', padx=10)
        tk.Label(mf, text="Buscar por:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10)).pack(side='left')
        for txt, val in [("Grupo", 'grupo'), ("Docente", 'docente'), ("Aula", 'aula')]:
            tk.Radiobutton(mf, text=txt, variable=modo_var, value=val,
                           bg=c['surface'], fg=c['text'], selectcolor=c['surface'],
                           font=('Segoe UI', 10)).pack(side='left', padx=8)

        cols = ('ID', 'Materia', 'Docente', 'Grado', 'Grupo', 'Día', 'Inicio', 'Fin', 'Aula')
        tree = self.tabla(self.right_panel, cols,
                          [90, 180, 180, 75, 55, 95, 65, 65, 90], height=17)
        cnt = tk.Label(self.right_panel, text="", bg=c['surface'], fg=c['text_light'],
                       font=('Segoe UI', 9))
        cnt.pack()

        def cargar(*a):
            t = sv.get().strip().lower()
            modo = modo_var.get()
            filas = []
            dias_ord = {d: i for i, d in enumerate(DIAS_SEMANA)}
            for h in self.sistema.horarios.values():
                # Filtrar por grupos del docente si aplica
                if grados_docente is not None and h.grado not in grados_docente:
                    continue
                mat = self.sistema.materias.get(h.materia_id)
                doc = self.sistema.docentes.get(h.docente_id)
                aula = self.sistema.aulas.get(h.aula_id)
                mat_n = mat.nombre if mat else h.materia_id
                doc_n = doc.get_nombre_completo() if doc else h.docente_id
                aula_n = str(aula) if aula else h.aula_id
                if modo == 'grupo':
                    match = not t or t in h.grado.lower() or t in h.grupo.lower()
                elif modo == 'docente':
                    match = not t or t in h.docente_id.lower() or t in doc_n.lower()
                else:
                    match = not t or t in h.aula_id.lower() or t in aula_n.lower()
                if match:
                    filas.append((h.id, mat_n, doc_n, h.grado, h.grupo,
                                  h.dia, h.hora_inicio, h.hora_fin, aula_n))
            filas.sort(key=lambda x: (dias_ord.get(x[5], 99), x[6]))
            self.insertar(tree, filas)
            cnt.config(text=f"Total: {len(filas)} horario(s)")

        sv.trace('w', cargar)
        modo_var.trace('w', cargar)
        cargar()
        se.focus()

    def _editar_horario_seleccionado(self, tree):
        """Abre el formulario de edición para el horario seleccionado."""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Por favor seleccione un horario de la lista")
            return
        horario_id = tree.item(sel[0])['values'][0]
        h = self.sistema.horarios.get(str(horario_id))
        if h:
            datos = self._form_horario_win(h)
            if datos:
                _, mat_id, doc_id, grado, grupo, dia, hi, hf, aula_id = datos
                ok, msg = self.sistema.editar_horario(h.id, mat_id, doc_id, grado, grupo, dia, hi, hf, aula_id)
                if ok:
                    messagebox.showinfo("✅ Éxito", msg)
                    cargar()
                else:
                    messagebox.showerror("❌ Error", msg)

    def _eliminar_horario_seleccionado(self, tree, cargar_fn):
        """Elimina el horario seleccionado tras confirmación del usuario."""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Por favor seleccione un horario de la lista")
            return
        valores = tree.item(sel[0])['values']
        horario_id = valores[0]
        materia   = valores[1]
        docente   = valores[2]
        dia       = valores[5]
        inicio    = valores[6]
        fin       = valores[7]

        confirmado = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Está seguro de eliminar el siguiente horario?\n\n"
            f"  Materia : {materia}\n"
            f"  Docente : {docente}\n"
            f"  Día     : {dia}  {inicio} – {fin}\n\n"
            "Esta acción no se puede deshacer."
        )
        if not confirmado:
            return

        ok, msg = self.sistema.eliminar_horario(str(horario_id))
        if ok:
            messagebox.showinfo("✅ Eliminado", msg)
            cargar_fn()
        else:
            messagebox.showerror("❌ Error", msg)

    def mostrar_mi_horario(self):
        """Para estudiantes: mostrar solo los horarios de su grupo."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🕐 Mi Horario")
        sf = self.scroll_frame(self.right_panel)
        
        uid = self.sistema.usuario_actual.id
        al = self.sistema.alumnos.get(uid)
        
        if not al:
            self.info_box(sf, "Tu cuenta de estudiante no está asociada a un alumno registrado.", 'error')
            return
        
        grado = al.grado
        grupo = al.grupo
        sm, cc, grp = self.sistema.parsear_grupo_completo(grado)
        
        t = (f"Mi Grupo: {grado} | {sm}° Semestre — {self.sistema.get_nombre_carrera(cc)} — Grupo {grp}"
             if sm else f"Grupo: {grado} — Grupo: {grupo}")
        
        tk.Label(sf, text=t, bg=c['surface'], fg=c['secondary'],
                 font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        horarios = sorted(self.sistema.obtener_horarios_por_grupo(grado, grupo),
                         key=lambda h: (DIAS_SEMANA.index(h.dia), h.hora_inicio))
        
        if not horarios:
            tk.Label(sf, text="No hay horarios asignados para tu grupo.", bg=c['surface'],
                     fg=c['text_light'], font=('Segoe UI', 10)).pack(pady=20)
            return
        
        cols = ('Materia', 'Docente', 'Día', 'Inicio', 'Fin', 'Aula')
        tree = self.tabla(sf, cols, [200, 200, 100, 80, 80, 150], height=14)
        
        filas = []
        for h in horarios:
            mat = self.sistema.materias.get(h.materia_id)
            doc = self.sistema.docentes.get(h.docente_id)
            aula = self.sistema.aulas.get(h.aula_id)
            mat_n = mat.nombre if mat else h.materia_id
            doc_n = doc.get_nombre_completo() if doc else h.docente_id
            aula_n = str(aula) if aula else h.aula_id
            filas.append((mat_n, doc_n, h.dia, h.hora_inicio, h.hora_fin, aula_n))
        
        self.insertar(tree, filas)

    # ===========================
    # CALIFICACIONES
    # ===========================

    def mostrar_registrar_calificacion(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("✏️ Registrar Calificación")
        sf = self.scroll_frame(self.right_panel)

        # Determinar filtro de grupos si es docente
        grados_docente = None
        docente_uid = None
        if self.sistema.es_docente():
            docente_uid = self.sistema.usuario_actual.id
            grados_docente = self.sistema.get_grados_del_docente(docente_uid)
            if grados_docente:
                grupos_str = ", ".join(sorted(grados_docente))
                tk.Label(sf, text=f"📌 Mostrando solo alumnos de tus grupos: {grupos_str}",
                         bg=c['surface'], fg=c['secondary'],
                         font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=12, pady=(4, 0))

        # ── Barra de búsqueda ──────────────────────────────────────────────
        sv, se = self.busqueda_bar(sf, label="🔍 Buscar alumno:", placeholder="(matrícula, nombre, grupo o grado)")

        # ── Radio buttons criterio ─────────────────────────────────────────
        criterio_var = tk.StringVar(value='nombre')
        rf = tk.Frame(sf, bg=c['surface'])
        rf.pack(fill='x', padx=10, pady=(0, 4))
        tk.Label(rf, text="Buscar por:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 9)).pack(side='left', padx=5)
        for txt, val in [("Nombre", 'nombre'), ("Matrícula", 'matricula'), ("Grupo/Grado", 'grupo')]:
            tk.Radiobutton(rf, text=txt, variable=criterio_var, value=val,
                           bg=c['surface'], fg=c['text'], selectcolor=c['surface'],
                           font=('Segoe UI', 9)).pack(side='left', padx=6)

        # ── Tabla de alumnos (con columnas Materia y Docente para rol Docente) ──
        if docente_uid:
            cols = ('Matrícula', 'Nombre', 'Grado', 'Carrera', 'Grupo', 'Materia(s) que imparte', 'Docente')
            tree_al = self.tabla(sf, cols, [110, 175, 65, 150, 55, 190, 155], height=7)
        else:
            cols = ('Matrícula', 'Nombre', 'Grado', 'Carrera', 'Grupo')
            tree_al = self.tabla(sf, cols, [110, 210, 65, 190, 55], height=7)
        sel_al  = [None]
        sel_lbl = tk.Label(sf, text="Seleccione un alumno", bg=c['surface'],
                           fg=c['text_light'], font=('Segoe UI', 9))
        sel_lbl.pack()

        def cargar_alumnos(*a):
            t    = sv.get().strip().lower()
            crit = criterio_var.get()
            alumnos = list(self.sistema.alumnos.values())
            alumnos = [al for al in alumnos if al.activo]
            if grados_docente is not None:
                alumnos = [al for al in alumnos if al.grado in grados_docente]
            if t:
                if crit == 'matricula':
                    alumnos = [al for al in alumnos if t in al.matricula.lower()]
                elif crit == 'grupo':
                    alumnos = [al for al in alumnos if t in al.grado.lower() or t in al.grupo.lower()]
                else:
                    alumnos = [al for al in alumnos if t in al.nombre.lower() or
                               t in al.apellido.lower() or t in al.get_nombre_completo().lower()]
            if crit == 'grupo':
                alumnos.sort(key=lambda x: (x.grado, x.apellido))
            elif crit == 'matricula':
                alumnos.sort(key=lambda x: x.matricula)
            else:
                alumnos.sort(key=lambda x: x.apellido)
            filas = []
            for al in alumnos:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
                if docente_uid:
                    # Materias que imparte el docente en el grado de este alumno
                    mats_ids = set(h.materia_id for h in self.sistema.horarios.values()
                                   if h.docente_id == docente_uid and h.grado == al.grado)
                    nombres_mat = sorted(self.sistema.materias[mid].nombre
                                         for mid in mats_ids if mid in self.sistema.materias)
                    materias_str = ", ".join(nombres_mat) if nombres_mat else "—"
                    doc = self.sistema.docentes.get(docente_uid)
                    doc_nombre = doc.get_nombre_completo() if doc else docente_uid
                    filas.append((al.matricula, al.get_nombre_completo(), al.grado, cn, al.grupo,
                                  materias_str, doc_nombre))
                else:
                    filas.append((al.matricula, al.get_nombre_completo(), al.grado, cn, al.grupo))
            self.insertar(tree_al, filas)

        # ── Al seleccionar alumno, actualiza materias disponibles ──────────
        def on_sel_al(e):
            s = tree_al.selection()
            if not s:
                return
            v = tree_al.item(s[0])['values']
            sel_al[0]   = v[0]   # matrícula
            grado_al    = v[2]   # grado completo ej '3SA'
            sel_lbl.config(text=f"✓ {v[1]} ({v[0]}) — Grado: {grado_al}", fg=c['success'])
            # Actualizar lista de materias según docente+grado o solo grado
            if docente_uid:
                nuevas_mats = self.sistema.get_materias_docente_grado(docente_uid, grado_al)
            else:
                # Admin: todas las materias que correspondan al grado
                nuevas_mats = [f"{m.id} - {m.nombre}"
                               for m in sorted(self.sistema.materias.values(), key=lambda x: x.nombre)
                               if not m.grado or m.grado == grado_al] or self.sistema.get_materias_lista() or ['(Sin materias)']
            mat_w['values'] = nuevas_mats
            if nuevas_mats:
                mat_w.current(0)

        tree_al.bind('<<TreeviewSelect>>', on_sel_al)
        sv.trace('w', cargar_alumnos)
        criterio_var.trace('w', cargar_alumnos)

        tk.Frame(sf, bg=c['border'], height=1).pack(fill='x', padx=10, pady=5)

        form = tk.Frame(sf, bg=c['surface'])
        form.pack(padx=20, pady=8, fill='x')
        form.columnconfigure(1, weight=1)

        # Materias: inicialmente todas (se actualizan al seleccionar alumno)
        mats_iniciales = self.sistema.get_materias_lista() or ['(Sin materias)']
        mat_w = self.campo_form(form, 0, "Materia:", 'combo', mats_iniciales)
        sem_w = self.campo_form(form, 1, "Semestre/Periodo (ej: 2024-1):", valor='')
        cal_var = tk.DoubleVar(value=70.0)
        tk.Label(form, text="Calificación (0-100):", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold'), anchor='w').grid(row=2, column=0, sticky='w', pady=5, padx=5)
        tk.Spinbox(form, from_=0, to=100, increment=0.5, textvariable=cal_var,
                   font=('Segoe UI', 10), relief='solid', bd=1, width=10,
                   bg=c['entry_bg'], fg=c['entry_fg']).grid(row=2, column=1, pady=5, padx=5, sticky='w')

        def guardar():
            if not sel_al[0]:
                messagebox.showwarning("Sin alumno", "Seleccione un alumno")
                return
            mat = mat_w.get()
            sem = sem_w.get().strip()
            if not mat or not sem or mat.startswith('('):
                messagebox.showwarning("Campos vacíos", "Complete todos los campos")
                return
            try:
                cal = float(cal_var.get())
                if not (0 <= cal <= 100):
                    raise ValueError()
            except:
                messagebox.showerror("Error", "Calificación debe ser entre 0 y 100")
                return
            mat_id = mat.split(' - ')[0]
            ok, msg = self.sistema.registrar_calificacion(sel_al[0], mat_id, sem, cal)
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
            else:
                messagebox.showerror("❌ Error", msg)

        self.btn(form, "💾 Registrar Calificación", guardar,
                 color=c['secondary'], padx=22, pady=9).grid(row=3, column=0, columnspan=2, pady=12)
        cargar_alumnos()
        se.focus()

    def mostrar_ver_calificaciones(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🔍 Ver Calificaciones")

        # Determinar filtro de grupos si es docente
        grados_docente = None
        if self.sistema.es_docente():
            uid = self.sistema.usuario_actual.id
            grados_docente = self.sistema.get_grados_del_docente(uid)

        # Frame superior con filtros
        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x', padx=10, pady=5)

        if grados_docente is not None:
            grupos_str = ", ".join(sorted(grados_docente)) if grados_docente else "ninguno"
            tk.Label(top, text=f"📌 Mostrando solo alumnos de tus grupos: {grupos_str}",
                     bg=c['surface'], fg=c['secondary'],
                     font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=5, pady=(2, 0))

        # Botón de edición de calificaciones
        action_frame = tk.Frame(top, bg=c['surface'])
        action_frame.pack(fill='x', pady=5)
        
        if self.sistema.es_admin() or self.sistema.es_docente():
            self.btn(action_frame, "✏️ Editar Calificación Seleccionada", 
                    lambda: self._editar_calificacion_seleccionada(tree_calif, tree_alumnos), 
                    color=c['warning'], padx=10, pady=5).pack(side='left', padx=5)
        
        # Selector de tipo de búsqueda
        tipo_busqueda = tk.StringVar(value='nombre')
        
        filtro_frame = tk.Frame(top, bg=c['surface'])
        filtro_frame.pack(fill='x', pady=5)
        
        tk.Label(filtro_frame, text="Buscar por:", bg=c['surface'], fg=c['text'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        
        for txt, val in [("Nombre/Apellido", 'nombre'), ("Matrícula", 'matricula'), ("Grupo", 'grupo')]:
            tk.Radiobutton(filtro_frame, text=txt, variable=tipo_busqueda, value=val,
                          bg=c['surface'], fg=c['text'], selectcolor=c['surface'],
                          font=('Segoe UI', 10)).pack(side='left', padx=10)
        
        # Barra de búsqueda
        sv, se = self.busqueda_bar(top, label="🔍 Buscar:", placeholder="Ingrese texto de búsqueda")
        
        # Lista de grupos disponibles — restringida para docentes
        if grados_docente is not None:
            grupos_disponibles = sorted(grados_docente)
        else:
            grupos_disponibles = sorted(set([a.grado for a in self.sistema.alumnos.values() if a.activo]))
        
        # Combobox para selección de grupo (inicialmente oculto)
        grupo_frame = tk.Frame(top, bg=c['surface'])
        grupo_frame.pack(fill='x', pady=5)
        grupo_frame.pack_forget()  # Oculto inicialmente
        
        tk.Label(grupo_frame, text="Seleccionar Grupo:", bg=c['surface'], fg=c['text'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        grupo_var = tk.StringVar()
        grupo_combo = ttk.Combobox(grupo_frame, textvariable=grupo_var, values=grupos_disponibles,
                                   state='readonly', width=20, font=('Segoe UI', 10))
        grupo_combo.pack(side='left', padx=5)
        
        # Función para mostrar/ocultar el combo de grupos
        def toggle_grupo_selector(*args):
            if tipo_busqueda.get() == 'grupo':
                grupo_frame.pack(fill='x', pady=5)
                se.pack_forget()  # Ocultar entry de búsqueda
                sv.set('')  # Limpiar búsqueda
            else:
                grupo_frame.pack_forget()
                se.pack(fill='x', padx=10, pady=5)  # Mostrar entry de búsqueda
        
        tipo_busqueda.trace('w', toggle_grupo_selector)
        
        # Árbol de alumnos
        cols_alumnos = ('Matrícula', 'Nombre', 'Grupo', 'Promedio')
        tree_alumnos = self.tabla(self.right_panel, cols_alumnos, [120, 250, 100, 100], height=8)
        
        # Árbol de calificaciones del alumno seleccionado
        tk.Label(self.right_panel, text="📊 Calificaciones del Alumno Seleccionado",
                bg=c['surface'], fg=c['text'], font=('Segoe UI', 11, 'bold'),
                anchor='w', padx=10).pack(fill='x', pady=(10, 0))
        
        cols_calif = ('ID', 'Materia', 'Semestre', 'Calificación', 'Estado', 'Fecha')
        tree_calif = self.tabla(self.right_panel, cols_calif, [80, 250, 120, 100, 100, 150], height=12)
        
        # Labels de información
        info_label = tk.Label(self.right_panel, text="", bg=c['surface'], fg=c['text_light'],
                             font=('Segoe UI', 9))
        info_label.pack()
        
        # Variable para almacenar el alumno seleccionado actualmente
        alumno_seleccionado = [None]
        
        def cargar_alumnos(*args):
            """Carga los alumnos según el filtro seleccionado"""
            termino = sv.get().strip().lower()
            tipo = tipo_busqueda.get()
            
            alumnos_filtrados = []
            
            if tipo == 'grupo':
                grupo_sel = grupo_var.get()
                if grupo_sel:
                    alumnos_filtrados = [a for a in self.sistema.alumnos.values() 
                                        if a.activo and a.grado == grupo_sel]
            elif tipo == 'matricula':
                alumnos_filtrados = [a for a in self.sistema.alumnos.values() 
                                   if a.activo and termino in a.matricula.lower()]
            else:  # nombre/apellido
                alumnos_filtrados = [a for a in self.sistema.alumnos.values() 
                                   if a.activo and (termino in a.nombre.lower() or 
                                                   termino in a.apellido.lower() or
                                                   termino in a.get_nombre_completo().lower())]
            
            # Filtrar por grupos del docente si aplica
            if grados_docente is not None:
                alumnos_filtrados = [a for a in alumnos_filtrados if a.grado in grados_docente]
            
            # Ordenar y mostrar en el árbol
            alumnos_filtrados.sort(key=lambda x: x.apellido)
            filas = []
            for al in alumnos_filtrados:
                prom = self.sistema.obtener_promedio_alumno(al.matricula)
                filas.append((al.matricula, al.get_nombre_completo(), al.grado, f"{prom:.2f}"))
            
            self.insertar(tree_alumnos, filas)
            info_label.config(text=f"Total de alumnos encontrados: {len(alumnos_filtrados)}")
        
        def on_alumno_seleccionado(event):
            """Cuando se selecciona un alumno, mostrar sus calificaciones"""
            seleccion = tree_alumnos.selection()
            if not seleccion:
                return
            
            valores = tree_alumnos.item(seleccion[0])['values']
            matricula = valores[0]
            alumno_seleccionado[0] = matricula
            
            # Obtener calificaciones del alumno
            calificaciones = self.sistema.obtener_calificaciones_alumno(matricula)
            
            filas = []
            for cal in sorted(calificaciones, key=lambda x: (x.semestre, x.materia_id)):
                materia = self.sistema.materias.get(cal.materia_id)
                nombre_materia = materia.nombre if materia else cal.materia_id
                estado = "✓ Aprobado" if cal.calificacion >= 70 else "✗ Reprobado"
                filas.append((
                    cal.id,
                    nombre_materia,
                    cal.semestre,
                    f"{cal.calificacion:.1f}",
                    estado,
                    cal.fecha_registro
                ))
            
            self.insertar(tree_calif, filas)
            
            # Actualizar info
            prom = self.sistema.obtener_promedio_alumno(matricula)
            aprobadas = sum(1 for c in calificaciones if c.calificacion >= 70)
            info_label.config(
                text=f"Alumno: {valores[1]} | Promedio: {prom:.2f} | "
                     f"Aprobadas: {aprobadas} | Reprobadas: {len(calificaciones) - aprobadas}"
            )
        
        # Vincular eventos
        tree_alumnos.bind('<<TreeviewSelect>>', on_alumno_seleccionado)
        sv.trace('w', cargar_alumnos)
        grupo_var.trace('w', cargar_alumnos)
        
        # Carga inicial
        cargar_alumnos()
        se.focus()

    def _editar_calificacion_seleccionada(self, tree_calif, tree_alumnos):
        """Abre el diálogo de edición para la calificación seleccionada."""
        sel_calif = tree_calif.selection()
        if not sel_calif:
            messagebox.showwarning("Sin selección", "Por favor seleccione una calificación de la lista")
            return
        
        # Obtener datos de la calificación seleccionada
        valores = tree_calif.item(sel_calif[0])['values']
        cal_id = valores[0]
        materia = valores[1]
        semestre = valores[2]
        cal_actual = float(valores[3]) if valores[3] else 70.0
        
        # Verificar que el usuario tenga permisos
        if not (self.sistema.es_admin() or self.sistema.es_docente()):
            messagebox.showerror("Permiso denegado", "Solo administradores y docentes pueden editar calificaciones")
            return
        
        # Diálogo de edición
        win = tk.Toplevel(self.root)
        win.title("Editar Calificación")
        win.geometry("400x250")
        win.configure(bg=self.c('surface'))
        win.grab_set()
        
        tk.Label(win, text="✏️ Editar Calificación", bg=self.c('surface'), fg=self.c('text'),
                 font=('Segoe UI', 12, 'bold')).pack(pady=(15, 10))
        
        f = tk.Frame(win, bg=self.c('surface'))
        f.pack(padx=20, fill='x')
        
        tk.Label(f, text=f"Materia: {materia}", bg=self.c('surface'), fg=self.c('text'),
                 font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        tk.Label(f, text=f"Semestre: {semestre}", bg=self.c('surface'), fg=self.c('text'),
                 font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        
        tk.Label(f, text="Nueva Calificación (0-100):", bg=self.c('surface'), fg=self.c('text'),
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(8, 2))
        
        cal_var = tk.DoubleVar(value=cal_actual)
        spin = tk.Spinbox(f, from_=0, to=100, increment=0.5, textvariable=cal_var,
                         font=('Segoe UI', 10), relief='solid', bd=1, width=10,
                         bg=self.c('entry_bg'), fg=self.c('entry_fg'))
        spin.pack(anchor='w', pady=2)
        
        def guardar():
            try:
                nueva = float(cal_var.get())
                if not (0 <= nueva <= 100):
                    raise ValueError()
            except:
                messagebox.showerror("Error", "Calificación debe ser entre 0 y 100", parent=win)
                return
            
            ok, msg = self.sistema.editar_calificacion(cal_id, nueva)
            if ok:
                messagebox.showinfo("✅ Éxito", msg, parent=win)
                win.destroy()
                # Recargar las calificaciones del alumno seleccionado
                if tree_alumnos.selection():
                    on_alumno_seleccionado(None)  # Esto recargará las calificaciones
            else:
                messagebox.showerror("❌ Error", msg, parent=win)
        
        bf = tk.Frame(win, bg=self.c('surface'))
        bf.pack(pady=15)
        self.btn(bf, "💾 Guardar", guardar, color=self.c('warning'),
                 padx=20, pady=6).pack()

    def mostrar_mis_calificaciones(self):
        """Para estudiantes: mostrar solo sus calificaciones con botón de boletín."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("🔍 Mis Calificaciones")
        sf = self.scroll_frame(self.right_panel)
        
        uid = self.sistema.usuario_actual.id
        al = self.sistema.alumnos.get(uid)
        
        if not al:
            self.info_box(sf, "Tu cuenta de estudiante no está asociada a un alumno registrado.", 'error')
            return
        
        sm, cc, grp = self.sistema.parsear_grupo_completo(al.grado)
        cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
        
        # Frame para la información del alumno y botón de boletín
        info_frame = tk.Frame(sf, bg=c['surface'])
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(info_frame, text=f"Alumno: {al.get_nombre_completo()}", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        tk.Label(info_frame, text=f"Grupo: {al.grado} | Carrera: {cn}", bg=c['surface'], fg=c['text_light'],
                 font=('Segoe UI', 10)).pack(anchor='w')
        
        # Botón de boletín
        self.btn(info_frame, "📄 Ver Mi Boletín", 
                lambda: self.mostrar_mi_boletin(), 
                color=c['secondary'], padx=15, pady=5).pack(anchor='e', pady=5)
        
        calificaciones = sorted(self.sistema.obtener_calificaciones_alumno(uid),
                               key=lambda x: (x.semestre, x.materia_id))
        
        if not calificaciones:
            tk.Label(sf, text="No tienes calificaciones registradas.", bg=c['surface'],
                     fg=c['text_light'], font=('Segoe UI', 11, 'italic')).pack(pady=30)
            return
        
        cols = ('Materia', 'Semestre', 'Calificación', 'Estado', 'Fecha')
        tree = self.tabla(sf, cols, [250, 120, 100, 110, 150], height=14)
        
        filas = []
        for cal in calificaciones:
            materia = self.sistema.materias.get(cal.materia_id)
            nombre_materia = materia.nombre if materia else cal.materia_id
            estado = "✓ Aprobado" if cal.calificacion >= 70 else "✗ Reprobado"
            filas.append((nombre_materia, cal.semestre, f"{cal.calificacion:.1f}", estado, cal.fecha_registro))
        
        self.insertar(tree, filas)
        
        prom = self.sistema.obtener_promedio_alumno(uid)
        aprobadas = sum(1 for c in calificaciones if c.calificacion >= 70)
        
        res = tk.Frame(sf, bg=c['surface'])
        res.pack(fill='x', padx=10, pady=6)
        for txt, col in [
            (f"📊 Promedio: {prom:.2f}", c['success'] if prom >= 70 else c['danger']),
            (f"✓ Aprobadas: {aprobadas}", c['success']),
            (f"✗ Reprobadas: {len(calificaciones)-aprobadas}", c['danger'] if len(calificaciones)-aprobadas else c['text_light']),
            (f"📚 Total: {len(calificaciones)}", c['info']),
        ]:
            tk.Label(res, text=txt, bg=c['surface'], fg=col,
                     font=('Segoe UI', 11, 'bold')).pack(side='left', padx=18)

    def mostrar_mi_boletin(self):
        """Para estudiantes: mostrar solo su boletín."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("📄 Mi Boletín de Calificaciones")
        
        uid = self.sistema.usuario_actual.id
        al = self.sistema.alumnos.get(uid)
        
        if not al:
            self.info_box(self.right_panel, "Tu cuenta de estudiante no está asociada a un alumno registrado.", 'error')
            return
        
        sf = self.scroll_frame(self.right_panel)

        sm, cc, grp = self.sistema.parsear_grupo_completo(al.grado)
        cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado

        hdr = tk.Frame(sf, bg=c['primary'])
        hdr.pack(fill='x', padx=10, pady=6)
        tk.Label(hdr, text=f"👤  {al.get_nombre_completo()}",
                 bg=c['primary'], fg='white', font=('Segoe UI', 13, 'bold'),
                 padx=12, pady=6).pack(anchor='w')
        datos = [("🎫 Matrícula", al.matricula), ("📅 Semestre", f"{sm}°" if sm else '?'),
                 ("🎓 Carrera", cn), ("🏫 Grupo", grp or al.grupo),
                 ("📌 Estado", "Activo ✓" if al.activo else "Dado de baja ⚠")]
        df = tk.Frame(hdr, bg=c['primary'])
        df.pack(fill='x', padx=12, pady=(0, 8))
        for lbl_t, val_t in datos:
            blk = tk.Frame(df, bg=c['primary'])
            blk.pack(side='left', padx=14)
            tk.Label(blk, text=lbl_t, bg=c['primary'], fg='#93C5FD', font=('Segoe UI', 8)).pack(anchor='w')
            tk.Label(blk, text=val_t, bg=c['primary'], fg='white',
                     font=('Segoe UI', 10, 'bold')).pack(anchor='w')

        cals = self.sistema.obtener_calificaciones_alumno(al.matricula)
        if not cals:
            tk.Label(sf, text="Sin calificaciones registradas.", bg=c['surface'],
                     fg=c['text_light'], font=('Segoe UI', 11, 'italic')).pack(pady=25)
            return

        cols2 = ('Materia', 'Semestre', 'Calificación', 'Estado', 'Fecha Registro')
        tbl = tk.Frame(sf, bg=c['surface'])
        tbl.pack(fill='both', expand=True, padx=10, pady=5)
        sby2 = ttk.Scrollbar(tbl)
        sby2.pack(side='right', fill='y')
        t2 = ttk.Treeview(tbl, columns=cols2, show='headings',
                           yscrollcommand=sby2.set, height=min(len(cals), 15))
        sby2.config(command=t2.yview)
        for col, w in zip(cols2, [240, 120, 110, 110, 160]):
            t2.heading(col, text=col)
            t2.column(col, width=w)
        t2.pack(fill='both', expand=True)
        t2.tag_configure('apr', background='#D1FAE5', foreground='#065F46')
        t2.tag_configure('rep', background='#FEE2E2', foreground='#991B1B')
        for i, cal in enumerate(sorted(cals, key=lambda x: (x.semestre, x.materia_id))):
            mat = self.sistema.materias.get(cal.materia_id)
            mn = mat.nombre if mat else cal.materia_id
            apr = cal.calificacion >= 70
            t2.insert('', 'end',
                       values=(mn, cal.semestre, f"{cal.calificacion:.1f}",
                               "✓ Aprobado" if apr else "✗ Reprobado", cal.fecha_registro),
                       tags=('apr' if apr else 'rep',))

        prom = self.sistema.obtener_promedio_alumno(al.matricula)
        aprs = sum(1 for c2 in cals if c2.calificacion >= 70)
        res = tk.Frame(sf, bg=c['surface'])
        res.pack(fill='x', padx=10, pady=6)
        for txt, col in [
            (f"📊 Promedio: {prom:.2f}", c['success'] if prom >= 70 else c['danger']),
            (f"✓ Aprobadas: {aprs}", c['success']),
            (f"✗ Reprobadas: {len(cals)-aprs}", c['danger'] if len(cals)-aprs else c['text_light']),
            (f"📚 Total: {len(cals)}", c['info']),
        ]:
            tk.Label(res, text=txt, bg=c['surface'], fg=col,
                     font=('Segoe UI', 11, 'bold')).pack(side='left', padx=18)

        # Botón para volver a mis calificaciones
        self.btn(sf, "🔙 Volver a Mis Calificaciones", self.mostrar_mis_calificaciones,
                 color=c['secondary'], padx=20, pady=8).pack(pady=10)

    def mostrar_boletin_alumno(self):
        """Para administración y docentes: buscar y ver boletín de cualquier alumno."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("📄 Boletín de Calificaciones")
        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x')

        # Determinar filtro de grupos si es docente
        grados_docente = None
        if self.sistema.es_docente():
            uid = self.sistema.usuario_actual.id
            grados_docente = self.sistema.get_grados_del_docente(uid)
            grupos_str = ", ".join(sorted(grados_docente)) if grados_docente else "ninguno"
            tk.Label(top, text=f"📌 Mostrando solo alumnos de tus grupos: {grupos_str}",
                     bg=c['surface'], fg=c['secondary'],
                     font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=12, pady=(4, 2))

        self.info_box(top, "Busque y seleccione un alumno para ver su boletín completo.\nPuede filtrar por nombre/matrícula o seleccionar directamente un grupo.", 'info')

        # ── Filtro por grupo ───────────────────────────────────────────────
        grupo_bar = tk.Frame(top, bg=c['surface'])
        grupo_bar.pack(fill='x', padx=10, pady=(2, 0))
        tk.Label(grupo_bar, text="🏫 Filtrar por Grupo:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        if grados_docente is not None:
            grupos_opciones = ["(Todos mis grupos)"] + sorted(grados_docente)
        else:
            grupos_opciones = ["(Todos los grupos)"] + sorted(
                set(al.grado for al in self.sistema.alumnos.values() if al.activo))
        grupo_filtro_var = tk.StringVar(value=grupos_opciones[0])
        grupo_filtro_cb = ttk.Combobox(grupo_bar, textvariable=grupo_filtro_var,
                                        values=grupos_opciones, state='readonly',
                                        width=25, font=('Segoe UI', 10))
        grupo_filtro_cb.pack(side='left', padx=5)

        sv, se = self.busqueda_bar(top, label="🔍 Buscar alumno:")

        cols = ('Matrícula', 'Nombre', 'Carrera', 'Semestre', 'Grupo')
        tree_al = self.tabla(top, cols, [110, 230, 200, 90, 60], height=6)
        sel_al = [None]

        def cargar_al(*a):
            alumnos = sorted(self.sistema.buscar_alumnos(sv.get(), False), key=lambda x: x.apellido)
            # Filtrar por grupos del docente si aplica
            if grados_docente is not None:
                alumnos = [al for al in alumnos if al.grado in grados_docente]
            # Filtrar por grupo seleccionado en el combobox
            grupo_sel = grupo_filtro_var.get()
            if grupo_sel and not grupo_sel.startswith("("):
                alumnos = [al for al in alumnos if al.grado == grupo_sel]
            filas = []
            for al in alumnos:
                sm, cc, _ = self.sistema.parsear_grupo_completo(al.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado
                filas.append((al.matricula, al.get_nombre_completo(), cn,
                               f"{sm}°" if sm else al.grado, al.grupo))
            self.insertar(tree_al, filas)

        def on_sel(e):
            s = tree_al.selection()
            if s:
                sel_al[0] = tree_al.item(s[0])['values'][0]

        tree_al.bind('<<TreeviewSelect>>', on_sel)
        tree_al.bind('<Double-1>', lambda e: ver_boletin())
        sv.trace('w', cargar_al)
        grupo_filtro_var.trace('w', cargar_al)

        resultado_frame = [None]

        def ver_boletin():
            if not sel_al[0]:
                messagebox.showwarning("Sin selección", "Seleccione un alumno")
                return
            al = self.sistema.alumnos.get(sel_al[0])
            if not al:
                return
            if resultado_frame[0]:
                resultado_frame[0].destroy()
            rf = self.scroll_frame(self.right_panel)
            resultado_frame[0] = rf.master

            sm, cc, grp = self.sistema.parsear_grupo_completo(al.grado)
            cn = self.sistema.get_nombre_carrera(cc) if sm else al.grado

            hdr = tk.Frame(rf, bg=c['primary'])
            hdr.pack(fill='x', padx=10, pady=6)
            tk.Label(hdr, text=f"👤  {al.get_nombre_completo()}",
                     bg=c['primary'], fg='white', font=('Segoe UI', 13, 'bold'),
                     padx=12, pady=6).pack(anchor='w')
            datos = [("🎫 Matrícula", al.matricula), ("📅 Semestre", f"{sm}°" if sm else '?'),
                     ("🎓 Carrera", cn), ("🏫 Grupo", grp or al.grupo),
                     ("📌 Estado", "Activo ✓" if al.activo else "Dado de baja ⚠")]
            df = tk.Frame(hdr, bg=c['primary'])
            df.pack(fill='x', padx=12, pady=(0, 8))
            for lbl_t, val_t in datos:
                blk = tk.Frame(df, bg=c['primary'])
                blk.pack(side='left', padx=14)
                tk.Label(blk, text=lbl_t, bg=c['primary'], fg='#93C5FD', font=('Segoe UI', 8)).pack(anchor='w')
                tk.Label(blk, text=val_t, bg=c['primary'], fg='white',
                         font=('Segoe UI', 10, 'bold')).pack(anchor='w')

            cals = self.sistema.obtener_calificaciones_alumno(al.matricula)
            if not cals:
                tk.Label(rf, text="Sin calificaciones registradas.", bg=c['surface'],
                         fg=c['text_light'], font=('Segoe UI', 11, 'italic')).pack(pady=25)
                return

            cols2 = ('Materia', 'Semestre', 'Calificación', 'Estado', 'Fecha Registro')
            tbl = tk.Frame(rf, bg=c['surface'])
            tbl.pack(fill='both', expand=True, padx=10, pady=5)
            sby2 = ttk.Scrollbar(tbl)
            sby2.pack(side='right', fill='y')
            t2 = ttk.Treeview(tbl, columns=cols2, show='headings',
                               yscrollcommand=sby2.set, height=min(len(cals), 15))
            sby2.config(command=t2.yview)
            for col, w in zip(cols2, [240, 120, 110, 110, 160]):
                t2.heading(col, text=col)
                t2.column(col, width=w)
            t2.pack(fill='both', expand=True)
            t2.tag_configure('apr', background='#D1FAE5', foreground='#065F46')
            t2.tag_configure('rep', background='#FEE2E2', foreground='#991B1B')
            for i, cal in enumerate(sorted(cals, key=lambda x: (x.semestre, x.materia_id))):
                mat = self.sistema.materias.get(cal.materia_id)
                mn = mat.nombre if mat else cal.materia_id
                apr = cal.calificacion >= 70
                t2.insert('', 'end',
                           values=(mn, cal.semestre, f"{cal.calificacion:.1f}",
                                   "✓ Aprobado" if apr else "✗ Reprobado", cal.fecha_registro),
                           tags=('apr' if apr else 'rep',))

            prom = self.sistema.obtener_promedio_alumno(al.matricula)
            aprs = sum(1 for c2 in cals if c2.calificacion >= 70)
            res = tk.Frame(rf, bg=c['surface'])
            res.pack(fill='x', padx=10, pady=6)
            for txt, col in [
                (f"📊 Promedio: {prom:.2f}", c['success'] if prom >= 70 else c['danger']),
                (f"✓ Aprobadas: {aprs}", c['success']),
                (f"✗ Reprobadas: {len(cals)-aprs}", c['danger'] if len(cals)-aprs else c['text_light']),
                (f"📚 Total: {len(cals)}", c['info']),
            ]:
                tk.Label(res, text=txt, bg=c['surface'], fg=col,
                         font=('Segoe UI', 11, 'bold')).pack(side='left', padx=18)

        self.btn(top, "📄 Ver Boletín", ver_boletin,
                 color=c['secondary'], padx=16, pady=6).pack(pady=5)
        cargar_al()
        se.focus()

    # ===========================
    # USUARIOS DEL SISTEMA (ADMIN)
    # ===========================

    def mostrar_lista_usuarios(self):
        """Muestra la lista completa de usuarios del sistema (solo admin)."""
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("👥 Usuarios del Sistema")

        # Barra superior con búsqueda y botón de registro
        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x')
        sv, se = self.busqueda_bar(top, placeholder="(ID, nombre, email o rol)")

        # Botón para registrar nuevo usuario
        btn_reg = tk.Button(
            top, text="➕ Registrar nuevo usuario",
            command=self.mostrar_registro_usuario_admin,
            bg=c['success'], fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat', cursor='hand2', padx=12, pady=5
        )
        btn_reg.pack(side='right', padx=10, pady=6)
        btn_reg.bind('<Enter>', lambda e: btn_reg.config(bg='#059669'))
        btn_reg.bind('<Leave>', lambda e: btn_reg.config(bg=c['success']))

        cols = ('ID', 'Nombre', 'Rol', 'Email', 'Activo')
        tree = self.tabla(self.right_panel, cols, [120, 250, 100, 220, 70], height=17)
        cnt = tk.Label(self.right_panel, text="", bg=c['surface'], fg=c['text_light'],
                       font=('Segoe UI', 9))
        cnt.pack()

        def cargar(*a):
            term = sv.get().strip().lower()
            filas = []
            for u in self.sistema.usuarios.values():
                if term and not (term in u.id.lower() or term in u.nombre.lower()
                                 or term in u.email.lower() or term in u.rol.lower()):
                    continue
                filas.append((u.id, u.nombre, u.rol, u.email, '✓' if u.activo else '✗'))
            filas.sort(key=lambda x: x[1])
            self.insertar(tree, filas)
            cnt.config(text=f"Total de usuarios: {len(filas)}")

        def on_doble_click(e):
            sel = tree.selection()
            if sel:
                user_id = tree.item(sel[0])['values'][0]
                self.mostrar_detalle_usuario(user_id)

        tree.bind('<Double-1>', on_doble_click)
        sv.trace('w', cargar)
        cargar()
        se.focus()

    def mostrar_registro_usuario_admin(self):
        """
        Ventana emergente para registrar nuevo usuario desde dentro del sistema.
        Permite al administrador elegir el rol: Administración, Docente o Estudiante.
        """
        win = tk.Toplevel(self.root)
        win.title("Registrar Nuevo Usuario")
        win.geometry("500x760")
        win.configure(bg='#1E293B')
        win.grab_set()

        # Scroll
        canvas = tk.Canvas(win, bg='#1E293B', highlightthickness=0)
        sb = ttk.Scrollbar(win, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        self.bind_scroll(canvas)

        frame = tk.Frame(canvas, bg='#1E293B')
        win_id = canvas.create_window((0, 0), window=frame, anchor='nw')
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width - 4))

        tk.Label(frame, text="📝 Registrar Nuevo Usuario",
                 bg='#1E293B', fg='white',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(20, 5))

        form = tk.Frame(frame, bg='#1E293B')
        form.pack(padx=30, fill='x')

        def lbl(txt):
            tk.Label(form, text=txt, bg='#1E293B', fg='#CBD5E1',
                     font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill='x', pady=(6, 0))

        def inp(show=None):
            e = tk.Entry(form, font=('Segoe UI', 10), bg='#334155', fg='white',
                         insertbackground='white', relief='flat', bd=6)
            if show:
                e.config(show=show)
            e.pack(fill='x', pady=(2, 0), ipady=4)
            return e

        # ── Selector de Rol ──
        lbl("Rol: *")
        rol_var = tk.StringVar(value='Administración')
        rol_cb = ttk.Combobox(form, values=['Administración', 'Docente', 'Estudiante'],
                              textvariable=rol_var, state='readonly',
                              font=('Segoe UI', 10))
        rol_cb.pack(fill='x', pady=(2, 8), ipady=3)

        lbl("ID de Usuario (matrícula o número empleado): *")
        id_e = inp()
        lbl("Nombre(s): *")
        nombre_e = inp()
        lbl("Apellido(s): *")
        apellido_e = inp()
        lbl("Email:")
        email_e = inp()
        lbl("Contraseña (mín. 8 chars, mayúscula, número): *")
        pw_e = inp('●')
        lbl("Confirmar Contraseña: *")
        pw2_e = inp('●')
        lbl("Fecha de Nacimiento (DD/MM/AAAA):")
        fecha_e = inp()
        lbl("Teléfono:")
        telefono_e = inp()

        # Campo especialidad (solo para Docente)
        esp_frame = tk.Frame(form, bg='#1E293B')
        esp_frame.pack(fill='x', pady=(6, 0))
        esp_lbl = tk.Label(esp_frame, text="Especialidad (solo Docentes):",
                           bg='#1E293B', fg='#CBD5E1',
                           font=('Segoe UI', 10, 'bold'), anchor='w')
        esp_lbl.pack(fill='x')
        especialidad_e = tk.Entry(esp_frame, font=('Segoe UI', 10), bg='#334155', fg='white',
                                  insertbackground='white', relief='flat', bd=6)
        especialidad_e.pack(fill='x', ipady=4)

        def on_rol_change(*a):
            """Muestra u oculta el campo especialidad según el rol."""
            if rol_var.get() == 'Docente':
                esp_frame.pack(fill='x', pady=(6, 0))
            else:
                esp_frame.pack_forget()

        rol_var.trace('w', on_rol_change)
        on_rol_change()  # estado inicial

        msg = tk.Label(frame, text='', bg='#1E293B', fg='#EF4444',
                       font=('Segoe UI', 9), wraplength=420)
        msg.pack(pady=5)

        def registrar():
            rol_sel = rol_var.get()
            if pw_e.get() != pw2_e.get():
                msg.config(text="❌ Las contraseñas no coinciden")
                return
            id_ = id_e.get().strip()
            nombre = nombre_e.get().strip()
            apellido = apellido_e.get().strip()
            if not id_ or not nombre or not apellido:
                msg.config(text="❌ ID, nombre y apellido son obligatorios")
                return
            especialidad = especialidad_e.get().strip() if rol_sel == 'Docente' else ''

            ok, texto = self.sistema.registrar_usuario(
                user_id=id_,
                nombre=nombre,
                apellido=apellido,
                password=pw_e.get(),
                rol=rol_sel,
                email=email_e.get().strip(),
                fecha_nacimiento=fecha_e.get().strip(),
                telefono=telefono_e.get().strip(),
                especialidad=especialidad,
            )
            if ok:
                messagebox.showinfo("Éxito", texto, parent=win)
                win.destroy()
                self.mostrar_lista_usuarios()   # refrescar la lista
            else:
                msg.config(text=f"❌ {texto}")

        tk.Button(frame, text="✅ Registrar Usuario", command=registrar,
                  bg='#10B981', fg='white', font=('Segoe UI', 11, 'bold'),
                  relief='flat', cursor='hand2').pack(pady=10, padx=30, fill='x', ipady=8)

        tk.Button(frame, text="Cancelar", command=win.destroy,
                  bg='#475569', fg='white', font=('Segoe UI', 10),
                  relief='flat', cursor='hand2').pack(pady=(0, 15), padx=30, fill='x', ipady=6)

    def mostrar_detalle_usuario(self, user_id):
        """Ventana emergente con información detallada del usuario."""
        usuario = self.sistema.usuarios.get(user_id)
        if not usuario:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        
        win = tk.Toplevel(self.root)
        win.title(f"Detalles de {usuario.nombre}")
        win.geometry("550x650")
        win.configure(bg=self.c('surface'))
        win.grab_set()
        
        # Scroll por si hay muchos datos
        canvas = tk.Canvas(win, bg=self.c('surface'), highlightthickness=0)
        sb = ttk.Scrollbar(win, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        self.bind_scroll(canvas)
        
        frame = tk.Frame(canvas, bg=self.c('surface'))
        win_id = canvas.create_window((0, 0), window=frame, anchor='nw')
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width - 4))
        
        # Cabecera
        tk.Label(frame, text="👤 Información del Usuario", bg=self.c('surface'),
                 fg=self.c('secondary'), font=('Segoe UI', 14, 'bold')).pack(pady=(10, 5))
        tk.Frame(frame, bg=self.c('border'), height=1).pack(fill='x', padx=20, pady=5)
        
        # Datos básicos del usuario
        info = tk.Frame(frame, bg=self.c('surface'))
        info.pack(fill='x', padx=25, pady=5)
        
        def row(lbl, val, fila):
            tk.Label(info, text=lbl, bg=self.c('surface'), fg=self.c('text_light'),
                     font=('Segoe UI', 10), anchor='w').grid(row=fila, column=0, sticky='w', pady=2)
            tk.Label(info, text=str(val) if val else '—', bg=self.c('surface'), fg=self.c('text'),
                     font=('Segoe UI', 10, 'bold'), anchor='w').grid(row=fila, column=1, sticky='w', padx=(10,0), pady=2)
        
        row("ID:", usuario.id, 0)
        row("Nombre:", usuario.nombre, 1)
        row("Rol:", usuario.rol, 2)
        row("Email:", usuario.email, 3)
        row("Activo:", "✓ Sí" if usuario.activo else "✗ No", 4)
        # Contraseña (no se puede recuperar, mostramos asteriscos)
        row("Contraseña:", "●●●●●●●● (no recuperable)", 5)
        
        # Botón para cambiar contraseña (solo admin)
        if self.sistema.es_admin():
            btn_frame = tk.Frame(frame, bg=self.c('surface'))
            btn_frame.pack(pady=5)
            self.btn(btn_frame, "🔑 Cambiar Contraseña", 
                     lambda: self.mostrar_cambiar_password(usuario.id),
                     color=self.c('warning'), padx=15, pady=5).pack()
        
        # Si es alumno, buscar en alumnos y mostrar más datos
        if usuario.rol == 'Estudiante':
            alumno = self.sistema.alumnos.get(usuario.id)
            if alumno:
                tk.Frame(frame, bg=self.c('border'), height=1).pack(fill='x', padx=20, pady=10)
                tk.Label(frame, text="🎓 Datos del Alumno", bg=self.c('surface'),
                         fg=self.c('secondary'), font=('Segoe UI', 12, 'bold')).pack(pady=(5, 5))
                info_al = tk.Frame(frame, bg=self.c('surface'))
                info_al.pack(fill='x', padx=25, pady=5)
                
                sm, cc, grp = self.sistema.parsear_grupo_completo(alumno.grado)
                cn = self.sistema.get_nombre_carrera(cc) if sm else alumno.grado
                
                def row_al(lbl, val, fila):
                    tk.Label(info_al, text=lbl, bg=self.c('surface'), fg=self.c('text_light'),
                             font=('Segoe UI', 10), anchor='w').grid(row=fila, column=0, sticky='w', pady=2)
                    tk.Label(info_al, text=str(val) if val else '—', bg=self.c('surface'), fg=self.c('text'),
                             font=('Segoe UI', 10, 'bold'), anchor='w').grid(row=fila, column=1, sticky='w', padx=(10,0), pady=2)
                
                row_al("Matrícula:", alumno.matricula, 0)
                row_al("Nombre completo:", alumno.get_nombre_completo(), 1)
                row_al("Fecha Nacimiento:", alumno.fecha_nacimiento, 2)
                row_al("Teléfono:", alumno.telefono, 3)
                row_al("Email:", alumno.email, 4)
                row_al("Grupo:", alumno.grado, 5)
                row_al("Carrera:", cn, 6)
                row_al("Lugar Nacimiento:", alumno.lugar_nacimiento, 7)
                row_al("Dirección:", alumno.direccion, 8)
                row_al("Último Grado:", alumno.ultimo_grado_estudios, 9)
                row_al("Fecha Alta:", alumno.fecha_alta, 10)
                row_al("Activo:", "Sí" if alumno.activo else "No", 11)
                if not alumno.activo:
                    row_al("Fecha Baja:", alumno.fecha_baja, 12)
                    row_al("Motivo Baja:", alumno.motivo_baja, 13)
                # Promedio
                prom = self.sistema.obtener_promedio_alumno(alumno.matricula)
                row_al("Promedio:", f"{prom:.2f}", 14)
        
        # Si es docente, buscar en docentes
        elif usuario.rol == 'Docente':
            docente = self.sistema.docentes.get(usuario.id)
            if docente:
                tk.Frame(frame, bg=self.c('border'), height=1).pack(fill='x', padx=20, pady=10)
                tk.Label(frame, text="👨‍🏫 Datos del Docente", bg=self.c('surface'),
                         fg=self.c('secondary'), font=('Segoe UI', 12, 'bold')).pack(pady=(5, 5))
                info_doc = tk.Frame(frame, bg=self.c('surface'))
                info_doc.pack(fill='x', padx=25, pady=5)
                
                def row_doc(lbl, val, fila):
                    tk.Label(info_doc, text=lbl, bg=self.c('surface'), fg=self.c('text_light'),
                             font=('Segoe UI', 10), anchor='w').grid(row=fila, column=0, sticky='w', pady=2)
                    tk.Label(info_doc, text=str(val) if val else '—', bg=self.c('surface'), fg=self.c('text'),
                             font=('Segoe UI', 10, 'bold'), anchor='w').grid(row=fila, column=1, sticky='w', padx=(10,0), pady=2)
                
                row_doc("Núm. Empleado:", docente.num_empleado, 0)
                row_doc("Nombre completo:", docente.get_nombre_completo(), 1)
                row_doc("Fecha Nacimiento:", docente.fecha_nacimiento, 2)
                row_doc("Teléfono:", docente.telefono, 3)
                row_doc("Email:", docente.email, 4)
                row_doc("Especialidad:", docente.especialidad, 5)
                row_doc("Tipo Contrato:", docente.tipo_contrato, 6)
                row_doc("Lugar Nacimiento:", docente.lugar_nacimiento, 7)
                row_doc("Dirección:", docente.direccion, 8)
                row_doc("Último Grado:", docente.ultimo_grado_estudios, 9)
                row_doc("Activo:", "Sí" if docente.activo else "No", 10)
                row_doc("Baja Temporal:", "Sí" if docente.baja_temporal else "No", 11)
        
        # Botón cerrar
        self.btn(frame, "Cerrar", win.destroy, color=self.c('secondary'),
                 padx=20, pady=8).pack(pady=15)

    def mostrar_detalle_alumno(self, matricula):
        """Muestra ventana emergente con detalles del alumno."""
        alumno = self.sistema.alumnos.get(str(matricula))
        if not alumno:
            messagebox.showerror("Error", "Alumno no encontrado")
            return
        # Reutilizamos la misma ventana de detalle de usuario, pero desde el contexto alumno podemos llamar a mostrar_detalle_usuario con la matrícula
        # Dado que el alumno debe tener un usuario asociado con la misma ID, lo intentamos.
        self.mostrar_detalle_usuario(matricula)

    def mostrar_detalle_docente(self, num_empleado):
        """Muestra ventana emergente con detalles del docente."""
        docente = self.sistema.docentes.get(str(num_empleado))
        if not docente:
            messagebox.showerror("Error", "Docente no encontrado")
            return
        self.mostrar_detalle_usuario(num_empleado)

    # ===========================
    # HISTORIAL
    # ===========================

    def mostrar_historial(self):
        self.limpiar_panel()
        c = self.colors
        self.titulo_panel("📋 Historial de Cambios")
        top = tk.Frame(self.right_panel, bg=c['surface'])
        top.pack(fill='x')

        sv, se = self.busqueda_bar(top, label="🔍 Filtrar:", placeholder="(tipo, descripción, usuario)")

        tipos = ["TODOS"] + sorted({h.get('tipo', '') for h in self.sistema.historial})
        tipo_var = tk.StringVar(value="TODOS")
        tf = tk.Frame(top, bg=c['surface'])
        tf.pack(fill='x', padx=10, pady=3)
        tk.Label(tf, text="Tipo:", bg=c['surface'], fg=c['text'],
                 font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        ttk.Combobox(tf, values=tipos, textvariable=tipo_var,
                     state='readonly', width=24, font=('Segoe UI', 10)).pack(side='left', padx=5)

        cols = ('#', 'Fecha', 'Usuario', 'Rol', 'Tipo', 'Descripción')
        tree = self.tabla(self.right_panel, cols, [50, 150, 120, 110, 150, 450], height=17)
        cnt = tk.Label(self.right_panel, text="", bg=c['surface'], fg=c['text_light'],
                       font=('Segoe UI', 9))
        cnt.pack()

        def limpiar():
            if messagebox.askyesno("Confirmar", "¿Limpiar TODO el historial? Esta acción no se puede deshacer."):
                self.sistema.historial = []
                self.sistema._guardar_historial()
                cargar()

        self.btn(self.right_panel, "🗑️ Limpiar Historial", limpiar,
                 color=c['danger'], padx=12, pady=5).pack(pady=3)

        def cargar(*a):
            t = sv.get().strip().lower()
            tipo_sel = tipo_var.get()
            filas = []
            for cambio in reversed(self.sistema.historial):
                tipo = cambio.get('tipo', '')
                if tipo_sel != "TODOS" and tipo != tipo_sel:
                    continue
                if t and not any(t in str(cambio.get(k, '')).lower()
                                 for k in ['tipo', 'descripcion', 'usuario', 'rol']):
                    continue
                filas.append((cambio.get('id', ''), cambio.get('fecha', ''),
                               cambio.get('usuario', ''), cambio.get('rol', ''),
                               tipo, cambio.get('descripcion', '')))
            self.insertar(tree, filas)
            cnt.config(text=f"Mostrando: {len(filas)} | Total: {len(self.sistema.historial)}")

        sv.trace('w', cargar)
        tipo_var.trace('w', cargar)
        cargar()
        se.focus()


# ===========================
# PUNTO DE ENTRADA
# ===========================

def main():
    root = tk.Tk()
    root.title("Sistema de Control Escolar v2.0")
    try:
        root.state('zoomed')  # Windows maximizado
    except:
        root.geometry("1400x820")
    app = SistemaEscolarGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()