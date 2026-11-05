
from transitions import Machine
from .catalogo import list_machines, search_machine


class InteractionManager:

    states = [
        "inactivo",
        "escuchando",
        "procesando",
        "confirmando",
        "ejecutando",
        "error"
    ]

    def reiniciar_intentos(self):
        self.try_nomatch = 0
        self.try_noinput = 0

    def __init__(self):
        self.try_nomatch = 0
        self.try_noinput = 0
        self.max_try = 3
        self.data = list_machines()
        self.cmin = 0.50
        self.cmax = 0.80
        self.machine_pendiente = None

        self.machine = Machine(
            model=self,
            states=self.states,
            initial="inactivo",
            auto_transitions=False
        )

        # Comenzar una interacción
        self.machine.add_transition(
            "iniciar_interaccion",
            "inactivo",
            "escuchando",
            after="reiniciar_intentos"
        )

        # Recibir una solicitud
        self.machine.add_transition(
            "recibir_solicitud", "escuchando", "procesando"
        )

        # La solicitud necesita confirmación
        self.machine.add_transition(
            "solicitar_confirmacion", "procesando", "confirmando"
        )

        # La solicitud puede ejecutarse
        self.machine.add_transition(
            "ejecutar", ["procesando", "confirmando"], "ejecutando"
        )

        # Terminar una operación
        self.machine.add_transition(
            "finalizar", "ejecutando", "inactivo"
        )

        # Volver a escuchar para corregir
        self.machine.add_transition(
            "reintentar", ["procesando", "confirmando"], "escuchando"
        )

        # Registrar un error
        self.machine.add_transition(
            "fallar",
            ["escuchando", "procesando", "confirmando", "ejecutando"],
            "error"
        )

        # Recuperarse de un error
        self.machine.add_transition(
            "recuperar", "error", "inactivo"
        )

        # Cancelar una operación
        self.machine.add_transition(
            "cancelar",
            ["escuchando", "procesando", "confirmando"],
            "inactivo"
        )

    def mostrar_estado(self):
        print("Estado actual:", self.state)

    # Evaluar los niveles de confianza de EMMA
    def evaluar_confianza(self, datos):

        confianza = datos["interpretation"]["confidence"]

        if confianza >= self.cmax:
            return "aceptar"

        elif confianza >= self.cmin:
            return "confirmar"

        else:
            return "rechazar"

    # Registrar una solicitud o confirmación no entendida
    def registrar_nomatch(self):

        if self.state not in ["procesando", "confirmando"]:
            return

        self.try_nomatch += 1

        print("Solicitud no entendida.")
        print("Intento:", self.try_nomatch, "de", self.max_try)

        if self.try_nomatch >= self.max_try:
            self.machine_pendiente = None
            self.fallar()

        elif self.state == "procesando":
            self.reintentar()

        else:
            print("Por favor, confirma con sí o no.")

    # Registrar cuando no se recibe ninguna respuesta
    def registrar_noinput(self):

        if self.state != "escuchando":
            return

        self.try_noinput += 1

        print("Noinput registrado:", self.try_noinput)

        if self.try_noinput >= self.max_try:
            self.fallar()
        else:
            print("No recibí respuesta. Puedes intentarlo otra vez.")

    # Recibir una interpretación EMMA enviada por el bus de eventos
    def recibir_emma(self, datos):

        # Comprobar si estamos esperando una confirmación
        if self.state == "confirmando":

            decision = self.evaluar_confianza(datos)

            # Confianza insuficiente: registrar Nomatch
            if decision != "aceptar":
                self.registrar_nomatch()
                self.mostrar_estado()
                return

            # Obtener la respuesta desde EMMA
            respuesta = datos["interpretation"]["text"]

            # Procesar la respuesta afirmativa o negativa
            self.responder_confirmacion(respuesta)
            return

        # Si el asistente está inactivo, iniciar una interacción
        if self.state == "inactivo":
            self.iniciar_interaccion()

        # Comprobar que podemos recibir una solicitud
        if self.state != "escuchando":
            print("No puedo recibir solicitudes en este estado:", self.state)
            return

        # Cambiar al estado procesando
        self.recibir_solicitud()

        # Obtener los datos de la interpretación EMMA
        texto = datos["interpretation"]["text"]
        decision = self.evaluar_confianza(datos)

        print("Interpretación recibida:", texto)
        print("Decisión:", decision)

        # Confianza baja: registrar Nomatch
        if decision == "rechazar":
            self.registrar_nomatch()
            self.mostrar_estado()
            return

        # Buscar la máquina solicitada
        machine = search_machine(self.data, texto)

        # Si la máquina no existe, volver a escuchar
        if machine is None:
            print("No se encontró la máquina:", texto)
            self.reintentar()
            self.mostrar_estado()
            return

        # Confianza media: solicitar confirmación
        if decision == "confirmar":
            self.machine_pendiente = machine
            self.solicitar_confirmacion()

            print("¿Te refieres a la máquina", machine["nombre"], "?")
            self.mostrar_estado()
            return

        # Confianza alta: ejecutar la consulta
        if decision == "aceptar":
            self.ejecutar()

            print("Máquina encontrada:", machine["nombre"])

            for pieza in machine["piezas"]:
                print("Pieza disponible:", pieza["nombre"])

            # Comunicar el resultado a la interfaz gráfica
            if hasattr(self, "bus"):
                self.bus.publicar(
                    "resultado_consulta",
                    {"machine": machine}
                )

            self.finalizar()
            self.mostrar_estado()

    # Procesar la respuesta a una confirmación
    def responder_confirmacion(self, respuesta):

        # Comprobar que estamos esperando una confirmación
        if self.state != "confirmando":
            print("No hay ninguna confirmación pendiente.")
            return

        # Normalizar la respuesta
        respuesta = respuesta.strip().lower()

        # El usuario confirma la máquina
        if respuesta in ["si", "sí"]:
            self.ejecutar()

            machine = self.machine_pendiente

            print("Máquina confirmada:", machine["nombre"])

            for pieza in machine["piezas"]:
                print("Pieza disponible:", pieza["nombre"])

            # Comunicar el resultado a la interfaz gráfica
            if hasattr(self, "bus"):
                self.bus.publicar(
                    "resultado_consulta",
                    {"machine": machine}
                )

            self.machine_pendiente = None
            self.finalizar()

        # El usuario rechaza la máquina
        elif respuesta == "no":
            print("Confirmación rechazada. Inténtalo nuevamente.")

            self.machine_pendiente = None
            self.reintentar()

        # La respuesta no es válida
        else:
            print("Respuesta de confirmación no válida.")
            self.registrar_nomatch()

        self.mostrar_estado()

    # Conectar el gestor con el bus de eventos
    def conectar_bus(self, bus):
        self.bus = bus

        self.bus.suscribir(
            "NewContextRequest",
            self.gestionar_contexto
        )

        self.bus.suscribir(
            "DoneNotification",
            self.gestionar_resultado
        )

    # Gestionar la solicitud de un nuevo contexto
    def gestionar_contexto(self, datos):

        if self.state != "inactivo":
            print("El asistente ya tiene una interacción activa.")
            return

        self.iniciar_interaccion()

        print("Nuevo contexto solicitado por:", datos["source"])

        self.bus.publicar(
            "StartRequest",
            {"target": datos["source"]}
        )

    # Procesar el resultado de un componente de modalidad
    def gestionar_resultado(self, datos):

        print("Resultado recibido de:", datos["source"])

        interpretacion = datos["emma"]

        self.recibir_emma(interpretacion)
