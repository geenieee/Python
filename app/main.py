"""
FastAPI 애플리케이션 초기화 및 라우터 등록
"""
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import (
    SECRET_KEY, 
    SESSION_MAX_AGE, 
    SESSION_COOKIE_NAME,
    SESSION_SAME_SITE,
    SESSION_HTTPS_ONLY
)
from app.routers import home, ldap_config, ldap_search, unlock


def create_app() -> FastAPI:
    """FastAPI 앱 생성 및 설정"""
    app = FastAPI(
        title="Python Web Server",
        description="FastAPI 기반 AD 관리 도구",
        version="1.0.0"
    )
    
    # 세션 미들웨어 추가
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        max_age=SESSION_MAX_AGE,
        session_cookie=SESSION_COOKIE_NAME,
        same_site=SESSION_SAME_SITE,
        https_only=SESSION_HTTPS_ONLY,
        path="/"
    )
    
    # 라우터 등록
    app.include_router(home.router)
    app.include_router(ldap_config.router)
    app.include_router(ldap_search.router)
    app.include_router(unlock.router)
    
    return app


# 앱 인스턴스 생성
app = create_app()
