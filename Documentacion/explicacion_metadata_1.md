# Explicación del archivo `metadata_1.json`

Este archivo contiene información de **metadata asociada a nodos de infraestructura vial**. Cada entrada describe una característica adicional del nodo, útil para enriquecer el análisis de rutas y condiciones del entorno.

## 🔍 Estructura del archivo

El archivo es un arreglo de objetos JSON con los siguientes campos:

- `id`: Identificador único de la metadata.
- `nodo_id`: Referencia al nodo de infraestructura al que se asocia esta metadata.
- `tipo`: Tipo de información que se está registrando (por ejemplo, tipo de vía, iluminación, estado del pavimento).
- `valor`: Valor específico correspondiente al tipo de metadata.

## 📌 Ejemplo de contenido

```json
[
  {
    "id": 1,
    "nodo_id": 1,
    "tipo": "tipo_via",
    "valor": "asfaltada"
  }
]
