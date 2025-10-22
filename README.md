# 🚀 Ruteo Resiliente - Optimización de Trámites Públicos

**Fase 2**: Sistema de ruteo inteligente para minimizar tiempos en trámites públicos en Santiago Centro.

## 📋 Descripción del Proyecto

Sistema basado en Sistemas de Información Geográfica (SIG) que optimiza la realización de trámites múltiples en oficinas públicas, considerando:

- 📍 Ubicación de oficinas (notarías, SII, ChileAtiende, etc.)
- 📄 Documentos requeridos por trámite
- ⏰ Horarios de atención
- ⚠️ Amenazas en tiempo real (manifestaciones, cortes, clima)
- 🗺️ Red vial de Santiago Centro

## 🎯 Trámites Soportados

1. **Compraventa de Inmueble**: Notaría → Conservador de Bienes Raíces → SII
2. **Constitución de Sociedad**: Notaría → Registro de Empresas → SII
3. **Cambio de Nombre**: Notaría → Registro Civil → Tribunal de Familia

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    APLICACIÓN WEB                        │
│              (Leaflet + Nginx) :8087                     │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                  BASE DE DATOS                           │
│        PostgreSQL 16 + PostGIS 3.4 + pgRouting          │
│  - red_vial (infraestructura)                           │
│  - oficinas (metadata)                                   │
│  - amenazas (alertas en tiempo real)                    │
│  - rutas_calculadas (historial)                         │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                   PIPELINE ETL                           │
│  1. Extracción: OSM, APIs públicas                      │
│  2. Transformación: JSON → GeoJSON                      │
│  3. Carga: PostgreSQL                                    │
│  4. Routing: pgr_dijkstra (peor caso)                   │
└─────────────────────────────────────────────────────────┘
```

## 📦 Estructura del Proyecto

```
Tarea2_A_Ruteo/
├── README.md                          # Este archivo
├── diagrama_bd.png                    # Diagrama ER de la base de datos
├── main.sh                            # Script maestro de ejecución
├── docker-compose.yml                 # Orquestación de contenedores
│
├── db/                                # Base de Datos
│   └── init/
│       └── 00_schema_completo.sql     # Schema completo con todas las tablas
│
├── etl/                               # Pipeline ETL
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run_etl.py                     # Orquestador principal
│   │
│   ├── Infraestructura/
│   │   ├── etl_infra_osm.py           # Extrae red vial de OSM
│   │   ├── loader_infraestructura.py  # Carga a PostgreSQL
│   │   └── README_infraestructura.md  # Documentación
│   │
│   ├── Metadata/
│   │   ├── etl_notarios.py            # ETL notarías
│   │   ├── etl_chileatiende.py        # ETL ChileAtiende
│   │   ├── etl_sii.py                 # ETL SII
│   │   ├── loader_metadata.py         # Carga oficinas a BD
│   │   ├── README_notarios.md         # Docs notarías
│   │   ├── README_chileatiende.md     # Docs ChileAtiende
│   │   └── README_sii.md              # Docs SII
│   │
│   ├── Amenazas/
│   │   ├── etl_amenaza_alertas.py     # ETL alertas de tráfico
│   │   ├── etl_amenaza_cortes_luz.py  # ETL cortes de luz
│   │   ├── loader_amenazas.py         # Carga amenazas a BD
│   │   └── README_amenazas.md         # Documentación
│   │
│   └── Routing/
│       └── etl_ruta_dijkstra.py       # Genera ruta peor caso
│
└── web/                               # Servidor Web
    ├── Dockerfile
    ├── nginx.conf
    ├── index.html                     # Aplicación Leaflet
    └── data/                          # GeoJSON públicos
        ├── infraestructura.geojson
        ├── notarios.geojson
        ├── chileatiende.geojson
        ├── sii.geojson
        ├── amenaza_alertas.geojson
        ├── amenaza_cortes_luz.geojson
        └── ruta_dijkstra.geojson
```

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Docker >= 24.0
- Docker Compose >= 2.20
- 4 GB RAM disponibles
- Puertos 8087 y 5432 libres

### Ejecución Completa (Automatizada)

```bash
# Clonar repositorio
git clone https://github.com/usuario/Tarea2_A_Ruteo.git
cd Tarea2_A_Ruteo

# Dar permisos de ejecución
chmod +x main.sh

# Ejecutar sistema completo
./main.sh
```

El script `main.sh` ejecuta automáticamente:

1. ✅ Limpia contenedores anteriores
2. ✅ Construye imágenes Docker
3. ✅ Inicia PostgreSQL/PostGIS
4. ✅ Ejecuta pipeline ETL completo
5. ✅ Carga datos a base de datos
6. ✅ Genera ruta con pgr_dijkstra
7. ✅ Inicia servidor web en http://localhost:8087

### Ejecución Manual (Paso a Paso)

```bash
# 1. Construir imágenes
docker compose build

# 2. Iniciar base de datos
docker compose up -d db

# 3. Esperar a que BD esté lista (30-60 seg)
docker compose exec db pg_isready -U postgres

# 4. Ejecutar ETL
docker compose run --rm etl

# 5. Iniciar servidor web
docker compose up -d web

