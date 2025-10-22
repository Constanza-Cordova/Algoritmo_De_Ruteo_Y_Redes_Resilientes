#!/usr/bin/env python3
"""
ETL: Definición de Trámites y sus Pasos
Basado en la metadata de ChileAtiende y plan del proyecto.
Genera un JSON simple, no un GeoJSON.
"""
import json
import os
import shutil

def generar_datos_tramites():
    """
    Define la secuencia de pasos para cada trámite soportado.
    Esto se basa en la lógica de las PPTs.
    """
    return [
        {
            "id_tramite": "T-01",
            "nombre": "Compraventa de Inmueble",
            "fuente": "ChileAtiende / Notarios",
            "pasos": [
                {
                    "orden": 1,
                    "tipo_oficina": "notaria",
                    "descripcion": "Firma de escritura de compraventa",
                    "requisitos": ["Cédula de identidad", "Borrador escritura", "Certificados del inmueble"]
                },
                {
                    "orden": 2,
                    "tipo_oficina": "conservador",
                    "descripcion": "Inscripción en Conservador de Bienes Raíces",
                    "requisitos": ["Copia autorizada de escritura"]
                },
                {
                    "orden": 3,
                    "tipo_oficina": "sii",
                    "descripcion": "Declaración y pago de impuesto a la transferencia",
                    "requisitos": ["Escritura inscrita", "Formulario 2890"]
                }
            ]
        },
        {
            "id_tramite": "T-02",
            "nombre": "Transferencia de vehículo usado",
            "fuente": "ChileAtiende Ficha 3449",
            "pasos": [
                {
                    "orden": 1,
                    "tipo_oficina": "registro_civil",
                    "descripcion": "Declaración consensual de transferencia",
                    "requisitos": ["Cédula de identidad (comprador y vendedor)", "Permiso de circulación", "Certificado de revisión técnica"]
                }
            ]
        },
        {
            "id_tramite": "T-03",
            "nombre": "Constitución de Sociedad (en un día)",
            "fuente": "ChileAtiende Ficha 30419",
            "pasos": [
                {
                    "orden": 1,
                    "tipo_oficina": "notaria",
                    "descripcion": "Firma electrónica de socios",
                    "requisitos": ["ClaveÚnica de socios", "Borrador de estatutos"]
                },
                {
                    "orden": 2,
                    "tipo_oficina": "sii",
                    "descripcion": "Obtención de RUT e Inicio de Actividades",
                    "requisitos": ["Formulario de constitución firmado"]
                }
            ]
        }
    ]

def main(out_dir="/app/out"):
    """Función principal del ETL"""
    print("🧠 ETL Trámites (ChileAtiende) - Generando pasos...")
    os.makedirs(out_dir, exist_ok=True)
    
    # Generar datos
    datos = generar_datos_tramites()
    
    # Guardar JSON
    json_path = os.path.join(out_dir, "tramites.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    # Copiar a web/data
    web_data_dir = os.environ.get("WEB_DATA_DIR")
    if web_data_dir and os.path.isdir(web_data_dir):
        shutil.copy2(json_path, os.path.join(web_data_dir, "tramites.json"))
    
    print(f"✓ Generados {len(datos)} trámites con sus pasos")
    print(f"✓ {json_path}")
    return datos

if __name__ == "__main__":
    main()
