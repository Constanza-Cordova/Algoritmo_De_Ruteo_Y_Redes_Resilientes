import json

def extraer_metadata():
    metadata = [
        {"id": 2, "nodo_id": 2, "tipo": "iluminacion", "valor": "buena"},
        {"id": 3, "nodo_id": 3, "tipo": "iluminacion", "valor": "deficiente"}
    ]
    with open("metadata_2.json", "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    extraer_metadata()
