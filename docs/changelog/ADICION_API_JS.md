# 📦 Adición de `api.js` - Módulo Centralizado de Comunicación con Backend

## 🎯 Introducción

Se ha añadido el módulo `frontend/src/api.js` para centralizar toda la comunicación entre el frontend React y el backend FastAPI. Este cambio mejora significativamente la organización del código, su mantenibilidad y reutilización.

---

## ❓ ¿Por qué un módulo separado?

### ¿Se puede hacer directamente en React?

**Sí**, técnicamente es posible incluir todo el código de comunicación con el backend directamente en los componentes de React (`App.jsx`, `GamePage.jsx`, etc.). Sin embargo, esto no es una práctica recomendada por las siguientes razones:

### Problemas de hacerlo directamente en React:

1. **Código duplicado**: Cada componente tendría que repetir la lógica de:
   - Construcción de URLs del backend
   - Manejo de errores HTTP
   - Parsing de respuestas
   - Logging y debugging

2. **Difícil mantenimiento**: Si cambia la URL del backend o el formato de respuesta, hay que modificar múltiples archivos

3. **Mezcla de responsabilidades**: Los componentes React se encargan tanto de:
   - Renderizar la UI
   - Gestionar estado
   - Comunicarse con el backend
   - Manejar errores de red

4. **Testing complejo**: Para probar la comunicación con el backend, necesitas montar componentes completos de React

---

## ✅ Ventajas de `api.js`

### 1. **Separación de Responsabilidades (Separation of Concerns)**

Cada módulo tiene una responsabilidad clara y única:

- **React Components** (`App.jsx`, `GamePage.jsx`): 
  - Se enfocan en la UI y el estado de la interfaz
  - Renderizan componentes y manejan interacciones del usuario

- **`api.js`**: 
  - Se enfoca exclusivamente en la comunicación con el backend
  - Maneja URLs, headers, errores HTTP y transformación de datos

**Ejemplo:**
```javascript
// Componente React - solo se preocupa por UI
function App() {
  const [engines, setEngines] = useState([]);
  
  useEffect(() => {
    fetchEngines()  // ← Llamada simple y clara
      .then(setEngines)
      .catch(console.error);
  }, []);
  
  return <div>{/* UI */}</div>;
}
```

### 2. **Reutilización de Código**

Una función definida una vez puede ser usada en múltiples componentes:

```javascript
// api.js - definido una sola vez
export const fetchEngines = async () => { ... }
export const fetchBestMove = async (engine, fen, depth) => { ... }

// App.jsx - usa fetchEngines
import { fetchEngines } from './api';

// GamePage.jsx - usa fetchBestMove
import { fetchBestMove } from './api';

// SettingsPage.jsx (futuro) - puede usar ambas
import { fetchEngines, fetchBestMove } from './api';
```

**Sin `api.js`**, tendrías que copiar y pegar el código de `fetch` en cada componente que lo necesite.

### 3. **Mantenibilidad Mejorada**

**Escenario 1: Cambio de URL del backend**

Con `api.js`:
```javascript
// Solo modificas api.js
export const getBackendUrl = () => {
  return 'https://nuevo-backend.com';  // ← Un solo cambio
};
```

Sin `api.js`:
```javascript
// Tienes que buscar y cambiar en TODOS los componentes:
// App.jsx
const backendUrl = 'https://nuevo-backend.com';  // ← Cambio 1

// GamePage.jsx  
const backendUrl = 'https://nuevo-backend.com';  // ← Cambio 2

// SettingsPage.jsx
const backendUrl = 'https://nuevo-backend.com';  // ← Cambio 3
// ... y así en cada archivo
```

**Escenario 2: Cambio en el formato de respuesta**

Si el backend cambia de `{engines: []}` a `{data: {engines: []}}`:

Con `api.js`:
```javascript
// Solo modificas api.js
export const fetchEngines = async () => {
  const data = await response.json();
  return data.data.engines;  // ← Un solo cambio
};
```

Sin `api.js`: Tienes que modificar cada componente que usa `fetchEngines`.

### 4. **Testing Más Fácil**

Con `api.js`, puedes probar la comunicación con el backend de forma aislada:

```javascript
// test/api.test.js
import { fetchEngines } from '../api';

describe('fetchEngines', () => {
  it('debe retornar array de motores', async () => {
    const engines = await fetchEngines();
    expect(Array.isArray(engines)).toBe(true);
  });
});
```

Sin `api.js`, tendrías que:
- Montar componentes React completos
- Simular eventos del usuario
- Verificar que el estado se actualiza correctamente
- Todo esto solo para probar una llamada HTTP

### 5. **Consistencia**

Todas las llamadas al backend siguen el mismo patrón:

- ✅ Mismo manejo de errores
- ✅ Mismo formato de URLs
- ✅ Mismos headers
- ✅ Mismo logging
- ✅ Misma transformación de datos

**Ejemplo de consistencia:**
```javascript
// Todas las funciones siguen el mismo patrón
export const fetchEngines = async () => {
  const backendUrl = getBackendUrl();  // ← Misma función
  const response = await fetch(`${backendUrl}/engines`);  // ← Mismo patrón
  // ... mismo manejo de errores
};

export const fetchBestMove = async (engine, fen, depth) => {
  const backendUrl = getBackendUrl();  // ← Misma función
  const response = await fetch(`${backendUrl}/move`, {  // ← Mismo patrón
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },  // ← Mismos headers
  });
  // ... mismo manejo de errores
};
```

### 6. **Manejo Centralizado de Errores**

Todos los errores de comunicación se manejan en un solo lugar:

