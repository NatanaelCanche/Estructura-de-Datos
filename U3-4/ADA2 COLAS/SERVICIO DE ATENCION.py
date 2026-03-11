class Cola:
    def __init__(self):
        self.items = []

    def encolar(self, elemento):
        self.items.append(elemento)

    def desencolar(self):
        if not self.esta_vacia():
            return self.items.pop(0)
        return None 

    def esta_vacia(self):
        return len(self.items) == 0

def ejecutar_sistema_consolas():
    colas_por_servicio = {}
    turnos_por_servicio = {}

    print("========================================")
    print("   Servicio al cliente")
    print("========================================")
    print(" Comandos permitidos:")
    print("  C<número> o C <número> : Llegada (Ej: C1 o C 1)")
    print("  A<número> o A <número> : Atender (Ej: A1 o A 1)")
    print("  S                      : Salir")
    print("========================================\n")

    while True:
        try:
            entrada_original = input("Ingrese comando: ").upper()
        except KeyboardInterrupt:
            print("\n[!] Cierre forzado del sistema. ¡Hasta luego!")
            break
        except EOFError:
            break
        if not entrada_original.strip():
            continue
        entrada_normalizada = entrada_original.replace(" ", "")

        if entrada_normalizada == 'S':
            print("Sistema finalizado de manera correcta.")
            break

        if len(entrada_normalizada) < 2:
            print("[Error] Formato incompleto. Utilice 'Letra Número' (Ej: C1 o C 1).\n")
            continue
        accion = entrada_normalizada[0]
        servicio = entrada_normalizada[1:]

        if accion not in ['C', 'A']:
            print(f"[Error] Comando '{accion}' no reconocido. Utilice únicamente 'C' o 'A'.\n")
            continue

        if not servicio.isdigit():
            print(f"[Error] El servicio '{servicio}' no es válido. Debe ser un número entero positivo.\n")
            continue

        if accion == 'C':
            if servicio not in colas_por_servicio:
                colas_por_servicio[servicio] = Cola()
                turnos_por_servicio[servicio] = 1
                
            numero_atencion = turnos_por_servicio[servicio]
            colas_por_servicio[servicio].encolar(numero_atencion)
            
            print(f"--> [REGISTRO EXITOSO] Entregando número: {numero_atencion} (Servicio {servicio})\n")
            
            turnos_por_servicio[servicio] += 1

        elif accion == 'A':
            if servicio in colas_por_servicio and not colas_por_servicio[servicio].esta_vacia():
                numero_llamado = colas_por_servicio[servicio].desencolar()
                print(f"--> [LLAMADA A VENTANILLA] Número: {numero_llamado} (Servicio {servicio})\n")
            else:
                print(f"--> [AVISO] La cola del servicio {servicio} está vacía o no existe.\n")
if __name__ == "__main__":
    ejecutar_sistema_consolas()