#!/bin/bash

echo "🚀 Starting HispanoComply..."

# 检查 .env 文件
if [ ! -f "apps/api/.env" ]; then
    echo "⚠️  apps/api/.env not found, copying from .env.example"
    cp apps/api/.env.example apps/api/.env
    echo "📝 Please edit apps/api/.env and add your Stripe keys"
fi

# 启动 Docker Compose
echo "🐳 Starting Docker Compose..."
docker-compose up --build

