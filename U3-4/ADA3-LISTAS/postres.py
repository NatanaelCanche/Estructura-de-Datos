POSTRES = {
    "Brownie": ["chocolate", "harina", "huevo", "mantequilla", "azúcar"],
    "Cheesecake": ["queso crema", "galleta", "mantequilla", "azúcar", "huevo"],
    "Flan": ["leche", "huevo", "azúcar", "vainilla"],
    "Gelatina": ["agua", "azúcar", "grenetina", "colorante"],
    "Pastel de chocolate": ["harina", "cacao", "azúcar", "huevo", "mantequilla", "leche"],
    "Tiramisú": ["café", "queso mascarpone", "bizcocho", "azúcar", "cocoa"],
}


# ─────────────────────────── helpers ────────────────────────────

def _ordenar():
    """Reordena POSTRES alfabéticamente (insensible a mayúsculas)."""
    global POSTRES
    POSTRES = dict(sorted(POSTRES.items(), key=lambda x: x[0].lower()))


def _buscar_postre(nombre: str):
    """
    Devuelve la clave exacta si el postre existe (búsqueda insensible
    a mayúsculas/minúsculas), o None si no se encuentra.
    """
    for clave in POSTRES:
        if clave.lower() == nombre.lower():
            return clave
    return None


def _pedir_texto(mensaje: str, campo: str = "valor") -> str | None:
    """Solicita texto no vacío al usuario. Retorna None si cancela."""
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


# ─────────────────────────── opciones ───────────────────────────

def ver_ingredientes():
    """a. Mostrar ingredientes de un postre."""
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
    """b. Agregar ingredientes a un postre existente."""
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

    print("\n  Ingrese los nuevos ingredientes (deje vacío y presione Enter para terminar).")
    agregados = []
    while True:
        nuevo = input("  Ingrediente: ").strip()
        if nuevo == "":
            break
        # Verificar duplicado (insensible a mayúsculas)
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
    """c. Eliminar un ingrediente de un postre."""
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

    # Buscar insensible a mayúsculas
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
    """d. Registrar un nuevo postre con sus ingredientes."""
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
                    "  ⚠  No ha ingresado ningún ingrediente. ¿Desea continuar agregando? (s/n): "
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
    """e. Eliminar un postre completo del catálogo."""
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


# ─────────────────────────── menú ───────────────────────────────

def menu():
    opciones = {
        "1": ("Ver ingredientes de un postre",   ver_ingredientes),
        "2": ("Agregar ingredientes a un postre", agregar_ingredientes),
        "3": ("Eliminar ingrediente de un postre",eliminar_ingrediente),
        "4": ("Dar de alta un postre",            dar_alta_postre),
        "5": ("Dar de baja un postre",            dar_baja_postre),
        "6": ("Salir",                            None),
    }

    while True:
        print("         GESTIÓN DE POSTRES           ")
        for k, (desc, _) in opciones.items():
            print(f"║  {k}. {desc:<34}║")

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
