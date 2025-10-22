#!/usr/bin/env python3
"""
ETL: Genera ruta con pgr_dijkstra simulando trámite de Compraventa
Ruta: Notaría → Conservador de Bienes Raíces → SII
*** CON FALLBACK VISUAL MÁS AGRESIVO: Si Dijkstra da un rodeo > 2.5x,
    dibuja una línea recta para claridad en la presentación. ***
"""
import json
import os
import shutil
import psycopg2
from psycopg2.extras import RealDictCursor
import math # Para calcular distancia recta

def get_connection():
    # (Misma función que ya tienes)
    return psycopg2.connect(
        host=os.getenv("PGHOST", "db"), port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "ruteo_resiliente"),
        user=os.getenv("PGUSER", "postgres"), password=os.getenv("PGPASSWORD", "postgres")
    )

def encontrar_vertice_cercano(cur, lat, lon):
    # (Misma función inteligente que ya tienes)
    print(f"   Buscando vértice cercano a ({lat}, {lon}) en el componente principal...")
    # ... (código SQL idéntico) ...
    cur.execute("""
        WITH componentes AS (
            SELECT component, COUNT(node) as num_nodos
            FROM pgr_connectedComponents('SELECT id, source, target, costo as cost FROM red_vial WHERE source IS NOT NULL AND costo > 0')
            GROUP BY component ORDER BY num_nodos DESC LIMIT 1
        ), vertices_validos AS (
            SELECT id FROM red_vial_vertices_pgr v
            JOIN pgr_connectedComponents('SELECT id, source, target, costo as cost FROM red_vial WHERE source IS NOT NULL AND costo > 0') cc ON v.id = cc.node
            JOIN componentes c ON cc.component = c.component
        )
        SELECT v.id, ST_Distance(v.the_geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) as dist
        FROM red_vial_vertices_pgr v JOIN vertices_validos vv ON v.id = vv.id
        ORDER BY v.the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """, (lon, lat, lon, lat))
    resultado = cur.fetchone()
    if resultado: print(f"   ✓ Vértice encontrado: {resultado['id']} (dist: {resultado['dist']:.0f}m)")
    else: print(f"   ❌ No se pudo encontrar un vértice válido para ({lat}, {lon})")
    return resultado


def haversine(lat1, lon1, lat2, lon2):
     # (Misma función que ya tienes)
    R = 6371000; phi1 = math.radians(lat1); phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1); delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)); return R * c

