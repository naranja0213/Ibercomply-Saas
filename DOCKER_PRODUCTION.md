# Docker 生产环境部署指南

本项目已完全 Docker 化，所有代码打包在镜像中，不再依赖 volumes 挂载。

## 🐳 构建和启动

### 1. 构建镜像

```bash
# 构建所有服务
docker-compose build

# 或强制重建（清除缓存）
docker-compose build --no-cache
```

### 2. 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f api
```

### 3. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除 volumes（如果有）
docker-compose down -v
```

## 🔧 环境变量配置

### 后端环境变量

在 `docker-compose.yml` 中配置，或创建 `.env` 文件：

```bash
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PRICE_BASIC=price_xxx
STRIPE_PRICE_EXPERT=price_xxx
FRONTEND_URL=http://localhost:3001
```

### 前端环境变量

通过 `docker-compose.yml` 的 `build.args` 传递：

```yaml
web:
  build:
    args:
      - NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

或在项目根目录创建 `.env` 文件：

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 📱 访问地址

- 前端：http://localhost:3001
- API 文档：http://localhost:8000/docs
- API 健康检查：http://localhost:8000/health

## 🔍 验证部署

### 检查容器状态

```bash
docker-compose ps
```

应该看到两个服务都是 `Up` 状态。

### 测试 API

```bash
curl http://localhost:8000/health
# 应该返回: {"status":"ok"}

curl http://localhost:8000/api/v1/compliance/assess \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"industry":"bazar","monthly_income":3000,"employee_count":0,"has_pos":true}'
```

### 测试前端

在浏览器中访问 http://localhost:3001，应该能看到前端页面。

## 🏗️ 构建说明

### 前端构建流程

1. **构建阶段 (builder)**:
   - 安装所有依赖（包括 devDependencies）
   - 复制源代码
   - 设置 `NEXT_PUBLIC_API_BASE_URL` 环境变量
   - 运行 `npm run build` 构建生产版本

2. **运行阶段 (runner)**:
   - 只安装生产依赖
   - 复制构建产物（`.next` 目录）
   - 运行 `npm start` 启动生产服务器

### 后端构建流程

1. 安装系统依赖（curl）
2. 安装 Python 依赖
3. 复制应用代码
4. 运行 `uvicorn` 生产服务器（无 `--reload`）

## ⚠️ 注意事项

1. **代码修改**：修改代码后需要重新构建镜像才能生效
   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. **环境变量**：`NEXT_PUBLIC_*` 变量需要在构建时设置（通过 build args），不能在运行时更改

3. **生产部署**：生产环境建议使用 Docker Swarm 或 Kubernetes，并配置反向代理（Nginx/Traefik）

4. **数据持久化**：当前配置不包含数据库，如需持久化数据，需要添加 volumes 或使用外部数据库服务

## 🔄 从开发模式迁移

如果你之前使用开发模式（带 volumes），现在迁移到完全 Docker 化：

1. 停止旧的容器：`docker-compose down`
2. 构建新镜像：`docker-compose build`
3. 启动新容器：`docker-compose up -d`

注意：代码修改后需要重新构建镜像。

