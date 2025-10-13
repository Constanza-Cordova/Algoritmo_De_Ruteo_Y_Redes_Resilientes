import subprocess

def ejecutar_todo():
    subprocess.run(["python", "Infraestructura/extraer_infraestructura.py"])
    subprocess.run(["python", "Metadata/extraer_metadata_1.py"])
    subprocess.run(["python", "Amenazas/extraer_amenaza_1.py"])
    subprocess.run(["python", "CargaBD/cargar_infraestructura.py"])
    print("Proceso ETL completo. Sitio web listo.")

if __name__ == "__main__":
    ejecutar_todo()
