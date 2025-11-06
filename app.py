"""
SISTEMA DE RECOMENDACIÓN MUSICAL - BACKEND API
Integrantes: Michael Esteban Guzman Narvaez - Karol Daniela Diaz Herrera
Fecha: Noviembre 2025

API REST con Flask para sistema de recomendación usando KNN desde cero.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from knn_engine import (
    calcular_similitud_coseno,
    encontrar_k_vecinos,
    clasificar_usuario,
    recomendar_canciones
)
import os

# Configuración de la aplicación
app = Flask(__name__)

# Configurar CORS para permitir peticiones desde cualquier origen
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Variable global para número de vecinos por defecto
K_VECINOS = 10


# ============================================================================
# CARGA DEL DATASET
# ============================================================================

print("="*70)
print("INICIANDO BACKEND - SISTEMA DE RECOMENDACIÓN MUSICAL")
print("="*70)
print("\n🔄 Cargando dataset...")

dataset_path = 'dataset_ratings.csv'

# Verificar que el archivo existe
if not os.path.exists(dataset_path):
    print(f"❌ ERROR: No se encuentra el archivo {dataset_path}")
    print(f"   Ubicación esperada: {os.path.abspath(dataset_path)}")
    print(f"   Archivos en el directorio: {os.listdir('.')}")
    exit(1)

# Cargar dataset
try:
    df_ratings = pd.read_csv(dataset_path)
    print(f"✓ Dataset cargado exitosamente")
    print(f"  Dimensiones originales: {df_ratings.shape}")
    
    # Limpiar datos
    print("🔧 Limpiando datos...")
    df_ratings = df_ratings.apply(pd.to_numeric, errors='coerce')
    df_ratings = df_ratings.fillna(0)
    df_ratings = df_ratings.astype(int)
    df_ratings = df_ratings.clip(lower=0, upper=5)
    
    print(f"  Dimensiones finales: {df_ratings.shape}")
    
except Exception as e:
    print(f"❌ ERROR al cargar dataset: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Convertir a matriz NumPy y extraer nombres
matriz_ratings = df_ratings.values.astype(float)
nombres_canciones = df_ratings.columns.tolist()

print(f"\n📊 Dataset preparado:")
print(f"   • Usuarios: {matriz_ratings.shape[0]:,}")
print(f"   • Canciones: {matriz_ratings.shape[1]:,}")
print(f"   • Densidad: {(np.sum(matriz_ratings>0)/matriz_ratings.size*100):.2f}%")
print(f"   • Primeras canciones: {nombres_canciones[:3]}")
print(f"   • Últimas canciones: {nombres_canciones[-3:]}")
print(f"\n✅ Backend listo para recibir peticiones\n")

df_ratings = df_ratings.clip(lower=0, upper=5)

# AGREGAR INMEDIATAMENTE DESPUÉS:
print("🧹 Eliminando columnas no musicales...")

# Eliminar columnas que no son canciones (UserID, Edad, Género, etc.)
columnas_a_eliminar = ['UserID', 'Edad', 'Género', 'edad', 'genero', 'userid', 'ID', 'id']
columnas_existentes = [col for col in columnas_a_eliminar if col in df_ratings.columns]

if columnas_existentes:
    print(f"   Eliminando: {columnas_existentes}")
    df_ratings = df_ratings.drop(columns=columnas_existentes)
    print(f"   Nuevas dimensiones: {df_ratings.shape}")

# También eliminar cualquier columna que no tenga valores válidos
columnas_vacias = df_ratings.columns[df_ratings.sum() == 0].tolist()
if columnas_vacias:
    print(f"   Eliminando columnas vacías: {len(columnas_vacias)}")
    df_ratings = df_ratings.drop(columns=columnas_vacias)
# ============================================================================
# ENDPOINTS DE LA API
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """
    Endpoint raíz - Información de la API
    
    Returns:
        JSON con información general y endpoints disponibles
    """
    return jsonify({
        'mensaje': 'API de Recomendación Musical con KNN',
        'version': '1.0.0',
        'estado': 'activo',
        'descripcion': 'Sistema de recomendación implementado desde cero usando KNN y similitud del coseno',
        'metrica': 'Similitud del Coseno',
        'integrantes': '[AGREGAR NOMBRES]',
        'endpoints': {
            'GET /': 'Información de la API',
            'GET /health': 'Health check del servicio',
            'GET /stats': 'Estadísticas del dataset',
            'GET /canciones': 'Lista de canciones disponibles',
            'GET /config': 'Configuración actual',
            'POST /config': 'Actualizar configuración',
            'POST /clasificar': 'Clasificar un nuevo usuario',
            'POST /recomendar': 'Recomendar canciones (endpoint principal)'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """
    Health check para monitoreo del servicio
    
    Returns:
        JSON indicando estado del servicio
    """
    return jsonify({
        'status': 'ok',
        'service': 'music-recommender-api',
        'dataset_loaded': matriz_ratings is not None,
        'dataset_shape': {
            'usuarios': int(matriz_ratings.shape[0]),
            'canciones': int(matriz_ratings.shape[1])
        }
    }), 200


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Retorna estadísticas generales del dataset
    
    Returns:
        JSON con métricas del dataset:
        - Total de usuarios y canciones
        - Evaluaciones totales y densidad
        - Rating promedio, mediana y desviación
        - Distribución de ratings (1-5 estrellas)
    """
    try:
        # Calcular métricas
        evaluaciones_totales = int(np.sum(matriz_ratings > 0))
        total_posible = int(matriz_ratings.size)
        densidad = (evaluaciones_totales / total_posible) * 100
        
        # Extraer solo ratings válidos
        ratings_validos = matriz_ratings[matriz_ratings > 0]
        
        return jsonify({
            'total_usuarios': int(matriz_ratings.shape[0]),
            'total_canciones': int(matriz_ratings.shape[1]),
            'evaluaciones_totales': evaluaciones_totales,
            'evaluaciones_posibles': total_posible,
            'densidad_porcentaje': round(float(densidad), 2),
            'rating_promedio_global': round(float(np.mean(ratings_validos)), 2),
            'rating_mediana_global': round(float(np.median(ratings_validos)), 2),
            'rating_desviacion_global': round(float(np.std(ratings_validos)), 2),
            'distribucion_ratings': {
                '1_estrella': int(np.sum(matriz_ratings == 1)),
                '2_estrellas': int(np.sum(matriz_ratings == 2)),
                '3_estrellas': int(np.sum(matriz_ratings == 3)),
                '4_estrellas': int(np.sum(matriz_ratings == 4)),
                '5_estrellas': int(np.sum(matriz_ratings == 5))
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500


@app.route('/canciones', methods=['GET'])
def get_canciones():
    """
    Retorna lista completa de canciones disponibles
    
    Query params opcionales:
        - limit: Número máximo de canciones a retornar
        - offset: Offset para paginación
    
    Returns:
        JSON con array de nombres de canciones
    """
    try:
        # Parámetros de paginación
        limit = request.args.get('limit', type=int, default=len(nombres_canciones))
        offset = request.args.get('offset', type=int, default=0)
        
        # Aplicar paginación
        canciones_paginadas = nombres_canciones[offset:offset+limit]
        
        return jsonify({
            'total': len(nombres_canciones),
            'offset': offset,
            'limit': limit,
            'count': len(canciones_paginadas),
            'canciones': canciones_paginadas
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error al obtener canciones: {str(e)}'}), 500


@app.route('/config', methods=['GET', 'POST'])
def config():
    """
    Obtiene o actualiza la configuración del sistema
    
    GET: Retorna configuración actual
    POST: Actualiza número de vecinos K
    
    Body para POST:
    {
        "k_vecinos": 15
    }
    
    Returns:
        JSON con configuración actual
    """
    global K_VECINOS
    
    if request.method == 'POST':
        try:
            data = request.json
            
            if 'k_vecinos' in data:
                nuevo_k = int(data['k_vecinos'])
                
                # Validar rango
                if 1 <= nuevo_k <= 100:
                    K_VECINOS = nuevo_k
                    return jsonify({
                        'mensaje': 'Configuración actualizada exitosamente',
                        'k_vecinos': K_VECINOS
                    }), 200
                else:
                    return jsonify({
                        'error': 'El valor de K debe estar entre 1 y 100'
                    }), 400
            else:
                return jsonify({
                    'error': 'Campo k_vecinos no encontrado en el body'
                }), 400
        
        except Exception as e:
            return jsonify({'error': f'Error al actualizar configuración: {str(e)}'}), 500
    
    # GET - Retornar configuración actual
    return jsonify({
        'k_vecinos': K_VECINOS,
        'dataset': {
            'total_usuarios': int(matriz_ratings.shape[0]),
            'total_canciones': int(matriz_ratings.shape[1])
        }
    }), 200


@app.route('/clasificar', methods=['POST'])
def clasificar():
    """
    Clasifica un nuevo usuario en una categoría
    
    Body (JSON):
    {
        "evaluaciones": [0, 5, 3, 0, 4, ...],
        "k_vecinos": 10  // Opcional
    }
    
    Returns:
        JSON con clasificación y métricas del vecindario
    """
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.json
        
        # Validar campo evaluaciones
        if 'evaluaciones' not in data:
            return jsonify({'error': 'Falta el campo "evaluaciones" en el body'}), 400
        
        # Convertir a array
        evaluaciones = np.array(data['evaluaciones'], dtype=float)
        
        # Validar dimensiones
        if len(evaluaciones) != len(nombres_canciones):
            return jsonify({
                'error': f'Se esperan {len(nombres_canciones)} evaluaciones, '
                        f'se recibieron {len(evaluaciones)}'
            }), 400
        
        # Validar rango de valores
        if np.any((evaluaciones < 0) | (evaluaciones > 5)):
            return jsonify({
                'error': 'Las evaluaciones deben estar entre 0 y 5'
            }), 400
        
        # Obtener K vecinos
        k = int(data.get('k_vecinos', K_VECINOS))
        
        # Validar K
        if k < 1 or k > matriz_ratings.shape[0]:
            return jsonify({
                'error': f'k_vecinos debe estar entre 1 y {matriz_ratings.shape[0]}'
            }), 400
        
        # Ejecutar clasificación
        resultado = clasificar_usuario(evaluaciones, matriz_ratings, k=k)
        
        return jsonify({
            'exito': True,
            'clasificacion': resultado,
            'parametros': {
                'k_vecinos_usado': k,
                'canciones_evaluadas': int(np.sum(evaluaciones > 0))
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'error': f'Error en los datos: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@app.route('/recomendar', methods=['POST'])
def recomendar():
    """
    Recomienda canciones personalizadas (ENDPOINT PRINCIPAL)
    
    Body (JSON):
    {
        "evaluaciones": [0, 5, 3, 0, 4, ...],
        "n_recomendaciones": 10,
        "k_vecinos": 10  // Opcional
    }
    
    Returns:
        JSON con clasificación del usuario y lista de recomendaciones
    """
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.json
        
        # Validar campo evaluaciones
        if 'evaluaciones' not in data:
            return jsonify({'error': 'Falta el campo "evaluaciones" en el body'}), 400
        
        # Convertir a array
        evaluaciones = np.array(data['evaluaciones'], dtype=float)
        
        # Validar dimensiones
        if len(evaluaciones) != len(nombres_canciones):
            return jsonify({
                'error': f'Se esperan {len(nombres_canciones)} evaluaciones, '
                        f'se recibieron {len(evaluaciones)}'
            }), 400
        
        # Validar rango
        if np.any((evaluaciones < 0) | (evaluaciones > 5)):
            return jsonify({
                'error': 'Las evaluaciones deben estar entre 0 y 5'
            }), 400
        
        # Verificar que haya canciones sin evaluar
        if np.sum(evaluaciones == 0) == 0:
            return jsonify({
                'error': 'El usuario ya evaluó todas las canciones. No hay recomendaciones disponibles.'
            }), 400
        
        # Obtener parámetros
        n_recomendaciones = int(data.get('n_recomendaciones', 10))
        k = int(data.get('k_vecinos', K_VECINOS))
        
        # Validar parámetros
        if n_recomendaciones <= 0:
            return jsonify({'error': 'n_recomendaciones debe ser mayor que 0'}), 400
        
        if k < 1 or k > matriz_ratings.shape[0]:
            return jsonify({
                'error': f'k_vecinos debe estar entre 1 y {matriz_ratings.shape[0]}'
            }), 400
        
        # Clasificar usuario
        clasificacion = clasificar_usuario(evaluaciones, matriz_ratings, k=k)
        
        # Generar recomendaciones
        recomendaciones = recomendar_canciones(
            evaluaciones,
            matriz_ratings,
            nombres_canciones,
            k_vecinos=k,
            n_recomendaciones=n_recomendaciones
        )
        
        return jsonify({
            'exito': True,
            'clasificacion': clasificacion,
            'recomendaciones': recomendaciones,
            'total_recomendaciones': len(recomendaciones),
            'parametros': {
                'k_vecinos_usado': k,
                'n_recomendaciones_solicitadas': n_recomendaciones,
                'canciones_evaluadas': int(np.sum(evaluaciones > 0)),
                'canciones_disponibles_recomendar': int(np.sum(evaluaciones == 0))
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'error': f'Error en los datos: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'mensaje': 'Verifica la URL y el método HTTP',
        'endpoints_disponibles': [
            'GET /',
            'GET /health',
            'GET /stats',
            'GET /canciones',
            'GET /config',
            'POST /config',
            'POST /clasificar',
            'POST /recomendar'
        ]
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Manejo de métodos HTTP no permitidos"""
    return jsonify({
        'error': 'Método HTTP no permitido',
        'mensaje': 'Verifica que estés usando el método correcto (GET/POST)'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos del servidor"""
    return jsonify({
        'error': 'Error interno del servidor',
        'mensaje': 'Contacta al administrador del sistema'
    }), 500


# ============================================================================
# INICIAR SERVIDOR
# ============================================================================

if __name__ == '__main__':
    # Configuración del servidor
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"\n🚀 Iniciando servidor en puerto {port}...")
    print(f"🌐 Modo: {'Desarrollo' if debug else 'Producción'}")
    print(f"📡 API disponible en: http://localhost:{port}")
    print(f"\n{'='*70}\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )