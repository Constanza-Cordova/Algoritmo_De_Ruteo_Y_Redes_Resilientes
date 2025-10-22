#!/usr/bin/env python3
"""
ETL: Amenazas - Cortes de luz programados y no programados
Datos simulados realistas (en producción: API Enel/CGE)
"""
import json
import os
import shutil
from datetime import datetime, timedelta

def generar_datos_cortes_luz():
    """Genera datos realistas de cortes de luz"""
    ahora = datetime.now()
    
    return [
        {
            "id": 101,
            "tipo": "corte_programado",
            "comuna": "Santiago",
            "sector": "Barrio Brasil - Concha y Toro",
            "causa": "Mantención preventiva de red eléctrica",
            "lat": -33.4508,
            "lon": -70.6587,
            "radio_afectacion_m": 300,
            "inicio": (ahora + timedelta(hours=2)).isoformat(),
            "fin": (ahora + timedelta(hours=5)).isoformat(),
            "duracion_estimada_min": 180,
            "clientes_afectados": 1200,
            "calles_afectadas": ["Concha y Toro", "Huérfanos", "Compañía"],
            "empresa": "Enel Distribución Chile",
            "aviso_previo": True,
            "fuente": "enel_api"
        },
        {
            "id": 102,
            "tipo": "corte_no_programado",
            "comuna": "Santiago",
            "sector": "San Diego - Av. Matta",
            "causa": "Falla en transformador",
            "lat": -33.4547,
            "lon": -70.6471,
            "radio_afectacion_m": 250,
            "inicio": (ahora - timedelta(minutes=30)).isoformat(),
            "fin": (ahora + timedelta(hours=2)).isoformat(),
            "duracion_estimada_min": 150,
            "clientes_afectados": 850,
            "calles_afectadas": ["San Diego", "Av. Matta", "Santa Rosa"],
            "empresa": "Enel Distribución Chile",
            "aviso_previo": False,
            "fuente": "enel_api"
        },
        {
            "id": 103,
            "tipo": "corte_programado",
            "comuna": "Santiago",
            "sector": "Barrio Cívico - Teatinos",
            "causa": "Renovación de postación",
            "lat": -33.4417,
            "lon": -70.6548,
            "radio_afectacion_m": 200,
            "inicio": (ahora + timedelta(hours=1)).isoformat(),
            "fin": (ahora + timedelta(hours=2, minutes=30)).isoformat(),
            "duracion_estimada_min": 90,
            "clientes_afectados": 500,
            "calles_afectadas": ["Teatinos", "Morandé", "Bandera"],
            "empresa": "Enel Distribución Chile",
            "aviso_previo": True,
            "fuente": "enel_api"
        },
        {
            "id": 104,
            "tipo": "corte_no_programado",
            "comuna": "Santiago",
            "sector": "Santa Lucía - Parque Forestal",
            "causa": "Daño en cables por condiciones climáticas",
            "lat": -33.4388,
            "lon": -70.6412,
            "radio_afectacion_m": 350,
            "inicio": (ahora - timedelta(hours=1)).isoformat(),
            "fin": (ahora + timedelta(hours=3)).isoformat(),
            "duracion_estimada_min": 240,
            "clientes_afectados": 1500,
            "calles_afectadas": ["José Victorino Lastarria", "Merced", "Parque Forestal"],
            "empresa": "Enel Distribución Chile",
            "aviso_previo": False,
            "fuente": "enel_api"
        },
        {
            "id": 105,
            "tipo": "corte_programado",
            "comuna": "Santiago",
            "sector": "Alameda - Universidad de Chile",
            "causa": "Instalación de nuevo equipamiento",
            "lat": -33.4455,
            "lon": -70.6520,
            "radio_afectacion_m": 180,
            "inicio": (ahora + timedelta(hours=4)).isoformat(),
            "fin": (ahora + timedelta(hours=5, minutes=30)).isoformat(),
            "duracion_estimada_min": 90,
            "clientes_afectados": 600,
            "calles_afectadas": ["Alameda", "Mac Iver"],
            "empresa": "Enel Distribución Chile",
            "aviso_previo": True,
            "fuente": "enel_api"
        }
    ]

def convertir_a_geojson(datos):
    """Convierte lista de cortes a GeoJSON"""
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
    print("💡 ETL Amenazas Cortes de Luz - Generando datos...")
    os.makedirs(out_dir, exist_ok=True)
    
    # Generar datos
    datos = generar_datos_cortes_luz()
    geojson = convertir_a_geojson(datos)
    
    # Guardar JSON
    json_path = os.path.join(out_dir, "amenaza_cortes_luz.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    # Guardar GeoJSON
    geojson_path = os.path.join(out_dir, "amenaza_cortes_luz.geojson")
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    # Copiar a web/data
    web_data_dir = os.environ.get("WEB_DATA_DIR")
    if web_data_dir and os.path.isdir(web_data_dir):
        shutil.copy2(json_path, os.path.join(web_data_dir, "amenaza_cortes_luz.json"))
        shutil.copy2(geojson_path, os.path.join(web_data_dir, "amenaza_cortes_luz.geojson"))
    
    print(f"✓ Generados {len(datos)} cortes de luz")
    print(f"✓ {json_path}")
    print(f"✓ {geojson_path}")
    return datos

if __name__ == "__main__":
    main()
