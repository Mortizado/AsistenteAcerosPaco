import json
from datetime import datetime, timezone

def guardar_emma(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)


# Leer una interpretación EMMA desde un archivo JSON
def leer_emma(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos


def crear_emma(texto, modalidad, confianza):
    interpretacion = {
        "interpretation": {
            "text": texto,
            "modality": modalidad,
            "confidence": confianza,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alternatives": []
        }
    }
    

    return interpretacion


