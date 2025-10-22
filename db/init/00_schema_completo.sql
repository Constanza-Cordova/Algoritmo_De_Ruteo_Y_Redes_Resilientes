-- ============================================================
-- SCHEMA COMPLETO - RUTEO RESILIENTE FASE 2
-- Se carga automáticamente al iniciar PostgreSQL
-- ============================================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- ============================================================
-- 1. RED VIAL (Infraestructura)
-- ============================================================
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
  reverse_costo DOUBLE PRECISION,
  CONSTRAINT enforce_dims_red_vial CHECK (ST_NDims(geom) = 2),
  CONSTRAINT enforce_srid_red_vial CHECK (ST_SRID(geom) = 4326)
);

CREATE INDEX IF NOT EXISTS red_vial_geom_idx ON red_vial USING GIST(geom);
CREATE INDEX IF NOT EXISTS red_vial_source_idx ON red_vial(source);
CREATE INDEX IF NOT EXISTS red_vial_target_idx ON red_vial(target);
CREATE INDEX IF NOT EXISTS red_vial_osm_id_idx ON red_vial(osm_id);

COMMENT ON TABLE red_vial IS 'Red vial extraída de OpenStreetMap para routing';
COMMENT ON COLUMN red_vial.length_m IS 'Longitud del segmento en metros';

-- ============================================================
-- 2. OFICINAS (Metadata)
-- ============================================================
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
CREATE INDEX IF NOT EXISTS oficinas_tipo_idx ON oficinas(tipo);
CREATE INDEX IF NOT EXISTS oficinas_activo_idx ON oficinas(activo);

COMMENT ON TABLE oficinas IS 'Oficinas públicas (notarías, SII, ChileAtiende)';
COMMENT ON COLUMN oficinas.tipo IS 'notaria | sii | chileatiende | registro_civil | conservador';

-- Trigger para sincronizar geometría desde lat/lon
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

