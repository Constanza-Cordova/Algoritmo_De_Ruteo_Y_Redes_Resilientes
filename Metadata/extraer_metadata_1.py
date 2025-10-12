import json

def extraer_metadata():
    metadata = [
        {"id": 1, "nodo_id": 1, "tipo": "tipo_via", "valor": "asfaltada"}
    ]
    with open("metadata_1.json", "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    extraer_metadata()