# 6. Acceder a http://localhost:8087
```

## 📊 Base de Datos

### Diagrama ER

Ver `diagrama_bd.png` para el diagrama completo de relaciones.

### Tablas Principales

| Tabla | Descripción | Registros Aprox |
|-------|-------------|-----------------|
| `red_vial` | Segmentos de calles (OSM) | ~2,500 |
| `red_vial_vertices_pgr` | Nodos de la red (auto) | ~1,800 |
| `oficinas` | Notarías, SII, ChileAtiende | ~30 |
| `metadata_raw` | Datos crudos de APIs | ~30 |
| `amenazas` | Alertas y eventos activos | ~10-20 |
| `tramites` | Catálogo de trámites | 3 |
| `rutas_calculadas` | Historial de rutas | Variable |

### Acceso Directo a PostgreSQL

```bash
# Desde terminal
docker compose exec db psql -U postgres -d ruteo_resiliente

# Consultas útiles
\dt                    # Listar tablas
\d red_vial           # Descripción de tabla
SELECT * FROM v_oficinas_activas;
SELECT * FROM v_amenazas_activas;
```

## 🗺️ Algoritmo de Routing

### Fase 2: Peor Caso (pgr_dijkstra)
- **Algoritmo**: Dijkstra (shortest path)
- **Costo**: Longitud de aristas (`length_m`)
- **No considera**: Amenazas, horarios, metadata
- **Propósito**: Baseline para comparación en Fase 3

### Fase 3 (Futuro): Routing Resiliente
- Considera amenazas con penalización de costos
- Respeta horarios de oficinas
- Valida disponibilidad de documentos
- Optimización multi-objetivo

## 📡 Fuentes de Datos

### Infraestructura
- **OpenStreetMap**: Red vial (Overpass API)
- **URL**: https://overpass-api.de/api/interpreter
- **Cobertura**: Santiago Centro (bbox: -33.50,-70.70,-33.40,-70.60)

### Metadata
- **Notarías**: NotariosChile.cl (scraping)
- **ChileAtiende**: Directorio oficial
- **SII**: Directorio de oficinas

### Amenazas
- **Alertas**: Datos simulados (futuro: Waze API)
- **Cortes Luz**: Datos simulados (futuro: ENEL API)
- **Clima**: Open-Meteo API (futuro)

## 🔧 Comandos Útiles

```bash
# Ver logs
docker compose logs db        # Logs de PostgreSQL
docker compose logs etl       # Logs del ETL
docker compose logs web       # Logs del servidor web

# Reiniciar servicios
docker compose restart db
docker compose restart web

# Ejecutar ETL nuevamente
docker compose run --rm etl

# Detener todo
docker compose down

# Eliminar volúmenes (CUIDADO: borra datos)
docker compose down -v

# Ver estado de servicios
docker compose ps

# Estadísticas de BD
docker compose exec db psql -U postgres -d ruteo_resiliente -c "
  SELECT 
    'Red Vial' as tabla, COUNT(*) as registros 
  FROM red_vial
  UNION ALL
  SELECT 'Oficinas', COUNT(*) FROM oficinas
  UNION ALL
  SELECT 'Amenazas', COUNT(*) FROM amenazas;
"
```

## 🎨 Interfaz Web

Acceder a http://localhost:8087

### Capas Disponibles
- ✅ Ruta pgr_dijkstra (peor caso) - Negro
- 📝 Notarías - Azul
- 🏛️ ChileAtiende - Naranja
- 💼 SII - Púrpura
- ⚠️ Alertas - Rojo
- 💡 Cortes de Luz - Rosa
- 🛣️ Infraestructura - Verde

### Interacción
- Click en marcadores para ver información
- Toggle capas en panel lateral
- Zoom y pan con mouse/touch
- Links directos a archivos JSON/GeoJSON

## 📈 Resultados Esperados

### Fase 2 (Actual)
- ✅ Sistema completamente dockerizado
- ✅ ETL automatizado y reproducible
- ✅ Datos cargados en PostgreSQL
- ✅ Ruta de ejemplo funcionando
- ✅ Visualización web operativa

### Métricas
- Tiempo de setup: ~3-5 minutos
- Segmentos de red vial: ~2,500
- Oficinas catalogadas: ~30
- Ruta de ejemplo: ~2-5 km

## 🐛 Troubleshooting

### PostgreSQL no inicia
```bash
# Verificar logs
docker compose logs db

# Verificar puerto
lsof -i :5432

# Recrear contenedor
docker compose down -v
docker compose up -d db
```

### ETL falla
```bash
# Ver logs detallados
docker compose logs etl

# Ejecutar con output en vivo
docker compose run --rm etl

# Verificar conexión a BD
docker compose exec db pg_isready
```

### Web no muestra capas
```bash
# Verificar archivos generados
ls -lh web/data/

# Regenerar datos
docker compose run --rm etl

# Ver logs de nginx
docker compose logs web
```

## 👥 Equipo

- Felipe Aros
- Kevin Cabrera
- Constanza Córdova

## 📄 Licencia

Este proyecto es parte del curso de Algoritmos de Ruteo y Redes Resilientes.

## 🔗 Enlaces Útiles

- [Documentación pgRouting](https://docs.pgrouting.org/)
- [PostGIS](https://postgis.net/)
- [Leaflet](https://leafletjs.com/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)

---

**Última actualización**: Octubre 2025 - Fase 2
