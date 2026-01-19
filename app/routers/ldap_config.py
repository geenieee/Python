"""
LDAP 설정 페이지 라우터
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.styles import COMMON_STYLES, get_top_nav
from app.services.ldap_service import test_ldap_connection

router = APIRouter()


@router.get("/ldapinfo", response_class=HTMLResponse)
async def ldapinfo_page(request: Request):
    """LDAP 설정 페이지"""
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


@router.post("/api/ldapinfo")
async def save_ldapinfo(
    request: Request,
    server: str = Form(...),
    base_dn: str = Form(...),
    bind_user: str = Form(...),
    bind_password: str = Form(...)
):
    """LDAP 설정 저장 API"""
    success, message = test_ldap_connection(server, bind_user, bind_password)
    
    if success:
        request.session["ldap_config"] = {
            "server": server,
            "base_dn": base_dn,
            "bind_user": bind_user,
            "bind_password": bind_password
        }
        return {"success": True, "message": "LDAP 설정이 저장되었습니다."}
    else:
        return {"success": False, "message": f"LDAP 연결 테스트 실패: {message}"}


@router.get("/api/ldapinfo/status")
async def ldapinfo_status(request: Request):
    """LDAP 설정 상태 확인 API"""
    ldap_config = request.session.get("ldap_config", {})
    is_configured = bool(ldap_config.get("server"))
    
    return {
        "configured": is_configured,
        "server": ldap_config.get("server", "") if is_configured else None
    }


@router.post("/api/ldapinfo/clear")
async def clear_ldapinfo(request: Request):
    """LDAP 설정 삭제 API"""
    request.session.pop("ldap_config", None)
    return {"success": True, "message": "LDAP 설정이 삭제되었습니다."}
