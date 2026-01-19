"""
홈 페이지 라우터
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.styles import COMMON_STYLES, get_top_nav

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    """메인 페이지"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python Web Server</title>
        <style>
            {COMMON_STYLES}
            .hero {{
                text-align: center;
                padding: 60px 20px;
            }}
            .hero h1 {{
                font-size: 3rem;
                margin-bottom: 15px;
                background: linear-gradient(90deg, #00d2ff, #3a7bd5, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .hero .description {{
                font-size: 1.2rem;
                color: #888;
                margin-bottom: 50px;
            }}
            .feature-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .feature-card {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 30px;
                text-align: center;
                transition: all 0.3s ease;
                text-decoration: none;
                color: inherit;
            }}
            .feature-card:hover {{
                background: rgba(0, 210, 255, 0.1);
                border-color: rgba(0, 210, 255, 0.3);
                transform: translateY(-5px);
            }}
            .feature-card .icon {{
                font-size: 2.5rem;
                margin-bottom: 15px;
            }}
            .feature-card h3 {{
                color: #00d2ff;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }}
            .feature-card p {{
                color: #888;
                font-size: 0.9rem;
                line-height: 1.5;
            }}
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                background: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.4);
                border-radius: 20px;
                color: #4caf50;
                font-size: 0.85rem;
                margin-bottom: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {get_top_nav("home")}
            
            <div class="hero">
                <h1>🐍 Python Web Server</h1>
                <p class="description">FastAPI 기반 AD 관리 도구</p>
                <div class="status-badge">✅ 서버가 정상적으로 실행 중입니다</div>
            </div>
            
            <div class="feature-cards">
                <a href="/ldapinfo" class="feature-card">
                    <div class="icon">⚙️</div>
                    <h3>LDAP 설정</h3>
                    <p>AD 서버 연결 정보를 설정합니다. 세션 동안 설정이 유지됩니다.</p>
                </a>
                <a href="/ldap" class="feature-card">
                    <div class="icon">📋</div>
                    <h3>AD 조회</h3>
                    <p>Active Directory 사용자 계정의 상세 정보를 조회합니다.</p>
                </a>
                <a href="/unlock-account" class="feature-card">
                    <div class="icon">🔓</div>
                    <h3>잠금 해제</h3>
                    <p>잠긴 AD 계정을 확인하고 잠금을 해제합니다.</p>
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/api/health")
async def health_check():
    """헬스 체크 API"""
    return {"status": "healthy", "message": "서버가 정상 작동 중입니다"}


@router.get("/api/hello/{name}")
async def say_hello(name: str):
    """인사 API"""
    return {"message": f"안녕하세요, {name}님!"}
