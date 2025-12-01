import { useState, useEffect, useMemo } from 'react';
import { fetchEnginesInfo, checkBackendHealth, reloadConfig } from '../api';

export const useEngines = () => {
  const [allEnginesInfo, setAllEnginesInfo] = useState([]); // Array de objetos con info completa
  const [enginesMap, setEnginesMap] = useState({}); // Mapa nombre -> info
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backendHealth, setBackendHealth] = useState(null);
  
  // Estados de filtros
  const [filterType, setFilterType] = useState("all");
  const [filterOrigin, setFilterOrigin] = useState("all");

  // Cargar datos iniciales
  const loadEngines = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Verificar salud primero
      const health = await checkBackendHealth().catch(err => {
        console.warn('⚠️ Backend health check failed:', err);
        return null;
      });
      setBackendHealth(health);

      // Cargar info detallada de motores
      // fetchEnginesInfo retorna { engines: [...], count: ... }
      // donde cada engine tiene { name, type, origin, available, ... }
      const infoData = await fetchEnginesInfo();
      
      if (infoData && Array.isArray(infoData.engines)) {
        console.log('📦 Motores recibidos del backend:', infoData.engines.length);
        console.log('📦 Motores disponibles:', infoData.engines.filter(e => e.available !== false).length);
        setAllEnginesInfo(infoData.engines);
        
        // Crear mapa para acceso rápido
        const map = {};
        infoData.engines.forEach(eng => {
          map[eng.name] = eng;
        });
        setEnginesMap(map);
      } else {
        throw new Error("Formato de respuesta de motores inválido");
      }
    } catch (err) {
      console.error("❌ Error cargando motores:", err);
      let errorMessage = 'Error desconocido al conectar con el backend';
      
      if (err.name === 'ConnectionError' || err.message.includes('No se pudo conectar') || err.message.includes('fetch')) {
        errorMessage = '⚠️ Backend no disponible. Asegúrate de iniciar el servidor.';
      } else {
        errorMessage = `⚠️ Error: ${err.message}`;
      }
      setError(errorMessage);
      setAllEnginesInfo([]);
      setEnginesMap({});
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEngines();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Solo ejecutar una vez al montar

  // Filtrado local (memoizado)
  // Esto soluciona los problemas de consistencia de filtros del usuario
  const filteredEngines = useMemo(() => {
    const filtered = allEnginesInfo.filter(engine => {
      // Filtro de disponibilidad: Solo mostrar motores disponibles
      // Si available es false explícitamente, lo ocultamos.
      // Si available es null/undefined, lo tratamos como disponible (por defecto)
      if (engine.available === false) return false;

      // Filtro por tipo
      if (filterType !== "all") {
        // Normalizar strings para comparación segura (traditional vs TRADITIONAL)
        if (engine.type.toLowerCase() !== filterType.toLowerCase()) return false;
      }
      
      // Filtro por origen
      if (filterOrigin !== "all") {
        if (engine.origin.toLowerCase() !== filterOrigin.toLowerCase()) return false;
      }
      
      return true;
    }).map(eng => eng.name); // Devolver solo nombres para mantener compatibilidad
    
    console.log('🔍 Filtrado aplicado:', {
      total: allEnginesInfo.length,
      disponibles: allEnginesInfo.filter(e => e.available !== false).length,
      filtrados: filtered.length,
      filterType,
      filterOrigin
    });
    
    return filtered;
  }, [allEnginesInfo, filterType, filterOrigin]);

  const handleReload = async () => {
    try {
      setIsLoading(true);
      const result = await reloadConfig();
      await loadEngines();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    engines: allEnginesInfo.filter(e => e.available !== false).map(e => e.name), // Nombres de todos los motores disponibles
    allEnginesRaw: allEnginesInfo, // Acceso crudo a todo (incluso no disponibles) si se necesita
    filteredEngines, // Nombres filtrados y disponibles
    enginesInfo: enginesMap, // Mapa completo para detalles
    isLoading,
    error,
    backendHealth,
    filterType,
    setFilterType,
    filterOrigin,
    setFilterOrigin,
    reloadEngines: handleReload
  };
};
