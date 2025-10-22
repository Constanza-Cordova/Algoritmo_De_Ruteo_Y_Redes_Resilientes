#!/usr/bin/env python3
"""
ETL MASTER - Orquestador principal
Ejecuta todo el pipeline ETL para Fase 2
"""
import os
import sys
import time
import psycopg2

OUT_DIR = os.environ.get("OUT_DIR", "/app/out")
WEB_DATA_DIR = os.environ.get("WEB_DATA_DIR", "/webdata")

def wait_for_db(max_wait=120):
    """Espera a que PostgreSQL esté disponible"""
    print("🔍 Esperando a que PostgreSQL esté listo...")
    start = time.time()
    
    while time.time() - start < max_wait:
        try:
            conn = psycopg2.connect(
                host=os.getenv("PGHOST", "db"),
                port=int(os.getenv("PGPORT", "5432")),
                dbname=os.getenv("PGDATABASE", "ruteo_resiliente"),
                user=os.getenv("PGUSER", "postgres"),
                password=os.getenv("PGPASSWORD", "postgres")
            )
            conn.close()
            print("✓ PostgreSQL está listo")
            return True
        except Exception:
            print(f"   Esperando... ({int(time.time() - start)}s)")
            time.sleep(3)
    
    print("❌ Timeout esperando PostgreSQL")
    return False

