"""
MOTOR KNN - IMPLEMENTACIÓN DESDE CERO
Integrantes: [AGREGAR NOMBRES]
Fecha: Noviembre 2025

Implementación completa del algoritmo K-Nearest Neighbors (KNN)
usando solo NumPy. No se utilizan librerías de Machine Learning.

MÉTRICA: Similitud del Coseno
JUSTIFICACIÓN:
1. Maneja eficientemente datos dispersos (muchos ceros)
2. Insensible a diferencias en cantidad de evaluaciones
3. Mide similitud por patrones, no por magnitud
4. Rango normalizado [0,1] facilita interpretación
5. Estándar de la industria en sistemas de recomendación
6. Computacionalmente eficiente
"""

import numpy as np


def calcular_similitud_coseno(vector_a, vector_b):
    """
    Calcula la similitud del coseno entre dos vectores de evaluaciones.
    
    FUNDAMENTO MATEMÁTICO:
    La similitud del coseno mide el coseno del ángulo entre dos vectores
    en un espacio multidimensional.
    
    FÓRMULA:
    similitud = cos(θ) = (A · B) / (||A|| × ||B||)
    
    Donde:
    - A · B es el producto punto (dot product)
    - ||A|| es la norma euclidiana (magnitud) del vector A
    - ||B|| es la norma euclidiana (magnitud) del vector B
    
    INTERPRETACIÓN:
    - 1.0: Vectores idénticos (ángulo 0°)
    - 0.5-0.9: Alta similitud
    - 0.0: Vectores ortogonales (sin relación)
    
    EJEMPLO:
    Usuario A: [5, 4, 0, 3, 5]
    Usuario B: [4, 5, 0, 4, 4]
    → Similitud alta (~0.99)
    
    Args:
        vector_a (np.array): Vector de evaluaciones del usuario A
        vector_b (np.array): Vector de evaluaciones del usuario B
    
    Returns:
        float: Similitud del coseno en rango [0, 1]
    
    Complejidad:
        O(n) donde n es la longitud de los vectores
    """
    # Paso 1: Calcular producto punto
    producto_punto = np.dot(vector_a, vector_b)
    
    # Paso 2: Calcular normas (magnitudes)
    norma_a = np.sqrt(np.sum(vector_a ** 2))
    norma_b = np.sqrt(np.sum(vector_b ** 2))
    
    # Paso 3: Manejar casos especiales (vectores nulos)
    if norma_a == 0 or norma_b == 0:
        return 0.0
    
    # Paso 4: Calcular similitud
    similitud = producto_punto / (norma_a * norma_b)
    
    return similitud


def encontrar_k_vecinos(candidato, matriz_usuarios, k=10):
    """
    Encuentra los K usuarios más similares al candidato.
    
    ALGORITMO:
    1. Calcular similitud del coseno entre candidato y cada usuario
    2. Ordenar usuarios por similitud (descendente)
    3. Seleccionar los K más similares
    
    PROCESO:
    Para cada usuario i en el dataset:
        similitud[i] = calcular_similitud_coseno(candidato, usuario[i])
    
    Args:
        candidato (np.array): Vector de evaluaciones del nuevo usuario
                             Dimensión: (n_canciones,)
        matriz_usuarios (np.array): Matriz con todos los usuarios
                                   Dimensión: (n_usuarios, n_canciones)
        k (int): Número de vecinos a retornar
    
    Returns:
        tuple: (indices_vecinos, similitudes_vecinos)
               - indices: np.array con posiciones de vecinos
               - similitudes: np.array con valores de similitud
    
    Complejidad:
        O(n × m + n log n)
        donde n = usuarios, m = canciones
    """
    n_usuarios = matriz_usuarios.shape[0]
    similitudes = np.zeros(n_usuarios)
    
    # Calcular similitud con cada usuario
    for i in range(n_usuarios):
        similitudes[i] = calcular_similitud_coseno(candidato, matriz_usuarios[i])
    
    # Ordenar por similitud (descendente)
    indices_ordenados = np.argsort(similitudes)[::-1]
    
    # Seleccionar top K
    k_vecinos_indices = indices_ordenados[:k]
    k_vecinos_similitudes = similitudes[k_vecinos_indices]
    
    return k_vecinos_indices, k_vecinos_similitudes


