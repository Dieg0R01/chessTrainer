import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';

function GamePage() {
  const location = useLocation();
  const { selectedEngineA, selectedEngineB } = location.state || {};
  const gameRef = useRef(new Chess());
  const [position, setPosition] = useState(gameRef.current.fen());
  const [status, setStatus] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

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

  useEffect(() => {
    console.log("GamePage montado.");
    console.log("Motor A seleccionado:", selectedEngineA);
    console.log("Motor B seleccionado:", selectedEngineB);
    updateStatus();
  }, [updateStatus]);

  const makeEngineMove = useCallback(async (engineName) => {
    if (isProcessing) return; // Evitar múltiples llamadas simultáneas
    
    setIsProcessing(true);
    try {
      const game = gameRef.current;
      const backendUrl = window.location.origin.replace(':5173', ':8000');
      const response = await fetch(`${backendUrl}/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ engine: engineName, fen: game.fen(), depth: 10 }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        console.error("Error del servidor:", errorData);
        setStatus(`Error: ${engineName} - ${errorData.detail || 'No se pudo obtener el movimiento'}`);
        return;
      }
      
      const data = await response.json();
      const bestMove = data.bestmove;

      if (bestMove) {
        try {
          game.move(bestMove);
          setPosition(game.fen());
          updateStatus();
        } catch (error) {
          console.error("Error al aplicar movimiento del motor:", error);
          setStatus(`Error: No se pudo aplicar el movimiento ${bestMove}`);
        }
      }
    } catch (error) {
      console.error("Error al obtener movimiento del motor:", error);
      setStatus(`Error: No se pudo conectar con el motor ${engineName}. La posición puede no estar en la base de datos de Lichess.`);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing, updateStatus]);

  const onPieceDrop = useCallback((sourceSquare, targetSquare) => {
    console.log("onPieceDrop llamado:", sourceSquare, "->", targetSquare);
    
    if (isProcessing) return false; // Evitar movimientos durante procesamiento
    
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
      setPosition(game.fen());
      
      // Actualizar status de forma síncrona
      updateStatus();
      
      // Programar movimiento del motor si es necesario
      const needsEngineMove = (selectedEngineA === 'human' && selectedEngineB !== 'none') || 
                             (selectedEngineA !== 'human' && selectedEngineB === 'none');
      
      if (needsEngineMove) {
        const engineToMove = selectedEngineA === 'human' ? selectedEngineB : selectedEngineA;
        console.log("Solicitando movimiento del motor:", engineToMove);
        
        // Usar setTimeout para evitar bloqueo del hilo principal
        setTimeout(() => {
          makeEngineMove(engineToMove);
        }, 100);
      }

      return true;
    } catch (error) {
      console.log("Movimiento ILEGAL:", error.message);
      return false;
    }
  }, [isProcessing, updateStatus, makeEngineMove, selectedEngineA, selectedEngineB]);

  // Memoizar el componente Chessboard para evitar re-renders innecesarios
  const memoizedChessboard = useMemo(() => (
    <Chessboard
      position={position}
      onPieceDrop={onPieceDrop}
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
  ), [position, onPieceDrop]);

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
