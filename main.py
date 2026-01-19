from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
from typing import Optional
import os
import secrets

app = FastAPI(
    title="Python Web Server",
    description="FastAPI 기반 웹 서버",
    version="1.0.0"
)

# 세션 미들웨어 추가 (세션 암호화를 위한 비밀키)
# 고정된 비밀키 사용 (서버 재시작 시에도 세션 유지)
# 운영 환경에서는 반드시 환경변수로 안전한 키를 설정하세요
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-12345")
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY, 
    max_age=3600,  # 1시간 세션 유지
    session_cookie="ldap_session",  # 세션 쿠키 이름
    same_site="lax",  # CSRF 보호
    https_only=False,  # 개발 환경에서는 False (운영에서는 True 권장)
    path="/"  # 모든 경로에서 세션 공유
)


# 공통 CSS 스타일
COMMON_STYLES = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Pretendard', 'Noto Sans KR', -apple-system, sans-serif;
    min-height: 100vh;
    background: linear-gradient(145deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #e0e0e0;
    padding: 40px 20px;
}
.container {
    max-width: 900px;
    margin: 0 auto;
}
h1 {
    text-align: center;
    font-size: 2.2rem;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #00d2ff, #3a7bd5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.subtitle {
    text-align: center;
    color: #888;
    margin-bottom: 40px;
    font-size: 0.95rem;
}
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 30px;
    backdrop-filter: blur(10px);
}
.form-group {
    margin-bottom: 20px;
}
label {
    display: block;
    margin-bottom: 8px;
    color: #aaa;
    font-size: 0.9rem;
    font-weight: 500;
}
input[type="text"], input[type="password"] {
    width: 100%;
    padding: 14px 18px;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    background: rgba(0,0,0,0.3);
    color: #fff;
    font-size: 1rem;
    transition: all 0.3s ease;
}
input:focus {
    outline: none;
    border-color: #3a7bd5;
    box-shadow: 0 0 0 3px rgba(58, 123, 213, 0.2);
}
.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}
button, .btn {
    display: inline-block;
    padding: 16px 32px;
    background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
    border: none;
    border-radius: 10px;
    color: #fff;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    text-align: center;
}
button:hover, .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(58, 123, 213, 0.4);
}
button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}
button.full-width { width: 100%; margin-top: 10px; }
.success-box {
    background: rgba(0, 210, 255, 0.1);
    border: 1px solid rgba(0, 210, 255, 0.3);
    color: #00d2ff;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    text-align: center;
}
.success-box h3 { margin-bottom: 10px; font-size: 1.1rem; }
.success-box p { font-size: 0.9rem; opacity: 0.9; }
.warning-box {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    color: #ffc107;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    text-align: center;
}
.error {
    background: rgba(255, 82, 82, 0.15);
    border: 1px solid rgba(255, 82, 82, 0.3);
    color: #ff5252;
    padding: 16px 20px;
    border-radius: 10px;
    margin-top: 15px;
}
.nav-links {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-top: 30px;
}
.nav-link {
    color: #888;
    text-decoration: none;
    transition: color 0.3s;
    font-size: 0.95rem;
}
.nav-link:hover { color: #00d2ff; }
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}
th, td {
    padding: 14px 16px;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
th {
    background: rgba(58, 123, 213, 0.2);
    color: #00d2ff;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
tr:hover td { background: rgba(255,255,255,0.03); }
td:first-child { color: #aaa; font-weight: 500; width: 35%; }
.loading {
    text-align: center;
    padding: 40px;
    color: #888;
}
.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255,255,255,0.1);
    border-top-color: #00d2ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.5s ease; }

/* 상단 네비게이션 바 */
.top-nav {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 40px;
    flex-wrap: wrap;
}
.top-nav a {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 18px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 25px;
    color: #ccc;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
}
.top-nav a:hover {
    background: rgba(0, 210, 255, 0.15);
    border-color: rgba(0, 210, 255, 0.4);
    color: #00d2ff;
    transform: translateY(-2px);
}
.top-nav a.active {
    background: linear-gradient(135deg, rgba(0, 210, 255, 0.2) 0%, rgba(58, 123, 213, 0.2) 100%);
    border-color: rgba(0, 210, 255, 0.5);
    color: #00d2ff;
}
"""

# 상단 네비게이션 바 HTML 생성 함수
def get_top_nav(current_page: str = "") -> str:
    nav_items = [
        ("home", "/", "🏠", "홈"),
        ("ldapinfo", "/ldapinfo", "⚙️", "LDAP 설정"),
        ("ldap", "/ldap", "📋", "AD 조회"),
        ("unlock", "/unlock-account", "🔓", "잠금 해제"),
    ]
    
    nav_html = '<nav class="top-nav">'
    for page_id, href, icon, label in nav_items:
        active_class = " active" if current_page == page_id else ""
        nav_html += f'<a href="{href}" class="{active_class}">{icon} {label}</a>'
    nav_html += '</nav>'
    
    return nav_html


@app.get("/", response_class=HTMLResponse)
async def root():
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


@app.get("/api/health")
async def health_check():
    """헬스 체크 API"""
    return {"status": "healthy", "message": "서버가 정상 작동 중입니다"}


@app.get("/api/hello/{name}")
async def say_hello(name: str):
    """인사 API"""
    return {"message": f"안녕하세요, {name}님!"}


@app.get("/ldapinfo", response_class=HTMLResponse)
async def ldapinfo_page(request: Request):
    """LDAP 설정 페이지"""
    # 세션에서 기존 설정 확인
    ldap_config = request.session.get("ldap_config", {})
    is_configured = bool(ldap_config.get("server"))
    
    config_status = ""
    if is_configured:
        config_status = f"""
        <div class="success-box">
            <h3>✅ LDAP 설정이 저장되어 있습니다</h3>
            <p>서버: {ldap_config.get('server', '')} | Base DN: {ldap_config.get('base_dn', '')}</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LDAP 설정</title>
        <style>{COMMON_STYLES}</style>
    </head>
    <body>
        <div class="container">
            {get_top_nav("ldapinfo")}
            
            <h1>⚙️ LDAP 연결 설정</h1>
            <p class="subtitle">AD 서버 연결 정보를 입력하세요 (세션 동안 유지됩니다)</p>
            
            <div class="card">
                {config_status}
                
                <form id="ldapConfigForm" method="post" action="/api/ldapinfo">
                    <div class="form-group">
                        <label>LDAP 서버 주소 *</label>
                        <input type="text" name="server" id="server" 
                               placeholder="ldap://your-ad-server.domain.com" 
                               value="{ldap_config.get('server', '')}" required>
                    </div>
                    <div class="form-group">
                        <label>Base DN *</label>
                        <input type="text" name="base_dn" id="base_dn" 
                               placeholder="DC=domain,DC=com" 
                               value="{ldap_config.get('base_dn', '')}" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>바인드 계정 (DN) *</label>
                            <input type="text" name="bind_user" id="bind_user" 
                                   placeholder="CN=admin,OU=Users,DC=domain,DC=com" 
                                   value="{ldap_config.get('bind_user', '')}" required>
                        </div>
                        <div class="form-group">
                            <label>바인드 비밀번호 *</label>
                            <input type="password" name="bind_password" id="bind_password" 
                                   placeholder="••••••••" required>
                        </div>
                    </div>
                    <button type="submit" class="full-width">💾 설정 저장</button>
                </form>
            </div>
            
        </div>
        
        <script>
            document.getElementById('ldapConfigForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                const formData = new FormData(e.target);
                
                try {{
                    const response = await fetch('/api/ldapinfo', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        alert('✅ LDAP 설정이 저장되었습니다!');
                        window.location.href = '/ldap';
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }} catch (error) {{
                    alert('❌ 오류가 발생했습니다: ' + error.message);
                }}
            }});
        </script>
    </body>
    </html>
    """


@app.post("/api/ldapinfo")
async def save_ldapinfo(
    request: Request,
    server: str = Form(...),
    base_dn: str = Form(...),
    bind_user: str = Form(...),
    bind_password: str = Form(...)
):
    """LDAP 설정 저장 API"""
    try:
        # 연결 테스트
        ldap_server = Server(server, get_info=ALL, connect_timeout=10)
        conn = Connection(ldap_server, user=bind_user, password=bind_password, auto_bind=True)
        conn.unbind()
        
        # 세션에 저장
        request.session["ldap_config"] = {
            "server": server,
            "base_dn": base_dn,
            "bind_user": bind_user,
            "bind_password": bind_password
        }
        
        return {"success": True, "message": "LDAP 설정이 저장되었습니다."}
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 테스트 실패: {str(e)}"}


@app.get("/api/ldapinfo/status")
async def ldapinfo_status(request: Request):
    """LDAP 설정 상태 확인 API"""
    ldap_config = request.session.get("ldap_config", {})
    is_configured = bool(ldap_config.get("server"))
    
    return {
        "configured": is_configured,
        "server": ldap_config.get("server", "") if is_configured else None
    }


@app.post("/api/ldapinfo/clear")
async def clear_ldapinfo(request: Request):
    """LDAP 설정 삭제 API"""
    request.session.pop("ldap_config", None)
    return {"success": True, "message": "LDAP 설정이 삭제되었습니다."}


@app.get("/ldap", response_class=HTMLResponse)
async def ldap_page(request: Request):
    """LDAP 조회 페이지"""
    # 세션에서 LDAP 설정 확인
    ldap_config = request.session.get("ldap_config", {})
    is_configured = bool(ldap_config.get("server"))
    
    if not is_configured:
        # 설정이 없으면 경고 메시지 표시
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AD 계정 조회</title>
            <style>{COMMON_STYLES}</style>
        </head>
        <body>
            <div class="container">
                {get_top_nav("ldap")}
                
                <h1>🔐 Active Directory 계정 조회</h1>
                <p class="subtitle">AD 서버에 연결하여 사용자 계정 정보를 조회합니다</p>
                
                <div class="card">
                    <div class="warning-box">
                        <h3>⚠️ LDAP 설정이 필요합니다</h3>
                        <p>먼저 LDAP 연결 정보를 설정해주세요.</p>
                    </div>
                    <a href="/ldapinfo" class="btn full-width" style="display: block;">⚙️ LDAP 설정하러 가기</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AD 계정 조회</title>
        <style>{COMMON_STYLES}</style>
    </head>
    <body>
        <div class="container">
            {get_top_nav("ldap")}
            
            <h1>🔐 Active Directory 계정 조회</h1>
            <p class="subtitle">AD 서버에 연결하여 사용자 계정 정보를 조회합니다</p>
            
            <div class="card">
                <div class="success-box">
                    <h3>✅ LDAP 연결 준비 완료</h3>
                    <p>서버: {ldap_config.get('server', '')}</p>
                </div>
                
                <form id="ldapSearchForm">
                    <div class="form-group">
                        <label>조회할 계정 (sAMAccountName)</label>
                        <input type="text" id="username" placeholder="예: hong.gildong" required autofocus>
                    </div>
                    <button type="submit" id="submitBtn" class="full-width">🔍 계정 조회</button>
                </form>
            </div>
            
            <div id="result" class="card" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('ldapSearchForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                const resultDiv = document.getElementById('result');
                const submitBtn = document.getElementById('submitBtn');
                const username = document.getElementById('username').value;
                
                submitBtn.disabled = true;
                submitBtn.textContent = '조회 중...';
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'card fade-in';
                resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>AD 서버에서 정보를 조회하고 있습니다...</div>';
                
                const formData = new FormData();
                formData.append('username', username);
                
                try {{
                    const response = await fetch('/api/ldap/search', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        let html = '<h3 style="color: #00d2ff; margin-bottom: 20px;">📋 ' + data.username + ' 계정 정보</h3>';
                        html += '<table><thead><tr><th>속성</th><th>값</th></tr></thead><tbody>';
                        
                        for (const [key, value] of Object.entries(data.attributes)) {{
                            let displayValue = value;
                            if (Array.isArray(value)) {{
                                displayValue = value.join(', ');
                            }}
                            html += '<tr><td>' + key + '</td><td>' + (displayValue || '-') + '</td></tr>';
                        }}
                        
                        html += '</tbody></table>';
                        resultDiv.innerHTML = html;
                    }} else {{
                        if (data.redirect) {{
                            alert(data.message);
                            window.location.href = data.redirect;
                        }} else {{
                            resultDiv.innerHTML = '<div class="error">❌ ' + data.message + '</div>';
                        }}
                    }}
                }} catch (error) {{
                    resultDiv.innerHTML = '<div class="error">❌ 요청 중 오류가 발생했습니다: ' + error.message + '</div>';
                }} finally {{
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🔍 계정 조회';
                }}
            }});
            
            async function clearSession() {{
                if (confirm('LDAP 설정을 삭제하시겠습니까?')) {{
                    await fetch('/api/ldapinfo/clear', {{ method: 'POST' }});
                    window.location.href = '/ldapinfo';
                }}
            }}
        </script>
    </body>
    </html>
    """


@app.post("/api/ldap/search")
async def search_ldap_user(
    request: Request,
    username: str = Form(...)
):
    """AD 계정 조회 API (세션에서 LDAP 설정 사용)"""
    # 세션에서 LDAP 설정 가져오기
    ldap_config = request.session.get("ldap_config", {})
    
    if not ldap_config.get("server"):
        return {
            "success": False, 
            "message": "LDAP 설정이 없습니다. 먼저 설정을 완료해주세요.",
            "redirect": "/ldapinfo"
        }
    
    try:
        # LDAP 서버 연결
        ldap_server = Server(ldap_config["server"], get_info=ALL)
        conn = Connection(
            ldap_server, 
            user=ldap_config["bind_user"], 
            password=ldap_config["bind_password"], 
            auto_bind=True
        )
        
        # 사용자 검색
        search_filter = f"(sAMAccountName={username})"
        conn.search(
            search_base=ldap_config["base_dn"],
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=[
                'cn', 'displayName', 'sAMAccountName', 'userPrincipalName',
                'mail', 'telephoneNumber', 'mobile', 'department', 'title',
                'company', 'manager', 'memberOf', 'whenCreated', 'whenChanged',
                'lastLogon', 'pwdLastSet', 'userAccountControl', 'distinguishedName',
                'description', 'physicalDeliveryOfficeName', 'streetAddress',
                'l', 'st', 'postalCode', 'co', 'employeeID', 'employeeNumber'
            ]
        )
        
        if len(conn.entries) == 0:
            conn.unbind()
            return {"success": False, "message": f"'{username}' 계정을 찾을 수 없습니다."}
        
        entry = conn.entries[0]
        
        # 속성을 딕셔너리로 변환
        attributes = {}
        attr_labels = {
            'cn': '이름 (CN)',
            'displayName': '표시 이름',
            'sAMAccountName': '로그인 ID',
            'userPrincipalName': 'UPN',
            'mail': '이메일',
            'telephoneNumber': '전화번호',
            'mobile': '휴대폰',
            'department': '부서',
            'title': '직책',
            'company': '회사',
            'manager': '관리자',
            'memberOf': '소속 그룹',
            'whenCreated': '생성일',
            'whenChanged': '수정일',
            'lastLogon': '마지막 로그인',
            'pwdLastSet': '비밀번호 변경일',
            'userAccountControl': '계정 상태',
            'distinguishedName': 'DN',
            'description': '설명',
            'physicalDeliveryOfficeName': '사무실',
            'streetAddress': '주소',
            'l': '도시',
            'st': '시/도',
            'postalCode': '우편번호',
            'co': '국가',
            'employeeID': '사번',
            'employeeNumber': '직원번호'
        }
        
        for attr_name, label in attr_labels.items():
            try:
                value = getattr(entry, attr_name, None)
                if value is not None:
                    val = value.value if hasattr(value, 'value') else str(value)
                    if val:
                        # memberOf 처리 (CN만 추출)
                        if attr_name == 'memberOf' and isinstance(val, list):
                            val = [v.split(',')[0].replace('CN=', '') for v in val[:5]]
                            if len(entry.memberOf.values) > 5:
                                val.append(f'... 외 {len(entry.memberOf.values) - 5}개')
                        attributes[label] = val
            except Exception:
                pass
        
        conn.unbind()
        
        return {
            "success": True,
            "username": username,
            "attributes": attributes
        }
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 오류: {str(e)}"}


@app.get("/unlock-account", response_class=HTMLResponse)
async def unlock_account_page(request: Request):
    """계정 잠금 해제 페이지"""
    # 세션에서 LDAP 설정 확인
    ldap_config = request.session.get("ldap_config", {})
    is_configured = bool(ldap_config.get("server"))
    
    if not is_configured:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AD 계정 잠금 해제</title>
            <style>{COMMON_STYLES}</style>
        </head>
        <body>
            <div class="container">
                {get_top_nav("unlock")}
                
                <h1>🔓 AD 계정 잠금 해제</h1>
                <p class="subtitle">잠긴 AD 계정을 조회하고 잠금을 해제합니다</p>
                
                <div class="card">
                    <div class="warning-box">
                        <h3>⚠️ LDAP 설정이 필요합니다</h3>
                        <p>먼저 LDAP 연결 정보를 설정해주세요.</p>
                    </div>
                    <a href="/ldapinfo" class="btn full-width" style="display: block;">⚙️ LDAP 설정하러 가기</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AD 계정 잠금 해제</title>
        <style>
            {COMMON_STYLES}
            .status-locked {{
                background: rgba(255, 82, 82, 0.15);
                border: 1px solid rgba(255, 82, 82, 0.4);
                color: #ff5252;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .status-unlocked {{
                background: rgba(76, 175, 80, 0.15);
                border: 1px solid rgba(76, 175, 80, 0.4);
                color: #4caf50;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .status-locked h3, .status-unlocked h3 {{
                margin-bottom: 8px;
                font-size: 1.2rem;
            }}
            .unlock-btn {{
                background: linear-gradient(135deg, #ff5252 0%, #d32f2f 100%);
                margin-top: 15px;
            }}
            .unlock-btn:hover {{
                box-shadow: 0 8px 25px rgba(255, 82, 82, 0.4);
            }}
            .user-info {{
                background: rgba(255,255,255,0.03);
                border-radius: 10px;
                padding: 15px 20px;
                margin-bottom: 15px;
            }}
            .user-info-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}
            .user-info-row:last-child {{ border-bottom: none; }}
            .user-info-label {{ color: #888; }}
            .user-info-value {{ color: #fff; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="container">
            {get_top_nav("unlock")}
            
            <h1>🔓 AD 계정 잠금 해제</h1>
            <p class="subtitle">잠긴 AD 계정을 조회하고 잠금을 해제합니다</p>
            
            <div class="card">
                <div class="success-box">
                    <h3>✅ LDAP 연결 준비 완료</h3>
                    <p>서버: {ldap_config.get('server', '')}</p>
                </div>
                
                <form id="checkLockForm">
                    <div class="form-group">
                        <label>조회할 계정 (sAMAccountName)</label>
                        <input type="text" id="username" placeholder="예: hong.gildong" required autofocus>
                    </div>
                    <button type="submit" id="checkBtn" class="full-width">🔍 잠금 상태 확인</button>
                </form>
            </div>
            
            <div id="result" class="card" style="display: none;"></div>
        </div>
        
        <script>
            let currentUserDN = null;
            let currentUsername = null;
            
            document.getElementById('checkLockForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                await checkLockStatus();
            }});
            
            async function checkLockStatus() {{
                const resultDiv = document.getElementById('result');
                const checkBtn = document.getElementById('checkBtn');
                const username = document.getElementById('username').value;
                
                checkBtn.disabled = true;
                checkBtn.textContent = '조회 중...';
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'card fade-in';
                resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>계정 잠금 상태를 확인하고 있습니다...</div>';
                
                const formData = new FormData();
                formData.append('username', username);
                
                try {{
                    const response = await fetch('/api/unlock-account/check', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        currentUserDN = data.user_dn;
                        currentUsername = data.username;
                        
                        let html = '';
                        
                        // 사용자 정보
                        html += '<div class="user-info">';
                        html += '<div class="user-info-row"><span class="user-info-label">계정명</span><span class="user-info-value">' + data.username + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">표시 이름</span><span class="user-info-value">' + (data.display_name || '-') + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">이메일</span><span class="user-info-value">' + (data.email || '-') + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">부서</span><span class="user-info-value">' + (data.department || '-') + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">잘못된 비밀번호 시도</span><span class="user-info-value" style="color: ' + (data.bad_pwd_count > 0 ? '#ff9800' : '#4caf50') + '; font-weight: 600;">' + data.bad_pwd_count + '회</span></div>';
                        html += '</div>';
                        
                        // 잠금 상태
                        if (data.is_locked) {{
                            html += '<div class="status-locked">';
                            html += '<h3>🔒 계정이 잠겨있습니다</h3>';
                            html += '<p>잠금 시간: ' + (data.lockout_time || '알 수 없음') + '</p>';
                            html += '<p style="margin-top: 8px; font-size: 0.9rem;">잘못된 비밀번호 시도: <strong>' + data.bad_pwd_count + '회</strong></p>';
                            html += '</div>';
                            html += '<button onclick="unlockAccount()" class="unlock-btn full-width" id="unlockBtn">🔓 계정 잠금 해제</button>';
                        }} else {{
                            html += '<div class="status-unlocked">';
                            html += '<h3>✅ 계정이 정상 상태입니다</h3>';
                            html += '<p>이 계정은 잠겨있지 않습니다.</p>';
                            html += '</div>';
                        }}
                        
                        resultDiv.innerHTML = html;
                    }} else {{
                        if (data.redirect) {{
                            alert(data.message);
                            window.location.href = data.redirect;
                        }} else {{
                            resultDiv.innerHTML = '<div class="error">❌ ' + data.message + '</div>';
                        }}
                    }}
                }} catch (error) {{
                    resultDiv.innerHTML = '<div class="error">❌ 요청 중 오류가 발생했습니다: ' + error.message + '</div>';
                }} finally {{
                    checkBtn.disabled = false;
                    checkBtn.textContent = '🔍 잠금 상태 확인';
                }}
            }}
            
            async function unlockAccount() {{
                if (!currentUserDN || !currentUsername) {{
                    alert('사용자 정보가 없습니다. 다시 조회해주세요.');
                    return;
                }}
                
                if (!confirm(currentUsername + ' 계정의 잠금을 해제하시겠습니까?')) {{
                    return;
                }}
                
                const unlockBtn = document.getElementById('unlockBtn');
                unlockBtn.disabled = true;
                unlockBtn.textContent = '처리 중...';
                
                const formData = new FormData();
                formData.append('user_dn', currentUserDN);
                formData.append('username', currentUsername);
                
                try {{
                    const response = await fetch('/api/unlock-account/unlock', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        alert('✅ ' + currentUsername + ' 계정의 잠금이 해제되었습니다!');
                        // 상태 다시 확인
                        await checkLockStatus();
                    }} else {{
                        alert('❌ ' + data.message);
                        unlockBtn.disabled = false;
                        unlockBtn.textContent = '🔓 계정 잠금 해제';
                    }}
                }} catch (error) {{
                    alert('❌ 오류가 발생했습니다: ' + error.message);
                    unlockBtn.disabled = false;
                    unlockBtn.textContent = '🔓 계정 잠금 해제';
                }}
            }}
        </script>
    </body>
    </html>
    """


@app.post("/api/unlock-account/check")
async def check_account_lock_status(
    request: Request,
    username: str = Form(...)
):
    """계정 잠금 상태 확인 API"""
    ldap_config = request.session.get("ldap_config", {})
    
    if not ldap_config.get("server"):
        return {
            "success": False,
            "message": "LDAP 설정이 없습니다. 먼저 설정을 완료해주세요.",
            "redirect": "/ldapinfo"
        }
    
    try:
        ldap_server = Server(ldap_config["server"], get_info=ALL)
        conn = Connection(
            ldap_server,
            user=ldap_config["bind_user"],
            password=ldap_config["bind_password"],
            auto_bind=True
        )
        
        search_filter = f"(sAMAccountName={username})"
        conn.search(
            search_base=ldap_config["base_dn"],
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=[
                'distinguishedName', 'sAMAccountName', 'displayName',
                'mail', 'department', 'lockoutTime', 'userAccountControl',
                'msDS-User-Account-Control-Computed',  # 실시간 계정 상태 확인용
                'badPwdCount'  # 잘못된 비밀번호 시도 횟수
            ]
        )
        
        if len(conn.entries) == 0:
            conn.unbind()
            return {"success": False, "message": f"'{username}' 계정을 찾을 수 없습니다."}
        
        entry = conn.entries[0]
        
        # 잠금 상태 확인
        lockout_time = None
        is_locked = False
        
        import datetime
        
        # 방법 1: msDS-User-Account-Control-Computed 속성 확인 (가장 정확)
        # UF_LOCKOUT = 0x0010 = 16
        try:
            uac_computed = getattr(entry, 'msDS-User-Account-Control-Computed', None)
            if uac_computed and uac_computed.value:
                is_locked = bool(int(uac_computed.value) & 0x0010)
        except Exception:
            pass
        
        # 방법 2: lockoutTime 속성으로 확인 (백업)
        # lockoutTime이 0이 아니고, 유효한 시간값이면 잠긴 상태
        try:
            lockout_value = entry.lockoutTime.value
            if lockout_value is not None:
                # datetime 객체인 경우
                if isinstance(lockout_value, datetime.datetime):
                    # 1601-01-01 (Windows epoch 0)이 아니면 잠긴 상태
                    if lockout_value.year > 1601:
                        is_locked = True
                        lockout_time = lockout_value.strftime("%Y-%m-%d %H:%M:%S")
                # 정수인 경우 (Windows FILETIME)
                elif isinstance(lockout_value, int) and lockout_value > 0:
                    is_locked = True
                    # Windows FILETIME: 1601년 1월 1일부터 100나노초 단위
                    windows_epoch = datetime.datetime(1601, 1, 1)
                    lockout_datetime = windows_epoch + datetime.timedelta(microseconds=lockout_value // 10)
                    lockout_time = lockout_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        
        # 사용자 정보 추출
        display_name = None
        email = None
        department = None
        user_dn = None
        
        try:
            user_dn = entry.distinguishedName.value
        except Exception:
            pass
        try:
            display_name = entry.displayName.value
        except Exception:
            pass
        try:
            email = entry.mail.value
        except Exception:
            pass
        try:
            department = entry.department.value
        except Exception:
            pass
        
        # 잘못된 비밀번호 시도 횟수
        bad_pwd_count = 0
        try:
            bad_pwd_value = entry.badPwdCount.value
            if bad_pwd_value is not None:
                bad_pwd_count = int(bad_pwd_value)
        except Exception:
            pass
        
        conn.unbind()
        
        return {
            "success": True,
            "username": username,
            "user_dn": user_dn,
            "display_name": display_name,
            "email": email,
            "department": department,
            "is_locked": is_locked,
            "lockout_time": lockout_time,
            "bad_pwd_count": bad_pwd_count
        }
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 오류: {str(e)}"}


@app.post("/api/unlock-account/unlock")
async def unlock_account(
    request: Request,
    user_dn: str = Form(...),
    username: str = Form(...)
):
    """계정 잠금 해제 API"""
    ldap_config = request.session.get("ldap_config", {})
    
    if not ldap_config.get("server"):
        return {
            "success": False,
            "message": "LDAP 설정이 없습니다.",
            "redirect": "/ldapinfo"
        }
    
    try:
        ldap_server = Server(ldap_config["server"], get_info=ALL)
        conn = Connection(
            ldap_server,
            user=ldap_config["bind_user"],
            password=ldap_config["bind_password"],
            auto_bind=True
        )
        
        # lockoutTime을 0으로 설정하여 잠금 해제
        result = conn.modify(
            user_dn,
            {'lockoutTime': [(MODIFY_REPLACE, [0])]}
        )
        
        if result:
            conn.unbind()
            return {
                "success": True,
                "message": f"'{username}' 계정의 잠금이 해제되었습니다."
            }
        else:
            error_msg = conn.result.get('description', '알 수 없는 오류')
            conn.unbind()
            return {
                "success": False,
                "message": f"잠금 해제 실패: {error_msg}"
            }
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 오류: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
