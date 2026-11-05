# Asistente multimodal — Aceros Paco S.L.

## Descripción
Prototipo de asistente multimodal desarrollado en Python
para consultar máquinas y piezas de un taller industrial.

## Tecnologías
- Python
- PySide6
- transitions
- JSON
- EventBus
- Interpretaciones EMMA simplificadas
- Eventos MMI simulados

## Instalación

Desde la carpeta principal del proyecto:

```powershell
py -m pip install PySide6 transitions
```

## Ejecución

### Interfaz gráfica
```powershell
py -m principal.interface
```

### Interfaz de consola
```powershell
py -m principal
```
Prueba 1. Estado inicial

Comprobar que el gestor comienza en estado inactivo.

gestor = InteractionManager()
print(gestor.state)

Resultado esperado: inactivo

Prueba 2. Inicio de una interacción

Comprobar la transición de inactivo a escuchando.

gestor = InteractionManager()
gestor.iniciar_interaccion()
print(gestor.state)

Resultado esperado: escuchando

Prueba 3. Solicitud con confianza alta

Simular una solicitud de la máquina Cizalla con una confianza del 95 %.

gestor = InteractionManager()
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.95))
print(gestor.state)

Resultado esperado: se muestran las piezas Rodamiento y Cuchilla. El gestor finaliza en inactivo.

Prueba 4. Solicitud con confianza media y confirmación positiva

Simular una solicitud con confianza del 65 %, que requiere confirmación explícita del usuario.

gestor = InteractionManager()
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.65))
print(gestor.state)

Resultado esperado: el gestor pregunta si se refiere a Cizalla y pasa a confirmando.

Responder afirmativamente:

gestor.recibir_emma(crear_emma("sí", "voz", 0.95))
print(gestor.state)

Resultado esperado: muestra las piezas de Cizalla y regresa a inactivo.

Prueba 5. Rechazar una confirmación

Comprobar qué ocurre cuando el usuario indica que la máquina propuesta no es la correcta.

gestor = InteractionManager()
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.65))
gestor.recibir_emma(crear_emma("no", "voz", 0.95))
print(gestor.state)

Resultado esperado: escuchando, permitiendo realizar una nueva solicitud.

Prueba 6. Solicitud con confianza baja (Nomatch)

Enviar tres solicitudes con confianza insuficiente.

gestor = InteractionManager()
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.20))
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.20))
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.20))
print(gestor.try_nomatch)
print(gestor.state)

Resultado esperado:

3
error

El gestor registra tres intentos fallidos y entra en estado de error.

Prueba 7. Ausencia de respuesta (Noinput)

Simular que el usuario no responde durante tres intentos.

gestor = InteractionManager()
gestor.iniciar_interaccion()
gestor.registrar_noinput()
gestor.registrar_noinput()
gestor.registrar_noinput()
print(gestor.try_noinput)
print(gestor.state)

Resultado esperado:

3
error

Prueba 8. Cancelación de una interacción

Comprobar que el usuario puede cancelar una interacción activa.

gestor = InteractionManager()
gestor.iniciar_interaccion()
gestor.cancelar()
print(gestor.state)

Resultado esperado: inactivo

Prueba 9. Recuperación de un error

Provocar un error por falta de respuestas y recuperar el funcionamiento del gestor.

gestor = InteractionManager()
gestor.iniciar_interaccion()
gestor.registrar_noinput()
gestor.registrar_noinput()
gestor.registrar_noinput()
print(gestor.state)
gestor.recuperar()
print(gestor.state)

Resultado esperado: primero error y después inactivo.

Prueba 10. Máquina inexistente

Comprobar el comportamiento cuando se solicita una máquina que no está registrada en el catálogo.

gestor = InteractionManager()
gestor.recibir_emma(crear_emma("Máquina inexistente", "teclado", 1.0))
print(gestor.state)

Resultado esperado: informa que no encontró la máquina y vuelve a escuchando.

Prueba 11. Confianza insuficiente durante una confirmación

Comprobar que tres respuestas de baja confianza durante una confirmación provocan un error.

gestor = InteractionManager()
gestor.recibir_emma(crear_emma("Cizalla", "voz", 0.65))
gestor.recibir_emma(crear_emma("tal vez", "voz", 0.20))
gestor.recibir_emma(crear_emma("tal vez", "voz", 0.20))
gestor.recibir_emma(crear_emma("tal vez", "voz", 0.20))
print(gestor.try_nomatch)
print(gestor.state)

Resultado esperado:

3
error

Prueba 12. Reinicio de contadores

Comprobar que los contadores de errores se reinician cuando comienza una nueva interacción.

gestor = InteractionManager()
gestor.iniciar_interaccion()
gestor.registrar_noinput()
print(gestor.try_noinput)
gestor.cancelar()
gestor.iniciar_interaccion()
print(gestor.try_noinput)

Resultado esperado: primero 1 y después 0.
## Pruebas automáticas

```powershell
py -m unittest discover -s test -p "pruebas.py" -v
```

## Funcionalidades implementadas
- Consulta de máquinas y sus piezas.
- Interfaz gráfica con PySide6.
- Máquina de estados para gestionar interacciones.
- Evaluación de niveles de confianza.
- Confirmación y recuperación de errores.
- Creación, guardado y lectura de interpretaciones EMMA.
- Comunicación mediante EventBus.
- Simulación de NewContextRequest, StartRequest
  y DoneNotification.
- Prueba automática del ciclo de eventos.