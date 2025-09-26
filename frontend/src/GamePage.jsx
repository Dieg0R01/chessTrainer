import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';

function GamePage() {
  const location = useLocation();
  const { selectedEngineA, selectedEngineB } = location.state || {};
  const chess = useRef(new Chess());
  const [gamePosition, setGamePosition] = useState(chess.current.fen());
  const [status, setStatus] = useState("");

  const updateStatus = useCallback(() => {
    let currentStatus = "";
    let moveColor = chess.current.turn() === 'w' ? "Blancas" : "Negras";

    if (chess.current.in_checkmate()) {
      currentStatus = "Jaque mate! " + moveColor + " pierde.";
    } else if (chess.current.in_draw()) {
      currentStatus = "Empate!";
    } else {
      currentStatus = moveColor + " para mover.";
      if (chess.current.in_check()) {
        currentStatus += " " + moveColor + " está en jaque.";
      }
    }
    setStatus(currentStatus);
  }, []);

  const safeGameMutate = useCallback((modify) => {
    setGamePosition((oldPosition) => {
      const newGame = new Chess(oldPosition);
      modify(newGame);
      return newGame.fen();
    });
  }, []);

  const onDrop = useCallback((sourceSquare, targetSquare) => {
    let move = null;
    safeGameMutate((game) => {
      move = game.move({ from: sourceSquare, to: targetSquare, promotion: 'q' });
    });
    // illegal move
    if (move === null) return false;

    updateStatus();

    // Si es humano vs motor, envía la jugada al backend
    if (selectedEngineA === 'human' && selectedEngineB !== 'none') {
      makeEngineMove(selectedEngineB);
    } else if (selectedEngineA !== 'human' && selectedEngineB === 'none') {
      // Si el jugador humano está jugando contra el motor A
      makeEngineMove(selectedEngineA);
    } else if (selectedEngineA !== 'human' && selectedEngineB !== 'none') {
      // Motor vs Motor
      console.log("Partida Motor vs Motor");
    }

    return true;
  }, [selectedEngineA, selectedEngineB, updateStatus, safeGameMutate]);

  const makeEngineMove = async (engineName) => {
    try {
      const response = await fetch('http://localhost:8000/move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ engine: engineName, fen: chess.current.fen(), depth: 10 }),
      });
      const data = await response.json();
      const bestMove = data.bestmove;

      if (bestMove) {
        safeGameMutate((game) => {
          game.move(bestMove);
        });
        updateStatus();
      }
    } catch (error) {
      console.error("Error al obtener movimiento del motor:", error);
    }
  };

  useEffect(() => {
    updateStatus();
  }, [gamePosition, updateStatus]);

  return (
    <div>
      <h1>Partida de Ajedrez</h1>
      <div>
        <p>Motor A: {selectedEngineA || "Humano"}</p>
        <p>Motor B: {selectedEngineB === "none" ? "Humano" : selectedEngineB}</p>
      </div>
      <div style={{ width: '500px' }}>
        <Chessboard
          position={gamePosition}
          onPieceDrop={onDrop}
        />
      </div>
      <p>Status: {status}</p>
    </div>
  );
}

export default GamePage;
