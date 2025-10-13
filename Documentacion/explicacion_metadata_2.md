# Explicación del archivo `metadata_2.json`

Este archivo contiene información de **iluminación asociada a nodos de infraestructura**. Cada entrada describe el nivel de iluminación en el entorno del nodo, lo cual puede influir en la seguridad y visibilidad de las rutas.

## 🔍 Estructura del archivo

Cada objeto JSON incluye:

- `id`: Identificador único de la metadata.
- `nodo_id`: ID del nodo al que se asocia esta metadata.
- `tipo`: Tipo de metadata registrada (en este caso, "iluminacion").
- `valor`: Valor específico que describe la calidad de la iluminación.

## 📌 Ejemplo de contenido

```json
[
  {
    "id": 2,
    "nodo_id": 2,
    "tipo": "iluminacion",
    "valor": "buena"
  },
  {
    "id": 3,
    "nodo_id": 3,
    "tipo": "iluminacion",
    "valor": "deficiente"
  }
]
