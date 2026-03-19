#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
#  Estructura de datos: diccionario ordenado alfabéticamente
#  Clave: nombre del postre (str)
#  Valor: lista de ingredientes (list)
#
#  Se incluyen duplicados intencionales para demostrar
#  el subprograma de limpieza automática.
# ============================================================

POSTRES = {
    "Brownie":             ["chocolate", "harina", "huevo", "mantequilla", "azúcar", "harina"],
    "brownie":             ["chocolate", "harina", "huevo", "mantequilla", "azúcar"],
    "Cheesecake":          ["queso crema", "galleta", "mantequilla", "azúcar", "huevo", "huevo"],
    "Flan":                ["leche", "huevo", "azúcar", "vainilla"],
    "flan":                ["leche", "huevo", "azúcar", "vainilla"],
    "Gelatina":            ["agua", "azúcar", "grenetina", "colorante", "agua"],
    "Pastel de chocolate": ["harina", "cacao", "azúcar", "huevo", "mantequilla", "leche"],
    "PASTEL DE CHOCOLATE": ["harina", "cacao", "azúcar", "huevo", "mantequilla", "leche"],
    "Tiramisú":            ["café", "queso mascarpone", "bizcocho", "azúcar", "cocoa"],
}


# ─────────────────────────── helpers ────────────────────────────

def _ordenar():
    global POSTRES
    POSTRES = dict(sorted(POSTRES.items(), key=lambda x: x[0].lower()))


def _buscar_postre(nombre: str):
    for clave in POSTRES:
        if clave.lower() == nombre.lower():
            return clave
    return None


def _pedir_texto(mensaje: str, campo: str = "valor") -> str | None:
    while True:
        valor = input(mensaje).strip()
        if valor == "":
            print(f"  ⚠  El {campo} no puede estar vacío.")
            reintentar = input("  ¿Desea intentarlo de nuevo? (s/n): ").strip().lower()
            if reintentar != "s":
                return None
        else:
            return valor


def _listar_postres():
    if not POSTRES:
        print("\n  (No hay postres registrados.)")
        return
    print("\n  Postres disponibles:")
    for i, nombre in enumerate(POSTRES, 1):
        print(f"    {i:2}. {nombre}")


# ─────────────────────────── opciones del menú original ─────────

def ver_ingredientes():
    print("\n══════════════════════════════")
    print("  VER INGREDIENTES DE UN POSTRE")
    print("══════════════════════════════")
    _listar_postres()
    if not POSTRES:
        return

    nombre = _pedir_texto("\n  Ingrese el nombre del postre: ", "nombre")
    if nombre is None:
        print("  Operación cancelada.")
        return

    clave = _buscar_postre(nombre)
    if clave is None:
        print(f"\n  ✗ El postre '{nombre}' no existe en el catálogo.")
        return

    ingredientes = POSTRES[clave]
    if not ingredientes:
        print(f"\n  El postre '{clave}' no tiene ingredientes registrados.")
        return

    print(f"\n  Ingredientes de '{clave}':")
    for i, ing in enumerate(ingredientes, 1):
        print(f"    {i:2}. {ing}")


def agregar_ingredientes():
    print("\n════════════════════════════════")
    print("  AGREGAR INGREDIENTES A UN POSTRE")
    print("════════════════════════════════")
    _listar_postres()
    if not POSTRES:
        return

    nombre = _pedir_texto("\n  Ingrese el nombre del postre: ", "nombre")
    if nombre is None:
        print("  Operación cancelada.")
        return

    clave = _buscar_postre(nombre)
    if clave is None:
        print(f"\n  ✗ El postre '{nombre}' no existe.")
        return

    print(f"\n  Ingredientes actuales de '{clave}':")
    for i, ing in enumerate(POSTRES[clave], 1):
        print(f"    {i}. {ing}")

    print("\n  Ingrese los nuevos ingredientes (vacío + Enter para terminar).")
    agregados = []
    while True:
        nuevo = input("  Ingrediente: ").strip()
        if nuevo == "":
            break
        existentes_lower = [x.lower() for x in POSTRES[clave]]
        if nuevo.lower() in existentes_lower:
            print(f"  ⚠  '{nuevo}' ya está en la lista. Se omite.")
        else:
            POSTRES[clave].append(nuevo)
            agregados.append(nuevo)
            print(f"  ✓  '{nuevo}' agregado.")

    if agregados:
        print(f"\n  Se agregaron {len(agregados)} ingrediente(s) a '{clave}'.")
    else:
        print("\n  No se agregó ningún ingrediente.")


