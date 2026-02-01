#!/bin/bash

echo "=== Stripe 配置检查工具 ==="
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ .env 文件不存在"
    echo "   请先创建 .env 文件或运行 ./setup_stripe.sh"
    exit 1
fi

echo "✅ .env 文件存在"
echo ""

# 检查关键配置项
MISSING=0

echo "1. 检查关键配置项："
echo ""

# 检查 STRIPE_SECRET_KEY
STRIPE_KEY=$(grep "^STRIPE_SECRET_KEY=" .env 2>/dev/null | cut -d'=' -f2- | tr -d ' ')
if [ -z "$STRIPE_KEY" ]; then
    echo "   ❌ STRIPE_SECRET_KEY: 未找到"
    MISSING=$((MISSING+1))
elif echo "$STRIPE_KEY" | grep -qE "请替换|your_secret_key|sk_test_\$|sk_test_xxx"; then
    echo "   ⚠️  STRIPE_SECRET_KEY: 还是占位符"
    echo "      当前值: $STRIPE_KEY"
    echo "      请替换为真实的 Stripe 测试密钥"
    echo "      获取地址: https://dashboard.stripe.com/test/apikeys"
    MISSING=$((MISSING+1))
elif [[ ! $STRIPE_KEY =~ ^sk_test_ ]]; then
    echo "   ⚠️  STRIPE_SECRET_KEY: 格式可能不正确（应该以 sk_test_ 开头）"
    echo "      当前值: ${STRIPE_KEY:0:20}..."
    MISSING=$((MISSING+1))
else
    echo "   ✅ STRIPE_SECRET_KEY: 已配置"
    echo "      密钥长度: ${#STRIPE_KEY} 字符"
    echo "      密钥前缀: ${STRIPE_KEY:0:20}..."
fi

# 检查 FRONTEND_URL
FRONTEND_URL=$(grep "^FRONTEND_URL=" .env 2>/dev/null | cut -d'=' -f2-)
if [ -z "$FRONTEND_URL" ]; then
    echo "   ⚠️  FRONTEND_URL: 未设置（将使用默认值）"
else
    echo "   ✅ FRONTEND_URL: $FRONTEND_URL"
fi

# 检查 DATABASE_URL
DATABASE_URL=$(grep "^DATABASE_URL=" .env 2>/dev/null | cut -d'=' -f2-)
if [ -z "$DATABASE_URL" ]; then
    echo "   ⚠️  DATABASE_URL: 未设置（将使用默认值）"
else
    echo "   ✅ DATABASE_URL: $DATABASE_URL"
fi

echo ""
echo "2. 检查 Docker Compose 配置："

if ! docker-compose config >/dev/null 2>&1; then
    echo "   ❌ docker-compose.yml 配置有误"
    MISSING=$((MISSING+1))
else
    echo "   ✅ docker-compose.yml 配置有效"
    
    # 检查环境变量引用
    ENV_REF=$(docker-compose config 2>/dev/null | grep -E "STRIPE_SECRET_KEY" | head -1)
    if echo "$ENV_REF" | grep -q "\${STRIPE_SECRET_KEY"; then
        echo "   ✅ 环境变量引用正确"
    else
        echo "   ⚠️  环境变量引用可能有问题"
    fi
fi

echo ""
echo "3. 检查服务状态："

if docker-compose ps api 2>/dev/null | grep -q "Up"; then
    echo "   ✅ API 服务正在运行"
    
    # 检查容器内的环境变量
    CONTAINER_KEY=$(docker-compose exec -T api sh -c 'echo $STRIPE_SECRET_KEY' 2>/dev/null | tr -d '\r\n')
    if [ -n "$CONTAINER_KEY" ] && [ "$CONTAINER_KEY" != "sk_test_xxx" ] && [ ${#CONTAINER_KEY} -gt 10 ]; then
        echo "   ✅ API 容器已加载 Stripe 密钥"
        echo "      容器内密钥前缀: ${CONTAINER_KEY:0:20}..."
    elif [ "$CONTAINER_KEY" = "sk_test_xxx" ] || [ -z "$CONTAINER_KEY" ]; then
        echo "   ⚠️  API 容器未加载正确的 Stripe 密钥"
        echo "      需要重启服务: docker-compose down && docker-compose up -d"
    fi
else
    echo "   ⚠️  API 服务未运行"
    echo "      启动服务: docker-compose up -d"
fi

echo ""
echo "=== 检查结果 ==="
if [ $MISSING -eq 0 ]; then
    echo "✅ 配置检查通过！"
    echo ""
    echo "如果刚修改了配置，请重启服务："
    echo "  docker-compose down && docker-compose up -d"
    echo ""
    echo "然后可以测试 Stripe 功能："
    echo "  curl -X POST http://localhost:8000/api/v1/stripe/create-checkout-session \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"tier\": \"basic\"}'"
    exit 0
else
    echo "⚠️  发现 $MISSING 个配置问题"
    echo ""
    echo "请按照以下步骤修复："
    echo "1. 获取 Stripe 密钥: https://dashboard.stripe.com/test/apikeys"
    echo "2. 编辑 .env 文件，设置 STRIPE_SECRET_KEY"
    echo "3. 重启服务: docker-compose down && docker-compose up -d"
    exit 1
fi

