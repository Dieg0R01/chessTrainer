import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import GamePage from './GamePage';
import { fetchEngines } from './api';

function SelectionPage() {
  const [selectedEngineA, setSelectedEngineA] = useState("");
  const [selectedEngineB, setSelectedEngineB] = useState("none"); // 'none' para jugar contra humano
  const [availableEngines, setAvailableEngines] = useState([]);
  const [isLoadingEngines, setIsLoadingEngines] = useState(true);
  const [engineError, setEngineError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Obtener los motores disponibles del backend
    console.log('🚀 Iniciando carga de motores...');
    setIsLoadingEngines(true);
    setEngineError(null);
    
    fetchEngines()
      .then(engines => {
        console.log('✅ Motores cargados exitosamente:', engines);
        setAvailableEngines(engines);
        setIsLoadingEngines(false);
        if (engines.length === 0) {
          setEngineError('No se encontraron motores disponibles en el backend');
        }
      })
      .catch(error => {
        console.error("❌ Error al obtener los motores:", error);
        
        setAvailableEngines([]);
        setIsLoadingEngines(false);
        
        // Mensaje de error más específico según el tipo
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
                <span className="blink">&gt;</span> SYSTEM STATUS: ONLINE
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> ENGINES: {availableEngines.length}
              </div>
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
                <div className="form-group">
                  <label className="form-label glow" htmlFor="engineA">
                    ▼ MOTOR BLANCO (TÚ O MOTOR A):
                  </label>
                  <select
                    className="retro-select"
                    id="engineA"
                    value={selectedEngineA}
                    onChange={(e) => setSelectedEngineA(e.target.value)}
                  >
                    <option value="">-- SELECCIONA UN MOTOR --</option>
                    {availableEngines.map((engine) => (
                      <option key={engine} value={engine}>
                        {engine}
                      </option>
                    ))}
                    <option value="human">HUMANO</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label className="form-label glow" htmlFor="engineB">
                    ▼ MOTOR NEGRO (MOTOR B O NINGUNO):
                  </label>
                  <select
                    className="retro-select"
                    id="engineB"
                    value={selectedEngineB}
                    onChange={(e) => setSelectedEngineB(e.target.value)}
                  >
                    <option value="none">NINGUNO (JUGARÁS CONTRA EL MOTOR A)</option>
                    <option value="human">HUMANO</option>
                    {availableEngines.map((engine) => (
                      <option key={engine} value={engine}>
                        {engine}
                      </option>
                    ))}
                  </select>
                </div>

                <button 
                  className="retro-button glow" 
                  onClick={handleStartGame} 
                  disabled={!selectedEngineA && selectedEngineB !== "none"}
                >
                  [ EMPEZAR PARTIDA ]
                </button>
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
                    availableEngines.map((engine, index) => (
                      <div key={index} className="history-item">
                        {index + 1}. {engine}
                      </div>
                    ))
                  )}
                </div>
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
      </Routes>
    </Router>
  );
}

export default App;
