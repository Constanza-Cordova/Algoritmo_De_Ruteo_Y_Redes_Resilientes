import json
import psycopg2

def cargar():
    conn = psycopg2.connect(dbname="tu_bd", user="usuario", password="clave")
    cur = conn.cursor()

    with open("infraestructura.json") as f:
        data = json.load(f)

    for nodo in data["nodos"]:
        cur.execute("INSERT INTO nodo (id, nombre, latitud, longitud) VALUES (%s, %s, %s, %s)",
                    (nodo["id"], nodo["nombre"], nodo["lat"], nodo["lon"]))

    for arista in data["aristas"]:
        cur.execute("INSERT INTO arista (id, origen, destino, longitud) VALUES (%s, %s, %s, %s)",
                    (arista["id"], arista["origen"], arista["destino"], arista["longitud"]))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    cargar()
