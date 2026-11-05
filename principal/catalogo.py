import json
from pathlib import Path

def list_machines():
    file_of_machines = Path(__file__).resolve().parent.parent / "data" / "machines.json"
    with open(file_of_machines, "r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    return data

def search_machine(data,machine_name):
  for maquina in data["maquinas"]:
    if maquina["nombre"].lower() == machine_name.lower():
        return maquina

  return None