# 🎵 Sistema de Recomendación Musical - Backend

**Integrantes:** [AGREGAR NOMBRES]  
**Fecha:** Noviembre 2025

Sistema de recomendación musical implementado completamente desde cero usando K-Nearest Neighbors (KNN) con similitud del coseno.

## 🎯 Características

- ✅ KNN implementado desde cero (sin librerías de ML)
- ✅ Similitud del coseno como métrica
- ✅ Clasificación de usuarios en 6 categorías
- ✅ Recomendaciones personalizadas
- ✅ API REST con Flask
- ✅ Dockerizado y listo para producción

## 📐 Métrica Utilizada

**Similitud del Coseno**: `cos(θ) = (A·B) / (||A|| × ||B||)`

### Justificación:
1. Maneja eficientemente datos dispersos (70% ceros)
2. Insensible a cantidad de evaluaciones
3. Mide similitud por patrones
4. Normalización implícita [0,1]
5. Estándar de la industria
6. Computacionalmente eficiente

## 🚀 Instalación y Ejecución

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd music-recommender-backend

# 2. Construir y ejecutar
docker-compose up -d

# 3. Verificar que esté funcionando
curl http://localhost:5000/health
```

### Opción 2: Sin Docker

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor
python app.py
```

## 📡 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/health` | Health check |
| GET | `/stats` | Estadísticas del dataset |
| GET | `/canciones` | Lista de canciones |
| GET | `/config` | Configuración actual |
| POST | `/config` | Actualizar configuración |
| POST | `/clasificar` | Clasificar usuario |
| POST | `/recomendar` | **Endpoint principal** - Recomendar canciones |

## 📝 Ejemplos de Uso

### Clasificar Usuario

```bash
curl -X POST http://localhost:5000/clasificar \
  -H "Content-Type: application/json" \
  -d '{
    "evaluaciones": [0,5,3,0,4,...],
    "k_vecinos": 10
  }'
```

### Recomendar Canciones

```bash
curl -X POST http://localhost:5000/recomendar \
  -H "Content-Type: application/json" \
  -d '{
    "evaluaciones": [0,5,3,0,4,...],
    "n_recomendaciones": 15,
    "k_vecinos": 10
  }'
```

## 🏗️ Estructura del Proyecto

```
music-recommender-backend/
├── app.py                  # Servidor Flask y endpoints
├── knn_engine.py          # Motor KNN desde cero
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación
├── nginx.conf           # Configuración proxy
├── dataset_ratings.csv  # Dataset de evaluaciones
└── README.md           # Esta documentación
```

## 🎭 Categorías de Usuarios

| Categoría | Rating | Actividad | Descripción |
|-----------|--------|-----------|-------------|
| Entusiastas | ≥4.0 | >100 | Muy activos, ratings altos |
| Selectivos Positivos | ≥4.0 | ≤100 | Poco activos, ratings altos |
| Moderados Activos | 3-4 | >100 | Muy activos, gustos variados |
| Moderados Casuales | 3-4 | ≤100 | Uso ocasional |
| Críticos | <3.0 | >100 | Muy activos, exigentes |
| Exploradores | <3.0 | ≤100 | Nuevos usuarios |

## 🌐 Despliegue en Cloudflare

### Preparar para Cloudflare Pages

```bash
# 1. Instalar Wrangler CLI
npm install -g wrangler

# 2. Login a Cloudflare
wrangler login

# 3. Configurar proyecto
wrangler pages project create music-recommender

# 4. Desplegar
wrangler pages publish frontend
```

### Cloudflare Workers (Backend)

```bash
# 1. Crear worker
wrangler init music-recommender-api

# 2. Desplegar
wrangler publish
```

## 🔧 Configuración

Variables de entorno en `.env`:

```bash
FLASK_ENV=production
PORT=5000
DATASET_PATH=dataset_ratings.csv
K_VECINOS_DEFAULT=10
```

## 📊 Requisitos del Sistema

- Python 3.9+
- 2GB RAM mínimo
- Docker y Docker Compose (opcional)

## 🐛 Troubleshooting

### Puerto ya en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8000:5000"  # Usar puerto 8000
```

### Dataset no encontrado
```bash
# Verificar que dataset_ratings.csv esté en el directorio raíz
ls -la dataset_ratings.csv
```

## 📚 Documentación Adicional

- **Algoritmo KNN**: Ver `knn_engine.py`
- **API Endpoints**: Ver `app.py`
- **Despliegue**: Ver sección de Cloudflare

## 👥 Equipo

[AGREGAR NOMBRES DE INTEGRANTES]

## 📄 Licencia

Este proyecto es parte de un trabajo académico.

---

**¿Preguntas?** Revisa la documentación en el código o contacta al equipo.