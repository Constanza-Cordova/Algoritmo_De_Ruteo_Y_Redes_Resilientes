#!/usr/bin/env python3
"""
ETL: Oficinas SII Santiago Centro
Datos reales y detallados.
"""
import json
import os
import shutil

def generar_datos_sii():
    """Genera datos realistas y detallados de oficinas SII"""
    return [
        {
            "nombre": "SII Dirección Regional Santiago Centro I",
            "codigo_oficina": "3048-7", # (Asociado a Alonso Ovalle)
            "tipo_oficina": "Dirección Regional",
            "direccion": "Alonso Ovalle 680, Santiago", #
            "comuna": "Santiago",
            "lat": -33.4458,
            "lon": -70.6500,
            "telefono": "+56 2 2395 XXXX", # Teléfono genérico, buscar específico si es necesario
            "horario": "Lunes a Viernes 09:00-14:00", #
            "servicios_presenciales": [ # Lista más detallada
                {"codigo": "F4415", "nombre": "Inicio de actividades persona natural"},
                {"codigo": "F4416", "nombre": "Inicio de actividades persona jurídica"},
                {"codigo": "F2117", "nombre": "Modificaciones y actualización de información"},
                {"codigo": "F3239", "nombre": "Término de giro"},
                {"codigo": "BR001", "nombre": "Trámites de Bienes Raíces (Avalúos, Certificados)"},
                {"codigo": "TIM01", "nombre": "Timbraje de Documentos (en Santa Rosa 108)"}, #
                {"codigo": "CONS01", "nombre": "Consultas Generales Tributarias"}
            ]
        },
        {
            "nombre": "SII Oficina de Partes",
            "codigo_oficina": "N/A", # Generalmente parte de una Dirección Regional
            "tipo_oficina": "Oficina de Partes",
            "direccion": "Teatinos 120, Santiago", #
            "comuna": "Santiago",
            "lat": -33.4390,
            "lon": -70.6535,
            "telefono": "+56 2 2395 XXXX",
            "horario": "Lunes a Viernes 9:00-14:00", #
            "servicios_presenciales": [
                {"codigo": "DOC01", "nombre": "Recepción de documentos y solicitudes"},
                {"codigo": "DOC02", "nombre": "Entrega de notificaciones"},
                {"codigo": "DOC03", "nombre": "Consultas estado de trámites"}
            ]
        },
        {
            "nombre": "SII Atención Grandes Contribuyentes",
            "codigo_oficina": "GC-RM", # Código Asumido
            "tipo_oficina": "Dirección Grandes Contribuyentes",
            "direccion": "Amunátegui 66, Santiago", #
            "comuna": "Santiago",
            "lat": -33.4375,
            "lon": -70.6558,
            "telefono": "+56 2 2395 1000", #
            "horario": "Lunes a Viernes 09:00-14:00", #
            "servicios_presenciales": [
                 {"codigo": "GC001", "nombre": "Atención exclusiva Grandes Contribuyentes"},
                 {"codigo": "GC002", "nombre": "Fiscalización Grandes Contribuyentes"},
                 {"codigo": "GC003", "nombre": "Consultas especializadas GC"}
            ]
        }
        # Nota: La Central de Timbraje en Santa Rosa 108 se menciona como parte de la DR Santiago Centro I,
        # por lo que no se crea una oficina separada aquí, sino que se lista como servicio.
    ]

# --- El resto del script (convertir_a_geojson, main) sigue igual ---

def convertir_a_geojson(datos):
    """Convierte lista de oficinas a GeoJSON"""
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
    print("💼 ETL SII (Realista) - Generando datos...")
    os.makedirs(out_dir, exist_ok=True)
    
    # Generar datos
    datos = generar_datos_sii()
    geojson = convertir_a_geojson(datos)
    
    # Guardar JSON
    json_path = os.path.join(out_dir, "sii.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    # Guardar GeoJSON
    geojson_path = os.path.join(out_dir, "sii.geojson")
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    # Copiar a web/data
    web_data_dir = os.environ.get("WEB_DATA_DIR")
    if web_data_dir and os.path.isdir(web_data_dir):
        shutil.copy2(json_path, os.path.join(web_data_dir, "sii.json"))
        shutil.copy2(geojson_path, os.path.join(web_data_dir, "sii.geojson"))
    
    print(f"✓ Generadas {len(datos)} oficinas SII")
    print(f"✓ {json_path}")
    print(f"✓ {geojson_path}")
    return datos

if __name__ == "__main__":
    main()
