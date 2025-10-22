#!/usr/bin/env python3
"""
ETL: Metadata completa de las 3 fuentes principales
1. Notarías (NotariosChile.cl)
2. ChileAtiende (fichas de trámites)
3. SII (oficinas y servicios)
"""
import json
import os
import shutil

def generar_notarios_completos():
    """
    METADATA 1: NOTARÍAS
    Fuente simulada: NotariosChile.cl
    Incluye: horarios, notarías de turno, servicios
    """
    return [
        # NOTARÍAS DE TURNO (fin de semana)
        {
            "nombre": "Primera Notaría de Santiago",
            "notario_titular": "Juan Carlos Rodríguez Pérez",
            "direccion": "Moneda 975, piso 2, Santiago Centro",
            "comuna": "Santiago",
            "lat": -33.4420,
            "lon": -70.6545,
            "telefono": "+56 2 2698 5411",
            "email": "contacto@primeranotariasantiago.cl",
            "horario_semana": "09:00-14:00",
            "horario_sabado": "09:00-13:00",
            "es_turno": True,
            "dias_turno": ["sabado"],
            "servicios": [
                "Compraventa de inmuebles",
                "Poderes generales y especiales",
                "Constitución de sociedades",
                "Testamentos abiertos",
                "Protocolización de documentos",
                "Autorización viaje menores"
            ],
            "tiempo_espera_promedio": 45,
            "atencion_con_hora": True,
            "accesibilidad": True,
            "estacionamiento": False,
            "web": "https://www.notarios.cl/notaria/primera-santiago",
            "estado": "abierto"
        },
        {
            "nombre": "Trigésima Notaría de Santiago",
            "notario_titular": "Patricia Isabel Fernández Rojas",
            "direccion": "Alameda 1851, Santiago Centro",
            "comuna": "Santiago",
            "lat": -33.4475,
            "lon": -70.6410,
            "telefono": "+56 2 2555 7632",
            "email": "info@notaria30stgo.cl",
            "horario_semana": "08:30-13:30",
            "horario_sabado": "09:00-13:00",
            "es_turno": True,
            "dias_turno": ["sabado", "domingo"],
            "servicios": [
                "Compraventa de inmuebles",
                "Sociedades y modificaciones",
                "Poderes bancarios",
                "Protocolizaciones",
                "Certificación de firmas",
                "Contratos de arriendo"
            ],
            "tiempo_espera_promedio": 30,
            "atencion_con_hora": False,
            "accesibilidad": True,
            "estacionamiento": True,
            "web": "https://www.notarios.cl/notaria/trigesima-santiago",
            "estado": "abierto"
        },
        # NOTARÍAS REGULARES
        {
            "nombre": "Décima Notaría de Santiago",
            "notario_titular": "María Elena González Silva",
            "direccion": "Agustinas 1442, oficina 503, Santiago Centro",
            "comuna": "Santiago",
            "lat": -33.4395,
            "lon": -70.6520,
            "telefono": "+56 2 2672 3890",
            "email": "info@decimanotaria.cl",
            "horario_semana": "09:00-13:30",
            "horario_sabado": "cerrado",
            "es_turno": False,
            "servicios": [
                "Compraventa de inmuebles",
                "Poderes generales",
                "Sociedades SpA",
                "Protocolizaciones",
                "Promesas de compraventa"
            ],
            "tiempo_espera_promedio": 60,
            "atencion_con_hora": True,
            "accesibilidad": False,
            "estacionamiento": False,
            "estado": "abierto"
        },
        {
            "nombre": "Vigésima Notaría de Santiago",
            "notario_titular": "Roberto Andrés Martínez Lagos",
            "direccion": "Huérfanos 1160, piso 8, Santiago Centro",
            "comuna": "Santiago",
            "lat": -33.4382,
            "lon": -70.6498,
            "telefono": "+56 2 2639 8745",
            "email": "contacto@notaria20.cl",
            "horario_semana": "09:00-14:00",
            "horario_sabado": "cerrado",
            "es_turno": False,
            "servicios": [
                "Escrituras públicas",
                "Testamentos",
                "Autorizaciones de viaje",
                "Mandatos judiciales",
                "Compraventas"
            ],
            "tiempo_espera_promedio": 55,
            "atencion_con_hora": True,
            "accesibilidad": True,
            "estacionamiento": False,
            "estado": "abierto"
        },
        {
            "nombre": "Cuadragésima Segunda Notaría de Santiago",
            "notario_titular": "Luis Fernando Muñoz Castro",
            "direccion": "San Diego 1470, Santiago Centro",
            "comuna": "Santiago",
            "lat": -33.4520,
            "lon": -70.6505,
            "telefono": "+56 2 2688 4521",
            "email": "notaria42santiago@gmail.com",
            "horario_semana": "09:00-13:00",
            "horario_sabado": "cerrado",
            "es_turno": False,
            "servicios": [
                "Poderes simples",
                "Autorizaciones",
                "Declaraciones juradas",
                "Finiquitos laborales"
            ],
            "tiempo_espera_promedio": 25,
            "atencion_con_hora": False,
            "accesibilidad": True,
            "estacionamiento": False,
            "estado": "abierto"
        }
    ]

