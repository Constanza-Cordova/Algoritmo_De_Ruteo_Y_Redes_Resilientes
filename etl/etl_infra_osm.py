#!/usr/bin/env python3
"""
ETL: Extracción de red vial desde OpenStreetMap
Fase 2 - Infraestructura
"""
import json
import os
import shutil
import requests
from typing import Dict, List, Tuple
import time

# Configuración
OSM_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
SANTIAGO_CENTRO_BBOX = (-33.50, -70.70, -33.40, -70.60)  # (sur, oeste, norte, este)

# Tipos de vías a incluir (highway types de OSM)
HIGHWAY_TYPES = [
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "residential", "living_street", "service",
    "motorway_link", "trunk_link", "primary_link", "secondary_link"
]

def build_overpass_query(bbox: Tuple[float, float, float, float]) -> str:
    """Construye query Overpass para extraer calles de Santiago Centro"""
    sur, oeste, norte, este = bbox
    highway_filter = '|'.join(HIGHWAY_TYPES)
    
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"~"^({highway_filter})$"]({sur},{oeste},{norte},{este});
    );
    out geom;
    """
    return query.strip()

def fetch_osm_data(bbox: Tuple[float, float, float, float]) -> Dict:
    """Extrae datos de OSM vía Overpass API"""
    query = build_overpass_query(bbox)
    print(f"📡 Consultando Overpass API...")
    
    try:
        response = requests.post(
            OSM_OVERPASS_URL,
            data={'data': query},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ Obtenidos {len(data.get('elements', []))} elementos")
        return data
    except requests.RequestException as e:
        print(f"⚠️  Error al consultar OSM: {e}")
        print("   Usando datos demo...")
        return _get_demo_data()

def _get_demo_data() -> Dict:
    """Datos demo si OSM falla (red básica Santiago Centro)"""
    return {
        "elements": [
            {
                "type": "way",
                "id": 1,
                "tags": {"name": "Av. Libertador Bernardo O'Higgins", "highway": "primary"},
                "geometry": [
                    {"lat": -33.4450, "lon": -70.6700},
                    {"lat": -33.4450, "lon": -70.6500}
                ]
            },
            {
                "type": "way",
                "id": 2,
                "tags": {"name": "Calle San Diego", "highway": "secondary"},
                "geometry": [
                    {"lat": -33.4400, "lon": -70.6590},
                    {"lat": -33.4600, "lon": -70.6590}
                ]
            },
            {
                "type": "way",
                "id": 3,
                "tags": {"name": "Calle Bandera", "highway": "secondary"},
                "geometry": [
                    {"lat": -33.4400, "lon": -70.6560},
                    {"lat": -33.4600, "lon": -70.6560}
                ]
            },
            {
                "type": "way",
                "id": 4,
                "tags": {"name": "Calle Moneda", "highway": "tertiary"},
                "geometry": [
                    {"lat": -33.4420, "lon": -70.6700},
                    {"lat": -33.4420, "lon": -70.6500}
                ]
            }
        ]
    }

def transform_to_geojson(osm_data: Dict) -> Dict:
    """Transforma elementos OSM a GeoJSON de calles"""
    features = []
    
    for element in osm_data.get('elements', []):
        if element.get('type') != 'way' or 'geometry' not in element:
            continue
            
        coords = [
            [node['lon'], node['lat']] 
            for node in element['geometry']
        ]
        
        if len(coords) < 2:
            continue
        
        tags = element.get('tags', {})
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "osm_id": element.get('id'),
                "nombre": tags.get('name', 'Sin nombre'),
                "tipo_via": tags.get('highway', 'unknown'),
                "superficie": tags.get('surface', 'unknown'),
                "carriles": tags.get('lanes', '1'),
                "sentido": tags.get('oneway', 'no'),
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def transform_to_nodes_edges(osm_data: Dict) -> Dict:
    """Transforma OSM a formato nodos/aristas para pgRouting"""
    nodes_dict = {}
    edges = []
    node_counter = 0
    edge_counter = 0
    
    for element in osm_data.get('elements', []):
        if element.get('type') != 'way' or 'geometry' not in element:
            continue
        
        geometry = element['geometry']
        tags = element.get('tags', {})
        
        # Procesar nodos de esta vía
        way_nodes = []
        for node in geometry:
            node_key = f"{node['lon']:.6f},{node['lat']:.6f}"
            
            if node_key not in nodes_dict:
                node_id = f"N{node_counter}"
                nodes_dict[node_key] = {
                    "id": node_id,
                    "lat": node['lat'],
                    "lon": node['lon'],
                    "tipo": "via"
                }
                node_counter += 1
            
            way_nodes.append(nodes_dict[node_key]['id'])
        
        # Crear aristas entre nodos consecutivos
        for i in range(len(way_nodes) - 1):
            source = way_nodes[i]
            target = way_nodes[i + 1]
            
            # Calcular costo aproximado (distancia euclidiana simple)
            source_coords = next(n for n in nodes_dict.values() if n['id'] == source)
            target_coords = next(n for n in nodes_dict.values() if n['id'] == target)
            
            # Distancia aproximada en metros (fórmula simple)
            lat_diff = target_coords['lat'] - source_coords['lat']
            lon_diff = target_coords['lon'] - source_coords['lon']
            dist_aprox = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111000  # ~111km por grado
            
            edge = {
                "id": f"E{edge_counter}",
                "source": source,
                "target": target,
                "costo": round(dist_aprox, 2),
                "nombre": tags.get('name', 'Sin nombre'),
                "tipo_via": tags.get('highway', 'unknown'),
                "osm_way_id": element.get('id')
            }
            edges.append(edge)
            edge_counter += 1
    
    return {
        "nodos": list(nodes_dict.values()),
        "aristas": edges
    }

def export_files(geojson_data: Dict, nodes_edges_data: Dict, out_dir: str):
    """Exporta archivos JSON y GeoJSON"""
    os.makedirs(out_dir, exist_ok=True)
    
    # GeoJSON
    geojson_path = os.path.join(out_dir, "infraestructura.geojson")
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Exportado: {geojson_path}")
    
    # Nodos/Aristas JSON
    json_path = os.path.join(out_dir, "infraestructura.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(nodes_edges_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Exportado: {json_path}")
    
    # Copiar a web/data si existe
    web_data_dir = os.environ.get("WEB_DATA_DIR")
    if web_data_dir and os.path.isdir(web_data_dir):
        shutil.copy2(geojson_path, os.path.join(web_data_dir, "infraestructura.geojson"))
        shutil.copy2(json_path, os.path.join(web_data_dir, "infraestructura.json"))
        print(f"✓ Copiado a {web_data_dir}")

def main(out_dir: str = "/app/out"):
    """Ejecuta ETL completo de infraestructura"""
    print("=" * 60)
    print("ETL INFRAESTRUCTURA - Red Vial OpenStreetMap")
    print("=" * 60)
    
    # 1. Extraer
    osm_data = fetch_osm_data(SANTIAGO_CENTRO_BBOX)
    
    # 2. Transformar
    geojson_data = transform_to_geojson(osm_data)
    nodes_edges_data = transform_to_nodes_edges(osm_data)
    
    print(f"📊 Estadísticas:")
    print(f"   - Nodos: {len(nodes_edges_data['nodos'])}")
    print(f"   - Aristas: {len(nodes_edges_data['aristas'])}")
    print(f"   - Features GeoJSON: {len(geojson_data['features'])}")
    
    # 3. Cargar (exportar archivos)
    export_files(geojson_data, nodes_edges_data, out_dir)
    
    print("✅ ETL Infraestructura completado")
    return geojson_data, nodes_edges_data

if __name__ == "__main__":
    main()
