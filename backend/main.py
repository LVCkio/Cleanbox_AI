"""
CleanInbox AI — FastAPI Main Application Entry Point
Tổng hợp tất cả routers và khởi tạo ứng dụng.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from datetime import timedelta

from backend.config import settings
from backend.database import engine, Base
from backend.auth.jwt_handler import (
    create_access_token, verify_password, get_password_hash,
    Token
)
from backend.routers import api_gateway, fatigue, ethical_ux, esg
import backend.models  # noqa: F401 — đăng ký tất cả models với Base.metadata


# ─── Lifecycle: Tạo DB tables khi khởi động ─────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: tạo tất cả tables nếu chưa tồn tại
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database tables initialized")
    yield
    # Shutdown
    await engine.dispose()
    print("[INFO] Database connection closed")


# ─── FastAPI App ─────────────────────────────────────
app = FastAPI(
    title="CleanInbox AI API",
    description="""
## 🌱 CleanInbox AI — Email Marketing Optimization Middleware

**4 Core Modules:**
- **API Gateway**: Kết nối Mailchimp / HubSpot / SendGrid
- **Fatigue Intelligence**: Tính Brand Fatigue Score (BFS) bằng AI
- **Ethical UX Manager**: Snooze & Unsubscribe văn minh
- **ESG Reporter**: Đo lường CO2 & báo cáo phát triển bền vững

**Tuân thủ:** Nghị định 13/2023/NĐ-CP | GHG Protocol Scope 3
    """,
    version="1.0.0-MVP",
    lifespan=lifespan,
)

# ─── Middleware ──────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include Routers ─────────────────────────────────
app.include_router(api_gateway.router)
app.include_router(fatigue.router)
app.include_router(ethical_ux.router)
app.include_router(esg.router)


# ─── Auth Endpoints ──────────────────────────────────
# Mock user store (TODO: thay bằng DB query)
MOCK_USERS = {
    "admin@cleaninbox.ai": {
        "org_id": "00000000-0000-0000-0000-000000000001",
        "hashed_password": get_password_hash("demo1234"),
    }
}

@app.post("/api/v1/auth/token", response_model=Token, tags=["🔐 Xác Thực"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Đăng nhập và nhận JWT token.
    Tài khoản demo: admin@cleaninbox.ai / demo1234
    """
    user = MOCK_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": form_data.username, "org_id": user["org_id"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ─── Health Check ────────────────────────────────────
@app.get("/health", tags=["⚙️ Hệ Thống"])
async def health_check():
    """Kiểm tra tình trạng hệ thống"""
    return {
        "status": "healthy",
        "version": "1.0.0-MVP",
        "environment": settings.ENVIRONMENT,
        "modules": ["api_gateway", "fatigue_intelligence", "ethical_ux", "esg_reporter"],
    }

@app.get("/", tags=["⚙️ Hệ Thống"])
async def root():
    """Trang chủ API"""
    return {"message": "🌱 CleanInbox AI API — Tài liệu tại /docs"}