def generar_chileatiende_completo():
    """
    METADATA 2: CHILEATIENDE
    Fuente simulada: fichas ChileAtiende con códigos de trámite
    Incluye: trámites disponibles, requisitos, tiempos
    """
    return [
        {
            "nombre": "ChileAtiende Moneda",
            "tipo_sucursal": "integral",
            "direccion": "Moneda 1342, Santiago Centro",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "lat": -33.4430,
            "lon": -70.6520,
            "telefono": "101",
            "email": "moneda@chileatiende.gob.cl",
            "horario_atencion": {
                "lunes_viernes": "08:30-14:00",
                "sabado": "cerrado",
                "atencion_preferencial": "08:30-09:30"
            },
            "servicios_destacados": [
                {
                    "codigo": "3379",
                    "nombre": "Certificado de nacimiento para todo trámite",
                    "institucion": "Registro Civil",
                    "tiempo_tramite": 15,
                    "costo": 1350,
                    "requisitos": ["Cédula de identidad vigente"]
                },
                {
                    "codigo": "445",
                    "nombre": "Copia de inscripción de constitución de sociedad",
                    "institucion": "Registro de Empresas",
                    "tiempo_tramite": 20,
                    "costo": 8100,
                    "requisitos": ["RUT empresa", "Cédula representante legal"]
                },
                {
                    "codigo": "30419",
                    "nombre": "Constitución de sociedad - Empresa en un día",
                    "institucion": "Registro de Empresas",
                    "tiempo_tramite": 60,
                    "costo": 0,
                    "requisitos": ["ClaveÚnica", "Datos socios", "Capital inicial"]
                }
            ],
            "infraestructura": {
                "acceso_discapacitados": True,
                "modulo_autoatencion": True,
                "sala_espera_climatizada": True,
                "baños_publicos": True,
                "wifi_gratuito": True,
                "estacionamiento": False
            },
            "indicadores_atencion": {
                "tiempo_espera_promedio": 35,
                "satisfaccion_usuarios": 4.2,
                "tramites_diarios": 450
            },
            "estado": "operativo"
        },
        {
            "nombre": "ChileAtiende Plaza de Armas",
            "tipo_sucursal": "integral",
            "direccion": "Compañía de Jesús 1131, Santiago Centro",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "lat": -33.4379,
            "lon": -70.6534,
            "telefono": "101",
            "email": "plazadearmas@chileatiende.gob.cl",
            "horario_atencion": {
                "lunes_viernes": "08:30-14:00",
                "sabado": "09:00-13:00",
                "atencion_preferencial": "todo horario"
            },
            "servicios_destacados": [
                {
                    "codigo": "1234",
                    "nombre": "Cédula de identidad - Renovación",
                    "institucion": "Registro Civil",
                    "tiempo_tramite": 20,
                    "costo": 5400,
                    "requisitos": ["Cédula anterior o denuncia"]
                },
                {
                    "codigo": "9876",
                    "nombre": "Certificado de antecedentes",
                    "institucion": "Registro Civil",
                    "tiempo_tramite": 10,
                    "costo": 1700,
                    "requisitos": ["Cédula de identidad"]
                },
                {
                    "codigo": "5555",
                    "nombre": "Posesión efectiva",
                    "institucion": "Registro Civil",
                    "tiempo_tramite": 45,
                    "costo": 12500,
                    "requisitos": ["Certificado defunción", "Documentos herederos"]
                }
            ],
            "infraestructura": {
                "acceso_discapacitados": True,
                "modulo_autoatencion": True,
                "sala_espera_climatizada": True,
                "baños_publicos": True,
                "wifi_gratuito": True,
                "estacionamiento": False
            },
            "indicadores_atencion": {
                "tiempo_espera_promedio": 40,
                "satisfaccion_usuarios": 4.0,
                "tramites_diarios": 520
            },
            "estado": "operativo"
        },
        {
            "nombre": "ChileAtiende Express Huérfanos",
            "tipo_sucursal": "express",
            "direccion": "Huérfanos 862, local 15, Santiago Centro",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "lat": -33.4385,
            "lon": -70.6497,
            "telefono": "101",
            "email": "huerfanos@chileatiende.gob.cl",
            "horario_atencion": {
                "lunes_viernes": "09:00-17:00",
                "sabado": "10:00-14:00",
                "atencion_preferencial": "sin restricción"
            },
            "servicios_destacados": [
                {
                    "codigo": "1111",
                    "nombre": "Certificados en línea",
                    "institucion": "Múltiples",
                    "tiempo_tramite": 5,
                    "costo": "variable",
                    "requisitos": ["ClaveÚnica"]
                },
                {
                    "codigo": "2222",
                    "nombre": "Orientación trámites",
                    "institucion": "ChileAtiende",
                    "tiempo_tramite": 10,
                    "costo": 0,
                    "requisitos": ["Ninguno"]
                }
            ],
            "infraestructura": {
                "acceso_discapacitados": True,
                "modulo_autoatencion": True,
                "sala_espera_climatizada": False,
                "baños_publicos": False,
                "wifi_gratuito": True,
                "estacionamiento": False
            },
            "indicadores_atencion": {
                "tiempo_espera_promedio": 15,
                "satisfaccion_usuarios": 4.5,
                "tramites_diarios": 180
            },
            "estado": "operativo"
        }
    ]

