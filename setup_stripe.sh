#!/bin/bash

echo "=== Stripe 配置助手 ==="
echo ""
echo "请按照以下步骤获取 Stripe 测试密钥："
echo ""
echo "1. 访问: https://dashboard.stripe.com/test/apikeys"
echo "2. 确保在 Test mode（测试模式，不是 Live mode）"
echo "3. 复制 Secret key（格式: sk_test_...）"
echo ""
read -p "请输入你的 Stripe Secret Key (sk_test_...): " STRIPE_KEY

if [ -z "$STRIPE_KEY" ]; then
    echo "错误：密钥不能为空"
    exit 1
fi

if [[ ! $STRIPE_KEY =~ ^sk_test_ ]]; then
    echo "警告：密钥格式看起来不正确（应该以 sk_test_ 开头）"
    read -p "是否继续？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

# 创建或更新 .env 文件
cat > .env << ENVEOF
# Stripe 配置
STRIPE_SECRET_KEY=$STRIPE_KEY

# Stripe 价格 ID（可选，不设置会自动使用一次性价格）
STRIPE_PRICE_BASIC=
STRIPE_PRICE_EXPERT=

# Stripe Webhook Secret（可选）
STRIPE_WEBHOOK_SECRET=

# 前端 URL
FRONTEND_URL=http://localhost:3001

# 数据库配置
DATABASE_URL=sqlite:///./payments.db

# API Base URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENVEOF

echo ""
echo "✅ .env 文件已创建/更新"
echo ""
echo "下一步："
echo "1. 运行: docker-compose down"
echo "2. 运行: docker-compose up -d"
echo ""
