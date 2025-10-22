#!/usr/bin/env python3
import json, os, psycopg2
from psycopg2.extras import execute_batch

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST","db"), port=int(os.getenv("PGPORT","5432")),
        dbname=os.getenv("PGDATABASE","ruteo_resiliente"),
        user=os.getenv("PGUSER","postgres"), password=os.getenv("PGPASSWORD","postgres")
    )

def main(data_dir="/app/out"):
    print("🔥 LOADER Infraestructura → PostgreSQL")
    gj_path = os.path.join(data_dir, "infraestructura.geojson")
    if not os.path.exists(gj_path):
        print("⚠️  Archivo no encontrado")
        return False
    
    with open(gj_path) as f:
        data = json.load(f)
    
    features = data.get('features', [])
    if not features:
        print("⚠️  Sin features")
        return False
    
    conn = get_conn()
    cur = conn.cursor()
    
    # Limpiar tabla si existe
    try:
        cur.execute("DROP TABLE IF EXISTS red_vial_vertices_pgr CASCADE;")
        cur.execute("TRUNCATE TABLE red_vial RESTART IDENTITY CASCADE;")
        conn.commit()
    except Exception as e:
        print(f"   (Error menor al limpiar: {e})")
        conn.rollback() # Asegura que la transacción fallida no bloquee
        cur = conn.cursor() # Restablece el cursor
    
    rows = []
    for feat in features:
        geom = feat.get('geometry')
        props = feat.get('properties', {})
        if not geom or geom.get('type') != 'LineString':
            continue
        coords = geom['coordinates']
        if len(coords) < 2:
            continue
        wkt = 'LINESTRING(' + ', '.join([f"{lon} {lat}" for lon,lat in coords]) + ')'
        rows.append((props.get('osm_id'), props.get('nombre','Sin nombre'), props.get('tipo_via','unknown'), wkt))
    
    if not rows:
        print("⚠️  No hay datos para insertar")
        return False
    
    # Insertar por lotes
    print(f"   Insertando {len(rows)} segmentos...")
    batch_size = 1000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        execute_batch(cur, """
            INSERT INTO red_vial (osm_id, nombre, tipo_via, geom)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326))
            ON CONFLICT DO NOTHING
        """, batch, page_size=100)
        if i % 5000 == 0 and i > 0:
            print(f"   ... {i}/{len(rows)}")
    
    conn.commit()
    print(f"✔ Insertados {len(rows)} segmentos")
    
    # Calcular longitudes y costos
    print("   Calculando longitudes y costos...")
    cur.execute("""
        UPDATE red_vial 
        SET length_m = ST_Length(ST_Transform(geom, 3857)),
            costo = ST_Length(ST_Transform(geom, 3857)),
            reverse_costo = ST_Length(ST_Transform(geom, 3857))
        WHERE length_m IS NULL OR costo IS NULL;
    """)
    conn.commit()
    
    # CRÍTICO: Crear topología pgRouting correctamente
    print("   Creando topología pgRouting (tolerancia 0.0002)...")
    try:
        # Primero, asegurar que las columnas source/target existen
        cur.execute("""
            ALTER TABLE red_vial 
            ADD COLUMN IF NOT EXISTS source INTEGER,
            ADD COLUMN IF NOT EXISTS target INTEGER;
        """)
        conn.commit()
        
        # Crear topología con tolerancia mayor para Santiago
        cur.execute("""
            SELECT pgr_createTopology(
                'red_vial',           -- tabla
                0.0002,               -- <<< TOLERANCIA CORREGIDA
                'geom',               -- columna geometría
                'id',                 -- columna id
                'source',             -- columna source
                'target',             -- columna target
                rows_where := 'true', -- procesar todas las filas
                clean := true         -- limpiar topología existente
            );
        """)
        conn.commit()
        
        # Verificar que se crearon vértices
        cur.execute("SELECT COUNT(*) FROM red_vial_vertices_pgr;")
        vertices_count = cur.fetchone()[0]
        
        if vertices_count == 0:
            print("⚠️  No se crearon vértices, reintentando con tolerancia 0.0005...")
            cur.execute("DROP TABLE IF EXISTS red_vial_vertices_pgr CASCADE;")
            cur.execute("""
                SELECT pgr_createTopology(
                    'red_vial', 
                    0.0005,    -- <<< TOLERANCIA FALLBACK CORREGIDA
                    'geom', 
                    'id',
                    'source',
                    'target',
                    clean := true
                );
            """)
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM red_vial_vertices_pgr;")
            vertices_count = cur.fetchone()[0]
        
        print(f"✔ Topología creada con {vertices_count} vértices")
        
        # Analizar la conectividad
        cur.execute("""
            SELECT COUNT(*) FROM red_vial 
            WHERE source IS NOT NULL AND target IS NOT NULL;
        """)
        connected_edges = cur.fetchone()[0]
        print(f"✔ Aristas conectadas: {connected_edges}")
        
    except Exception as e:
        print(f"⚠️  Error en topología: {e}")
        return False
    
    # Estadísticas finales
    cur.execute("SELECT COUNT(*) FROM red_vial;")
    total_edges = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM red_vial_vertices_pgr;")
    total_nodes = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(length_m) FROM red_vial WHERE length_m IS NOT NULL;")
    total_length = cur.fetchone()[0] or 0
    
    print(f"✔ Cargados {total_edges} segmentos")
    print(f"✔ Nodos: {total_nodes}")
    print(f"✔ Longitud total: {total_length/1000:.2f} km")
    
    cur.close()
    conn.close()
    return True

if __name__ == "__main__":
    main()
