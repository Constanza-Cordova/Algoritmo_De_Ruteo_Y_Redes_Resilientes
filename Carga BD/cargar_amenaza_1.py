import json
import psycopg2

def cargar_amenazas():
    conn = psycopg2.connect(dbname="tu_bd", user="usuario", password="clave", host="localhost")
    cur = conn.cursor()

    with open("Amenazas/amenaza_1.json") as f:
        amenazas = json.load(f)

    for amenaza in amenazas:
        cur.execute("""
            INSERT INTO amenaza (id, nodo_id, descripcion, nivel_riesgo)
            VALUES (%s, %s, %s, %s)
        """, (amenaza["id"], amenaza["nodo_id"], amenaza["descripcion"], amenaza["nivel_riesgo"]))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    cargar_amenazas()
