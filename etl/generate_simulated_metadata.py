#!/usr/bin/env python3
import os, json, random
OUT_DIR = os.environ.get("OUT_PATH_DIR", "/app/web/data")
os.makedirs(OUT_DIR, exist_ok=True)
bbox = (-70.70, -33.50, -70.60, -33.40)

def gen(kind, n):
    features = []
    for i in range(n):
        lon = random.uniform(bbox[0], bbox[2])
        lat = random.uniform(bbox[1], bbox[3])
        if kind=='notarios':
            name = f"Notaría {i+1}"
            tipo = 'notaria'
            tiempo = random.choice([45,60,75])
            docs = "Cédula de identidad, Escritura, Poder notarial"
        elif kind=='chileatiende':
            name = f"ChileAtiende {i+1}"
            tipo = 'chileatiende'
            tiempo = random.choice([20,30,40])
            docs = "Cédula, Formulario"
        else:
            name = f"SII Oficina {i+1}"
            tipo = 'sii'
            tiempo = random.choice([30,45])
            docs = "Formulario, Comprobante pago"
        features.append({
            "type":"Feature",
            "properties":{
                "name": name,
                "address": f"Calle {random.randint(1,300)}",
                "tipo_oficina": tipo,
                "tiempo_tramite": tiempo,
                "documentos": docs,
                "horario": "L-V 09:00-16:00",
                "capacidad_estimada": random.randint(3,12)
            },
            "geometry": {"type":"Point", "coordinates":[lon,lat]}
        })
    return {"type":"FeatureCollection","features":features}

open(os.path.join(OUT_DIR,'notarios.geojson'),'w',encoding='utf-8').write(json.dumps(gen('notarios',15), ensure_ascii=False))
open(os.path.join(OUT_DIR,'chileatiende.geojson'),'w',encoding='utf-8').write(json.dumps(gen('chileatiende',10), ensure_ascii=False))
open(os.path.join(OUT_DIR,'sii.geojson'),'w',encoding='utf-8').write(json.dumps(gen('sii',8), ensure_ascii=False))
print("Metadata simulada creada en", OUT_DIR)
