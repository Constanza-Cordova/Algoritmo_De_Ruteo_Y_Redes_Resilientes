# Explicación del archivo `amenaza_3.json`

Este archivo contiene información sobre **amenazas operacionales y ambientales** asociadas a nodos de infraestructura vial. Cada entrada representa una condición adversa que puede afectar la funcionalidad o seguridad de una ruta.

## 🔍 Estructura del archivo

Cada objeto JSON incluye:

- `id`: Identificador único de la amenaza.
- `nodo_id`: ID del nodo donde se presenta la amenaza.
- `descripcion`: Tipo de amenaza (por ejemplo, incendios forestales, cortes de energía).
- `nivel_riesgo`: Valor numérico del 1 al 5 que indica la gravedad del riesgo (5 es el más alto).

## 📌 Ejemplo de contenido

```json
[
  {
    "id": 4,
    "nodo_id": 4,
    "descripcion": "zona de incendios forestales",
    "nivel_riesgo": 3
  },
  {
    "id": 5,
    "nodo_id": 5,
    "descripcion": "corte de energía frecuente",
    "nivel_riesgo": 2
  }
]
