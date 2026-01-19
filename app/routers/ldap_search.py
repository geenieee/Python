"""
LDAP 조회 페이지 라우터
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.styles import COMMON_STYLES, get_top_nav
from app.services.ldap_service import search_user

router = APIRouter()


@router.get("/ldap", response_class=HTMLResponse)
async def ldap_page(request: Request):
    """LDAP 조회 페이지"""
    ldap_config = request.session.get("ldap_config", {})
    is_configured = bool(ldap_config.get("server"))
    
    if not is_configured:
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
        </script>
    </body>
    </html>
    """


@router.post("/api/ldap/search")
async def api_search_ldap_user(
    request: Request,
    username: str = Form(...)
):
    """AD 계정 조회 API"""
    ldap_config = request.session.get("ldap_config", {})
    
    if not ldap_config.get("server"):
        return {
            "success": False,
            "message": "LDAP 설정이 없습니다. 먼저 설정을 완료해주세요.",
            "redirect": "/ldapinfo"
        }
    
    return search_user(ldap_config, username)
