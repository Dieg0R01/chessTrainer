import { useState, useRef, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { compareEngines } from './api';

/**
 * Página de Comparación de Motores
 * 
 * Permite comparar las sugerencias de todos los motores disponibles
 * para una posición específica del tablero de ajedrez.
 * 
 * Características:
 * - Edición interactiva del tablero (click y drag & drop)
 * - Comparación de todos los motores disponibles
 * - Visualización estructurada de resultados
 * - Filtrado de resultados en tiempo real
 * - Manejo robusto de errores
 */
function ComparePage() {
  const navigate = useNavigate();
  
  // ============================================
  // ESTADOS
  // ============================================
  
  // Referencia al objeto Chess (no causa re-renders)
  const gameRef = useRef(new Chess());
  
  // Estado del tablero
  const [position, setPosition] = useState(() => gameRef.current.fen());
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [possibleMoves, setPossibleMoves] = useState({});
  
  // Estado de comparación
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Configuración
  const [depth, setDepth] = useState(10);
  const [resultFilter, setResultFilter] = useState('');

  // ============================================
  // FUNCIONES AUXILIARES DEL TABLERO
  // ============================================

  /**
   * Actualiza la posición FEN del tablero
   * Limpia resultados si la posición cambia
   */
  const updatePosition = useCallback(() => {
    const newFen = gameRef.current.fen();
    setPosition(newFen);
    
    // Limpiar resultados si la posición cambia
    if (comparisonResults && comparisonResults.fen !== newFen) {
      setComparisonResults(null);
      setError(null);
    }
  }, [comparisonResults]);

  /**
   * Obtiene los movimientos posibles de una casilla
   */
  const getPossibleMoves = useCallback((square) => {
    const moves = gameRef.current.moves({
      square,
      verbose: true
    });
    return moves.map(move => move.to);
  }, []);

  /**
   * Limpia la selección del tablero
   */
  const clearSelection = useCallback(() => {
    setSelectedSquare(null);
    setPossibleMoves({});
  }, []);

  // ============================================
  // MANEJADORES DE INTERACCIÓN DEL TABLERO
  // ============================================

  /**
   * Maneja el click en una casilla del tablero
   */
  const onSquareClick = useCallback((square) => {
    if (isComparing) return;

    const game = gameRef.current;
    const piece = game.get(square);

    // Si hay una casilla seleccionada, intentar mover
    if (selectedSquare) {
      try {
        const move = game.move({
          from: selectedSquare,
          to: square,
          promotion: 'q'
        });

        if (move) {
          updatePosition();
          clearSelection();
          return;
        }
      } catch (e) {
        // Movimiento inválido, continuar para seleccionar nueva pieza
      }
    }

    // Seleccionar pieza del turno actual
    if (piece && piece.color === game.turn()) {
      if (selectedSquare === square) {
        // Deseleccionar si se hace click en la misma pieza
        clearSelection();
      } else {
        // Seleccionar nueva pieza
        setSelectedSquare(square);
        const moves = getPossibleMoves(square);
        const movesObj = {};
        moves.forEach(m => movesObj[m] = true);
        setPossibleMoves(movesObj);
      }
    } else {
      // Clic en casilla vacía o pieza enemiga
      clearSelection();
    }
  }, [selectedSquare, isComparing, getPossibleMoves, updatePosition, clearSelection]);

  /**
   * Maneja el drag & drop de piezas
   */
  const onPieceDrop = useCallback((sourceSquare, targetSquare) => {
    if (isComparing) return false;

    try {
      const move = gameRef.current.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q'
      });

      if (move) {
        updatePosition();
        clearSelection();
        return true;
      }
    } catch (e) {
      // Movimiento inválido
    }
    
    return false;
  }, [isComparing, updatePosition, clearSelection]);

  // ============================================
  // ESTILOS PERSONALIZADOS DEL TABLERO
  // ============================================

  /**
   * Calcula los estilos personalizados para las casillas
   * Incluye resaltado de selección, movimientos posibles y jaque
   */
  const customSquareStyles = useMemo(() => {
    const styles = {};
    const game = gameRef.current;

    // Resaltar casilla seleccionada
    if (selectedSquare) {
      styles[selectedSquare] = {
        backgroundColor: 'rgba(255, 255, 0, 0.4)'
      };

      // Resaltar movimientos posibles
      Object.keys(possibleMoves).forEach(square => {
        styles[square] = {
          background: 'radial-gradient(circle, rgba(255,255,0,0.4) 36%, transparent 40%)',
          borderRadius: '50%'
        };
      });
    }

    // Resaltar rey en jaque
    if (game.inCheck()) {
      const board = game.board();
      const turn = game.turn();
      
      board.forEach((row, rIndex) => {
        row.forEach((piece, cIndex) => {
          if (piece && piece.type === 'k' && piece.color === turn) {
            const file = String.fromCharCode(97 + cIndex);
            const rank = 8 - rIndex;
            const square = `${file}${rank}`;
            styles[square] = {
              background: 'radial-gradient(circle, rgba(255,0,0,0.6) 40%, transparent 70%)'
            };
          }
        });
      });
    }

    return styles;
  }, [selectedSquare, possibleMoves, position]);

  // ============================================
  // LÓGICA DE COMPARACIÓN
  // ============================================

  /**
   * Maneja la comparación de motores
   */
  const handleCompare = useCallback(async () => {
    setIsComparing(true);
    setError(null);
    setComparisonResults(null);

    try {
      const results = await compareEngines(position, depth);

      // Validar respuesta
      if (!results || typeof results !== 'object') {
        throw new Error('Respuesta inválida del servidor');
      }

      if (!results.results) {
        throw new Error('La respuesta no contiene resultados');
      }

      setComparisonResults(results);
    } catch (err) {
      console.error('Error en handleCompare:', err);
      setError(err.message || 'Error desconocido al comparar motores');
      setComparisonResults(null);
    } finally {
      setIsComparing(false);
    }
  }, [position, depth]);

  /**
   * Resetea la posición a la inicial
   */
  const resetPosition = useCallback(() => {
    gameRef.current.reset();
    updatePosition();
    setComparisonResults(null);
    setError(null);
    clearSelection();
  }, [updatePosition, clearSelection]);

  // ============================================
  // PROCESAMIENTO DE RESULTADOS
  // ============================================

  /**
   * Transforma y filtra los resultados de la comparación
   */
  const getFilteredResults = useMemo(() => {
    if (!comparisonResults || !comparisonResults.results) {
      return [];
    }

    let resultsArray = [];

    // Convertir diccionario a array si es necesario (retrocompatibilidad)
    if (Array.isArray(comparisonResults.results)) {
      resultsArray = comparisonResults.results;
    } else if (typeof comparisonResults.results === 'object' && comparisonResults.results !== null) {
      resultsArray = Object.entries(comparisonResults.results).map(([engine, bestmove]) => ({
        engine,
        bestmove,
        explanation: null
      }));
    } else {
      return [];
    }

    // Procesar resultados: identificar errores
    const processedResults = resultsArray.map(result => ({
      ...result,
      isError: result.bestmove && result.bestmove.toString().startsWith('ERROR:')
    }));

    // Aplicar filtro si existe
    if (!resultFilter.trim()) {
      return processedResults;
    }

    const term = resultFilter.toLowerCase();
    return processedResults.filter(result =>
      result.engine.toLowerCase().includes(term) ||
      (result.bestmove && result.bestmove.toLowerCase().includes(term)) ||
      (result.explanation && result.explanation.toLowerCase().includes(term))
    );
  }, [comparisonResults, resultFilter]);

  // ============================================
  // INFORMACIÓN DEL ESTADO ACTUAL
  // ============================================

  const currentTurn = gameRef.current.turn() === 'w' ? 'BLANCAS' : 'NEGRAS';
  const modeText = isComparing ? 'ANALIZANDO...' : 'EDICIÓN / ESPERA';
  const footerText = isComparing ? 'PROCESSING DATA...' : 'READY FOR COMPARISON...';

  // ============================================
  // RENDERIZADO
  // ============================================

  return (
    <div className="retro-container compare-page">
      {/* Header */}
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
        {/* Panel de Estado Superior */}
        <div className="system-panel">
          <div className="panel-border">
            <div className="panel-content">
              <div className="status-line">
                <span className="blink">&gt;</span> MODO: {modeText}
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> TURNO: {currentTurn}
              </div>
              <div className="status-line" style={{
                fontSize: '14px',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                <span className="blink">&gt;</span> FEN: {position}
              </div>
            </div>
          </div>
        </div>

        {/* Contenedor Principal: Tablero + Panel de Control */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          {/* Tablero de Ajedrez */}
          <div className="board-container compare-board-container" style={{ flex: '1 1 400px' }}>
            <div className="board-frame game-mode compare-board-frame">
              <div className="board-inner game-mode compare-board-inner">
                <Chessboard
                  position={position}
                  onSquareClick={onSquareClick}
                  onPieceDrop={onPieceDrop}
                  customSquareStyles={customSquareStyles}
                  customBoardStyle={{
                    borderRadius: '0px',
                    boxShadow: 'none',
                    width: '100%',
                    height: '100%'
                  }}
                  customLightSquareStyle={{ backgroundColor: '#24a32a' }}
                  customDarkSquareStyle={{ backgroundColor: '#147e1f' }}
                  boardWidth={600}
                />
              </div>
              <div className="board-label glow">COMPARE.SYS v2.0</div>
            </div>
          </div>

          {/* Panel de Control Lateral */}
          <div className="control-panel" style={{ flex: '1 1 300px' }}>
            <div className="panel-border">
              <div className="panel-content" style={{ maxHeight: 'none', height: '100%' }}>
                {/* Control de Profundidad */}
                <div className="form-group">
                  <label className="form-label glow">PROFUNDIDAD</label>
                  <div className="retro-select-wrapper">
                    <input
                      type="number"
                      className="retro-select"
                      value={depth}
                      onChange={(e) => setDepth(Math.max(1, Math.min(30, parseInt(e.target.value) || 10)))}
                      min="1"
                      max="30"
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>

                {/* Botones de Acción */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <button
                    className="retro-button glow"
                    onClick={handleCompare}
                    disabled={isComparing}
                  >
                    {isComparing ? 'ANALIZANDO...' : 'COMPARAR MOTORES'}
                  </button>

                  <button
                    className="retro-button glow"
                    onClick={resetPosition}
                    disabled={isComparing}
                  >
                    RESET POSICIÓN
                  </button>

                  <button
                    className="retro-button glow"
                    onClick={() => navigate('/')}
                  >
                    VOLVER AL MENÚ
                  </button>
                </div>

                {/* Instrucciones */}
                <div className="move-history" style={{ marginTop: '20px' }}>
                  <div className="history-title glow">▼ INSTRUCCIONES:</div>
                  <div className="history-content" style={{ fontSize: '16px' }}>
                    1. Mueve las piezas para editar la posición.<br />
                    2. Elige profundidad de análisis.<br />
                    3. Pulsa COMPARAR MOTORES.<br />
                    4. Analiza los resultados en la tabla.
                  </div>
                </div>

                {/* Mensaje de Error */}
                {error && (
                  <div className="move-history" style={{ marginTop: '15px' }}>
                    <div className="history-title glow" style={{ color: '#ff4444' }}>
                      ▼ ERROR:
                    </div>
                    <div className="history-content" style={{ color: '#ff4444' }}>
                      ⚠ {error}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Panel de Resultados */}
        {comparisonResults && (
          <div className="system-panel" style={{ marginTop: '20px' }}>
            <div className="panel-border">
              <div className="panel-content" style={{ maxHeight: '500px' }}>
                {/* Header de Resultados con Filtro */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '10px',
                  flexWrap: 'wrap',
                  gap: '10px'
                }}>
                  <div className="history-title glow" style={{ margin: 0 }}>
                    ▼ RESULTADOS ({comparisonResults.engines_compared} motores)
                  </div>
                  <div style={{ width: '200px', minWidth: '150px' }}>
                    <input
                      type="text"
                      className="retro-select"
                      placeholder="Filtrar..."
                      style={{ padding: '5px 10px', fontSize: '16px', height: '40px' }}
                      value={resultFilter}
                      onChange={(e) => setResultFilter(e.target.value)}
                    />
                  </div>
                </div>

                {/* Tabla de Resultados */}
                <div style={{ overflowX: 'auto' }}>
                  <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    color: 'var(--retro-green)',
                    fontFamily: 'VT323, monospace',
                    fontSize: '18px'
                  }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid var(--retro-green)' }}>
                        <th style={{ textAlign: 'left', padding: '10px', width: '25%' }}>
                          MOTOR
                        </th>
                        <th style={{ textAlign: 'left', padding: '10px', width: '15%' }}>
                          MOVIMIENTO
                        </th>
                        <th style={{ textAlign: 'left', padding: '10px' }}>
                          ANÁLISIS / EXPLICACIÓN
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredResults.length > 0 ? (
                        getFilteredResults.map((result, index) => (
                          <tr
                            key={`${result.engine}-${index}`}
                            style={{
                              borderBottom: '1px solid rgba(36, 163, 42, 0.3)',
                              backgroundColor: result.isError
                                ? 'rgba(255, 0, 0, 0.1)'
                                : 'transparent'
                            }}
                          >
                            <td style={{
                              padding: '10px',
                              fontWeight: 'bold',
                              verticalAlign: 'top'
                            }}>
                              {index + 1}. {result.engine}
                            </td>
                            <td style={{
                              padding: '10px',
                              color: result.isError ? '#ff4444' : '#fff',
                              verticalAlign: 'top'
                            }}>
                              {result.bestmove || 'N/A'}
                            </td>
                            <td style={{
                              padding: '10px',
                              fontSize: '16px',
                              color: '#ccc',
                              verticalAlign: 'top'
                            }}>
                              {result.explanation ? (
                                <div style={{ whiteSpace: 'pre-wrap' }}>
                                  {result.explanation}
                                </div>
                              ) : result.isError ? (
                                <span style={{ color: '#ff6666' }}>
                                  Falló al analizar la posición.
                                </span>
                              ) : (
                                'Análisis completado (sin explicación textual).'
                              )}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3" style={{
                            padding: '20px',
                            textAlign: 'center',
                            fontStyle: 'italic'
                          }}>
                            {resultFilter.trim()
                              ? 'No hay resultados que coincidan con el filtro.'
                              : 'No hay resultados disponibles.'}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="terminal-footer">
        <div className="footer-text glow">
          <span className="blink">█</span> {footerText}
        </div>
      </div>
    </div>
  );
}

export default ComparePage;