def generar_sii_completo():
    """
    METADATA 3: SII
    Fuente simulada: directorio SII con servicios específicos
    Incluye: tipos de trámites, requisitos, códigos
    """
    return [
        {
            "nombre": "SII Santiago Centro - Teatinos",
            "codigo_oficina": "3048-7",
            "tipo_oficina": "direccion_regional",
            "direccion": "Teatinos 120, Santiago Centro",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "lat": -33.4370,
            "lon": -70.6530,
            "telefono": "+56 2 2 395 4000",
            "email": "santiago.centro@sii.cl",
            "horario": {
                "lunes_viernes": "09:00-14:00",
                "atencion_contribuyentes": "09:00-13:30",
                "mesa_ayuda": "09:00-14:00"
            },
            "servicios_presenciales": [
                {
                    "codigo": "F4415",
                    "nombre": "Inicio de actividades persona natural",
                    "tiempo_atencion": 30,
                    "documentos": [
                        "Cédula de identidad",
                        "Acreditación domicilio",
                        "Antecedentes actividad económica"
                    ],
                    "observaciones": "Agendar hora en sii.cl"
                },
                {
                    "codigo": "F2890",
                    "nombre": "Declaración y pago impuesto transferencia bienes raíces",
                    "tiempo_atencion": 45,
                    "documentos": [
                        "Escritura pública compraventa",
                        "Certificado avalúo fiscal",
                        "RUT vendedor y comprador",
                        "Formulario 2890 prellenado"
                    ],
                    "observaciones": "Plazo 60 días desde escritura"
                },
                {
                    "codigo": "F3239",
                    "nombre": "Término de giro",
                    "tiempo_atencion": 40,
                    "documentos": [
                        "RUT empresa",
                        "Certificado última declaración",
                        "Libro contable al día"
                    ],
                    "observaciones": "Requiere estar al día en declaraciones"
                },
                {
                    "codigo": "AT2021",
                    "nombre": "Rectificatoria IVA",
                    "tiempo_atencion": 35,
                    "documentos": [
                        "F29 original",
                        "Documentación respaldo",
                        "Carta explicativa"
                    ],
                    "observaciones": "Solo últimos 3 períodos"
                }
            ],
            "infraestructura": {
                "accesibilidad_universal": True,
                "modulos_atencion": 12,
                "sistema_turnos": "digital",
                "sala_espera": 80,
                "estacionamiento": False,
                "cafeteria": True
            },
            "estadisticas": {
                "atencion_diaria_promedio": 380,
                "tiempo_espera_promedio": 45,
                "horario_peak": "10:00-12:00",
                "satisfaccion": 3.8
            },
            "estado": "operativo"
        },
        {
            "nombre": "SII Dirección Regional Metropolitana Santiago Centro",
            "codigo_oficina": "3049-5",
            "tipo_oficina": "direccion_regional",
            "direccion": "Morandé 360, Santiago Centro",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "lat": -33.4355,
            "lon": -70.6542,
            "telefono": "+56 2 2 395 5000",
            "email": "drmsc@sii.cl",
            "horario": {
                "lunes_viernes": "09:00-14:00",
                "atencion_contribuyentes": "09:00-13:00",
                "tramites_complejos": "solo con hora"
            },
            "servicios_presenciales": [
                {
                    "codigo": "GC001",
                    "nombre": "Grandes contribuyentes - Fiscalización",
                    "tiempo_atencion": 120,
                    "documentos": [
                        "Citación SII",
                        "Contabilidad completa",
                        "Representación legal"
                    ],
                    "observaciones": "Solo con citación previa"
                },
                {
                    "codigo": "RES100",
                    "nombre": "Resoluciones y recursos",
                    "tiempo_atencion": 60,
                    "documentos": [
                        "Escrito de reclamación",
                        "Antecedentes del caso",
                        "Poder notarial si corresponde"
                    ],
                    "observaciones": "Plazo 60 días hábiles"
                },
                {
                    "codigo": "CERT99",
                    "nombre": "Certificados especiales",
                    "tiempo_atencion": 30,
                    "documentos": ["Según tipo certificado"],
                    "observaciones": "Algunos disponibles en línea"
                }
            ],
            "infraestructura": {
                "accesibilidad_universal": True,
                "modulos_atencion": 8,
                "sistema_turnos": "digital",
                "sala_espera": 60,
                "estacionamiento": True,
                "cafeteria": False
            },
            "estadisticas": {
                "atencion_diaria_promedio": 250,
                "tiempo_espera_promedio": 55,
                "horario_peak": "11:00-13:00",
                "satisfaccion": 3.5
            },
            "estado": "operativo"
        },
        {
            "nombre": "Centro de Atención SII Alameda",
            "codigo_oficina": "3050-9",
            "tipo_oficina": "centro_atencion",
            "direccion": "Alameda 1315, Santiago Centro",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "lat": -33.4450,
            "lon": -70.6575,
            "telefono": "+56 2 2 395 4100",
            "email": "alameda@sii.cl",
            "horario": {
                "lunes_viernes": "09:00-14:00",
                "atencion_express": "09:00-17:00",
                "sabado": "cerrado"
            },
            "servicios_presenciales": [
                {
                    "codigo": "EX001",
                    "nombre": "Obtención RUT primera vez",
                    "tiempo_atencion": 15,
                    "documentos": [
                        "Cédula de identidad",
                        "Comprobante domicilio"
                    ],
                    "observaciones": "Entrega inmediata"
                },
                {
                    "codigo": "EX002",
                    "nombre": "Clave tributaria",
                    "tiempo_atencion": 10,
                    "documentos": ["Cédula de identidad"],
                    "observaciones": "Reseteo inmediato"
                },
                {
                    "codigo": "EX003",
                    "nombre": "Certificados simples",
                    "tiempo_atencion": 5,
                    "documentos": ["RUT o cédula"],
                    "observaciones": "Varios disponibles"
                },
                {
                    "codigo": "ORI001",
                    "nombre": "Orientación tributaria",
                    "tiempo_atencion": 20,
                    "documentos": ["Según consulta"],
                    "observaciones": "Sin costo"
                }
            ],
            "infraestructura": {
                "accesibilidad_universal": True,
                "modulos_atencion": 6,
                "sistema_turnos": "manual",
                "sala_espera": 40,
                "estacionamiento": False,
                "cafeteria": False
            },
            "estadisticas": {
                "atencion_diaria_promedio": 180,
                "tiempo_espera_promedio": 25,
                "horario_peak": "09:00-11:00",
                "satisfaccion": 4.1
            },
            "estado": "operativo"
        }
    ]

