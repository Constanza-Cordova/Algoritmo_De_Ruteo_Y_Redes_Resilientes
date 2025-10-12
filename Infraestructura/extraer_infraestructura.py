import json

def extraer_infraestructura():
    nodos = [{"id": 1, "nombre": "A", "lat": -33.45, "lon": -70.66}]
    aristas = [{"id": 1, "origen": 1, "destino": 2, "longitud": 120.5}]
    with open("infraestructura.json", "w") as f:
        json.dump({"nodos": nodos, "aristas": aristas}, f, indent=2)

if __name__ == "__main__":
    extraer_infraestructura()
