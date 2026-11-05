
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget
)

from .catalogo import list_machines
from .interaction_manager import InteractionManager
from .events import EventBus
from .emma import crear_emma
from .modality_component import ModalityComponent


def main():

    # Crear el bus de eventos y el gestor
    bus = EventBus()
    gestor = InteractionManager()

    # Conectar el gestor con el bus
    gestor.conectar_bus(bus)

    # Crear el componente de modalidad de teclado
    teclado = ModalityComponent("teclado", bus)

    # Crear la aplicación y la ventana
    app = QApplication(sys.argv)

    ventana = QWidget()
    ventana.setWindowTitle("Asistente Aceros Paco S.L.")
    ventana.resize(500, 350)

    diseño = QVBoxLayout()

    titulo = QLabel("Bienvenido a Aceros Paco S.L.")
    diseño.addWidget(titulo)

    estado = QLabel("Estado: " + gestor.state)
    diseño.addWidget(estado)

    subtitulo = QLabel("Máquinas disponibles:")
    diseño.addWidget(subtitulo)

    # Crear la lista de máquinas
    lista = QListWidget()

    data = list_machines()

    for maquina in data["maquinas"]:
        lista.addItem(maquina["nombre"])

    lista.setAccessibleName("Lista de máquinas disponibles")
    diseño.addWidget(lista)

    # Crear la lista de piezas
    nombre_de_pieza = QLabel("Piezas disponibles:")
    diseño.addWidget(nombre_de_pieza)

    lista_piezas = QListWidget()
    lista_piezas.setAccessibleName("Lista de piezas disponibles")
    diseño.addWidget(lista_piezas)

    # Recibir los resultados enviados por InteractionManager
    def mostrar_resultado(datos):

        lista_piezas.clear()

        machine = datos["machine"]

        for pieza in machine["piezas"]:
            lista_piezas.addItem(pieza["nombre"])

    # Suscribir la interfaz al evento de resultados
    bus.suscribir("resultado_consulta", mostrar_resultado)

    # Detectar la máquina seleccionada por el usuario
    def mostrar_piezas():

        lista_piezas.clear()

        seleccion = lista.currentItem()

        if seleccion is None:
            return

        # Solicitar un nuevo contexto MMI
        teclado.solicitar_contexto()

        # Crear la interpretación EMMA
        solicitud = crear_emma(
            seleccion.text(),
            "teclado",
            1.0
        )

        # Enviar la interpretación al gestor mediante EventBus
        teclado.enviar_resultado(solicitud)

        # Actualizar el estado de la interfaz
        estado.setText("Estado: " + gestor.state)

    # Ejecutar mostrar_piezas cuando cambie la selección
    lista.itemSelectionChanged.connect(mostrar_piezas)

    ventana.setLayout(diseño)
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
