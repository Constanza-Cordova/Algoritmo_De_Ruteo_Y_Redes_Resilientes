import json
import psycopg2

def cargar_metadata():
    conn = psycopg2.connect(dbname="tu_bd", user="usuario", password="clave", host="localhost")
    cur = conn.cursor()

    with open("Metadata/metadata_2.json") as f:
        metadata = json.load(f)

    for item in metadata:
        cur.execute("""
            INSERT INTO metadata (id, nodo_id, tipo, valor)
            VALUES (%s, %s, %s, %s)
        """, (item["id"], item["nodo_id"], item["tipo"], item["valor"]))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    cargar_metadata()
