/**
 * MUSIC RECOMMENDER - FRONTEND APPLICATION
 * Integrantes: [AGREGAR NOMBRES]
 * Fecha: Noviembre 2025
 */

// ============================================================================
// CONFIGURACIÓN
// ============================================================================

// URL del backend API
// Cambiar según el entorno:
// - Desarrollo local: 'http://localhost:5000'
// - Docker local: 'http://localhost:5000'
// - Producción: URL de tu servidor
const API_URL = 'https://music-recommender-api-ojm4.onrender.com';

// Estado global de la aplicación
const state = {
    songs: [],              // Lista de todas las canciones
    ratings: {},            // Calificaciones del usuario {nombreCancion: rating}
    recommendations: null,  // Recomendaciones recibidas
    classification: null,   // Clasificación del usuario
    currentFilter: 'all',   // Filtro actual
    searchQuery: ''         // Búsqueda actual
};

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 Music Recommender iniciado');
    
    // Inicializar aplicación
    init();
    
    // Event listeners
    setupEventListeners();
});

async function init() {
    // Cargar estadísticas del hero
    await loadStats();
    
    // Cargar lista de canciones
    await loadSongs();
    
    // Cargar ratings guardados (si existen)
    loadSavedRatings();
}

// ============================================================================
// CARGA DE DATOS
// ============================================================================

/**
 * Carga las estadísticas del sistema
 */
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        
        if (!response.ok) {
            throw new Error('Error al cargar estadísticas');
        }
        
        const data = await response.json();
        
        // Actualizar UI
        document.getElementById('total-songs').textContent = data.total_canciones.toLocaleString();
        document.getElementById('total-users').textContent = data.total_usuarios.toLocaleString();
        document.getElementById('avg-rating').textContent = data.rating_promedio_global.toFixed(1);
        
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
        showToast('Error al cargar estadísticas', 'error');
    }
}

/**
 * Carga la lista de canciones del backend
 */
