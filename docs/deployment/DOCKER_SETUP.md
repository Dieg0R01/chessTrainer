# Docker Setup - Chess Trainer

Esta guía explica cómo usar Docker para ejecutar Chess Trainer con todos los motores incluidos.

---

## 🚀 Inicio Rápido

### 1. Construir la imagen

```bash
docker-compose build
```

O manualmente:

```bash
docker build -t chess-trainer .
```

### 2. Iniciar el contenedor

```bash
docker-compose up -d
```

O manualmente:

```bash
docker run -d \
  --name chess-trainer \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/weights:/app/weights:rw \
  chess-trainer
```

### 3. Verificar que funciona

```bash
curl http://localhost:8000/health
```

O abre en el navegador: http://localhost:8000

---

## 📦 Motores Incluidos

El Dockerfile instala automáticamente:

- **Stockfish**: Motor tradicional más fuerte del mundo
- **Lc0**: Motor neuronal Leela Chess Zero

Ambos están disponibles en `/app/bin/` dentro del contenedor y en el PATH.

---

## 🧠 Añadir Redes Neuronales

### Opción 1: Montar carpeta local

1. Crea una carpeta `weights/` en tu proyecto:
   ```bash
   mkdir -p weights
   ```

2. Descarga las redes que quieras (ver `docs/deployment/FUENTES_MOTORES.md`):
   ```bash
   cd weights
   wget https://lczero.org/networks/weights/T80-3010.pb.gz
   wget https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1500.pb.gz
   ```

3. El `docker-compose.yml` ya monta esta carpeta, así que las redes estarán disponibles en `/app/weights/` dentro del contenedor.

### Opción 2: Copiar al contenedor

```bash
docker cp weights/maia-1500.pb.gz chess-trainer:/app/weights/
```

---

## ⚙️ Configuración

### Editar configuración de motores

1. Edita `config/engines_local.yaml` en tu máquina local.
2. El archivo se monta como volumen de solo lectura (`:ro`), así que los cambios se reflejarán al reiniciar el contenedor.
3. O usa el endpoint `/reload` para recargar sin reiniciar.

### Variables de entorno

Edita `docker-compose.yml` para añadir variables de entorno:

```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

Y crea un archivo `.env` en la raíz:

```
OPENAI_API_KEY=tu_key_aqui
ANTHROPIC_API_KEY=tu_key_aqui
```

---

## 🔍 Ver Logs

```bash
docker-compose logs -f
```

O:

```bash
docker logs -f chess-trainer
```

---

## 🛑 Detener el contenedor

```bash
docker-compose down
```

O:

```bash
docker stop chess-trainer
docker rm chess-trainer
```

---

## 🔄 Reconstruir después de cambios

Si cambias el código o la configuración:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Los motores no aparecen como disponibles

1. Verifica que los binarios están en el contenedor:
   ```bash
   docker exec chess-trainer ls -la /app/bin/
   ```

2. Verifica que son ejecutables:
   ```bash
   docker exec chess-trainer /app/bin/stockfish --version
   docker exec chess-trainer /app/bin/lc0 --version
   ```

3. Revisa los logs del backend:
   ```bash
   docker logs chess-trainer | grep -i "motor\|engine\|error"
   ```

### El contenedor no inicia

1. Verifica que el puerto 8000 no está en uso:
   ```bash
   lsof -i :8000
   ```

2. Revisa los logs:
   ```bash
   docker-compose logs
   ```

### Las redes neuronales no cargan

1. Verifica que el archivo existe en el contenedor:
   ```bash
   docker exec chess-trainer ls -la /app/weights/
   ```

2. Verifica que la ruta en `engines_local.yaml` es correcta:
   ```yaml
   weights: "weights/maia-1500.pb.gz"  # Relativa a /app
   ```

---

## 📚 Más Información

- Ver `docs/deployment/FUENTES_MOTORES.md` para fuentes de descarga de motores y redes.
- Ver `docs/deployment/DESPLIEGUE.md` para información general de despliegue.