def verificar_y_crear_schema():
    """Verifica y crea el schema si no existe"""
    print("\n🔧 Verificando schema de base de datos...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "db"),
            port=int(os.getenv("PGPORT", "5432")),
            dbname=os.getenv("PGDATABASE", "ruteo_resiliente"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", "postgres")
        )
        cur = conn.cursor()
        
        # Verificar si existe la tabla red_vial
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'red_vial'
            );
        """)
        
        tabla_existe = cur.fetchone()[0]
        
        if not tabla_existe:
            print("   📋 Creando schema completo...")
            
            # Crear schema completo
            schema_sql = """
            CREATE EXTENSION IF NOT EXISTS postgis;
            CREATE EXTENSION IF NOT EXISTS pgrouting;

            CREATE TABLE IF NOT EXISTS red_vial (
              id BIGSERIAL PRIMARY KEY,
              osm_id BIGINT,
              nombre TEXT,
              tipo_via TEXT,
              geom geometry(LineString, 4326) NOT NULL,
              source INTEGER,
              target INTEGER,
              length_m DOUBLE PRECISION,
              costo DOUBLE PRECISION,
              reverse_costo DOUBLE PRECISION
            );
            CREATE INDEX IF NOT EXISTS red_vial_geom_idx ON red_vial USING GIST(geom);
            CREATE INDEX IF NOT EXISTS red_vial_source_idx ON red_vial(source);
            CREATE INDEX IF NOT EXISTS red_vial_target_idx ON red_vial(target);

            CREATE TABLE IF NOT EXISTS oficinas (
              id SERIAL PRIMARY KEY,
              nombre TEXT NOT NULL,
              tipo TEXT NOT NULL,
              direccion TEXT,
              comuna TEXT,
              region TEXT,
              lat DOUBLE PRECISION NOT NULL,
              lon DOUBLE PRECISION NOT NULL,
              geom geometry(Point, 4326),
              horario_apertura TIME,
              horario_cierre TIME,
              dias_atencion TEXT[],
              telefono TEXT,
              email TEXT,
              url TEXT,
              es_turno BOOLEAN DEFAULT false,
              activo BOOLEAN DEFAULT true,
              created_at TIMESTAMP DEFAULT NOW(),
              updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS oficinas_geom_idx ON oficinas USING GIST(geom);

            CREATE OR REPLACE FUNCTION oficinas_sync_geom()
            RETURNS TRIGGER AS $$
            BEGIN
              NEW.geom = ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326);
              NEW.updated_at = NOW();
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS oficinas_geom_trigger ON oficinas;
            CREATE TRIGGER oficinas_geom_trigger
            BEFORE INSERT OR UPDATE ON oficinas
            FOR EACH ROW EXECUTE FUNCTION oficinas_sync_geom();

            CREATE TABLE IF NOT EXISTS metadata_raw (
              id SERIAL PRIMARY KEY,
              oficina_id INTEGER REFERENCES oficinas(id) ON DELETE CASCADE,
              fuente TEXT NOT NULL,
              datos JSONB NOT NULL,
              fecha_extraccion TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS amenazas (
              id SERIAL PRIMARY KEY,
              tipo TEXT NOT NULL,
              severidad INTEGER CHECK (severidad BETWEEN 1 AND 5),
              categoria TEXT,
              titulo TEXT,
              descripcion TEXT,
              lat DOUBLE PRECISION,
              lon DOUBLE PRECISION,
              geom geometry(Point, 4326),
              radio_afectacion_m DOUBLE PRECISION DEFAULT 500,
              fecha_inicio TIMESTAMP NOT NULL,
              fecha_fin TIMESTAMP,
              activo BOOLEAN DEFAULT true,
              fuente TEXT,
              datos_raw JSONB,
              created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS amenazas_geom_idx ON amenazas USING GIST(geom);

            CREATE OR REPLACE FUNCTION amenazas_sync_geom()
            RETURNS TRIGGER AS $$
            BEGIN
              IF NEW.lat IS NOT NULL AND NEW.lon IS NOT NULL THEN
                NEW.geom = ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326);
              END IF;
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS amenazas_geom_trigger ON amenazas;
            CREATE TRIGGER amenazas_geom_trigger
            BEFORE INSERT OR UPDATE ON amenazas
            FOR EACH ROW EXECUTE FUNCTION amenazas_sync_geom();
            """
            
            cur.execute(schema_sql)
            conn.commit()
            print("   ✓ Schema creado exitosamente")
        else:
            print("   ✓ Schema ya existe")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ⚠️  Error verificando schema: {e}")
        return False

def print_header(text):
    """Imprime header decorado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def ejecutar_etl():
    """Ejecuta pipeline ETL completo"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🚀 ETL RUTEO RESILIENTE - FASE 2" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(WEB_DATA_DIR, exist_ok=True)
    
    # Esperar BD
    if not wait_for_db():
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    # Verificar y crear schema
    verificar_y_crear_schema()
    
    try:
        # ═══════════════════════════════════════════════════════════
        # FASE 1: EXTRACCIÓN Y TRANSFORMACIÓN (ETL)
        # ═══════════════════════════════════════════════════════════
        
        print_header("FASE 1: EXTRACCIÓN Y TRANSFORMACIÓN")
        
        # 1. Infraestructura
        print("\n📍 [1/6] Infraestructura - Red Vial OSM")
        print("-" * 70)
        try:
            from etl_infra_osm import main as etl_infra
            etl_infra(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # 2. Metadata - Notarios
        print("\n📝 [2/6] Metadata - Notarías")
        print("-" * 70)
        try:
            from etl_notarios import main as etl_notarios
            etl_notarios(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # 3. Metadata - Trámites (lógica de ChileAtiende)
        print("\n🧠 [3/6] Metadata - Trámites y Pasos")
        print("-" * 70)
        try:
            from etl_tramites import main as etl_tramites
            etl_tramites(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # 4. Metadata - SII
        print("\n💼 [4/6] Metadata - SII")
        print("-" * 70)
        try:
            from etl_sii import main as etl_sii
            etl_sii(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # 5. Amenazas - Alertas
        print("\n⚠️  [5/6] Amenazas - Alertas")
        print("-" * 70)
        try:
            from etl_amenaza_alertas import main as etl_alertas
            etl_alertas(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # 6. Amenazas - Cortes de Luz
        print("\n💡 [6/6] Amenazas - Cortes de Luz")
        print("-" * 70)
        try:
            from etl_amenaza_cortes_luz import main as etl_cortes
            etl_cortes(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # ═══════════════════════════════════════════════════════════
        # FASE 2: CARGA A BASE DE DATOS
        # ═══════════════════════════════════════════════════════════
        
        print_header("FASE 2: CARGA A BASE DE DATOS")
        
        # 2.1 Cargar Infraestructura
        print("\n📥 [1/3] Cargando Infraestructura...")
        print("-" * 70)
        try:
            from loader_infraestructura import main as load_infra
            load_infra(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        time.sleep(1)
        
        # 2.2 Cargar Metadata
        print("\n📥 [2/3] Cargando Metadata (Oficinas)...")
        print("-" * 70)
        try:
            from loader_metadata import main as load_metadata
            load_metadata(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        time.sleep(1)
        
        # 2.3 Cargar Amenazas
        print("\n📥 [3/3] Cargando Amenazas...")
        print("-" * 70)
        try:
            from loader_amenazas import main as load_amenazas
            load_amenazas(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # ═══════════════════════════════════════════════════════════
        # FASE 3: GENERACIÓN DE RUTA (PEOR CASO)
        # ═══════════════════════════════════════════════════════════
        
        print_header("FASE 3: GENERACIÓN DE RUTA - pgr_dijkstra")
        
        print("\n🗺️  Generando ruta de ejemplo (peor caso)...")
        print("-" * 70)
        try:
            from etl_ruta_dijkstra import main as etl_ruta
            etl_ruta(OUT_DIR)
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # ═══════════════════════════════════════════════════════════
        # RESUMEN FINAL
        # ═══════════════════════════════════════════════════════════
        
        print_header("✅ RESUMEN FINAL")
        
        # Listar archivos generados
        print("\n📦 Archivos generados en", OUT_DIR)
        if os.path.exists(OUT_DIR):
            archivos = sorted([f for f in os.listdir(OUT_DIR) if f.endswith(('.json', '.geojson'))])
            for archivo in archivos:
                try:
                    size = os.path.getsize(os.path.join(OUT_DIR, archivo))
                    print(f"   ✓ {archivo:<35} ({size:>8} bytes)")
                except:
                    pass
        
        # Estadísticas de BD
        print("\n📊 Estadísticas de Base de Datos:")
        try:
            conn = psycopg2.connect(
                host=os.getenv("PGHOST", "db"),
                port=int(os.getenv("PGPORT", "5432")),
                dbname=os.getenv("PGDATABASE", "ruteo_resiliente"),
                user=os.getenv("PGUSER", "postgres"),
                password=os.getenv("PGPASSWORD", "postgres")
            )
            cur = conn.cursor()
            
            try:
                cur.execute("SELECT COUNT(*) FROM red_vial;")
                count_vial = cur.fetchone()[0]
                print(f"   - Red vial: {count_vial} segmentos")
            except:
                print("   - Red vial: 0 segmentos")
            
            try:
                cur.execute("SELECT COUNT(*) FROM oficinas;")
                count_oficinas = cur.fetchone()[0]
                print(f"   - Oficinas: {count_oficinas}")
            except:
                print("   - Oficinas: 0")
            
            try:
                cur.execute("SELECT COUNT(*) FROM amenazas;")
                count_amenazas = cur.fetchone()[0]
                print(f"   - Amenazas: {count_amenazas}")
            except:
                print("   - Amenazas: 0")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"   ⚠️  No se pudieron obtener estadísticas")
        
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "✅ ETL COMPLETADO EXITOSAMENTE" + " " * 18 + "║")
        print("╚" + "═" * 68 + "╝\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error fatal en ETL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ejecutar_etl()
    sys.exit(0 if success else 1)
