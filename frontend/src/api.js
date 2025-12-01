/**
 * API Client para Chess Trainer
 * Centraliza la comunicación con el backend FastAPI
 */

/**
 * Obtiene la URL base del backend
 * En desarrollo (puerto 5173): usa localhost:8000
 * En producción: usa la misma URL pero puerto 8000
 */
export const getBackendUrl = () => {
  // Detectar entorno y construir URL del backend
  const isDevelopment = import.meta.env.DEV;
  const currentOrigin = window.location.origin;
  
  // En desarrollo: siempre usar localhost:8000
  if (isDevelopment) {
    // Verificar si estamos en Vite dev server (puerto 5173)
    if (currentOrigin.includes(':5173')) {
      return 'http://localhost:8000';
    }
    // Fallback para desarrollo local
    return 'http://localhost:8000';
  }
  
  // En producción: usar el mismo hostname pero puerto 8000
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const url = `${protocol}//${hostname}:8000`;
  
  // Validar que la URL sea válida
  if (!url || !url.startsWith('http://') && !url.startsWith('https://')) {
    console.warn('⚠️ URL del backend inválida, usando fallback localhost:8000');
    return 'http://localhost:8000';
  }
  
  return url;
};

/**
 * Obtiene la lista de motores disponibles del backend
 * @returns {Promise<string[]>} Array de nombres de motores
 */
export const fetchEngines = async () => {
  const backendUrl = getBackendUrl();
  const url = `${backendUrl}/engines`;
  
  try {
    console.log('🔍 Obteniendo motores desde:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Error desconocido');
      console.error('❌ Error HTTP:', response.status, errorText);
      throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    
    // Validar formato de respuesta
    if (!data || typeof data !== 'object') {
      throw new Error('Respuesta inválida del servidor: formato incorrecto');
    }
    
    if (!data.engines) {
      console.warn('⚠️ Respuesta sin campo "engines":', data);
      // Si no hay engines pero hay count, retornar array vacío
      if (data.count !== undefined) {
        return [];
      }
      throw new Error('Respuesta inválida: falta campo "engines"');
    }
    
    if (!Array.isArray(data.engines)) {
      throw new Error(`Formato inválido: "engines" debe ser un array, recibido: ${typeof data.engines}`);
    }
    
    console.log(`✅ ${data.engines.length} motores cargados:`, data.engines);
    return data.engines;
    
  } catch (error) {
    // Manejo específico de errores de red
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      const connectionError = new Error(
        `No se pudo conectar con el backend en ${backendUrl}. ` +
        `Verifica que el servidor esté corriendo. ` +
        `Ejecuta: python main.py o bash start_backend.sh`
      );
      connectionError.name = 'ConnectionError';
      console.error('❌ Error de conexión:', connectionError.message);
      throw connectionError;
    }
    
    console.error('❌ Error al obtener motores:', error);
    throw error;
  }
};

/**
 * Obtiene el mejor movimiento de un motor para una posición FEN
 * @param {string} engineName - Nombre del motor a usar
 * @param {string} fen - Posición del tablero en formato FEN
 * @param {number} depth - Profundidad de análisis (opcional)
 * @param {object} options - Opciones adicionales para motores generativos
 * @returns {Promise<{engine: string, bestmove: string, explanation?: string}>}
 */
export const fetchBestMove = async (engineName, fen, depth = 10, options = {}) => {
  try {
    const backendUrl = getBackendUrl();
    
    // Validar que backendUrl sea válido
    if (!backendUrl || (!backendUrl.startsWith('http://') && !backendUrl.startsWith('https://'))) {
      throw new Error(`URL del backend inválida: ${backendUrl}`);
    }
    
    const url = `${backendUrl}/move`;
    console.log('🔍 Llamando a:', url);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        engine: engineName,
        fen: fen,
        depth: depth,
        ...options, // move_history, strategy, explanation para motores generativos
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Error HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.detail || 'Error desconocido del servidor');
    }
    
    const data = await response.json();
    
    // El backend devuelve { engine: string, bestmove: string, explanation?: string }
    if (!data.bestmove) {
      throw new Error('El backend no devolvió un movimiento válido');
    }
    
    return data;
  } catch (error) {
    console.error(`Error al obtener movimiento del motor ${engineName}:`, error);
    throw error;
  }
};

/**
 * Verifica la salud del backend
 * @returns {Promise<{status: string, engines: number, version: string}>}
 */
export const checkBackendHealth = async () => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al verificar salud del backend:', error);
    throw error;
  }
};

/**
 * Obtiene información detallada de todos los motores
 * @returns {Promise<{engines: Array<{name: string, type: string, origin: string, validation_mode: string, initialized: boolean}>, count: number}>}
 */
export const fetchEnginesInfo = async () => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/engines/info`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Error desconocido');
      throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error al obtener información de motores:', error);
    throw error;
  }
};

/**
 * Obtiene la matriz de clasificación de motores
 * @returns {Promise<{matrix: Array, count: number, description: {type: string[], origin: string[], validation_mode: string[]}}>}
 */
export const fetchEnginesMatrix = async () => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/engines/matrix`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Error desconocido');
      throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error al obtener matriz de clasificación:', error);
    throw error;
  }
};

/**
 * Filtra motores por tipo
 * @param {string} motorType - Tipo de motor: 'traditional', 'neuronal', o 'generative'
 * @returns {Promise<{type: string, engines: string[], count: number}>}
 */
export const filterEnginesByType = async (motorType) => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/engines/filter/type/${motorType}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Error HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.detail || 'Error desconocido del servidor');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error al filtrar motores por tipo ${motorType}:`, error);
    throw error;
  }
};

/**
 * Filtra motores por origen
 * @param {string} motorOrigin - Origen del motor: 'internal' o 'external'
 * @returns {Promise<{origin: string, engines: string[], count: number}>}
 */
export const filterEnginesByOrigin = async (motorOrigin) => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/engines/filter/origin/${motorOrigin}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Error HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.detail || 'Error desconocido del servidor');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error al filtrar motores por origen ${motorOrigin}:`, error);
    throw error;
  }
};

/**
 * Obtiene la lista de estrategias disponibles para motores generativos
 * @returns {Promise<{strategies: Object, count: number, default: string}>}
 */
export const fetchStrategies = async () => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/strategies`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Error desconocido');
      throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error al obtener estrategias:', error);
    throw error;
  }
};

/**
 * Compara las sugerencias de todos los motores disponibles para una posición
 * @param {string} fen - Posición del tablero en formato FEN
 * @param {number} depth - Profundidad de análisis (opcional)
 * @returns {Promise<{fen: string, results: Array, engines_compared: number}>}
 */
export const compareEngines = async (fen, depth = null) => {
  try {
    const backendUrl = getBackendUrl();
    const requestBody = { fen };
    if (depth !== null) {
      requestBody.depth = depth;
    }
    
    const response = await fetch(`${backendUrl}/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Error HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.detail || 'Error desconocido del servidor');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error al comparar motores:', error);
    throw error;
  }
};

/**
 * Recarga la configuración de motores desde el archivo YAML
 * @returns {Promise<{status: string, message: string, engines_loaded: number}>}
 */
export const reloadConfig = async () => {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/reload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Error HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.detail || 'Error desconocido del servidor');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error al recargar configuración:', error);
    throw error;
  }
};