def generar_conservador_bienes_raices():
    """
    BONUS: Conservador de Bienes Raíces (para completar el trámite)
    """
    return {
        "nombre": "Conservador de Bienes Raíces de Santiago",
        "tipo": "conservador",
        "direccion": "Morandé 440, Santiago Centro",
        "comuna": "Santiago",
        "region": "Metropolitana",
        "lat": -33.4380,
        "lon": -70.6540,
        "telefono": "+56 2 2639 4500",
        "email": "info@cbrsantiago.cl",
        "horario": "09:00-13:30",
        "dias_atencion": ["lunes", "martes", "miercoles", "jueves", "viernes"],
        "servicios": [
            "Inscripción de dominio",
            "Certificados de dominio vigente",
            "Certificados de hipotecas y gravámenes",
            "Inscripción de hipotecas",
            "Alzamiento de hipotecas"
        ],
        "tiempo_tramite_promedio": 90,
        "costo_inscripcion_promedio": 95000,
        "documentos_requeridos": [
            "Escritura pública notariada",
            "Certificado de avalúo fiscal",
            "Certificado de no expropiación",
            "Minuta de inscripción"
        ],
        "observaciones": "Inscripción demora 15-20 días hábiles",
        "estado": "operativo"
    }

def convertir_a_geojson(datos):
    """Convierte lista de oficinas a GeoJSON con propiedades completas"""
    features = []
    for item in datos:
        # Si es una lista, procesarla
        if isinstance(datos, list):
            items = datos
        else:
            items = [datos]
            
        for item in items:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [item["lon"], item["lat"]]
                },
                "properties": item
            }
            features.append(feature)
        break
    
    return {
        "type": "FeatureCollection",
        "metadata": {
            "descripcion": "Oficinas públicas con metadata completa",
            "fuentes": ["NotariosChile.cl", "ChileAtiende.gob.cl", "SII.cl"],
            "fecha_actualizacion": "2024-10-27"
        },
        "features": features
    }

