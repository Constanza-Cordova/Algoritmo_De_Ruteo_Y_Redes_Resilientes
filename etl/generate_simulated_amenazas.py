#!/usr/bin/env python3
import os, json, random, math
OUT_DIR = os.environ.get("OUT_PATH_DIR", "/app/web/data")
os.makedirs(OUT_DIR, exist_ok=True)
bbox = (-70.70, -33.50, -70.60, -33.40)

def random_point():
    return (random.uniform(bbox[0], bbox[2]), random.uniform(bbox[1], bbox[3]))

alerts = {"type":"FeatureCollection","features":[]}
for i in range(5):
    lon,lat = random_point()
    coords=[]
    for a in range(8):
        ang = math.radians(a * 45)
        r = random.uniform(0.0015, 0.0045)
        x = lon + r * math.cos(ang)
        y = lat + r * math.sin(ang)
        coords.append([x,y])
    coords.append(coords[0])
    alerts['features'].append({
        "type":"Feature",
        "properties":{
            "title": f"Manifestación {i+1}",
            "severity": random.choice(["low","medium","high"]),
            "start_time": "2025-10-18T10:00:00Z"
        },
        "geometry":{"type":"Polygon","coordinates":[coords]}
    })

cortes = {"type":"FeatureCollection","features":[]}
for i in range(6):
    lon,lat = random_point()
    cortes['features'].append({
        "type":"Feature",
        "properties":{
            "affected_barrio": f"Barrio {random.randint(1,10)}",
            "expected_duration_hours": random.choice([2,4,8,24])
        },
        "geometry":{"type":"Point","coordinates":[lon,lat]}
    })

open(os.path.join(OUT_DIR,'amenaza_alertas.geojson'),'w',encoding='utf-8').write(json.dumps(alerts, ensure_ascii=False))
open(os.path.join(OUT_DIR,'amenaza_cortes_luz.geojson'),'w',encoding='utf-8').write(json.dumps(cortes, ensure_ascii=False))
print("Amenazas simuladas creadas en", OUT_DIR)
