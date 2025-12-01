# 🚀 Instrucciones Rápidas para Compilar Lc0

## Opción Rápida: Compilación Manual (Recomendada)

El script ya está copiado en el contenedor. Solo ejecuta:

```bash
docker exec chess-trainer /app/scripts/build_lc0.sh
```

**⏱️ Tiempo**: 10-30 minutos (depende de tu CPU)

---

## Verificar que Funciona

```bash
# 1. Verificar que el binario existe
docker exec chess-trainer ls -lh /app/bin/lc0

# 2. Recargar configuración
curl -X POST http://localhost:8000/reload

# 3. Verificar en el frontend
# Abre http://localhost:5173 y verifica que lc0-local aparece disponible
```

---

## Si el Script No Está en el Contenedor

```bash
# Copiar el script
docker exec chess-trainer mkdir -p /app/scripts
docker cp scripts/build_lc0.sh chess-trainer:/app/scripts/build_lc0.sh
docker exec chess-trainer chmod +x /app/scripts/build_lc0.sh

# Ejecutar
docker exec chess-trainer /app/scripts/build_lc0.sh
```

---

## Documentación Completa

Para más detalles, ver: `docs/deployment/COMPILAR_LC0.md`

