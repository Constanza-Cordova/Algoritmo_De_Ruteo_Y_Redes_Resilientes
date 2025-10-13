# Explicación del archivo `amenaza_1.json`

Este archivo contiene información sobre **amenazas asociadas a nodos de infraestructura vial**. Cada entrada representa un riesgo o condición adversa que puede afectar la seguridad o accesibilidad de una ruta.

## 🔍 Estructura del archivo

Cada objeto JSON incluye los siguientes campos:

- `id`: Identificador único de la amenaza.
- `nodo_id`: Referencia al nodo de infraestructura donde se presenta la amenaza.
- `descripcion`: Tipo o naturaleza de la amenaza (por ejemplo, inundación, corte de energía).
- `nivel_riesgo`: Valor numérico que representa la gravedad del riesgo (escala del 1 al 5, donde 5 es el más alto).

## 📌 Ejemplo de contenido

```json
[
  {
    "id": 1,
    "nodo_id": 1,
    "descripcion": "inundación",
    "nivel_riesgo": 3
  }
]
