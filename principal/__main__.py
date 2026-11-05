
from .interaction_manager import InteractionManager
from .catalogo import list_machines, search_machine


def main():
    print("Bienvenido a Aceros Paco S.L.")

    gestor = InteractionManager()
    gestor.mostrar_estado()

    data = list_machines()

    # Muestra las maquinas disponibles del taller
    for maquina in data["maquinas"]:
        print("Máquina disponible:", maquina["nombre"])

    # Iniciar interacción
    gestor.iniciar_interaccion()
    gestor.mostrar_estado()

    # Aqui pregunto que maquina quiere consultar
    while True:
        machine_for_consult = input(
            "Ingrese el nombre de la máquina o 'salir' para cancelar:\n"
        ).strip()

        if machine_for_consult.lower() == "salir":
            gestor.cancelar()
            print("Consulta cancelada.")
            break

        if machine_for_consult == "":
            print("No ingresaste ninguna máquina.")
            continue

        # Procesa la solicitud
        gestor.recibir_solicitud()
        gestor.mostrar_estado()

        machine = search_machine(data, machine_for_consult)

        if machine is not None:
            gestor.ejecutar()
            gestor.mostrar_estado()

            print("Seleccionaste la máquina:", machine["nombre"])

            for pieza in machine["piezas"]:
                print("Pieza disponible:", pieza["nombre"])

            gestor.finalizar()
            gestor.mostrar_estado()
            break

        else:
            print("No se encontró la máquina:", machine_for_consult)

            gestor.reintentar()
            gestor.mostrar_estado()


if __name__ == "__main__":
    main()
