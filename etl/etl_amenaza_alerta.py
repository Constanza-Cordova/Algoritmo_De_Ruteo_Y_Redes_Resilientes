#!/usr/bin/env python3
"""
ETL: Amenazas - Alertas de tráfico y manifestaciones
Datos simulados realistas (en producción: Waze API)
"""
import json
import os
import shutil
from datetime import datetime, timedelta

def generar_datos_alertas():
    """Genera datos realistas de alertas de tráfico"""
    ahora = datetime.now()
    
    return [
        {
            "id": 1,
            "tipo": "manifestacion",
            "severidad": 4,
            "titulo": "Manifestación en Plaza Baquedano",
            "descripcion": "Concentración con marchas intermitentes hacia La Moneda",
            "lat": -33.4378,
            "lon": -70.6341,
            "radio_afectacion_m": 500,
            "inicio": (ahora - timedelta(hours=2)).isoformat(),
            "fin": (ahora + timedelta(hours=3)).isoformat(),
            "fuente": "carabineros_chile",
            "calles_afectadas": ["Av. Libertador Bernardo O'Higgins", "Vicuña Mackenna"],
            "recomendacion": "Evitar sector, usar vías alternativas"
        },
        {
            "id": 2,
            "tipo": "corte_calle",
            "severidad": 3,
            "titulo": "Corte de tránsito San Diego",
            "descripcion": "Intervención de calzada por trabajos de emergencia",
            "lat": -33.4526,
            "lon": -70.6368,
            "radio_afectacion_m": 300,
            "inicio": (ahora - timedelta(minutes=45)).isoformat(),
            "fin": (ahora + timedelta(hours=4)).isoformat(),
            "fuente": "aguas_andinas",
            "calles_afectadas": ["San Diego", "Av. Matta"],
            "recomendacion": "Desvío por Santa Rosa"
        },
        {
            "id": 3,
            "tipo": "manifestacion",
            "severidad": 2,
            "titulo": "Actividad sindical Alameda",
            "descripcion": "Grupo con pancartas, tránsito lento pero fluido",
            "lat": -33.4450,
            "lon": -70.6450,
            "radio_afectacion_m": 200,
            "inicio": (ahora - timedelta(minutes=30)).isoformat(),
            "fin": (ahora + timedelta(hours=2)).isoformat(),
            "fuente": "carabineros_chile",
            "calles_afectadas": ["Av. Libertador Bernardo O'Higgins"],
            "recomendacion": "Considerar 15-20 min de retraso"
        },
        {
            "id": 4,
            "tipo": "accidente",
            "severidad": 3,
            "titulo": "Accidente de tránsito Nataniel Cox",
            "descripcion": "Colisión entre vehículos, una pista bloqueada",
            "lat": -33.4473,
            "lon": -70.6498,
            "radio_afectacion_m": 250,
            "inicio": (ahora - timedelta(minutes=20)).isoformat(),
            "fin": (ahora + timedelta(hours=1)).isoformat(),
            "fuente": "carabineros_chile",
            "calles_afectadas": ["Nataniel Cox", "Alameda"],
            "recomendacion": "Tránsito por pista izquierda únicamente"
        },
        {
            "id": 5,
            "tipo": "aglomeracion",
            "severidad": 2,
            "titulo": "Alta afluencia Barrio Lastarria",
            "descripcion": "Evento cultural, alta concentración peatonal",
            "lat": -33.4399,
            "lon": -70.6418,
            "radio_afectacion_m": 150,
            "inicio": (ahora - timedelta(minutes=15)).isoformat(),
            "fin": (ahora + timedelta(hours=5)).isoformat(),
            "fuente": "municipalidad_santiago",
            "calles_afectadas": ["José Victorino Lastarria", "Rosal"],
            "recomendacion": "Velocidad reducida, prioridad peatonal"
        },
        {
            "id": 6,
            "tipo": "manifestacion",
            "severidad": 3,
            "titulo": "Concentración Plaza de Armas",
            "descripcion": "Actividad pacífica con presencia policial",
            "lat": -33.4370,
            "lon": -70.6505,
            "radio_afectacion_m": 400,
            "inicio": (ahora - timedelta(minutes=10)).isoformat(),
            "fin": (ahora + timedelta(hours=3)).isoformat(),
            "fuente": "carabineros_chile",
            "calles_afectadas": ["Puente", "Compañía", "21 de Mayo"],
            "recomendacion": "Evitar circulación por el centro de la plaza"
        },
        {
            "id": 7,
            "tipo": "corte_calle",
            "severidad": 4,
            "titulo": "Cierre Bandera por evento",
            "descripcion": "Calle completamente cerrada por evento oficial",
            "lat": -33.4420,
            "lon": -70.6560,
            "radio_afectacion_m": 200,
            "inicio": (ahora - timedelta(hours=1)).isoformat(),
            "fin": (ahora + timedelta(hours=2)).isoformat(),
            "fuente": "ministerio_interior",
            "calles_afectadas": ["Bandera"],
            "recomendacion": "Usar Morandé o Teatinos como alternativa"
        },
        {
            "id": 8,
            "tipo": "trabajos",
            "severidad": 2,
            "titulo": "Mantención Av. Matta",
            "descripcion": "Trabajos de pavimentación, una pista habilitada",
            "lat": -33.4555,
            "lon": -70.6490,
            "radio_afectacion_m": 300,
            "inicio": (ahora - timedelta(hours=3)).isoformat(),
            "fin": (ahora + timedelta(hours=6)).isoformat(),
            "fuente": "serviu",
            "calles_afectadas": ["Av. Matta"],
            "recomendacion": "Transitar con precaución, velocidad reducida"
        }
    ]

def convertir_a_geojson(datos):
    """Convierte lista de amenazas a GeoJSON"""
    features = []
    for item in datos:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item["lon"], item["lat"]]
            },
            "properties": {k: v for k, v in item.items() if k not in ["lat", "lon"]}
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def main(out_dir="/app/out"):
    """Función principal del ETL"""
    print("⚠️  ETL Amenazas Alertas - Generando datos...")
    os.makedirs(out_dir, exist_ok=True)
    
    # Generar datos
    datos = generar_datos_alertas()
    geojson = convertir_a_geojson(datos)
    
    # Guardar JSON
    json_path = os.path.join(out_dir, "amenaza_alertas.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    # Guardar GeoJSON
    geojson_path = os.path.join(out_dir, "amenaza_alertas.geojson")
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    # Copiar a web/data
    web_data_dir = os.environ.get("WEB_DATA_DIR")
    if web_data_dir and os.path.isdir(web_data_dir):
        shutil.copy2(json_path, os.path.join(web_data_dir, "amenaza_alertas.json"))
        shutil.copy2(geojson_path, os.path.join(web_data_dir, "amenaza_alertas.geojson"))
    
    print(f"✓ Generadas {len(datos)} alertas")
    print(f"✓ {json_path}")
    print(f"✓ {geojson_path}")
    return datos

if __name__ == "__main__":
    main()
