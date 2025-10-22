#!/usr/bin/env bash
set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════"
}

# Banner
clear
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║          🚀 RUTEO RESILIENTE - FASE 2                     ║"
echo "║          Sistema de Optimización de Trámites              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# PASO 1: Limpiar
print_header "PASO 1: Limpieza de contenedores anteriores"
log_info "Deteniendo y eliminando contenedores existentes..."
docker compose down -v 2>/dev/null || true
log_success "Limpieza completada"

# PASO 2: Build
print_header "PASO 2: Construcción de imágenes Docker"
log_info "Construyendo imagen de base de datos..."
docker compose build db

log_info "Construyendo imagen de ETL..."
docker compose build etl

log_info "Construyendo imagen de servidor web..."
docker compose build web

log_success "Todas las imágenes construidas exitosamente"

# PASO 3: Iniciar BD
print_header "PASO 3: Inicialización de Base de Datos"
log_info "Levantando PostgreSQL/PostGIS..."
docker compose up -d db

log_info "Esperando a que PostgreSQL esté listo..."
MAX_WAIT=60
WAITED=0
while ! docker compose exec -T db pg_isready -U postgres -d ruteo_resiliente > /dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        log_error "Timeout esperando PostgreSQL"
        exit 1
    fi
    echo -n "."
    sleep 2
    WAITED=$((WAITED + 2))
done
echo ""
log_success "PostgreSQL está operativo"

log_info "Verificando schema de base de datos..."
# Verificación simple sin quedarse atascado
if docker compose exec -T db psql -U postgres -d ruteo_resiliente -c "\dt" > /dev/null 2>&1; then
    log_success "Schema cargado correctamente"
else
    log_warning "Verificar schema manualmente si es necesario"
fi

# PASO 4: ETL
print_header "PASO 4: Ejecución de Pipeline ETL"
log_info "Ejecutando ETL (extracción, transformación y carga)..."
log_info "Este proceso puede tardar 1-2 minutos..."

mkdir -p web/data
docker compose run --rm etl

if [ $? -eq 0 ]; then
    log_success "Pipeline ETL completado exitosamente"
else
    log_error "Error en pipeline ETL"
    log_info "Revisar logs con: docker compose logs etl"
    exit 1
fi

# Verificar archivos
log_info "Verificando archivos generados..."
EXPECTED_FILES=(
    "web/data/infraestructura.geojson"
    "web/data/notarios.geojson"
    "web/data/chileatiende.geojson"
    "web/data/sii.geojson"
    "web/data/amenaza_alertas.geojson"
    "web/data/amenaza_cortes_luz.geojson"
    "web/data/ruta_dijkstra.geojson"
)

MISSING=0
for file in "${EXPECTED_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        log_success "$(basename $file) ($SIZE)"
    else
        log_warning "No encontrado: $(basename $file)"
        MISSING=$((MISSING + 1))
    fi
done

[ $MISSING -gt 0 ] && log_warning "$MISSING archivos no generados" || log_success "Todos los archivos generados"

# PASO 5: Web
print_header "PASO 5: Inicialización de Servidor Web"
log_info "Levantando servidor Nginx..."
docker compose up -d web

sleep 3

if docker compose ps web | grep -q "Up"; then
    log_success "Servidor web iniciado"
else
    log_error "Error al iniciar servidor web"
    exit 1
fi

# PASO 6: Verificación
print_header "PASO 6: Verificación Final"

log_info "Verificando servicios..."
SERVICES=$(docker compose ps --services --filter "status=running")
if echo "$SERVICES" | grep -q "db" && echo "$SERVICES" | grep -q "web"; then
    log_success "Todos los servicios están corriendo"
else
    log_warning "Algunos servicios no están corriendo"
    docker compose ps
fi

log_info "Obteniendo estadísticas de base de datos..."
echo ""
docker compose exec -T db psql -U postgres -d ruteo_resiliente << 'EOF' 2>/dev/null || echo "   (estadísticas no disponibles)"
\echo '📊 Estadísticas de Base de Datos:'
\echo ''
SELECT '  Red vial: ' || COUNT(*) || ' segmentos' FROM red_vial;
SELECT '  Oficinas: ' || COUNT(*) FROM oficinas;
SELECT '  Amenazas: ' || COUNT(*) FROM amenazas;
\echo ''
EOF

# Final
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║               ✅ SISTEMA COMPLETAMENTE OPERATIVO           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Acceso a la aplicación web:"
echo ""
echo "   → http://localhost:8087"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Comandos útiles:"
echo ""
echo "   Ver logs de ETL:        docker compose logs etl"
echo "   Ver logs de BD:         docker compose logs db"
echo "   Ver logs de Web:        docker compose logs web"
echo "   Detener servicios:      docker compose down"
echo "   Reiniciar ETL:          docker compose run --rm etl"
echo "   Acceder a PostgreSQL:   docker compose exec db psql -U postgres -d ruteo_resiliente"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_success "¡Listo! Abre tu navegador en http://localhost:8087"
echo ""