def generar_ruta_compraventa(cur):
    # (Misma definición de paradas que ya tienes)
    print("🏠 Simulando trámite: COMPRAVENTA DE INMUEBLE")
    print("=" * 60)
    paradas = [
        {"nombre": "Primera Notaría de Santiago", "tipo": "notaria", "direccion": "Moneda 975", "lat": -33.4420, "lon": -70.6545, "tiempo_tramite": 60, "documentos": ["..."]},
        {"nombre": "Conservador de Bienes Raíces Santiago", "tipo": "conservador", "direccion": "Morandé 440", "lat": -33.4380, "lon": -70.6540, "tiempo_tramite": 90, "documentos": ["..."]},
        {"nombre": "SII Santiago Centro", "tipo": "sii", "direccion": "Teatinos 120", "lat": -33.4370, "lon": -70.6530, "tiempo_tramite": 45, "documentos": ["..."]}
    ]
    print("\n📋 RUTA DEL TRÁMITE:"); [print(f"\n{i+1}. {p['nombre']}\n   📍 {p['direccion']}") for i, p in enumerate(paradas)]
    
    all_features = []; distancia_total_ruta = 0; distancia_total_directa = 0
    tiempo_total = sum(p['tiempo_tramite'] for p in paradas)
    
    print("\n🗺️  CALCULANDO RUTAS (con fallback visual MÁS AGRESIVO):")
    print("-" * 60)
    
    for i in range(len(paradas) - 1):
        origen = paradas[i]; destino = paradas[i + 1]
        distancia_directa_segmento = haversine(origen['lat'], origen['lon'], destino['lat'], destino['lon'])
        distancia_total_directa += distancia_directa_segmento
        print(f"\n🚶 Segmento {i+1}: {origen['nombre']} → {destino['nombre']}")
        print(f"   Distancia directa: {distancia_directa_segmento:.0f}m")
        
        v_origen = encontrar_vertice_cercano(cur, origen['lat'], origen['lon'])
        v_destino = encontrar_vertice_cercano(cur, destino['lat'], destino['lon'])
        
        rows = None; distancia_calculada_segmento = 0; ruta_valida = False

        if v_origen and v_destino:
            print(f"   Vértices: {v_origen['id']} → {v_destino['id']}")
            try:
                # (Misma consulta SQL a pgr_dijkstra que ya tienes)
                cur.execute("""
                    WITH ruta AS ( SELECT seq, node, edge, cost FROM pgr_dijkstra(
                        'SELECT id, source, target, costo as cost, reverse_costo as reverse_cost FROM red_vial WHERE source IS NOT NULL AND target IS NOT NULL AND costo > 0',
                        %s::bigint, %s::bigint, directed := false ) WHERE edge > 0 )
                    SELECT r.seq, ST_AsGeoJSON(rv.geom)::json AS geometry, COALESCE(rv.length_m, 0) AS distancia_m,
                           COALESCE(rv.nombre, 'Calle sin nombre') as calle, rv.tipo_via
                    FROM ruta r JOIN red_vial rv ON r.edge = rv.id ORDER BY r.seq;
                """, (v_origen['id'], v_destino['id']))
                rows = cur.fetchall()
                
                if rows:
                    distancia_calculada_segmento = sum(float(row['distancia_m'] or 0) for row in rows)
                    # *** ÚNICO CAMBIO: UMBRAL MÁS BAJO (2.5x) ***
                    if distancia_calculada_segmento < (distancia_directa_segmento * 2.5): # <-- DE 5 A 2.5
                         ruta_valida = True
                    else:
                        print(f"   ⚠️  Ruta Dijkstra descartada: demasiado larga ({distancia_calculada_segmento:.0f}m vs {distancia_directa_segmento:.0f}m). Usando fallback.")
            except Exception as e: print(f"   ❌ Error en pgr_dijkstra: {e}")
        
        if ruta_valida and rows:
            # Dijkstra OK: usar ruta calculada
            print(f"   ✓ Ruta Dijkstra válida: {distancia_calculada_segmento:.0f}m")
            distancia_total_ruta += distancia_calculada_segmento
            calles_usadas = []
            for row in rows:
                if row['geometry']:
                    all_features.append({"type": "Feature", "geometry": row['geometry'], "properties": { "tipo": "ruta_calculada", "segmento": i+1, "origen": origen['nombre'], "destino": destino['nombre'], "calle": row['calle'], "tipo_via": row['tipo_via'], "distancia_m": round(float(row['distancia_m'] or 0), 1), "secuencia": row['seq'] } })
                    if row['calle'] != 'Calle sin nombre' and row['calle'] not in calles_usadas: calles_usadas.append(row['calle'])
            if calles_usadas: print(f"   ✓ Calles principales: {', '.join(calles_usadas[:3])}")
        else:
            # Fallback: dibujar línea recta
            if not (v_origen and v_destino): print(f"   ⚠️  Fallback: No se encontraron vértices válidos.")
            elif not rows: print(f"   ⚠️  Fallback: pgr_dijkstra no encontró ruta.")
            print(f"   ➡️  Dibujando línea recta visual.")
            distancia_total_ruta += distancia_directa_segmento
            all_features.append({"type": "Feature", "geometry": { "type": "LineString", "coordinates": [[origen['lon'], origen['lat']], [destino['lon'], destino['lat']]] }, "properties": { "tipo": "ruta_fallback", "segmento": i+1, "origen": origen['nombre'], "destino": destino['nombre'], "distancia_m": round(distancia_directa_segmento, 1), "nota": "Línea recta visual" } })

    # (Misma lógica para agregar marcadores de paradas)
    for i, parada in enumerate(paradas):
        all_features.append({"type": "Feature", "geometry": { "type": "Point", "coordinates": [parada['lon'], parada['lat']] }, "properties": { "tipo": "parada", "numero": i+1, "nombre": parada['nombre'], "direccion": parada['direccion'], "tipo_oficina": parada['tipo'], "tiempo_tramite": parada['tiempo_tramite'], "documentos": parada['documentos'] } })
    
    tiempo_caminata_total = round(distancia_total_ruta / 83.33)
    tiempo_total += tiempo_caminata_total
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL TRÁMITE (Distancia Ruta Real / Fallback):") # Título ajustado
    print(f"   📏 Distancia total ruta: {distancia_total_ruta/1000:.2f} km")
    print(f"   🚶 Tiempo caminando: {tiempo_caminata_total} min")
    print(f"   📋 Tiempo en trámites: {sum(p['tiempo_tramite'] for p in paradas)} min")
    print(f"   ⏱️  TIEMPO TOTAL ESTIMADO: {tiempo_total} min ({tiempo_total/60:.1f} horas)")
    print("=" * 60)
    
    return all_features, distancia_total_ruta, tiempo_total