def eliminar_ingrediente():
    print("\n══════════════════════════════════")
    print("  ELIMINAR INGREDIENTE DE UN POSTRE")
    print("══════════════════════════════════")
    _listar_postres()
    if not POSTRES:
        return

    nombre = _pedir_texto("\n  Ingrese el nombre del postre: ", "nombre")
    if nombre is None:
        print("  Operación cancelada.")
        return

    clave = _buscar_postre(nombre)
    if clave is None:
        print(f"\n  ✗ El postre '{nombre}' no existe.")
        return

    if not POSTRES[clave]:
        print(f"\n  '{clave}' no tiene ingredientes que eliminar.")
        return

    print(f"\n  Ingredientes de '{clave}':")
    for i, ing in enumerate(POSTRES[clave], 1):
        print(f"    {i:2}. {ing}")

    ing_eliminar = _pedir_texto("\n  Ingrese el ingrediente a eliminar: ", "ingrediente")
    if ing_eliminar is None:
        print("  Operación cancelada.")
        return

    indice = None
    for i, ing in enumerate(POSTRES[clave]):
        if ing.lower() == ing_eliminar.lower():
            indice = i
            break

    if indice is None:
        print(f"\n  ✗ El ingrediente '{ing_eliminar}' no se encontró en '{clave}'.")
        return

    confirmacion = input(
        f"\n  ¿Confirma eliminar '{POSTRES[clave][indice]}' de '{clave}'? (s/n): "
    ).strip().lower()

    if confirmacion == "s":
        eliminado = POSTRES[clave].pop(indice)
        print(f"\n  ✓ Ingrediente '{eliminado}' eliminado de '{clave}'.")
    else:
        print("  Operación cancelada.")


def dar_alta_postre():
    print("\n════════════════════════")
    print("  DAR DE ALTA UN POSTRE")
    print("════════════════════════")

    nombre = _pedir_texto("\n  Nombre del nuevo postre: ", "nombre")
    if nombre is None:
        print("  Operación cancelada.")
        return

    if _buscar_postre(nombre) is not None:
        print(f"\n  ✗ El postre '{nombre}' ya existe en el catálogo.")
        return

    print(f"\n  Ingrese los ingredientes de '{nombre}'.")
    print("  (Deje vacío y presione Enter para terminar.)")
    ingredientes = []
    while True:
        ing = input("  Ingrediente: ").strip()
        if ing == "":
            if not ingredientes:
                continuar = input(
                    "  ⚠  No ha ingresado ningún ingrediente. ¿Desea continuar? (s/n): "
                ).strip().lower()
                if continuar == "s":
                    continue
                else:
                    break
            break
        if ing.lower() in [x.lower() for x in ingredientes]:
            print(f"  ⚠  '{ing}' ya fue ingresado. Se omite.")
        else:
            ingredientes.append(ing)

    POSTRES[nombre] = ingredientes
    _ordenar()
    print(f"\n  ✓ Postre '{nombre}' dado de alta con {len(ingredientes)} ingrediente(s).")


def dar_baja_postre():
    print("\n══════════════════════════")
    print("  DAR DE BAJA UN POSTRE")
    print("══════════════════════════")
    _listar_postres()
    if not POSTRES:
        return

    nombre = _pedir_texto("\n  Nombre del postre a dar de baja: ", "nombre")
    if nombre is None:
        print("  Operación cancelada.")
        return

    clave = _buscar_postre(nombre)
    if clave is None:
        print(f"\n  ✗ El postre '{nombre}' no existe en el catálogo.")
        return

    print(f"\n  Postre: {clave}")
    print(f"  Ingredientes: {', '.join(POSTRES[clave]) if POSTRES[clave] else '(ninguno)'}")

    confirmacion = input(
        f"\n  ¿Confirma eliminar '{clave}' y todos sus ingredientes? (s/n): "
    ).strip().lower()

    if confirmacion == "s":
        del POSTRES[clave]
        print(f"\n  ✓ Postre '{clave}' dado de baja exitosamente.")
    else:
        print("  Operación cancelada.")


