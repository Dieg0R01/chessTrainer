import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { fetchBestMove } from './api';

function GamePage() {
  const location = useLocation();
  const { selectedEngineA, selectedEngineB } = location.state || {};
  const gameRef = useRef(new Chess());
  const [position, setPosition] = useState(gameRef.current.fen());
  const [status, setStatus] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const lastMoveWasEngineRef = useRef(false);
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [possibleMoves, setPossibleMoves] = useState({});

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
      
      // Obtener el movimiento del backend usando la API centralizada
      // Pasar move_history para que los motores generativos tengan contexto del juego
      const data = await fetchBestMove(engineName, currentFen, 10, {
        move_history: moveHistory
      });
      const bestMove = data.bestmove;

      if (bestMove) {
        try {
          // Aplicar el movimiento al juego
          game.move(bestMove);
          lastMoveWasEngineRef.current = true; // Marcar que el último movimiento fue del motor
          setPosition(game.fen());
          updateStatus();
          
          // Si hay explicación disponible (motores generativos), mostrarla en consola
          if (data.explanation) {
            console.log(`Explicación del motor ${engineName}:`, data.explanation);
          }
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
  }, [isProcessing, updateStatus]);

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
      if (selectedEngineB && selectedEngineB !== 'none' && selectedEngineB !== 'human') {
        return selectedEngineB;
      }
      return null; // Es humano o none
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
    
    // Limpiar selección cuando se hace drag and drop
    setSelectedSquare(null);
    setPossibleMoves({});
    
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
  const memoizedChessboard = useMemo(() => (
    <Chessboard
      position={position}
      onPieceDrop={onPieceDrop}
      onSquareClick={onSquareClick}
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
      boardWidth={600}
    />
  ), [position, onPieceDrop, onSquareClick, customSquareStyles]);

  console.log("Renderizando GamePage, FEN:", position);

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
                <span className="blink">&gt;</span> GAME: IN PROGRESS
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> ENGINE A: {selectedEngineA || "HUMANO"}
              </div>
              <div className="status-line">
                <span className="blink">&gt;</span> ENGINE B: {selectedEngineB === "none" ? "HUMANO" : selectedEngineB}
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
          <div className="board-frame">
            <div className="board-inner">
              {memoizedChessboard}
            </div>
            <div className="board-label glow">CHESS.SYS v2.1</div>
          </div>
        </div>

        {/* Control panel */}
        <div className="control-panel">
          <div className="panel-border">
            <div className="panel-content">
              <button className="retro-button glow" onClick={() => window.location.href = '/'}>
                [ VOLVER A SELECCIÓN ]
              </button>
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
