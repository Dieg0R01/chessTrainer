import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchEnginesMatrix } from './api';

function EnginesMatrixPage() {
  const navigate = useNavigate();
  const [matrix, setMatrix] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEnginesMatrix()
      .then(data => {
        setMatrix(data);
        setIsLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setIsLoading(false);
      });
  }, []);

  const getTypeColor = (type) => {
    switch(type) {
      case 'traditional': return '#4a90e2';
      case 'neuronal': return '#e24a4a';
      case 'generative': return '#4ae2a0';
      default: return '#888';
    }
  };

  const getOriginColor = (origin) => {
    return origin === 'internal' ? '#90e24a' : '#e2a04a';
  };

  return (
    <div className="retro-container">
      <div className="terminal-header">
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
        <h1 className="main-title glow">MATRIZ DE CLASIFICACIÓN</h1>
        <div className="terminal-title glow">
          ═══════════════════════════════════════
        </div>
      </div>

      <div className="content-wrapper">
        <div className="system-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="status-line">
                <span className="blink">&gt;</span> MODO: ANÁLISIS
              </div>
              {matrix && (
                <div className="status-line">
                  <span className="blink">&gt;</span> MOTORES: {matrix.count}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="board-container">
          <div className="board-frame">
            <div className="board-inner" style={{ padding: '20px', overflow: 'auto' }}>
              {isLoading ? (
                <div className="history-item blink">_ CARGANDO MATRIZ...</div>
              ) : error ? (
                <div className="history-item" style={{ color: '#ff4444' }}>
                  ⚠ ERROR: {error}
                </div>
              ) : matrix && matrix.matrix ? (
                <div>
                  <div style={{ marginBottom: '20px' }}>
                    <h3 className="glow" style={{ marginBottom: '10px' }}>LEGENDA:</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '12px' }}>
                      <div>
                        <strong>TIPOS:</strong>
                        <div style={{ marginTop: '5px' }}>
                          <span style={{ color: '#4a90e2' }}>■</span> Traditional
                          <br />
                          <span style={{ color: '#e24a4a' }}>■</span> Neuronal
                          <br />
                          <span style={{ color: '#4ae2a0' }}>■</span> Generative
                        </div>
                      </div>
                      <div>
                        <strong>ORIGEN:</strong>
                        <div style={{ marginTop: '5px' }}>
                          <span style={{ color: '#90e24a' }}>■</span> Internal
                          <br />
                          <span style={{ color: '#e2a04a' }}>■</span> External
                        </div>
                      </div>
                    </div>
                  </div>

                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid #0f0' }}>
                        <th style={{ padding: '8px', textAlign: 'left', color: '#0f0' }}>MOTOR</th>
                        <th style={{ padding: '8px', textAlign: 'left', color: '#0f0' }}>TIPO</th>
                        <th style={{ padding: '8px', textAlign: 'left', color: '#0f0' }}>ORIGEN</th>
                        <th style={{ padding: '8px', textAlign: 'left', color: '#0f0' }}>VALIDACIÓN</th>
                      </tr>
                    </thead>
                    <tbody>
                      {matrix.matrix.map((row, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #0a0' }}>
                          <td style={{ padding: '8px', color: '#0f0' }}>
                            <strong>{row.name}</strong>
                          </td>
                          <td style={{ padding: '8px', color: getTypeColor(row.type) }}>
                            {row.type}
                          </td>
                          <td style={{ padding: '8px', color: getOriginColor(row.origin) }}>
                            {row.origin}
                          </td>
                          <td style={{ padding: '8px', color: '#aaa' }}>
                            {row.validation_mode}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </div>
            <div className="board-label glow">MATRIX.SYS v1.0</div>
          </div>
        </div>

        <div className="control-panel">
          <div className="panel-border">
            <div className="panel-content">
              <button 
                className="retro-button glow" 
                onClick={() => navigate('/')}
                style={{ width: '100%' }}
              >
                VOLVER
              </button>

              {matrix && matrix.description && (
                <div className="move-history" style={{ marginTop: '15px' }}>
                  <div className="history-title glow">▼ DESCRIPCIÓN:</div>
                  <div className="history-content">
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      <strong>Tipos:</strong> {matrix.description.type?.join(', ')}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      <strong>Orígenes:</strong> {matrix.description.origin?.join(', ')}
                    </div>
                    <div className="history-item" style={{ fontSize: '11px' }}>
                      <strong>Validación:</strong> {matrix.description.validation_mode?.join(', ')}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="terminal-footer">
        <div className="footer-text glow">
          <span className="blink">█</span> MATRIZ CARGADA...
        </div>
      </div>
    </div>
  );
}

export default EnginesMatrixPage;

