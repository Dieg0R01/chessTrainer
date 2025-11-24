import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import GamePage from './GamePage';
import ComparePage from './ComparePage';
import EnginesMatrixPage from './EnginesMatrixPage';
import CustomSelect from './CustomSelect';
import { 
  fetchEngines, 
  fetchEnginesInfo, 
  filterEnginesByType, 
  filterEnginesByOrigin,
  checkBackendHealth,
  reloadConfig
} from './api';

function SelectionPage() {
  const [selectedEngineA, setSelectedEngineA] = useState("");
  const [selectedEngineB, setSelectedEngineB] = useState("none"); // 'none' para jugar contra humano
  const [availableEngines, setAvailableEngines] = useState([]);
  const [filteredEngines, setFilteredEngines] = useState([]);
  const [enginesInfo, setEnginesInfo] = useState({});
  const [selectedEngineInfo, setSelectedEngineInfo] = useState(null);
  const [isLoadingEngines, setIsLoadingEngines] = useState(true);
  const [engineError, setEngineError] = useState(null);
  const [backendHealth, setBackendHealth] = useState(null);
  const [filterType, setFilterType] = useState("all");
  const [filterOrigin, setFilterOrigin] = useState("all");
  const navigate = useNavigate();

  // Verificar salud del backend al inicio
  useEffect(() => {
    checkBackendHealth()
      .then(health => {
        setBackendHealth(health);
        console.log('✅ Backend saludable:', health);
      })
      .catch(error => {
        console.warn('⚠️ No se pudo verificar salud del backend:', error);
        setBackendHealth(null);
      });
  }, []);

  // Cargar motores e información detallada
  useEffect(() => {
    console.log('🚀 Iniciando carga de motores...');
    setIsLoadingEngines(true);
    setEngineError(null);
    
    Promise.all([
      fetchEngines(),
      fetchEnginesInfo()
    ])
      .then(([engines, infoData]) => {
        console.log('✅ Motores cargados exitosamente:', engines);
        console.log('✅ Información de motores cargada:', infoData);
        
        setAvailableEngines(engines);
        
        // Crear mapa de información por nombre de motor
        const infoMap = {};
        if (infoData.engines) {
          infoData.engines.forEach(engineInfo => {
            infoMap[engineInfo.name] = engineInfo;
          });
        }
        setEnginesInfo(infoMap);
        
        setIsLoadingEngines(false);
        if (engines.length === 0) {
          setEngineError('No se encontraron motores disponibles en el backend');
        }
      })
      .catch(error => {
        console.error("❌ Error al obtener los motores:", error);
        
        setAvailableEngines([]);
        setFilteredEngines([]);
        setIsLoadingEngines(false);
        
        let errorMessage = 'Error desconocido al conectar con el backend';
        
        if (error.name === 'ConnectionError' || error.message.includes('No se pudo conectar')) {
          errorMessage = '⚠️ Backend no disponible. Asegúrate de iniciar el servidor en http://localhost:8000';
        } else if (error.message.includes('Error del servidor')) {
          errorMessage = `⚠️ Error del servidor: ${error.message}`;
        } else {
          errorMessage = `⚠️ Error: ${error.message}`;
        }
        
        setEngineError(errorMessage);
      });
  }, []);

  // Aplicar filtros cuando cambian los filtros o los motores disponibles
  useEffect(() => {
    if (availableEngines.length === 0) {
      setFilteredEngines([]);
      return;
    }

    let filtered = [...availableEngines];

    // Aplicar filtro por tipo
    if (filterType !== "all") {
      filterEnginesByType(filterType)
        .then(result => {
          const typeFiltered = result.engines || [];
          filtered = filtered.filter(engine => typeFiltered.includes(engine));
          applyOriginFilter(filtered);
        })
        .catch(error => {
          console.error('Error filtrando por tipo:', error);
          applyOriginFilter(filtered);
        });
    } else {
      applyOriginFilter(filtered);
    }
  }, [filterType, filterOrigin, availableEngines]);

  const applyOriginFilter = (engines) => {
    if (filterOrigin === "all") {
      setFilteredEngines(engines);
      return;
    }

    filterEnginesByOrigin(filterOrigin)
      .then(result => {
        const originFiltered = result.engines || [];
        const finalFiltered = engines.filter(engine => originFiltered.includes(engine));
        setFilteredEngines(finalFiltered);
      })
      .catch(error => {
        console.error('Error filtrando por origen:', error);
        setFilteredEngines(engines);
      });
  };

  // Actualizar información del motor seleccionado
  useEffect(() => {
    const engineToShow = selectedEngineA || (selectedEngineB !== "none" && selectedEngineB !== "human" ? selectedEngineB : null);
    if (engineToShow && enginesInfo[engineToShow]) {
      setSelectedEngineInfo(enginesInfo[engineToShow]);
    } else {
      setSelectedEngineInfo(null);
    }
  }, [selectedEngineA, selectedEngineB, enginesInfo]);

  const handleReloadConfig = async () => {
    try {
      const result = await reloadConfig();
      alert(`✅ Configuración recargada. ${result.engines_loaded} motores cargados.`);
      // Recargar la página para actualizar los motores
      window.location.reload();
    } catch (error) {
      alert(`❌ Error al recargar configuración: ${error.message}`);
    }
  };

  const handleStartGame = () => {
    navigate('/game', { state: { selectedEngineA, selectedEngineB } });
  };

  return (
    <div className="retro-container">
      {/* Terminal header */}
      <div className="terminal-header">
        <div className="chess-logo-container">
          <img 
            src="/chess_image.svg" 
            alt="Chess Logo" 
            className="chess-logo"
            style={{ 
              width: '321px', 
              height: 'auto', 
              maxWidth: '321px', 
              margin: '0 auto',
              display: 'block'
            }}
          />
        </div>
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
        <h1 className="main-title glow">CHESS TRAINER TERMINAL v2.0</h1>
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
      </div>

      {/* Main content area */}
      <div className="content-wrapper">
        {/* System info panel */}
        <div className="system-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="status-line">
                <span className="blink">&gt;</span> SYSTEM STATUS: {backendHealth ? 'ONLINE' : 'CHECKING...'}
              </div>
              {backendHealth && (
                <>
                  <div className="status-line">
                    <span className="blink">&gt;</span> VERSION: {backendHealth.version}
                  </div>
                  <div className="status-line">
                    <span className="blink">&gt;</span> ENGINES: {backendHealth.engines}
                  </div>
                </>
              )}
              <div className="status-line">
                <span className="blink">&gt;</span> MODE: ENGINE SELECTION
              </div>
            </div>
          </div>
        </div>

        {/* Selection form container */}
        <div className="board-container">
          <div className="board-frame">
            <div className="board-inner">
              <div className="selection-form">
                {/* Filtros */}
                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label glow">FILTRO TIPO</label>
                    <CustomSelect
                      value={filterType}
                      onChange={(value) => setFilterType(value)}
                      options={[
                        { value: 'all', label: 'TODOS' },
                        { value: 'traditional', label: 'TRADICIONAL' },
                        { value: 'neuronal', label: 'NEURONAL' },
                        { value: 'generative', label: 'GENERATIVO' }
                      ]}
                    />
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label glow">FILTRO ORIGEN</label>
                    <CustomSelect
                      value={filterOrigin}
                      onChange={(value) => setFilterOrigin(value)}
                      options={[
                        { value: 'all', label: 'TODOS' },
                        { value: 'internal', label: 'INTERNO' },
                        { value: 'external', label: 'EXTERNO' }
                      ]}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label glow" htmlFor="engineA">
                    MOTOR BLANCO (TÚ O MOTOR A)
                  </label>
                  <CustomSelect
                    value={selectedEngineA}
                    onChange={(value) => setSelectedEngineA(value)}
                    placeholder="-- SELECCIONA UN MOTOR --"
                    options={[
                      { value: '', label: '-- SELECCIONA UN MOTOR --' },
                      ...(filteredEngines.length > 0 ? filteredEngines : availableEngines).map(engine => ({
                        value: engine,
                        label: engine
                      })),
                      { value: 'human', label: 'HUMANO' }
                    ]}
                  />
                </div>
                
                <div className="form-group">
                  <label className="form-label glow" htmlFor="engineB">
                    MOTOR NEGRO (MOTOR B O NINGUNO)
                  </label>
                  <CustomSelect
                    value={selectedEngineB}
                    onChange={(value) => setSelectedEngineB(value)}
                    options={[
                      { value: 'none', label: 'NINGUNO (JUGARÁS CONTRA EL MOTOR A)' },
                      { value: 'human', label: 'HUMANO' },
                      ...(filteredEngines.length > 0 ? filteredEngines : availableEngines).map(engine => ({
                        value: engine,
                        label: engine
                      }))
                    ]}
                  />
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '15px', flexWrap: 'wrap' }}>
                  <button 
                    className="retro-button glow" 
                    onClick={handleStartGame} 
                    disabled={!selectedEngineA && selectedEngineB !== "none"}
                    style={{ flex: 1, minWidth: '200px' }}
                  >
                    EMPEZAR PARTIDA
                  </button>
                  <button 
                    className="retro-button glow" 
                    onClick={() => navigate('/compare')}
                    style={{ flex: 1, minWidth: '150px' }}
                  >
                    COMPARAR
                  </button>
                  <button 
                    className="retro-button glow" 
                    onClick={() => navigate('/matrix')}
                    style={{ flex: 1, minWidth: '150px' }}
                  >
                    MATRIZ
                  </button>
                </div>
              </div>
            </div>
            <div className="board-label glow">ENGINE.SYS v3.0</div>
          </div>
        </div>

        {/* Control panel */}
        <div className="control-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="status-line">
                <span className="blink">&gt;</span> MOTOR A: {selectedEngineA || "NO SELECCIONADO"}
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> MOTOR B: {selectedEngineB === "none" ? "NINGUNO" : selectedEngineB || "NO SELECCIONADO"}
              </div>
              <div className="move-history">
                <div className="history-title glow">▼ ENGINE INFO:</div>
                <div className="history-content">
                  {isLoadingEngines ? (
                    <div className="history-item blink">_ CARGANDO MOTORES...</div>
                  ) : engineError ? (
                    <div className="history-item" style={{ color: '#ff4444' }}>
                      ⚠ {engineError}
                    </div>
                  ) : availableEngines.length === 0 ? (
                    <div className="history-item" style={{ color: '#ffaa00' }}>
                      ⚠ NO HAY MOTORES DISPONIBLES
                    </div>
                  ) : (
                    <>
                      {(filteredEngines.length > 0 ? filteredEngines : availableEngines).slice(0, 10).map((engine, index) => (
                        <div key={index} className="history-item">
                          {index + 1}. {engine}
                        </div>
                      ))}
                      {(filteredEngines.length > 0 ? filteredEngines : availableEngines).length > 10 && (
                        <div className="history-item" style={{ color: '#888' }}>
                          ... +{(filteredEngines.length > 0 ? filteredEngines : availableEngines).length - 10} más
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
              {selectedEngineInfo && (
                <div className="move-history" style={{ marginTop: '10px' }}>
                  <div className="history-title glow">▼ SELECCIONADO:</div>
                  <div className="history-content">
                    <div className="history-item">
                      <strong>{selectedEngineInfo.name}</strong>
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Tipo: {selectedEngineInfo.type}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Origen: {selectedEngineInfo.origin}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Validación: {selectedEngineInfo.validation_mode}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Estado: {selectedEngineInfo.initialized ? '✓ Inicializado' : '✗ No inicializado'}
                    </div>
                  </div>
                </div>
              )}
              <div style={{ marginTop: '10px' }}>
                <button 
                  className="retro-button glow" 
                  onClick={handleReloadConfig}
                  style={{ fontSize: '18px', width: '100%' }}
                  title="Recargar configuración de motores"
                >
                  RECARGAR CONFIG
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Terminal footer */}
      <div className="terminal-footer">
        <div className="footer-text glow">
          <span className="blink">█</span> READY FOR INPUT...
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SelectionPage />} />
        <Route path="/game" element={<GamePage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/matrix" element={<EnginesMatrixPage />} />
      </Routes>
    </Router>
  );
}

export default App;
