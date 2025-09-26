import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import GamePage from './GamePage'; // Vamos a crear este archivo

function SelectionPage() {
  const [selectedEngineA, setSelectedEngineA] = useState("");
  const [selectedEngineB, setSelectedEngineB] = useState("none"); // 'none' para jugar contra humano
  const [availableEngines, setAvailableEngines] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Aquí haremos una llamada al backend para obtener los motores disponibles
    // Por ahora, usamos un mock
    setAvailableEngines(["lichess", "stockfish-local", "otro-motor-rest"]);
  }, []);

  const handleStartGame = () => {
    navigate('/game', { state: { selectedEngineA, selectedEngineB } });
  };

  return (
    <div className="App">
      <h1>Selección de Motores de Ajedrez</h1>
      <div>
        <label htmlFor="engineA">Motor Blanco (Tú o Motor A):</label>
        <select
          id="engineA"
          value={selectedEngineA}
          onChange={(e) => setSelectedEngineA(e.target.value)}
        >
          <option value="">-- Selecciona un motor --</option>
          {availableEngines.map((engine) => (
            <option key={engine} value={engine}>
              {engine}
            </option>
          ))}
          <option value="human">Humano</option>
        </select>
      </div>
      <div>
        <label htmlFor="engineB">Motor Negro (Motor B o Ninguno):</label>
        <select
          id="engineB"
          value={selectedEngineB}
          onChange={(e) => setSelectedEngineB(e.target.value)}
        >
          <option value="none">Ninguno (Jugarás contra el motor A)</option>
          {availableEngines.map((engine) => (
            <option key={engine} value={engine}>
              {engine}
            </option>
          ))}
        </select>
      </div>
      <button onClick={handleStartGame} disabled={!selectedEngineA && selectedEngineB !== "none"}>
        Empezar Partida
      </button>
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