```javascript
// api.js - manejo de errores consistente
catch (error) {
  console.error('❌ Error al obtener motores del backend:', error);
  if (error.message.includes('Failed to fetch')) {
    console.error('💡 Posible problema de conexión...');
  }
  throw error;  // El componente decide qué hacer con el error
}
```

Esto permite:
- Logging consistente en todos los errores
- Mensajes de error más informativos
- Debugging más fácil

### 7. **Funciones Utilitarias Compartidas**

Funciones como `getBackendUrl()` pueden ser reutilizadas:

```javascript
// api.js
export const getBackendUrl = () => {
  // Lógica compleja para detectar entorno
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  return `${window.location.protocol}//${window.location.hostname}:8000`;
};

// Todas las funciones usan la misma lógica
export const fetchEngines = async () => {
  const backendUrl = getBackendUrl();  // ← Reutiliza la función
  // ...
};

export const fetchBestMove = async (...) => {
  const backendUrl = getBackendUrl();  // ← Reutiliza la función
  // ...
};
```

---

## 📋 Estructura de `api.js`

El módulo `api.js` contiene:

### Funciones Principales:

1. **`getBackendUrl()`**: Calcula la URL del backend según el entorno (desarrollo/producción)
2. **`fetchEngines()`**: Obtiene la lista de motores disponibles
3. **`fetchBestMove()`**: Solicita el mejor movimiento de un motor
4. **`checkBackendHealth()`**: Verifica el estado del backend

### Características:

- ✅ **Detección automática de entorno**: Desarrollo vs Producción
- ✅ **Logging detallado**: Facilita debugging
- ✅ **Manejo robusto de errores**: Errores informativos y manejables
- ✅ **Validación de respuestas**: Verifica formato antes de retornar
- ✅ **Soporte para opciones avanzadas**: Parámetros para motores generativos

---

## 🔄 Comparación: Con vs Sin `api.js`

### Sin `api.js` (Menos Organizado):

```javascript
// App.jsx
useEffect(() => {
  const backendUrl = window.location.origin.replace(':5173', ':8000');
  fetch(`${backendUrl}/engines`)
    .then(response => {
      if (!response.ok) throw new Error('HTTP error');
      return response.json();
    })
    .then(data => {
      if (!data.engines) throw new Error('Formato inválido');
      setAvailableEngines(data.engines);
    })
    .catch(error => {
      console.error('Error:', error);
      setAvailableEngines([]);
    });
}, []);

// GamePage.jsx - CÓDIGO DUPLICADO
const makeEngineMove = async (engineName) => {
  const backendUrl = window.location.origin.replace(':5173', ':8000');  // ← Duplicado
  fetch(`${backendUrl}/move`, {  // ← Lógica duplicada
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ engine: engineName, fen: game.fen(), depth: 10 }),
  })
    .then(response => {
      if (!response.ok) throw new Error('HTTP error');  // ← Duplicado
      return response.json();
    })
    .then(data => {
      if (!data.bestmove) throw new Error('Sin movimiento');  // ← Duplicado
      // ...
    })
    .catch(error => {
      console.error('Error:', error);  // ← Duplicado
    });
};
```

**Problemas:**
- ❌ Código duplicado en múltiples componentes
- ❌ Dificulta cambios (hay que modificar varios archivos)
- ❌ Lógica de negocio mezclada con UI
- ❌ Difícil de testear

### Con `api.js` (Mejor Organizado):

```javascript
// api.js - Un solo lugar para toda la lógica
export const fetchEngines = async () => { /* ... */ };
export const fetchBestMove = async (engine, fen, depth) => { /* ... */ };

// App.jsx - Simple y claro
import { fetchEngines } from './api';

useEffect(() => {
  fetchEngines()
    .then(setAvailableEngines)
    .catch(console.error);
}, []);

// GamePage.jsx - Simple y claro
import { fetchBestMove } from './api';

const makeEngineMove = async (engineName) => {
  const data = await fetchBestMove(engineName, game.fen(), 10);
  // ...
};
```

**Ventajas:**
- ✅ Código reutilizable
- ✅ Fácil de mantener (un solo lugar para cambios)
- ✅ Separación clara de responsabilidades
- ✅ Fácil de testear

---

## 🎓 Principios de Diseño Aplicados

### 1. **DRY (Don't Repeat Yourself)**
Evita duplicación de código: la lógica de comunicación está en un solo lugar.

### 2. **Single Responsibility Principle**
Cada módulo tiene una responsabilidad única:
- `api.js`: Comunicación con backend
- Componentes React: UI y estado

### 3. **Separation of Concerns**
Separación clara entre:
- Lógica de negocio (comunicación API)
- Lógica de presentación (React)

### 4. **Abstraction**
Los componentes React no necesitan saber los detalles de cómo se construyen las URLs o se manejan los errores HTTP.

---

## 📝 Resumen

La adición de `api.js` mejora significativamente la calidad del código del frontend:

- ✅ **Organización**: Código más limpio y estructurado
- ✅ **Mantenibilidad**: Cambios centralizados y fáciles
- ✅ **Reutilización**: Funciones compartidas entre componentes
- ✅ **Testing**: Pruebas más simples y aisladas
- ✅ **Consistencia**: Mismo patrón en todas las llamadas API
- ✅ **Escalabilidad**: Fácil añadir nuevas funciones API

Este patrón es una **buena práctica** ampliamente utilizada en aplicaciones React profesionales y sigue los principios de diseño de software moderno.

---

**Fecha de adición**: 2025  
**Archivo**: `frontend/src/api.js`  
**Relacionado con**: Integración Frontend-Backend

