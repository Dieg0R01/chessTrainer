import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import GamePage from './GamePage';

function SelectionPage() {
  const [selectedEngineA, setSelectedEngineA] = useState("");
  const [selectedEngineB, setSelectedEngineB] = useState("none"); // 'none' para jugar contra humano
  const [availableEngines, setAvailableEngines] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Obtener los motores disponibles del backend
    // Obtener la URL del backend dinámicamente basándose en la URL actual
    const backendUrl = window.location.origin.replace(':5173', ':8000');
    fetch(`${backendUrl}/engines`)
      .then(response => response.json())
      .then(data => {
        setAvailableEngines(data.engines);
      })
      .catch(error => {
        console.error("Error al obtener los motores:", error);
        // En caso de error, usar una lista vacía
        setAvailableEngines([]);
      });
  }, []);

  const handleStartGame = () => {
    navigate('/game', { state: { selectedEngineA, selectedEngineB } });
  };

  return (
    <div className="retro-container">
      {/* Terminal header */}
      <div className="terminal-header">
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
                  {availableEngines.length === 0 ? (
                    <div className="history-item blink">_ CARGANDO MOTORES...</div>
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
