
class EventBus:

    def __init__(self):
        self.suscriptores = {}

    def suscribir(self, tipo, funcion):
        if tipo not in self.suscriptores:
            self.suscriptores[tipo] = []

        self.suscriptores[tipo].append(funcion)

    def publicar(self, tipo, datos):
        for funcion in self.suscriptores.get(tipo, []):
            funcion(datos)
