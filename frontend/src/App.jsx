import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import GamePage from './GamePage';
import ComparePage from './ComparePage';
import EnginesMatrixPage from './EnginesMatrixPage';
import CustomSelect from './CustomSelect';
import { useEngines } from './hooks/useEngines';

function SelectionPage({ enginesContext }) {
  // Selección de jugadores: Motor A y Motor B por defecto son HUMANO
  const [selectedEngineA, setSelectedEngineA] = useState("human");
  const [selectedEngineB, setSelectedEngineB] = useState("human");
  const [use3DBoard, setUse3DBoard] = useState(false);
  
  const navigate = useNavigate();

  // Usar el contexto de motores pasado desde App, o crear uno local si no existe
  const enginesHook = enginesContext || useEngines();
  const {
    engines: availableEngines,
    filteredEngines,
    enginesInfo,
    isLoading: isLoadingEngines,
    error: engineError,
    backendHealth,
    filterType,
    setFilterType,
    filterOrigin,
    setFilterOrigin
  } = enginesHook;



  const handleStartGame = () => {
    navigate('/game', { state: { selectedEngineA, selectedEngineB, use3DBoard } });
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
              width: '200px', 
              height: 'auto', 
              maxWidth: '200px', 
              margin: '0 auto',
              display: 'block'
            }}
          />
        </div>
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
        <h1 className="main-title glow">CHESS TRAINER TERMINAL</h1>
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
                <div className="status-line">
                  <span className="blink">&gt;</span> ENGINES: {availableEngines.length}
                </div>
              )}
              <div className="status-line">
                <span className="blink">&gt;</span> MODE: ENGINE SELECTION
              </div>
            </div>
          </div>
        </div>

        {/* Selection form container */}
        <div className="board-container">
          <div className="board-frame selection-mode">
            <div className="board-inner selection-mode">
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
                    MOTOR BLANCO (MOTOR A)
                  </label>
                  <CustomSelect
                    value={selectedEngineA}
                    onChange={(value) => setSelectedEngineA(value)}
                    placeholder="-- SELECCIONA UN MOTOR --"
                    options={[
                      { value: 'human', label: 'HUMANO' },
                      ...(filteredEngines.length > 0 ? filteredEngines : availableEngines).map(engine => ({
                        value: engine,
                        label: engine
                      }))
                    ]}
                  />
                </div>
                
                <div className="form-group">
                  <label className="form-label glow" htmlFor="engineB">
                    MOTOR NEGRO (MOTOR B)
                  </label>
                  <CustomSelect
                    value={selectedEngineB}
                    onChange={(value) => setSelectedEngineB(value)}
                    options={[
                      { value: 'human', label: 'HUMANO' },
                      ...(filteredEngines.length > 0 ? filteredEngines : availableEngines).map(engine => ({
                        value: engine,
                        label: engine
                      }))
                    ]}
                  />
                </div>

                {/* Switch para tablero 3D */}
                <div style={{ 
                  marginTop: '15px', 
                  marginBottom: '10px', 
                  border: '2px solid var(--retro-green)', 
                  padding: '12px 15px', 
                  borderRadius: '0px',
                  background: 'rgba(36, 163, 42, 0.05)'
                }}>
                  <label style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '12px', 
                    cursor: 'pointer',
                    fontFamily: 'VT323, monospace',
                    fontSize: '22px',
                    letterSpacing: '1.5px',
                    color: 'var(--retro-green)'
                  }}>
                    <input
                      type="checkbox"
                      checked={use3DBoard}
                      onChange={(e) => setUse3DBoard(e.target.checked)}
                      style={{
                        width: '28px',
                        height: '28px',
                        cursor: 'pointer',
                        accentColor: 'var(--retro-green)',
                        filter: 'brightness(1.2)'
                      }}
                    />
                    <span className="glow">TABLERO 3D</span>
                  </label>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '15px', flexWrap: 'wrap' }}>
                  <button 
                    className="retro-button glow" 
                    onClick={handleStartGame} 
                    disabled={!selectedEngineA || (selectedEngineA === 'human' && selectedEngineB === 'human')}
                    style={{ flex: 1, minWidth: '200px' }}
                    title={(!selectedEngineA || (selectedEngineA === 'human' && selectedEngineB === 'human')) ? "Selecciona al menos un motor para jugar" : ""}
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
            <div className="board-label glow">ENGINE.SYS</div>
          </div>
        </div>

        {/* Control panel */}
        <div className="control-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="status-line">
                <span className="blink">&gt;</span> MOTOR A: {selectedEngineA === 'human' ? "HUMANO" : (selectedEngineA || "NO SELECCIONADO")}
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> MOTOR B: {selectedEngineB === 'human' ? "HUMANO" : (selectedEngineB || "NO SELECCIONADO")}
              </div>
              
              {/* Información del Motor A */}
              {selectedEngineA && selectedEngineA !== 'human' && enginesInfo[selectedEngineA] && (
                <div className="move-history" style={{ marginTop: '10px' }}>
                  <div className="history-title glow">▼ MOTOR A:</div>
                  <div className="history-content">
                    <div className="history-item">
                      <strong>{enginesInfo[selectedEngineA].name}</strong>
                    </div>
                    {enginesInfo[selectedEngineA].description && (
                      <div className="history-item" style={{ fontSize: '11px', color: '#aaa', marginTop: '5px', lineHeight: '1.4' }}>
                        {enginesInfo[selectedEngineA].description}
                      </div>
                    )}
                    <div className="history-item" style={{ fontSize: '11px', marginTop: '8px' }}>
                      Tipo: {enginesInfo[selectedEngineA].type}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Origen: {enginesInfo[selectedEngineA].origin}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Validación: {enginesInfo[selectedEngineA].validation_mode}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Estado: {enginesInfo[selectedEngineA].initialized ? '✓ Inicializado' : '✗ No inicializado'}
                    </div>
                    {enginesInfo[selectedEngineA].available !== undefined && (
                      <div className="history-item" style={{ fontSize: '11px' }}>
                        Disponible: {enginesInfo[selectedEngineA].available ? '✓ Sí' : '✗ No'}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Información del Motor B */}
              {selectedEngineB && selectedEngineB !== 'human' && enginesInfo[selectedEngineB] && (
                <div className="move-history" style={{ marginTop: '10px' }}>
                  <div className="history-title glow">▼ MOTOR B:</div>
                  <div className="history-content">
                    <div className="history-item">
                      <strong>{enginesInfo[selectedEngineB].name}</strong>
                    </div>
                    {enginesInfo[selectedEngineB].description && (
                      <div className="history-item" style={{ fontSize: '11px', color: '#aaa', marginTop: '5px', lineHeight: '1.4' }}>
                        {enginesInfo[selectedEngineB].description}
                      </div>
                    )}
                    <div className="history-item" style={{ fontSize: '11px', marginTop: '8px' }}>
                      Tipo: {enginesInfo[selectedEngineB].type}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Origen: {enginesInfo[selectedEngineB].origin}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Validación: {enginesInfo[selectedEngineB].validation_mode}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      Estado: {enginesInfo[selectedEngineB].initialized ? '✓ Inicializado' : '✗ No inicializado'}
                    </div>
                    {enginesInfo[selectedEngineB].available !== undefined && (
                      <div className="history-item" style={{ fontSize: '11px' }}>
                        Disponible: {enginesInfo[selectedEngineB].available ? '✓ Sí' : '✗ No'}
                      </div>
                    )}
                  </div>
                </div>
              )}
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
  // Crear el contexto de motores una sola vez a nivel de App
  // Esto evita que se recargue cada vez que se navega
  const enginesContext = useEngines();
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SelectionPage enginesContext={enginesContext} />} />
        <Route path="/game" element={<GamePage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/matrix" element={<EnginesMatrixPage />} />
      </Routes>
    </Router>
  );
}

export default App;