def main(out_dir="/app/out"):
    # (Misma función main que ya tenías)
    print("\n" + "🚀 " * 20); print("GENERADOR DE RUTA - TRÁMITE DE COMPRAVENTA (con fallback visual MÁS AGRESIVO)"); print("Algoritmo: pgr_dijkstra / Línea Recta si falla"); print("🚀 " * 20 + "\n")
    os.makedirs(out_dir, exist_ok=True); out_file = os.path.join(out_dir, "ruta_dijkstra.geojson")
    try:
        conn = get_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT (SELECT COUNT(*) FROM red_vial WHERE source IS NOT NULL) as aristas, (SELECT COUNT(*) FROM red_vial_vertices_pgr) as vertices, (SELECT COUNT(*) FROM oficinas WHERE activo = true) as oficinas"); estado = cur.fetchone()
        print(f"📊 Estado del sistema:\n   • Segmentos viales conectados: {estado['aristas']:,}\n   • Vértices en la red: {estado['vertices']:,}\n   • Oficinas disponibles: {estado['oficinas']}")
        if estado['aristas'] == 0 or estado['vertices'] == 0: raise Exception("La red vial no está lista")
        if estado['oficinas'] == 0: print("⚠️ ADVERTENCIA: No hay oficinas cargadas en la BD, la ruta podría fallar.")

        features, distancia, tiempo = generar_ruta_compraventa(cur)
        if not features: raise Exception("No se pudo generar ninguna ruta")
        
        geojson = { "type": "FeatureCollection", "features": features, "metadata": { "tipo": "ruta_tramite_compraventa", "algoritmo": "pgr_dijkstra (con fallback 2.5x)", "descripcion": "Ruta para trámite de compraventa (puede ser línea recta)", "tramite": { "nombre": "Compraventa de Inmueble", "pasos": 3, "oficinas": ["Notaría", "Conservador BR", "SII"], "duracion_estimada_min": tiempo, "distancia_total_km": round(distancia/1000, 2) }, "nota": "Tiempos estimados." } }
        with open(out_file, 'w', encoding='utf-8') as f: json.dump(geojson, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Archivo generado: {out_file}")
        web_data_dir = os.environ.get("WEB_DATA_DIR");
        if web_data_dir and os.path.isdir(web_data_dir): shutil.copy2(out_file, os.path.join(web_data_dir, "ruta_dijkstra.geojson")); print("✅ Copiado a servidor web")
        cur.close(); conn.close()
    except Exception as e:
        print(f"\n❌ Error: {e}"); import traceback; traceback.print_exc()
        print("\n⚠️  Generando ruta de respaldo MUY simple..."); geojson = {"type": "FeatureCollection", "features": [ {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[-70.6545, -33.4420], [-70.6540, -33.4380]]}, "properties": {"tipo":"fallback_total"}}, {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[-70.6540, -33.4380], [-70.6530, -33.4370]]}, "properties": {"tipo":"fallback_total"}} ]}
        with open(out_file, 'w', encoding='utf-8') as f: json.dump(geojson, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