-- ============================================================
-- 3. METADATA RAW (Trazabilidad)
-- ============================================================
CREATE TABLE IF NOT EXISTS metadata_raw (
  id SERIAL PRIMARY KEY,
  oficina_id INTEGER REFERENCES oficinas(id) ON DELETE CASCADE,
  fuente TEXT NOT NULL,
  datos JSONB NOT NULL,
  fecha_extraccion TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS metadata_raw_oficina_idx ON metadata_raw(oficina_id);
CREATE INDEX IF NOT EXISTS metadata_raw_fuente_idx ON metadata_raw(fuente);
CREATE INDEX IF NOT EXISTS metadata_raw_datos_idx ON metadata_raw USING GIN(datos);

COMMENT ON TABLE metadata_raw IS 'Datos crudos de APIs para auditoría';

-- ============================================================
-- 4. AMENAZAS
-- ============================================================
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
CREATE INDEX IF NOT EXISTS amenazas_tipo_idx ON amenazas(tipo);
CREATE INDEX IF NOT EXISTS amenazas_activo_idx ON amenazas(activo);
CREATE INDEX IF NOT EXISTS amenazas_fecha_inicio_idx ON amenazas(fecha_inicio);

COMMENT ON TABLE amenazas IS 'Eventos que afectan routing (alertas, cortes, etc)';
COMMENT ON COLUMN amenazas.severidad IS '1=bajo, 2=medio, 3=alto, 4=muy_alto, 5=critico';

-- Trigger para sincronizar geometría
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

-- ============================================================
-- 5. TRAMITES (Catálogo)
-- ============================================================
CREATE TABLE IF NOT EXISTS tramites (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  tiempo_estimado_min INTEGER,
  documentos_requeridos TEXT[],
  pasos JSONB,
  url_info TEXT
);

CREATE INDEX IF NOT EXISTS tramites_nombre_idx ON tramites(nombre);

COMMENT ON TABLE tramites IS 'Catálogo de trámites con requisitos';

-- Datos iniciales de trámites
INSERT INTO tramites (nombre, tiempo_estimado_min, documentos_requeridos, pasos) 
VALUES
  ('Compraventa de Inmueble', 120, 
   ARRAY['Cédula de identidad', 'Escritura del inmueble', 'Certificado de avalúo fiscal'],
   '[{"orden":1,"oficina_tipo":"notaria","descripcion":"Firma de escritura"},
     {"orden":2,"oficina_tipo":"conservador","descripcion":"Inscripción en CBR"},
     {"orden":3,"oficina_tipo":"sii","descripcion":"Pago de impuestos"}]'::jsonb),
  
  ('Constitución de Sociedad', 90,
   ARRAY['Cédula de identidad', 'Estatutos sociales', 'RUT provisorio'],
   '[{"orden":1,"oficina_tipo":"notaria","descripcion":"Escritura pública"},
     {"orden":2,"oficina_tipo":"registro_empresas","descripcion":"Inscripción"},
     {"orden":3,"oficina_tipo":"sii","descripcion":"Obtención RUT definitivo"}]'::jsonb),
  
  ('Cambio de Nombre', 480,
   ARRAY['Cédula de identidad', 'Certificado de nacimiento', 'Solicitud judicial'],
   '[{"orden":1,"oficina_tipo":"notaria","descripcion":"Declaración jurada"},
     {"orden":2,"oficina_tipo":"registro_civil","descripcion":"Solicitud inicial"},
     {"orden":3,"oficina_tipo":"tribunal_familia","descripcion":"Resolución judicial"}]'::jsonb)
ON CONFLICT DO NOTHING;

-- ============================================================
-- 6. RUTAS CALCULADAS (Historial)
-- ============================================================
CREATE TABLE IF NOT EXISTS rutas_calculadas (
  id SERIAL PRIMARY KEY,
  tramite_id INTEGER REFERENCES tramites(id),
  origen_lat DOUBLE PRECISION,
  origen_lon DOUBLE PRECISION,
  destino_lat DOUBLE PRECISION,
  destino_lon DOUBLE PRECISION,
  algoritmo TEXT,
  geom geometry(LineString, 4326),
  distancia_m DOUBLE PRECISION,
  tiempo_estimado_min INTEGER,
  costo_total DOUBLE PRECISION,
  considera_amenazas BOOLEAN DEFAULT false,
  amenazas_evitadas INTEGER[],
  fecha_calculo TIMESTAMP DEFAULT NOW(),
  parametros JSONB
);

CREATE INDEX IF NOT EXISTS rutas_geom_idx ON rutas_calculadas USING GIST(geom);
CREATE INDEX IF NOT EXISTS rutas_tramite_idx ON rutas_calculadas(tramite_id);
CREATE INDEX IF NOT EXISTS rutas_fecha_idx ON rutas_calculadas(fecha_calculo);

COMMENT ON TABLE rutas_calculadas IS 'Historial de rutas para análisis';

-- ============================================================
-- 7. VISTAS ÚTILES
-- ============================================================

-- Vista: Oficinas activas
CREATE OR REPLACE VIEW v_oficinas_activas AS
SELECT 
  id, nombre, tipo, direccion, comuna,
  lat, lon, geom,
  CONCAT(horario_apertura, ' - ', horario_cierre) as horario,
  array_to_string(dias_atencion, ', ') as dias,
  telefono, activo
FROM oficinas
WHERE activo = true;

-- Vista: Amenazas activas ahora
CREATE OR REPLACE VIEW v_amenazas_activas AS
SELECT 
  id, tipo, severidad, titulo, descripcion,
  lat, lon, geom, radio_afectacion_m,
  fecha_inicio, fecha_fin, fuente
FROM amenazas
WHERE activo = true
  AND fecha_inicio <= NOW()
  AND (fecha_fin IS NULL OR fecha_fin >= NOW());

-- ============================================================
-- 8. FUNCIONES AUXILIARES
-- ============================================================

-- Función: Buscar oficinas cercanas
CREATE OR REPLACE FUNCTION buscar_oficinas_cercanas(
  p_lat DOUBLE PRECISION,
  p_lon DOUBLE PRECISION,
  p_tipo TEXT DEFAULT NULL,
  p_radio_m INTEGER DEFAULT 1000,
  p_limite INTEGER DEFAULT 10
)
RETURNS TABLE (
  id INTEGER,
  nombre TEXT,
  tipo TEXT,
  direccion TEXT,
  distancia_m DOUBLE PRECISION
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    o.id, o.nombre, o.tipo, o.direccion,
    ST_Distance(
      o.geom::geography,
      ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography
    ) as distancia_m
  FROM oficinas o
  WHERE o.activo = true
    AND (p_tipo IS NULL OR o.tipo = p_tipo)
    AND ST_DWithin(
      o.geom::geography,
      ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography,
      p_radio_m
    )
  ORDER BY distancia_m
  LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- FIN DEL SCHEMA
-- ============================================================

-- Mensaje de confirmación
DO $$
BEGIN
  RAISE NOTICE '✅ Schema cargado correctamente - Ruteo Resiliente Fase 2';
END $$;
