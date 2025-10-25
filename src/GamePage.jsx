import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';

function GamePage() {
  const location = useLocation();
  const { selectedEngineA, selectedEngineB } = location.state || {};
  const gameRef = useRef(new Chess());
  const [position, setPosition] = useState(gameRef.current.fen());
  const [status, setStatus] = useState("");

  const updateStatus = () => {
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
  };

  useEffect(() => {
    console.log("GamePage montado.");
    console.log("Motor A seleccionado:", selectedEngineA);
    console.log("Motor B seleccionado:", selectedEngineB);
    updateStatus();
  }, []);

  const makeEngineMove = async (engineName) => {
    try {
      const game = gameRef.current;
      // Obtener la URL del backend dinámicamente basándose en la URL actual
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
    }
  };

  function onPieceDrop(sourceSquare, targetSquare) {
    console.log("onPieceDrop llamado:", sourceSquare, "->", targetSquare);
    
    try {
      const game = gameRef.current;
      const move = game.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q'
      });

      console.log("Resultado del movimiento:", move);
      console.log("Movimiento VÁLIDO - Actualizando estado");
      setPosition(game.fen());
      
      // Actualizar status después de un breve delay
      setTimeout(() => {
        updateStatus();
        
        // Si es humano vs motor, hacer que el motor juegue
        if (selectedEngineA === 'human' && selectedEngineB !== 'none') {
          console.log("Solicitando movimiento del motor:", selectedEngineB);
          makeEngineMove(selectedEngineB);
        } else if (selectedEngineA !== 'human' && selectedEngineB === 'none') {
          console.log("Solicitando movimiento del motor:", selectedEngineA);
          makeEngineMove(selectedEngineA);
        }
      }, 50);

      return true;
    } catch (error) {
      // En chess.js v1.4.0, los movimientos ilegales lanzan excepciones
      console.log("Movimiento ILEGAL:", error.message);
      return false;
    }
  }

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
            </div>
          </div>
        </div>

        {/* Chess board container */}
        <div className="board-container">
          <div className="board-frame">
            <div className="board-inner">
              <Chessboard
                position={position}
                onPieceDrop={onPieceDrop}
                customBoardStyle={{
                  borderRadius: '0px',
                  boxShadow: 'none'
                }}
                customLightSquareStyle={{
                  backgroundColor: '#1a5c1a'
                }}
                customDarkSquareStyle={{
                  backgroundColor: '#0a3d0a'
                }}
              />
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