def clasificar_usuario(candidato, matriz_usuarios, k=10):
    """
    Clasifica un usuario en una categoría según su vecindario.
    
    METODOLOGÍA:
    Se analizan dos dimensiones del vecindario:
    1. Rating promedio (preferencia: alta/media/baja)
    2. Canciones evaluadas (actividad: alta/baja)
    
    CATEGORÍAS (6 tipos):
    
    ┌─────────────────────┬──────────────┬─────────────────┐
    │ Categoría          │ Rating Prom. │ Actividad       │
    ├─────────────────────┼──────────────┼─────────────────┤
    │ Entusiastas        │ ≥4.0         │ >100 canciones  │
    │ Selectivos Positiv │ ≥4.0         │ ≤100 canciones  │
    │ Moderados Activos  │ 3.0-4.0      │ >100 canciones  │
    │ Moderados Casuales │ 3.0-4.0      │ ≤100 canciones  │
    │ Críticos           │ <3.0         │ >100 canciones  │
    │ Exploradores       │ <3.0         │ ≤100 canciones  │
    └─────────────────────┴──────────────┴─────────────────┘
    
    Args:
        candidato (np.array): Vector de evaluaciones
        matriz_usuarios (np.array): Matriz de usuarios
        k (int): Número de vecinos a considerar
    
    Returns:
        dict: {
            'categoria': str,
            'indices_vecinos': list,
            'similitudes': list,
            'promedio_rating_vecindario': float,
            'desviacion_rating_vecindario': float,
            'canciones_evaluadas_vecindario': float,
            'similitud_promedio': float
        }
    """
    # Encontrar K vecinos
    indices_vecinos, similitudes = encontrar_k_vecinos(candidato, matriz_usuarios, k)
    
    # Extraer evaluaciones de vecinos
    vecinos = matriz_usuarios[indices_vecinos]
    
    # Calcular estadísticas (solo evaluaciones válidas > 0)
    evaluaciones_vecinos = vecinos[vecinos > 0]
    
    if len(evaluaciones_vecinos) > 0:
        promedio_rating = np.mean(evaluaciones_vecinos)
        desviacion_rating = np.std(evaluaciones_vecinos)
    else:
        promedio_rating = 0
        desviacion_rating = 0
    
    # Promedio de canciones evaluadas por vecinos
    canciones_evaluadas_vecinos = np.mean(np.sum(vecinos > 0, axis=1))
    
    # Determinar categoría
    if promedio_rating >= 4.0:
        if canciones_evaluadas_vecinos > 100:
            categoria = "Entusiastas"
        else:
            categoria = "Selectivos Positivos"
    elif promedio_rating >= 3.0:
        if canciones_evaluadas_vecinos > 100:
            categoria = "Moderados Activos"
        else:
            categoria = "Moderados Casuales"
    else:
        if canciones_evaluadas_vecinos > 100:
            categoria = "Críticos"
        else:
            categoria = "Exploradores"
    
    return {
        'categoria': categoria,
        'indices_vecinos': indices_vecinos.tolist(),
        'similitudes': similitudes.tolist(),
        'promedio_rating_vecindario': float(promedio_rating),
        'desviacion_rating_vecindario': float(desviacion_rating),
        'canciones_evaluadas_vecindario': float(canciones_evaluadas_vecinos),
        'similitud_promedio': float(np.mean(similitudes))
    }


