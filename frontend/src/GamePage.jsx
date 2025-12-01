import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { fetchBestMove, fetchStrategies, fetchEnginesInfo } from './api';
import CustomSelect from './CustomSelect';

function GamePage() {
  const location = useLocation();
  const { selectedEngineA, selectedEngineB, use3DBoard = false } = location.state || {};
  const gameRef = useRef(new Chess());
  const [position, setPosition] = useState(gameRef.current.fen());
  const [status, setStatus] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const lastMoveWasEngineRef = useRef(false);
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [possibleMoves, setPossibleMoves] = useState({});
  const [strategies, setStrategies] = useState({});
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [boardSize, setBoardSize] = useState(600);
  const [enginesInfo, setEnginesInfo] = useState({});
  
  // Determinar si el motor actual es generativo
  const isCurrentEngineGenerative = useMemo(() => {
    const currentEngine = gameRef.current.turn() === 'w' ? selectedEngineA : selectedEngineB;
    if (!currentEngine || currentEngine === 'human') return false;
    const engineInfo = enginesInfo[currentEngine];
    return engineInfo && engineInfo.type === 'generative';
  }, [selectedEngineA, selectedEngineB, enginesInfo, position]);

  const updateStatus = useCallback(() => {
    const game = gameRef.current;
    let currentStatus = "";
    let moveColor = game.turn() === 'w' ? "Blancas" : "Negras";

    if (game.isCheckmate()) {
      currentStatus = "Jaque mate! " + moveColor + " pierde.";
    } else if (game.isDraw()) {
      currentStatus = "Empate!";
    } else {
      currentStatus = moveColor + " para mover.";
      if (game.isCheck()) {
        currentStatus += " " + moveColor + " está en jaque.";
      }
    }
    setStatus(currentStatus);
  }, []);

  // Función para hacer que un motor juegue
  const makeEngineMove = useCallback(async (engineName) => {
    if (isProcessing) return; // Evitar múltiples llamadas simultáneas
    
    setIsProcessing(true);
    try {
      const game = gameRef.current;
      const currentFen = game.fen();
      
      // Obtener historial de movimientos en formato UCI (separado por espacios)
      // CRÍTICO: game.history() devuelve PGN, necesitamos UCI para el prompt
      // Usamos history({ verbose: true }) para obtener objetos con información completa
      let moveHistory = 'Inicio de la partida';
      const historyVerbose = game.history({ verbose: true });
      
      if (historyVerbose.length > 0) {
        // Convertir cada movimiento a formato UCI: from + to + (promotion si aplica)
        const uciMoves = historyVerbose.map(move => {
          let uci = move.from + move.to;
          if (move.promotion) {
            uci += move.promotion.toLowerCase();
          }
          return uci;
        });
        moveHistory = uciMoves.join(' ');
      }
      
      // Log para debugging: verificar que el historial se envía correctamente
      console.log(`📜 Historial de movimientos (UCI) enviado a ${engineName}:`, moveHistory);
      console.log(`📊 Total de movimientos en historial:`, historyVerbose.length);
      
      // Preparar opciones para motores generativos
      const options = {
        move_history: moveHistory
      };
      
      // Agregar estrategia si está seleccionada
      if (selectedStrategy) {
        options.strategy = selectedStrategy;
      }
      
      // Obtener el movimiento del backend usando la API centralizada
      // Pasar move_history para que los motores generativos tengan contexto del juego
      const data = await fetchBestMove(engineName, currentFen, 10, options);
      const bestMove = data.bestmove;

      if (bestMove) {
        try {
          // Aplicar el movimiento al juego
          game.move(bestMove);
          lastMoveWasEngineRef.current = true; // Marcar que el último movimiento fue del motor
          setPosition(game.fen());
          updateStatus();
        } catch (error) {
          console.error("Error al aplicar movimiento del motor:", error);
          setStatus(`Error: No se pudo aplicar el movimiento ${bestMove}. ${error.message}`);
        }
      } else {
        setStatus(`Error: El motor ${engineName} no devolvió un movimiento válido`);
      }
    } catch (error) {
      console.error("Error al obtener movimiento del motor:", error);
      setStatus(`Error: ${error.message || `No se pudo conectar con el motor ${engineName}`}`);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing, updateStatus, selectedStrategy]);

  // Determinar qué motor debe jugar según el turno actual
  const getCurrentPlayer = useCallback(() => {
    const game = gameRef.current;
    const isWhiteTurn = game.turn() === 'w';
    
    // EngineA juega con blancas, EngineB con negras
    if (isWhiteTurn) {
      // Turno de blancas
      if (selectedEngineA && selectedEngineA !== 'human') {
        return selectedEngineA;
      }
      return null; // Es humano
    } else {
      // Turno de negras
      if (selectedEngineB && selectedEngineB !== 'human') {
        return selectedEngineB;
      }
      return null; // Es humano
    }
  }, [selectedEngineA, selectedEngineB]);

  // Efecto para hacer que los motores jueguen automáticamente cuando es su turno
  useEffect(() => {
    const game = gameRef.current;
    
    // No hacer nada si el juego terminó o está procesando
    if (game.isGameOver() || isProcessing) {
      return;
    }
    
    // Si el último movimiento fue del motor, resetear la bandera y no hacer nada más
    // El motor ya hizo su movimiento, ahora esperamos al siguiente cambio de posición
    if (lastMoveWasEngineRef.current) {
      lastMoveWasEngineRef.current = false;
      return;
    }
    
    const currentPlayer = getCurrentPlayer();
    
    // Si es turno de un motor, limpiar selección y hacer que juegue automáticamente
    if (currentPlayer) {
      // Limpiar selección cuando es turno de un motor
      setSelectedSquare(null);
      setPossibleMoves({});
      
      console.log(`Es turno del motor: ${currentPlayer}`);
      // Pequeño delay para evitar problemas de estado
      const timeoutId = setTimeout(() => {
        makeEngineMove(currentPlayer);
      }, 200);
      
      return () => clearTimeout(timeoutId);
    }
  }, [position, isProcessing, getCurrentPlayer, makeEngineMove]);

  // Cargar estrategias y información de motores al montar
  useEffect(() => {
    fetchStrategies()
      .then(data => {
        setStrategies(data.strategies || {});
        console.log('✅ Estrategias cargadas:', data);
      })
      .catch(error => {
        console.warn('⚠️ No se pudieron cargar estrategias:', error);
      });
    
    fetchEnginesInfo()
      .then(data => {
        const infoMap = {};
        data.engines.forEach(engine => {
          infoMap[engine.name] = engine;
        });
        setEnginesInfo(infoMap);
      })
      .catch(error => {
        console.warn('⚠️ No se pudo cargar información de motores:', error);
      });
  }, []);

  // Calcular tamaño del tablero de forma responsive
  // El tablero siempre será múltiplo de 75px (tamaño de cada casilla)
  useEffect(() => {
    const updateBoardSize = () => {
      const width = window.innerWidth;
      const squareSize = 75; // Tamaño de cada casilla
      const squaresPerRow = 8; // 8x8 tablero
      
      if (width <= 480) {
        // Móviles pequeños - calcular múltiplo de 75px que quepa
        const maxWidth = width - 50;
        const maxSquares = Math.floor(maxWidth / squareSize);
        const boardSize = Math.min(maxSquares, squaresPerRow) * squareSize;
        setBoardSize(boardSize);
      } else if (width <= 768) {
        // Tablets pequeñas y móviles grandes
        const maxWidth = width - 60;
        const maxSquares = Math.floor(maxWidth / squareSize);
        const boardSize = Math.min(maxSquares, squaresPerRow) * squareSize;
        setBoardSize(boardSize);
      } else if (width <= 1024) {
        // Tablets
        const maxWidth = width - 80;
        const maxSquares = Math.floor(maxWidth / squareSize);
        const boardSize = Math.min(maxSquares, squaresPerRow) * squareSize;
        setBoardSize(boardSize);
      } else {
        // Desktop, tamaño fijo: 8 casillas * 75px = 600px
        setBoardSize(squaresPerRow * squareSize);
      }
    };
    
    updateBoardSize();
    window.addEventListener('resize', updateBoardSize);
    return () => window.removeEventListener('resize', updateBoardSize);
  }, []);

  useEffect(() => {
    console.log("GamePage montado.");
    console.log("Motor A seleccionado:", selectedEngineA);
    console.log("Motor B seleccionado:", selectedEngineB);
    updateStatus();
    
    // Si el primer turno es de un motor, hacer que juegue
    const firstPlayer = getCurrentPlayer();
    if (firstPlayer) {
      setTimeout(() => {
        makeEngineMove(firstPlayer);
      }, 500);
    }
  }, [updateStatus, getCurrentPlayer, makeEngineMove, selectedEngineA, selectedEngineB]);

  // Función para obtener los movimientos posibles de una casilla
  const getPossibleMoves = useCallback((square) => {
    const game = gameRef.current;
    const moves = game.moves({
      square: square,
      verbose: true
    });
    
    const moveSquares = {};
    moves.forEach((move) => {
      // Usar un pequeño círculo verde centrado usando backgroundImage con gradiente radial
      moveSquares[move.to] = {
        backgroundImage: 'radial-gradient(circle, rgba(0, 255, 0, 0.6) 0%, rgba(0, 255, 0, 0.6) 40%, transparent 40%)',
        backgroundSize: '20px 20px',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        animation: 'blink-green 1s infinite'
      };
    });
    
    return moveSquares;
  }, []);

  // Función para manejar clicks en casillas
  const onSquareClick = useCallback((square) => {
    if (isProcessing) return; // Evitar interacciones durante procesamiento
    
    const game = gameRef.current;
    
    // Verificar si es turno de un motor (no permitir interacción humana)
    const currentPlayer = getCurrentPlayer();
    if (currentPlayer) {
      // Es turno de un motor, no permitir clicks
      return;
    }
    
    const piece = game.get(square);
    
    // Si hay una pieza seleccionada y se hace click en una casilla destino
    if (selectedSquare && selectedSquare !== square) {
      // Intentar hacer el movimiento
      try {
        const move = game.move({
          from: selectedSquare,
          to: square,
          promotion: 'q'
        });

        console.log("Movimiento por click:", move);
        
        // Limpiar selección y casillas posibles
        setSelectedSquare(null);
        setPossibleMoves({});
        
        // Actualizar posición
        lastMoveWasEngineRef.current = false; // El movimiento fue humano
        setPosition(game.fen());
        updateStatus();
        
        return;
      } catch (error) {
        console.log("Movimiento ILEGAL:", error.message);
        // Si el movimiento es ilegal, limpiar selección y permitir nueva selección
        setSelectedSquare(null);
        setPossibleMoves({});
      }
    }
    
    // Si se hace click en una pieza del color que tiene el turno
    if (piece && piece.color === game.turn()) {
      setSelectedSquare(square);
      const moves = getPossibleMoves(square);
      setPossibleMoves(moves);
    } else {
      // Si se hace click en una casilla vacía o pieza del otro color, limpiar selección
      setSelectedSquare(null);
      setPossibleMoves({});
    }
  }, [selectedSquare, isProcessing, getPossibleMoves, updateStatus, getCurrentPlayer]);

  const onPieceDrop = useCallback((sourceSquare, targetSquare) => {
    console.log("onPieceDrop llamado:", sourceSquare, "->", targetSquare);
    
    if (isProcessing) return false; // Evitar movimientos durante procesamiento
    
    // Verificar si es turno de un motor (no permitir interacción humana)
    const currentPlayer = getCurrentPlayer();
    if (currentPlayer) {
      // Es turno de un motor, no permitir drag and drop
      return false;
    }
    
    try {
      const game = gameRef.current;
      const move = game.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q'
      });

      console.log("Resultado del movimiento:", move);
      console.log("Movimiento VÁLIDO - Actualizando estado");
      
      // Actualizar posición inmediatamente
      lastMoveWasEngineRef.current = false; // El movimiento fue humano
      setPosition(game.fen());
      
      // Limpiar selección/estilos al completar el movimiento
      setSelectedSquare(null);
      setPossibleMoves({});
      
      // Actualizar status de forma síncrona
      updateStatus();
      
      // El efecto useEffect se encargará de hacer jugar al motor si es necesario
      // No necesitamos programar el movimiento aquí porque el efecto detectará el cambio de posición

      return true;
    } catch (error) {
      console.log("Movimiento ILEGAL:", error.message);
      return false;
    }
  }, [isProcessing, updateStatus, getCurrentPlayer]);

  const onPieceDragBegin = useCallback((piece, sourceSquare) => {
    if (isProcessing) return;

    const currentPlayer = getCurrentPlayer();
    if (currentPlayer) return;

    const game = gameRef.current;
    const pieceData = game.get(sourceSquare);
    if (!pieceData || pieceData.color !== game.turn()) return;

    setSelectedSquare(sourceSquare);
    const moves = getPossibleMoves(sourceSquare);
    setPossibleMoves(moves);
  }, [isProcessing, getCurrentPlayer, getPossibleMoves]);

  const onPieceDragEnd = useCallback(() => {
    setSelectedSquare(null);
    setPossibleMoves({});
  }, []);

  // Combinar estilos personalizados: casilla seleccionada + casillas posibles
  const customSquareStyles = useMemo(() => {
    const styles = { ...possibleMoves };
    
    // Agregar estilo para la casilla seleccionada (mismo color verde que las casillas posibles)
    if (selectedSquare) {
      styles[selectedSquare] = {
        backgroundImage: 'radial-gradient(circle, rgba(0, 255, 0, 0.6) 0%, rgba(0, 255, 0, 0.6) 40%, transparent 40%)',
        backgroundSize: '20px 20px',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        animation: 'blink-green 1s infinite'
      };
    }
    
    return styles;
  }, [selectedSquare, possibleMoves]);

  // Memoizar el componente Chessboard para evitar re-renders innecesarios
  const memoizedChessboard = useMemo(() => {
    // Calcular tamaño del tablero 3D (un poco más pequeño para que quepa)
    const board3DSize = use3DBoard ? Math.floor(boardSize * 0.85) : boardSize;
    
    if (use3DBoard) {
      // Tablero 3D con estética retro verde, grosor y centrado
      const boardTotalSize = board3DSize + 48; // tablero + bordes
      const boardThickness = 30;
      
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          width: '100%',
          height: '100%',
          perspective: '1200px',
          perspectiveOrigin: 'center center'
        }}>
          <div style={{
            transform: 'rotateX(27.5deg)',
            transformOrigin: 'center center',
            transformStyle: 'preserve-3d',
            position: 'relative',
            width: `${boardTotalSize}px`,
            height: `${boardTotalSize + boardThickness}px`
          }}>
            {/* Tablero con casillas (cara superior) */}
            <div style={{
              position: 'relative',
              zIndex: 2,
              transform: 'translateZ(0px)'
            }}>
              <Chessboard
                position={position}
                onPieceDrop={onPieceDrop}
                onSquareClick={onSquareClick}
                onPieceDragBegin={onPieceDragBegin}
                onPieceDragEnd={onPieceDragEnd}
                customSquareStyles={customSquareStyles}
                customBoardStyle={{
                  border: '24px solid #0f3d14',
                  borderStyle: 'solid',
                  borderRadius: '6px',
                  boxShadow: `
                    inset 0 0 0 3px #1a5a1f,
                    inset 0 0 0 6px #0f3d14,
                    0 0 0 3px #1a5a1f,
                    0 0 0 6px #0f3d14,
                    rgba(0, 0, 0, 0.7) 0px 35px 70px -15px,
                    rgba(0, 0, 0, 0.5) 0px 20px 40px -20px
                  `,
                  padding: '15px',
                  background: '#24a32a',
                  overflow: 'visible',
                  position: 'relative',
                  width: `${boardTotalSize}px`,
                  height: `${boardTotalSize}px`,
                  boxSizing: 'border-box'
                }}
                customLightSquareStyle={{
                  backgroundColor: '#24a32a'
                }}
                customDarkSquareStyle={{
                  backgroundColor: '#147e1f'
                }}
                boardWidth={board3DSize}
                arePiecesDraggable={!isProcessing}
              />
            </div>
            {/* Grosor del tablero - cara inferior (detrás del tablero) */}
            <div style={{
              position: 'absolute',
              top: `${boardTotalSize}px`,
              left: '0',
              width: `${boardTotalSize}px`,
              height: `${boardThickness}px`,
              background: 'linear-gradient(to bottom, #0a2d0f 0%, #051a08 100%)',
              transform: 'rotateX(-90deg)',
              transformOrigin: 'top center',
              borderRadius: '0 0 6px 6px',
              boxShadow: 'rgba(0, 0, 0, 0.6) 0px 15px 30px',
              border: '24px solid #0f3d14',
              borderTop: 'none',
              borderLeftWidth: '24px',
              borderRightWidth: '24px',
              borderBottomWidth: '24px',
              boxSizing: 'border-box',
              zIndex: 1
            }} />
          </div>
        </div>
      );
    } else {
      // Tablero tradicional
      return (
        <Chessboard
          position={position}
          onPieceDrop={onPieceDrop}
          onSquareClick={onSquareClick}
          onPieceDragBegin={onPieceDragBegin}
          onPieceDragEnd={onPieceDragEnd}
          customSquareStyles={customSquareStyles}
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
          boardWidth={boardSize}
          arePiecesDraggable={!isProcessing}
        />
      );
    }
  }, [position, onPieceDrop, onSquareClick, onPieceDragBegin, onPieceDragEnd, customSquareStyles, boardSize, isProcessing, use3DBoard]);

  console.log("Renderizando GamePage, FEN:", position);

  return (
    <div className="retro-container">
      {/* Terminal header */}
      <div className="terminal-header">
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
                <span className="blink">&gt;</span> SYSTEM STATUS: ONLINE
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> GAME: IN PROGRESS
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> ENGINE A: {selectedEngineA || "HUMANO"}
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> ENGINE B: {selectedEngineB === 'human' ? "HUMANO" : selectedEngineB}
              </div>
              {isProcessing && (
                <div className="status-line">
                  <span className="blink">&gt;</span> PROCESSING: ENGINE THINKING...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chess board container */}
        <div className="board-container">
          <div className="board-frame game-mode">
            <div className="board-inner game-mode">
              {memoizedChessboard}
            </div>
          </div>
        </div>

        {/* Control panel */}
        <div className="control-panel">
          <div className="panel-border">
            <div className="panel-content">
              <button className="retro-button glow" onClick={() => window.location.href = '/'} style={{ width: '100%', marginBottom: '10px' }}>
                VOLVER A SELECCIÓN
              </button>

              {/* Selector de estrategias para motores generativos - Solo mostrar si el motor actual es generativo */}
              {isCurrentEngineGenerative && Object.keys(strategies).length > 0 && (
                <div className="form-group" style={{ marginBottom: '10px' }}>
                  <label className="form-label glow">ESTRATEGIA</label>
                  <CustomSelect
                    value={selectedStrategy || ''}
                    onChange={(value) => setSelectedStrategy(value || null)}
                    placeholder="AUTO (por defecto)"
                    options={[
                      { value: '', label: 'AUTO (por defecto)' },
                      ...Object.entries(strategies).map(([key, strategy]) => ({
                        value: key,
                        label: strategy.name || key
                      }))
                    ]}
                  />
                </div>
              )}

              <div className="move-history">
                <div className="history-title glow">▼ GAME STATUS:</div>
                <div className="history-content">
                  <div className="history-item">
                    {status || "Cargando estado del juego..."}
                  </div>
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

export default GamePage;
