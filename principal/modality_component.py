
class ModalityComponent:

    def __init__(self, nombre, bus):
        self.nombre = nombre
        self.bus = bus

        # Escuchar órdenes de inicio
        self.bus.suscribir("StartRequest", self.iniciar)

    # Solicitar el inicio de una interacción
    def solicitar_contexto(self):
        self.bus.publicar(
            "NewContextRequest",
            {"source": self.nombre}
        )

    # Recibir una orden de inicio
    def iniciar(self, datos):
        if datos["target"] == self.nombre:
            print("Componente iniciado:", self.nombre)

    # Comunicar que la interpretación terminó
    def enviar_resultado(self, emma):
        self.bus.publicar(
            "DoneNotification",
            {
                "source": self.nombre,
                "emma": emma
            }
        )
