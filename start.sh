#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando Configuración de Business Backend...${NC}"

# 1. Configurar Entorno
echo -e "\n${YELLOW}1. Verificando archivo .env...${NC}"
if [ ! -f .env ]; then
    echo "Copiando .env.dev a .env..."
    cp .env.dev .env
    echo -e "${GREEN}✅ Archivo .env creado.${NC}"
    echo "⚠️  NOTA: Recuerda editar .env si necesitas cambiar las API keys de OpenAI."
else
    echo -e "${GREEN}✅ Archivo .env ya existe.${NC}"
fi

# 2. Base de Datos
echo -e "\n${YELLOW}2. Iniciando Base de Datos (Docker)...${NC}"
CONTAINER_NAME="business_backend_db"

# Check if container exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🔄 El contenedor ${CONTAINER_NAME} existe. Iniciándolo..."
    if docker start "$CONTAINER_NAME"; then
        echo -e "${GREEN}✅ Base de datos iniciada.${NC}"
    else
        echo "❌ Error iniciando el contenedor existente."
        exit 1
    fi
else
    echo "🆕 Creando e iniciando contenedor de base de datos..."
    if docker run -d \
        --name "$CONTAINER_NAME" \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=app \
        -p 5432:5432 \
        -v postgres_data:/var/lib/postgresql/data \
        pgvector/pgvector:pg16; then
        echo -e "${GREEN}✅ Base de datos creada e iniciada.${NC}"
    else
        echo "❌ Error ejecutando docker run."
        exit 1
    fi
fi

# Esperar a que PG esté listo (simple sleep por compatibilidad)
echo "⏳ Esperando a que la base de datos acepte conexiones..."
sleep 3

# 3. Dependencias
echo -e "\n${YELLOW}3. Instalando Dependencias (Poetry)...${NC}"

# Asegurar que Poetry está en el PATH (para instalaciones recientes)
export PATH="/home/pablo/.local/bin:$PATH"

if command -v poetry &> /dev/null; then
    if poetry install --no-root; then
        echo -e "${GREEN}✅ Dependencias instaladas.${NC}"
    else
        echo "❌ Error instalando dependencias via Poetry."
        exit 1
    fi
else
    echo "❌ Poetry no está instalado o no se encuentra en el PATH."
    echo "ℹ️  Puedes instalarlo con: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# 4. Ejecutar Aplicación
echo -e "\n${BLUE}====================================================${NC}"
echo -e "${GREEN}🎉 Todo listo! Iniciando servidor...${NC}"
echo -e "   - GraphQL UI: http://localhost:9000/graphql"
echo -e "   - API Docs:   http://localhost:9000/docs"
echo -e "${BLUE}====================================================${NC}"

# Configurar PYTHONPATH para que encuentre el módulo 'business_backend'
export PYTHONPATH=$PYTHONPATH:$(pwd)/..

# Ejecutar el comando defined en el README
poetry run python -m business_backend.main --port 9000
