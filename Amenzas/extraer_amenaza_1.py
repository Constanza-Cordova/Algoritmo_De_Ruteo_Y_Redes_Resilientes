import json

def extraer_amenazas():
    amenazas = [
        {"id": 1, "nodo_id": 1, "descripcion": "inundación", "nivel_riesgo": 3}
    ]
    with open("amenaza_1.json", "w") as f:
        json.dump(amenazas, f, indent=2)

if __name__ == "__main__":
    extraer_amenazas()
