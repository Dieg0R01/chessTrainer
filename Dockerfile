# Usar una imagen base de Python para el backend
FROM python:3.10-slim-buster as backend-builder

WORKDIR /app

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY main.py .
COPY engine_manager.py .
COPY config/ /app/config/

# Usar una imagen base de Node.js para construir el frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copiar y instalar dependencias de Node.js
COPY frontend/package*.json ./
RUN npm install

# Copiar el código del frontend y construirlo
COPY frontend/src /app/frontend/src
COPY frontend/public /app/frontend/public
RUN npm run build

# Etapa final: construir la imagen de producción
FROM python:3.10-slim-buster

WORKDIR /app

# Copiar las dependencias de Python de la etapa backend-builder
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copiar el código del backend
COPY --from=backend-builder /app/main.py /app/main.py
COPY --from=backend-builder /app/engine_manager.py /app/engine_manager.py
COPY --from=backend-builder /app/config/ /app/config/

# Copiar los archivos estáticos del frontend desde la etapa frontend-builder
COPY --from=frontend-builder /app/frontend/dist /app/static

# Exponer el puerto que usará FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación (usando Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
