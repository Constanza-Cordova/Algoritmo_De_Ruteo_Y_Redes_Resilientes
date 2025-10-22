#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loader_metadata.py
Carga notarios.geojson y sii.geojson a la tabla 'oficinas'.
"""

import os
import json
import psycopg2
from psycopg2.extras import execute_batch

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST","db"), port=int(os.getenv("PGPORT","5432")),
        dbname=os.getenv("PGDATABASE","ruteo_resiliente"),
        user=os.getenv("PGUSER","postgres"), password=os.getenv("PGPASSWORD","postgres")
    )

def ensure_table(cur, conn):
    """Crea la tabla oficinas si no existe, con las columnas necesarias"""
    print("   Verificando/Creando tabla 'oficinas'...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS oficinas (
      id SERIAL PRIMARY KEY,
      nombre TEXT NOT NULL,
      tipo TEXT NOT NULL,
      direccion TEXT,
      comuna TEXT,
      lat DOUBLE PRECISION NOT NULL,
      lon DOUBLE PRECISION NOT NULL,
      telefono TEXT,
      geom geometry(Point, 4326), -- Columna geom para PostGIS
      -- Columnas opcionales que podrían existir por 00_schema_completo.sql
      -- pero no son estrictamente necesarias para este loader simple
      region TEXT,
      horario_apertura TIME,
      horario_cierre TIME,
      dias_atencion TEXT[],
      email TEXT,
      url TEXT,
      es_turno BOOLEAN DEFAULT false,
      activo BOOLEAN DEFAULT true,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW(),
      datos_raw JSONB -- Agregada para compatibilidad si el schema completo ya existe
    );
    """)
    # Asegurar que la columna datos_raw exista si la tabla ya existía sin ella
    try:
        cur.execute("ALTER TABLE oficinas ADD COLUMN IF NOT EXISTS datos_raw JSONB;")
    except Exception as e_alter:
        print(f"    (Nota: No se pudo añadir columna datos_raw, puede que ya exista o haya otro problema: {e_alter})")
        conn.rollback() # Anula el ALTER si falla, pero continúa
        cur = conn.cursor()

    # Asegurar que el trigger de geometría exista (copiado de 00_schema_completo.sql)
    cur.execute("""
        CREATE OR REPLACE FUNCTION oficinas_sync_geom()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.geom = ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326);
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    cur.execute("""
        DROP TRIGGER IF EXISTS oficinas_geom_trigger ON oficinas;
    """)
    cur.execute("""
        CREATE TRIGGER oficinas_geom_trigger
        BEFORE INSERT OR UPDATE ON oficinas
        FOR EACH ROW EXECUTE FUNCTION oficinas_sync_geom();
    """)
    conn.commit()
    print("   ✓ Tabla 'oficinas' lista.")


def safe_clear_oficinas(cur, conn):
    """Intenta TRUNCATE CASCADE; si falla, hace DELETE y resetea secuencia."""
    print("   Limpiando tabla 'oficinas'...")
    try:
        cur.execute("TRUNCATE TABLE oficinas RESTART IDENTITY CASCADE;")
        conn.commit()
    except Exception as e:
        print(f"   (TRUNCATE falló: {e}. Usando DELETE.)")
        conn.rollback()
        cur = conn.cursor() # Restablecer cursor por si TRUNCATE falló
        cur.execute("DELETE FROM oficinas;")
        try:
            # Intenta resetear la secuencia si existe
            cur.execute("SELECT 1 FROM information_schema.sequences WHERE sequence_name = 'oficinas_id_seq';")
            if cur.fetchone():
                cur.execute("ALTER SEQUENCE oficinas_id_seq RESTART WITH 1;")
        except Exception as e_seq:
            print(f"   (No se pudo resetear secuencia: {e_seq})")
        conn.commit()
    print("   ✓ Tabla 'oficinas' limpiada.")


def load_geojson(cur, path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    
    feats = data.get("features", [])
    if not feats:
        return 0
        
    # Determinar el 'tipo' de oficina basado en el nombre del archivo
    tipo_oficina = "desconocido"
    if "notarios" in path:
        tipo_oficina = "notaria"
    elif "sii" in path:
        tipo_oficina = "sii"

    rows = []
    for ft in feats:
        props = ft.get("properties", {}) or {}
        geom  = ft.get("geometry")
        if not geom or geom.get("type") != "Point":
            continue
        coords = geom.get("coordinates", [])
        if not coords or len(coords) < 2:
            continue
        
        lon, lat = float(coords[0]), float(coords[1])
        
        # Prepara la fila SÓLO con las columnas que sabemos que existen
        rows.append((
            props.get("nombre"),
            tipo_oficina,
            props.get("direccion"),
            props.get("comuna"),
            lat,
            lon,
            props.get("telefono")
            # Ya no intentamos insertar en datos_raw aquí
        ))

    # Insertar por lotes en las columnas específicas
    execute_batch(cur, """
        INSERT INTO oficinas
        (nombre, tipo, direccion, comuna, lat, lon, telefono)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, rows, page_size=100)
    
    return len(rows)

def main(data_dir="/app/out"):
    print("📥 LOADER Metadata (Oficinas) → PostgreSQL")
    
    # Definir los archivos a cargar
    files_to_load = ["notarios.geojson", "sii.geojson"]
    
    conn = get_conn()
    cur  = conn.cursor()

    # 1) Asegurar que la tabla y trigger existan
    ensure_table(cur, conn)

    # 2) Limpiar la tabla de oficinas
    safe_clear_oficinas(cur, conn)

    # 3) Cargar archivos
    total = 0
    for fname in files_to_load:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            print(f"⚠️  No existe: {path}")
            continue
        
        print(f"   Cargando {fname} ...")
        try:
            cnt = load_geojson(cur, path)
            conn.commit()
            print(f"     → {cnt} filas insertadas")
            total += cnt
        except Exception as e:
            print(f"     ❌ Error cargando {fname}: {e}")
            conn.rollback()
            cur = conn.cursor() # Restablecer cursor por si INSERT falló

    print(f"✅ Total oficinas cargadas: {total}")
    
    # 4. Forzar actualización de 'geom' (si el trigger no se disparó en INSERT por alguna razón)
    #    Aunque el trigger DEBERÍA haberlo hecho, esto es una capa extra de seguridad.
    print("   Verificando/Actualizando geometrías...")
    try:
        updated_count = cur.execute("UPDATE oficinas SET lon = lon WHERE geom IS NULL;")
        conn.commit()
        if updated_count and updated_count > 0:
             print(f"    ✓ {updated_count} geometrías actualizadas.")
        else:
             print("    ✓ Geometrías ya estaban actualizadas.")
    except Exception as e_update:
        print(f"    ⚠️ Error actualizando geometrías: {e_update}")
        conn.rollback()

    cur.close()
    conn.close()

if __name__ == "__main__":
    # Permite ejecutar el script con un directorio por defecto si se llama directamente
    main(data_dir=os.environ.get("OUT_DIR", "/app/out"))