def main(out_dir="/app/out"):
    """Genera los 3 archivos de metadata principales"""
    print("📊 ETL METADATA COMPLETA - Las 3 fuentes principales")
    print("=" * 60)
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. NOTARÍAS
    print("\n📝 [1/4] Procesando NOTARÍAS...")
    notarios = generar_notarios_completos()
    
    with open(os.path.join(out_dir, "notarios.json"), 'w', encoding='utf-8') as f:
        json.dump(notarios, f, ensure_ascii=False, indent=2)
    
    geojson = convertir_a_geojson(notarios)
    with open(os.path.join(out_dir, "notarios.geojson"), 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ {len(notarios)} notarías ({sum(1 for n in notarios if n['es_turno'])} de turno)")
    
    # 2. CHILEATIENDE
    print("\n🏛️  [2/4] Procesando CHILEATIENDE...")
    chileatiende = generar_chileatiende_completo()
    
    with open(os.path.join(out_dir, "chileatiende.json"), 'w', encoding='utf-8') as f:
        json.dump(chileatiende, f, ensure_ascii=False, indent=2)
    
    geojson = convertir_a_geojson(chileatiende)
    with open(os.path.join(out_dir, "chileatiende.geojson"), 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ {len(chileatiende)} sucursales")
    print(f"   ✓ {sum(len(s['servicios_destacados']) for s in chileatiende)} servicios catalogados")
    
    # 3. SII
    print("\n💼 [3/4] Procesando SII...")
    sii = generar_sii_completo()
    
    with open(os.path.join(out_dir, "sii.json"), 'w', encoding='utf-8') as f:
        json.dump(sii, f, ensure_ascii=False, indent=2)
    
    geojson = convertir_a_geojson(sii)
    with open(os.path.join(out_dir, "sii.geojson"), 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ {len(sii)} oficinas SII")
    print(f"   ✓ {sum(len(s['servicios_presenciales']) for s in sii)} servicios disponibles")
    
    # 4. BONUS: Conservador BR
    print("\n🏛️  [4/4] Procesando CONSERVADOR BR...")
    conservador = generar_conservador_bienes_raices()
    
    # Lo agregamos como oficina adicional
    with open(os.path.join(out_dir, "conservador.json"), 'w', encoding='utf-8') as f:
        json.dump([conservador], f, ensure_ascii=False, indent=2)
    
    # Copiar a web/data si existe
    web_data_dir = os.environ.get("WEB_DATA_DIR")
    if web_data_dir and os.path.isdir(web_data_dir):
        for archivo in ["notarios.json", "notarios.geojson", 
                       "chileatiende.json", "chileatiende.geojson",
                       "sii.json", "sii.geojson", "conservador.json"]:
            origen = os.path.join(out_dir, archivo)
            if os.path.exists(origen):
                shutil.copy2(origen, os.path.join(web_data_dir, archivo))
        print("\n✓ Archivos copiados a web/data")
    
    print("\n" + "=" * 60)
    print("✅ METADATA COMPLETA GENERADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