async function loadSongs() {
    try {
        showLoading();
        
        const response = await fetch(`${API_URL}/canciones`);
        
        if (!response.ok) {
            throw new Error('Error al cargar canciones');
        }
        
        const data = await response.json();
        state.songs = data.canciones;
        
        // Renderizar canciones
        renderSongs();
        
    } catch (error) {
        console.error('Error cargando canciones:', error);
        showToast('Error al cargar canciones. Verifica que el backend esté activo.', 'error');
        
        // Mostrar mensaje de error en la UI
        const grid = document.getElementById('songs-grid');
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <span class="empty-icon">⚠️</span>
                <h3>Error al cargar canciones</h3>
                <p>Verifica que el backend esté activo en ${API_URL}</p>
                <button class="btn btn-primary" onclick="loadSongs()">Reintentar</button>
            </div>
        `;
    }
}

/**
 * Carga ratings guardados en localStorage
 */
function loadSavedRatings() {
    const saved = localStorage.getItem('musicRecommenderRatings');
    if (saved) {
        state.ratings = JSON.parse(saved);
        updateProgress();
        updateRecommendationsButton();
    }
}

/**
 * Guarda ratings en localStorage
 */
function saveRatings() {
    localStorage.setItem('musicRecommenderRatings', JSON.stringify(state.ratings));
}

// ============================================================================
// RENDERIZADO
// ============================================================================

/**
 * Renderiza las canciones en el grid
 */
function renderSongs() {
    const grid = document.getElementById('songs-grid');
    
    // Filtrar canciones según búsqueda y filtro
    let filteredSongs = state.songs;
    
    // Aplicar búsqueda
    if (state.searchQuery) {
        filteredSongs = filteredSongs.filter(song => 
            song.toLowerCase().includes(state.searchQuery.toLowerCase())
        );
    }
    
    // Aplicar filtro
    if (state.currentFilter === 'rated') {
        filteredSongs = filteredSongs.filter(song => state.ratings[song]);
    } else if (state.currentFilter === 'unrated') {
        filteredSongs = filteredSongs.filter(song => !state.ratings[song]);
    }
    
    // Renderizar
    if (filteredSongs.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <span class="empty-icon">🔍</span>
                <h3>No se encontraron canciones</h3>
                <p>Intenta con otra búsqueda o filtro</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filteredSongs.map(song => createSongCard(song)).join('');
}

/**
 * Crea el HTML de una tarjeta de canción
 */
function createSongCard(songName) {
    const rating = state.ratings[songName] || 0;
    const isRated = rating > 0;
    
    return `
        <div class="song-card" data-song="${songName}">
            <div class="song-header">
                <span class="song-icon">🎵</span>
                <div class="song-info">
                    <h3 class="song-name">${songName}</h3>
                    <p class="song-status">${isRated ? `Calificada: ${rating}⭐` : 'Sin calificar'}</p>
                </div>
            </div>
            <div class="song-rating">
                ${[1, 2, 3, 4, 5].map(star => `
                    <span 
                        class="star ${rating >= star ? 'active' : ''}" 
                        data-rating="${star}"
                        onclick="rateSong('${songName}', ${star})"
                    >⭐</span>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Muestra el estado de carga
 */
function showLoading() {
    const grid = document.getElementById('songs-grid');
    grid.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Cargando canciones...</p>
        </div>
    `;
}

// ============================================================================
// CALIFICACIÓN DE CANCIONES
// ============================================================================

/**
 * Califica una canción
 */
function rateSong(songName, rating) {
    // Si ya tiene este rating, removerlo (toggle)
    if (state.ratings[songName] === rating) {
        delete state.ratings[songName];
    } else {
        state.ratings[songName] = rating;
    }
    
    // Guardar y actualizar UI
    saveRatings();
    updateProgress();
    updateRecommendationsButton();
    
    // Re-renderizar solo si el filtro actual lo requiere
    if (state.currentFilter !== 'all') {
        renderSongs();
    } else {
        // Actualizar solo la tarjeta específica
        updateSongCard(songName);
    }
    
    // Feedback visual
    showToast(`${songName} calificada con ${rating}⭐`, 'success');
}

/**
 * Actualiza una tarjeta de canción específica
 */
function updateSongCard(songName) {
    const card = document.querySelector(`[data-song="${songName}"]`);
    if (card) {
        const rating = state.ratings[songName] || 0;
        
        // Actualizar status
        const status = card.querySelector('.song-status');
        status.textContent = rating > 0 ? `Calificada: ${rating}⭐` : 'Sin calificar';
        
        // Actualizar estrellas
        const stars = card.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
}

/**
 * Actualiza la barra de progreso
 */
function updateProgress() {
    const ratedCount = Object.keys(state.ratings).length;
    const totalSongs = state.songs.length;
    const percentage = totalSongs > 0 ? (ratedCount / totalSongs * 100) : 0;
    
    document.getElementById('rated-count').textContent = ratedCount;
    document.getElementById('progress-percentage').textContent = `${percentage.toFixed(1)}%`;
    document.getElementById('progress-fill').style.width = `${percentage}%`;
}

/**
 * Actualiza el botón de recomendaciones
 */
function updateRecommendationsButton() {
    const button = document.getElementById('get-recommendations-btn');
    const hint = document.getElementById('recommendations-hint');
    const ratedCount = Object.keys(state.ratings).length;
    
    if (ratedCount >= 10) {
        button.disabled = false;
        hint.textContent = `¡Listo! Tienes ${ratedCount} canciones calificadas`;
        hint.style.color = 'var(--success)';
    } else {
        button.disabled = true;
        hint.textContent = `Califica al menos ${10 - ratedCount} canciones más`;
        hint.style.color = 'var(--text-muted)';
    }
}

// ============================================================================
// RECOMENDACIONES
// ============================================================================

/**
 * Obtiene recomendaciones del backend
 */
async function getRecommendations() {
    try {
        const ratedCount = Object.keys(state.ratings).length;
        
        if (ratedCount < 10) {
            showToast('Debes calificar al menos 10 canciones', 'warning');
            return;
        }
        
        // Mostrar loading
        showToast('Generando recomendaciones...', 'success');
        
        // Crear array de evaluaciones (0 para no calificadas)
        const evaluaciones = state.songs.map(song => state.ratings[song] || 0);
        
        // Hacer petición al backend
        const response = await fetch(`${API_URL}/recomendar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                evaluaciones: evaluaciones,
                n_recomendaciones: 20,
                k_vecinos: 10
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener recomendaciones');
        }
        
        const data = await response.json();
        
        // Guardar en estado
        state.recommendations = data.recomendaciones;
        state.classification = data.clasificacion;
        
        // Mostrar resultados
        displayRecommendations();
        
        // Scroll a la sección de recomendaciones
        scrollToSection('recommendations');
        
        showToast('¡Recomendaciones generadas con éxito!', 'success');
        
    } catch (error) {
        console.error('Error obteniendo recomendaciones:', error);
        showToast(error.message || 'Error al obtener recomendaciones', 'error');
    }
}

/**
 * Muestra las recomendaciones en la UI
 */
function displayRecommendations() {
    // Ocultar empty state
    document.getElementById('empty-state').style.display = 'none';
    
    // Mostrar resultados
    const container = document.getElementById('results-container');
    container.classList.remove('results-hidden');
    
    // Actualizar clasificación
    displayClassification();
    
    // Mostrar recomendaciones
    displayRecommendationsList();
}

/**
 * Muestra la clasificación del usuario
 */
function displayClassification() {
    const classification = state.classification;
    
    // Iconos por categoría
    const categoryIcons = {
        'Entusiastas': '🎉',
        'Selectivos Positivos': '⭐',
        'Moderados Activos': '🎵',
        'Moderados Casuales': '🎧',
        'Críticos': '🎯',
        'Exploradores': '🔍'
    };
    
    // Actualizar UI
    document.getElementById('category-icon').textContent = 
        categoryIcons[classification.categoria] || '🎭';
    document.getElementById('user-category').textContent = classification.categoria;
    document.getElementById('similarity-score').textContent = 
        classification.similitud_promedio.toFixed(3);
    document.getElementById('neighborhood-rating').textContent = 
        classification.promedio_rating_vecindario.toFixed(2);
    document.getElementById('songs-evaluated').textContent = 
        Math.round(classification.canciones_evaluadas_vecindario);
}

/**
 * Muestra la lista de recomendaciones
 */
function displayRecommendationsList() {
    const list = document.getElementById('recommendations-list');
    
    if (!state.recommendations || state.recommendations.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">🎵</span>
                <h3>No hay recomendaciones disponibles</h3>
                <p>No pudimos encontrar canciones para recomendar</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = state.recommendations.map((rec, index) => `
        <div class="recommendation-card">
            <div class="recommendation-rank">#${index + 1}</div>
            <span class="recommendation-icon">🎵</span>
            <div class="recommendation-info">
                <h3 class="recommendation-name">${rec.cancion}</h3>
                <div class="recommendation-meta">
                    <div class="meta-item">
                        <span class="meta-icon">⭐</span>
                        <span>Rating: ${rec.rating_promedio_vecinos.toFixed(2)}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-icon">👥</span>
                        <span>${rec.vecinos_que_evaluaron} vecinos</span>
                    </div>
                </div>
            </div>
            <div class="recommendation-score">
                <span class="score-value">${rec.score_predicho.toFixed(2)}</span>
                <span class="score-label">Score</span>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Botón de recomendaciones
    document.getElementById('get-recommendations-btn').addEventListener('click', getRecommendations);
    
    // Búsqueda
    document.getElementById('search-input').addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        renderSongs();
    });
    
    // Filtros
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Actualizar botones activos
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Aplicar filtro
            state.currentFilter = e.target.dataset.filter;
            renderSongs();
        });
    });
    
    // Navegación
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = e.target.getAttribute('href').substring(1);
            scrollToSection(target);
            
            // Actualizar active
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            e.target.classList.add('active');
        });
    });
}

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * Scroll suave a una sección
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Reinicia todas las calificaciones
 */
function resetRatings() {
    if (!confirm('¿Estás seguro de que quieres borrar todas tus calificaciones?')) {
        return;
    }
    
    state.ratings = {};
    state.recommendations = null;
    state.classification = null;
    
    saveRatings();
    updateProgress();
    updateRecommendationsButton();
    renderSongs();
    
    // Ocultar recomendaciones
    document.getElementById('results-container').classList.add('results-hidden');
    document.getElementById('empty-state').style.display = 'block';
    
    // Scroll al inicio
    scrollToSection('rate');
    
    showToast('Calificaciones reiniciadas', 'success');
}

// ============================================================================
// LOGS DE DEBUG
// ============================================================================

// Log del estado en consola (útil para debug)
window.addEventListener('load', () => {
    console.log('🎵 Estado inicial:', state);
    console.log('🔗 API URL:', API_URL);
});

// Exponer funciones al scope global (necesario para onclick en HTML)
window.rateSong = rateSong;
window.getRecommendations = getRecommendations;
window.scrollToSection = scrollToSection;
window.resetRatings = resetRatings;
window.loadSongs = loadSongs;