# ─────────────────────────── SUBPROGRAMA NUEVO ──────────────────

def eliminar_duplicados_postres():
    """
    Elimina automáticamente:
      1. Postres con nombre duplicado (insensible a mayúsculas).
         ¡NOTA! No se puede usar set() sobre los VALORES del dict
         porque son listas → mutables → NO hashables → TypeError.
         Se usa comparación manual con un dict de claves normalizadas.
      2. Ingredientes duplicados dentro de cada lista.
         Aquí SÍ se usa set() porque cada ingrediente es un str (hashable).
    """
    global POSTRES

    print("\n══════════════════════════════════════════════")
    print("  ELIMINANDO DUPLICADOS AUTOMÁTICAMENTE")
    print("══════════════════════════════════════════════")

    # ── Paso 1: postres duplicados ───────────────────────────────
    # ¿Por qué NO set()?
    #   set(POSTRES.values())  →  TypeError: unhashable type: 'list'
    # ¿Por qué sí dict de claves normalizadas?
    #   Comparamos strings normalizados (hashables) como claves,
    #   nunca las listas directamente.

    postres_vistos = {}   # {nombre_normalizado: nombre_original_a_conservar}
    eliminados_postres = []

    for nombre in list(POSTRES.keys()):
        clave_norm = nombre.strip().lower()
        if clave_norm not in postres_vistos:
            postres_vistos[clave_norm] = nombre
        else:
            eliminados_postres.append(nombre)

    if eliminados_postres:
        print(f"\n  Postres duplicados eliminados ({len(eliminados_postres)}):")
        for p in eliminados_postres:
            conservado = postres_vistos[p.strip().lower()]
            print(f"    • '{p}'  →  se conserva '{conservado}'")
            del POSTRES[p]
    else:
        print("\n  No se encontraron postres duplicados.")

    # ── Paso 2: ingredientes duplicados dentro de cada lista ─────
    # str es hashable → set() funciona perfectamente aquí.
    print("\n  Ingredientes duplicados eliminados por postre:")
    hubo = False

    for nombre in POSTRES:
        seen = set()
        limpios = []
        duplicados_ing = []

        for ing in POSTRES[nombre]:
            ing_norm = ing.strip().lower()
            if ing_norm not in seen:
                seen.add(ing_norm)
                limpios.append(ing)
            else:
                duplicados_ing.append(ing)

        if duplicados_ing:
            hubo = True
            print(f"    '{nombre}': eliminado(s) → {duplicados_ing}")

        POSTRES[nombre] = limpios

    if not hubo:
        print("    (Ningún ingrediente duplicado encontrado.)")

    # ── Paso 3: reordenar ────────────────────────────────────────
    _ordenar()

    print(f"\n  ✓ Limpieza completa. Postres en catálogo: {len(POSTRES)}")
    print("══════════════════════════════════════════════")


# ─────────────────────────── menú ───────────────────────────────

def menu():
    opciones = {
        "1": ("Ver ingredientes de un postre",          ver_ingredientes),
        "2": ("Agregar ingredientes a un postre",        agregar_ingredientes),
        "3": ("Eliminar ingrediente de un postre",       eliminar_ingrediente),
        "4": ("Dar de alta un postre",                   dar_alta_postre),
        "5": ("Dar de baja un postre",                   dar_baja_postre),
        "6": ("Eliminar duplicados automáticamente",     eliminar_duplicados_postres),
        "7": ("Salir",                                   None),
    }

    while True:
        print("\n╔════════════════════════════════════════════╗")
        print("║           GESTIÓN DE POSTRES               ║")
        print("╠════════════════════════════════════════════╣")
        for k, (desc, _) in opciones.items():
            print(f"║  {k}. {desc:<40}║")
        print("╚════════════════════════════════════════════╝")

        eleccion = input("  Seleccione una opción: ").strip()

        if eleccion not in opciones:
            print("\n  ✗ Opción inválida. Intente de nuevo.")
            continue

        desc, funcion = opciones[eleccion]

        if funcion is None:
            print("\n  ¡Hasta luego!\n")
            break

        funcion()
        input("\n  Presione Enter para continuar...")


# ─────────────────────────── entrada ────────────────────────────

if __name__ == "__main__":
    menu()
