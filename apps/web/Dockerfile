FROM node:20-alpine AS builder

WORKDIR /app

# Allow npm registry override to avoid network timeouts
ARG NPM_CONFIG_REGISTRY=https://registry.npmmirror.com
ENV NPM_CONFIG_REGISTRY=${NPM_CONFIG_REGISTRY}

# 复制 package 文件
COPY package*.json ./

# 安装所有依赖（包括 devDependencies，用于构建）
RUN npm ci

# 复制应用代码
COPY . .

# 构建生产版本
# 注意：NEXT_PUBLIC_API_BASE_URL 需要在构建时设置（通过 build args），会被嵌入到客户端代码中
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

RUN npm run build

# 生产阶段
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ARG NPM_CONFIG_REGISTRY=https://registry.npmmirror.com
ENV NPM_CONFIG_REGISTRY=${NPM_CONFIG_REGISTRY}

# 只安装生产依赖
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 从构建阶段复制构建产物
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.js ./
# 复制 public 目录（如果存在）
COPY --from=builder /app/public ./public

# 暴露端口
EXPOSE 3000

# 启动生产服务器
CMD ["npm", "start"]

