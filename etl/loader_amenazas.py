#!/usr/bin/env python3
import json, os, psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST","db"), port=int(os.getenv("PGPORT","5432")),
        dbname=os.getenv("PGDATABASE","ruteo_resiliente"),
        user=os.getenv("PGUSER","postgres"), password=os.getenv("PGPASSWORD","postgres")
    )

def load_file(path, tipo_base, fuente, conn):
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        data = json.load(f)
    items = data if isinstance(data, list) else data.get('features', [])
    
    cur = conn.cursor()
    rows = []
    for item in items:
        if 'properties' in item:
            props = item['properties']
            if 'coordinates' in item.get('geometry', {}):
                coords = item['geometry']['coordinates']
                props['lon'], props['lat'] = coords[0], coords[1]
            item = props
        
        if 'lat' not in item or 'lon' not in item:
            continue
        
        inicio_str = item.get('inicio', item.get('fecha_inicio'))
        inicio = datetime.fromisoformat(inicio_str.replace('Z','')) if inicio_str else datetime.now()
        
        rows.append((
            item.get('tipo', tipo_base), int(item.get('severidad', 3)),
            item.get('categoria', tipo_base), item.get('titulo', item.get('descripcion',''))[:100],
            item.get('descripcion',''), float(item['lat']), float(item['lon']),
            item.get('radio_afectacion_m', 500), inicio, True, fuente,
            json.dumps(item, ensure_ascii=False)
        ))
    
    execute_batch(cur, """
        INSERT INTO amenazas (tipo, severidad, categoria, titulo, descripcion, lat, lon, radio_afectacion_m, fecha_inicio, activo, fuente, datos_raw)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
    """, rows, page_size=100)
    conn.commit()
    cur.close()
    return len(rows)

def main(data_dir="/app/out"):
    print("📥 LOADER Amenazas → PostgreSQL")
    conn = get_conn()
    sources = [
        ("amenaza_alertas.json", "alerta", "demo_alertas"),
        ("amenaza_cortes_luz.json", "corte_luz", "demo_cortes")
    ]
    total = 0
    for fname, tipo, fuente in sources:
        count = load_file(os.path.join(data_dir, fname), tipo, fuente, conn)
        total += count
        print(f"✓ {tipo}: {count}")
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM amenazas;")
    print(f"✓ Total amenazas: {cur.fetchone()[0]}")
    cur.close()
    conn.close()
    return True

if __name__ == "__main__":
    main()
