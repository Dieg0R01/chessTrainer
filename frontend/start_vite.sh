#!/bin/bash
# Script wrapper para iniciar Vite de manera persistente
cd "$(dirname "$0")"
exec npm run dev -- --host

