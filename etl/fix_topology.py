#!/usr/bin/env python3
"""
Script para diagnosticar y reparar la topología de pgRouting
"""
import psycopg2
import os

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST","db"),
        port=int(os.getenv("PGPORT","5432")),
        dbname=os.getenv("PGDATABASE","ruteo_resiliente"),
        user=os.getenv("PGUSER","postgres"),
        password=os.getenv("PGPASSWORD","postgres")
    )

def diagnosticar_red():
    print("🔍 Diagnosticando red vial...")
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # 1. Verificar estructura de tabla
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'red_vial'
            ORDER BY ordinal_position;
        """)
        columnas = [row[0] for row in cur.fetchall()]
        print(f"\n✓ Columnas en red_vial: {', '.join(columnas)}")
        
        # 2. Estadísticas básicas
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(source) as con_source,
                COUNT(target) as con_target,
                COUNT(costo) as con_costo,
                COUNT(length_m) as con_longitud
            FROM red_vial;
        """)
        stats = cur.fetchone()
        print(f"\n📊 Estadísticas:")
        print(f"   Total segmentos: {stats[0]}")
        print(f"   Con source: {stats[1]}")
        print(f"   Con target: {stats[2]}")
        print(f"   Con costo: {stats[3]}")
        print(f"   Con longitud: {stats[4]}")
        
        # 3. Verificar vértices
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'red_vial_vertices_pgr'
            );
        """)
        tiene_vertices = cur.fetchone()[0]
        
        if tiene_vertices:
            cur.execute("SELECT COUNT(*) FROM red_vial_vertices_pgr;")
            num_vertices = cur.fetchone()[0]
            print(f"\n✓ Tabla de vértices existe con {num_vertices} vértices")
        else:
            print("\n⚠️  NO existe tabla de vértices")
        
        # 4. Verificar conectividad
        if stats[1] > 0:
            cur.execute("""
                SELECT COUNT(DISTINCT source) + COUNT(DISTINCT target) 
                FROM red_vial 
                WHERE source IS NOT NULL AND target IS NOT NULL;
            """)
            nodos_unicos = cur.fetchone()[0]
            print(f"   Nodos únicos en la red: {nodos_unicos}")
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
    finally:
        cur.close()
        conn.close()

def reparar_topologia():
    print("\n🔧 Reparando topología...")
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # 1. Asegurar columnas necesarias
        print("   1. Verificando estructura...")
        cur.execute("""
            ALTER TABLE red_vial 
            ADD COLUMN IF NOT EXISTS source INTEGER,
            ADD COLUMN IF NOT EXISTS target INTEGER,
            ADD COLUMN IF NOT EXISTS length_m DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS costo DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS reverse_costo DOUBLE PRECISION;
        """)
        conn.commit()
        
        # 2. Calcular longitudes si faltan
        print("   2. Calculando longitudes...")
        cur.execute("""
            UPDATE red_vial 
            SET length_m = ST_Length(ST_Transform(geom, 3857))
            WHERE length_m IS NULL;
        """)
        
        cur.execute("""
            UPDATE red_vial 
            SET costo = length_m,
                reverse_costo = length_m
            WHERE costo IS NULL OR reverse_costo IS NULL;
        """)
        conn.commit()
        
        # 3. Limpiar topología existente
        print("   3. Limpiando topología anterior...")
        cur.execute("DROP TABLE IF EXISTS red_vial_vertices_pgr CASCADE;")
        conn.commit()
        
        # 4. Crear nueva topología
        print("   4. Creando nueva topología...")
        cur.execute("""
            SELECT pgr_createTopology(
                'red_vial',     -- tabla
                0.00001,        -- tolerancia
                'geom',         -- columna geometría
                'id',           -- columna id
                'source',       -- columna source
                'target',       -- columna target
                rows_where := 'costo > 0',
                clean := true
            );
        """)
        conn.commit()
        
        # 5. Verificar resultado
        cur.execute("SELECT COUNT(*) FROM red_vial_vertices_pgr;")
        vertices = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM red_vial 
            WHERE source IS NOT NULL AND target IS NOT NULL;
        """)
        conectados = cur.fetchone()[0]
        
        print(f"\n✅ Topología reparada:")
        print(f"   - Vértices creados: {vertices}")
        print(f"   - Segmentos conectados: {conectados}")
        
        # 6. Test de routing
        print("\n🧪 Probando routing...")
        cur.execute("""
            WITH test AS (
                SELECT * FROM pgr_dijkstra(
                    'SELECT id, source, target, costo as cost 
                     FROM red_vial 
                     WHERE source IS NOT NULL AND target IS NOT NULL',
                    (SELECT id FROM red_vial_vertices_pgr ORDER BY RANDOM() LIMIT 1),
                    (SELECT id FROM red_vial_vertices_pgr ORDER BY RANDOM() LIMIT 1),
                    directed := false
                ) LIMIT 5
            )
            SELECT COUNT(*) FROM test;
        """)
        test_result = cur.fetchone()[0]
        
        if test_result > 0:
            print(f"   ✓ Routing funciona correctamente")
        else:
            print(f"   ⚠️  Routing no pudo calcular ruta de prueba")
        
    except Exception as e:
        print(f"❌ Error reparando: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DIAGNÓSTICO Y REPARACIÓN DE TOPOLOGÍA")
    print("=" * 60)
    
    diagnosticar_red()
    
    respuesta = input("\n¿Desea reparar la topología? (s/n): ")
    if respuesta.lower() == 's':
        reparar_topologia()
        print("\n" + "=" * 60)
        diagnosticar_red()
    else:
        print("Operación cancelada")
