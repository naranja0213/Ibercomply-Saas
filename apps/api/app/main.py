from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import os
import time
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from app.api.v1.routes import risk, stripe, compliance, payment, assessments
from app.database import init_db, Base, engine
# 确保所有模型都被导入，以便 SQLAlchemy 创建表
from app.models import PaymentSession, Assessment

# Sentry 初始化（无 DSN 时不启用）
_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        environment=os.getenv("SENTRY_ENV", os.getenv("ENVIRONMENT", "local")),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
        send_default_pii=False,
        integrations=[FastApiIntegration(), StarletteIntegration()],
    )

app = FastAPI(
    title="HispanoComply API",
    description="西班牙华人 Autónomo 合规风险评估 API",
    version="2.0.0"
)

# 简易限流（内存级，单实例使用）
_rate_bucket = {}
_rate_window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
_rate_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "120"))

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    # 创建所有表
    Base.metadata.create_all(bind=engine)

# 限流中间件（生产建议替换为 Redis/网关）
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    # 跳过健康检查与文档
    if path in ("/health", "/docs", "/openapi.json", "/"):
        return await call_next(request)
    if not path.startswith("/api/"):
        return await call_next(request)

    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    key = f"{client_ip}:{path}"
    now = time.time()
    window = _rate_window_seconds
    max_requests = _rate_max_requests

    timestamps = _rate_bucket.get(key, [])
    timestamps = [t for t in timestamps if now - t < window]
    if len(timestamps) >= max_requests:
        return JSONResponse(
            status_code=429,
            content={"detail": "请求过于频繁，请稍后再试。"},
        )
    timestamps.append(now)
    _rate_bucket[key] = timestamps

    return await call_next(request)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["risk"])  # 保留旧接口以兼容
app.include_router(stripe.router, prefix="/api/v1/stripe", tags=["stripe"])
app.include_router(payment.router, prefix="/api/v1/payment", tags=["payment"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])


@app.get("/")
async def root():
    return {
        "message": "HispanoComply API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

