import json

def extraer_amenazas():
    amenazas = [
        {"id": 4, "nodo_id": 4, "descripcion": "zona de incendios forestales", "nivel_riesgo": 3},
        {"id": 5, "nodo_id": 5, "descripcion": "corte de energía frecuente", "nivel_riesgo": 2}
    ]
    with open("amenaza_3.json", "w") as f:
        json.dump(amenazas, f, indent=2)

if __name__ == "__main__":
    extraer_amenazas()
