import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { compareEngines } from './api';

function ComparePage() {
  const navigate = useNavigate();
  const gameRef = useState(() => new Chess())[0];
  const [position, setPosition] = useState(gameRef.fen());
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [error, setError] = useState(null);
  const [depth, setDepth] = useState(10);

  const handleCompare = async () => {
    setIsComparing(true);
    setError(null);
    setComparisonResults(null);

    try {
      const results = await compareEngines(position, depth);
      setComparisonResults(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsComparing(false);
    }
  };

  const onSquareClick = (square) => {
    // Permitir seleccionar casillas para análisis (no implementado completamente)
    console.log('Casilla clickeada:', square);
  };

  const resetPosition = () => {
    gameRef.reset();
    setPosition(gameRef.fen());
    setComparisonResults(null);
    setError(null);
  };

  return (
    <div className="retro-container">
      <div className="terminal-header">
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
        <h1 className="main-title glow">COMPARACIÓN DE MOTORES</h1>
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
      </div>

      <div className="content-wrapper">
        <div className="system-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="status-line">
                <span className="blink">&gt;</span> MODO: COMPARACIÓN
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> POSICIÓN: {position.substring(0, 20)}...
              </div>
            </div>
          </div>
        </div>

        <div className="board-container">
          <div className="board-frame">
            <div className="board-inner">
              <Chessboard
                position={position}
                onSquareClick={onSquareClick}
                customBoardStyle={{
                  borderRadius: '0px',
                  boxShadow: 'none',
                  width: '100%',
                  height: '100%'
                }}
                customLightSquareStyle={{
                  backgroundColor: '#24a32a'
                }}
                customDarkSquareStyle={{
                  backgroundColor: '#147e1f'
                }}
                boardWidth={600}
              />
            </div>
            <div className="board-label glow">COMPARE.SYS v1.0</div>
          </div>
        </div>

        <div className="control-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="form-group">
                <label className="form-label glow">PROFUNDIDAD</label>
                <div className="retro-select-wrapper">
                  <input
                    type="number"
                    className="retro-select"
                    value={depth}
                    onChange={(e) => setDepth(parseInt(e.target.value) || 10)}
                    min="1"
                    max="30"
                    style={{ width: '100%' }}
                  />
                </div>
              </div>
              
              <button 
                className="retro-button glow" 
                onClick={handleCompare}
                disabled={isComparing}
                style={{ width: '100%', marginBottom: '10px' }}
              >
                {isComparing ? 'COMPARANDO...' : 'COMPARAR MOTORES'}
              </button>

              <button 
                className="retro-button glow" 
                onClick={resetPosition}
                style={{ width: '100%', marginBottom: '10px' }}
              >
                RESET POSICIÓN
              </button>

              <button 
                className="retro-button glow" 
                onClick={() => navigate('/')}
                style={{ width: '100%' }}
              >
                VOLVER
              </button>

              {error && (
                <div className="move-history" style={{ marginTop: '15px' }}>
                  <div className="history-title glow">▼ ERROR:</div>
                  <div className="history-content">
                    <div className="history-item" style={{ color: '#ff4444' }}>
                      ⚠ {error}
                    </div>
                  </div>
                </div>
              )}

              {comparisonResults && (
                <div className="move-history" style={{ marginTop: '15px' }}>
                  <div className="history-title glow">
                    ▼ RESULTADOS ({comparisonResults.engines_compared} motores):
                  </div>
                  <div className="history-content" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {comparisonResults.results && comparisonResults.results.map((result, index) => (
                      <div key={index} className="history-item">
                        <strong>{result.engine}:</strong> {result.bestmove || 'N/A'}
                        {result.explanation && (
                          <div style={{ fontSize: '10px', color: '#aaa', marginTop: '2px' }}>
                            {result.explanation.substring(0, 50)}...
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="terminal-footer">
        <div className="footer-text glow">
          <span className="blink">█</span> READY FOR COMPARISON...
        </div>
      </div>
    </div>
  );
}

export default ComparePage;

