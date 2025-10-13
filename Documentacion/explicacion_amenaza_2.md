# Explicación del archivo `amenaza_2.json`

Este archivo contiene información sobre **amenazas naturales y geológicas** asociadas a nodos de infraestructura vial. Cada entrada representa un riesgo que puede afectar la seguridad de las rutas en zonas específicas.

## 🔍 Estructura del archivo

Cada objeto JSON incluye:

- `id`: Identificador único de la amenaza.
- `nodo_id`: ID del nodo donde se presenta la amenaza.
- `descripcion`: Tipo de amenaza (por ejemplo, deslizamiento de tierra, zona sísmica).
- `nivel_riesgo`: Valor numérico del 1 al 5 que indica la gravedad del riesgo (5 es el más alto).

## 📌 Ejemplo de contenido

```json
[
  {
    "id": 2,
    "nodo_id": 2,
    "descripcion": "deslizamiento de tierra",
    "nivel_riesgo": 4
  },
  {
    "id": 3,
    "nodo_id": 3,
    "descripcion": "zona sísmica activa",
    "nivel_riesgo": 5
  }
]
