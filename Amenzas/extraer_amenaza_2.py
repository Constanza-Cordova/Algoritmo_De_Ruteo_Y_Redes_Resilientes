import json

def extraer_amenazas():
    amenazas = [
        {"id": 2, "nodo_id": 2, "descripcion": "deslizamiento de tierra", "nivel_riesgo": 4},
        {"id": 3, "nodo_id": 3, "descripcion": "zona sísmica activa", "nivel_riesgo": 5}
    ]
    with open("amenaza_2.json", "w") as f:
        json.dump(amenazas, f, indent=2)

if __name__ == "__main__":
    extraer_amenazas()