def recomendar_canciones(candidato, matriz_usuarios, nombres_canciones,
                        k_vecinos=10, n_recomendaciones=10):
    """
    Recomienda canciones usando filtrado colaborativo basado en usuario.
    
    ALGORITMO DE RECOMENDACIÓN:
    
    1. Identificar K vecinos más similares
    2. Encontrar canciones no evaluadas por el candidato
    3. Para cada canción:
       a. Obtener ratings de vecinos que la evaluaron
       b. Calcular score ponderado por similitud
       c. Formula: Σ(rating × similitud) / Σ(similitud)
    4. Ordenar por score y retornar top N
    
    VENTAJAS:
    ✓ Personalización basada en usuarios similares
    ✓ Ponderación inteligente (vecinos más similares pesan más)
    ✓ Normalización evita sesgos
    ✓ Predice rating esperado (1-5)
    
    EJEMPLO:
    Candidato: [5, 4, 0, 0, 3] (no evaluó canciones 3 y 4)
    
    Vecino 1 (sim=0.9): [5, 5, 4, 3, 4]
    Vecino 2 (sim=0.8): [4, 4, 5, 2, 3]
    
    Para Canción 3:
    Score = (4×0.9 + 5×0.8) / (0.9 + 0.8)
          = 9.6 / 1.7 = 4.04
    
    Args:
        candidato (np.array): Vector de evaluaciones
        matriz_usuarios (np.array): Matriz de usuarios
        nombres_canciones (list): Lista de nombres
        k_vecinos (int): Número de vecinos
        n_recomendaciones (int): Cantidad a recomendar
    
    Returns:
        list: Lista de diccionarios con recomendaciones:
        [{
            'cancion': str,
            'score_predicho': float,
            'vecinos_que_evaluaron': int,
            'rating_promedio_vecinos': float
        }, ...]
    
    Complejidad:
        O(k × m) donde k = vecinos, m = canciones
    """
    # Encontrar vecinos
    indices_vecinos, similitudes = encontrar_k_vecinos(candidato, matriz_usuarios, k_vecinos)
    vecinos = matriz_usuarios[indices_vecinos]
    
    # Canciones no evaluadas
    canciones_no_evaluadas = np.where(candidato == 0)[0]
    
    if len(canciones_no_evaluadas) == 0:
        return []
    
    # Calcular scores
    scores = np.zeros(len(canciones_no_evaluadas))
    
    for idx, cancion_idx in enumerate(canciones_no_evaluadas):
        ratings_vecinos = vecinos[:, cancion_idx]
        mascara_evaluados = ratings_vecinos > 0
        
        if np.any(mascara_evaluados):
            # Score ponderado
            ratings_ponderados = ratings_vecinos[mascara_evaluados] * similitudes[mascara_evaluados]
            suma_similitudes = np.sum(similitudes[mascara_evaluados])
            
            if suma_similitudes > 0:
                scores[idx] = np.sum(ratings_ponderados) / suma_similitudes
            else:
                scores[idx] = np.mean(ratings_vecinos[mascara_evaluados])
        else:
            scores[idx] = 0
    
    # Ordenar y seleccionar top N
    indices_ordenados = np.argsort(scores)[::-1]
    top_n = min(n_recomendaciones, len(indices_ordenados))
    
    # Construir lista de recomendaciones
    recomendaciones = []
    for i in range(top_n):
        idx_score = indices_ordenados[i]
        idx_cancion = canciones_no_evaluadas[idx_score]
        
        ratings_vecinos = vecinos[:, idx_cancion]
        vecinos_evaluaron = np.sum(ratings_vecinos > 0)
        
        if vecinos_evaluaron > 0:
            rating_prom = float(np.mean(ratings_vecinos[ratings_vecinos > 0]))
        else:
            rating_prom = 0.0
        
        recomendaciones.append({
            'cancion': nombres_canciones[idx_cancion],
            'score_predicho': float(scores[idx_score]),
            'vecinos_que_evaluaron': int(vecinos_evaluaron),
            'rating_promedio_vecinos': rating_prom
        })
    
    return recomendaciones