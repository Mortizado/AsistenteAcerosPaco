
import unittest

from principal.events import EventBus
from principal.emma import crear_emma
from principal.interaction_manager import InteractionManager
from principal.modality_component import ModalityComponent


class TestMMI(unittest.TestCase):

    def test_ciclo_completo(self):

        # Crear el bus y la lista para registrar eventos
        bus = EventBus()
        eventos = []
        resultados = []

        # Registrar los eventos que se producen
        bus.suscribir(
            "NewContextRequest",
            lambda datos: eventos.append("NewContextRequest")
        )

        bus.suscribir(
            "StartRequest",
            lambda datos: eventos.append("StartRequest")
        )

        bus.suscribir(
            "DoneNotification",
            lambda datos: eventos.append("DoneNotification")
        )

        bus.suscribir(
            "resultado_consulta",
            lambda datos: resultados.append(datos["machine"])
        )

        # Crear el gestor y el componente simulado
        gestor = InteractionManager()
        gestor.conectar_bus(bus)

        teclado = ModalityComponent("teclado", bus)

        # Solicitar una interacción
        teclado.solicitar_contexto()

        # Comprobar que el asistente está escuchando
        self.assertEqual(gestor.state, "escuchando")

        # Enviar una interpretación EMMA
        solicitud = crear_emma("Cizalla", "teclado", 1.0)
        teclado.enviar_resultado(solicitud)

        # Comprobar los tres eventos MMI
        self.assertEqual(
            eventos,
            [
                "NewContextRequest",
                "StartRequest",
                "DoneNotification"
            ]
        )

        # Comprobar que se encontró la máquina correcta
        self.assertEqual(resultados[0]["nombre"], "Cizalla")

        # Comprobar que la interacción terminó
        self.assertEqual(gestor.state, "inactivo")


if __name__ == "__main__":
    unittest.main()
