import json

def extraer_metadata():
    metadata = [
        {"id": 4, "nodo_id": 4, "tipo": "estado_pavimento", "valor": "regular"},
        {"id": 5, "nodo_id": 5, "tipo": "estado_pavimento", "valor": "excelente"}
    ]
    with open("metadata_3.json", "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    extraer_metadata()
