# Windows PowerShell 启动脚本
Write-Host "🚀 Starting HispanoComply..." -ForegroundColor Green

# 检查 .env 文件
if (-not (Test-Path "apps/api/.env")) {
    Write-Host "⚠️  apps/api/.env not found, copying from .env.example" -ForegroundColor Yellow
    Copy-Item "apps/api/.env.example" "apps/api/.env"
    Write-Host "📝 Please edit apps/api/.env and add your Stripe keys" -ForegroundColor Yellow
}

# 启动 Docker Compose
Write-Host "🐳 Starting Docker Compose..." -ForegroundColor Cyan
docker compose up --build -d

Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "🔌 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

