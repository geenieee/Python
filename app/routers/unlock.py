"""
계정 잠금 해제 페이지 라우터
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.styles import COMMON_STYLES, get_top_nav
from app.services.ldap_service import check_lock_status, unlock_user_account

router = APIRouter()


@router.get("/unlock-account", response_class=HTMLResponse)
async def unlock_account_page(request: Request):
    """계정 잠금 해제 페이지"""
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
                        
                        html += '<div class="user-info">';
                        html += '<div class="user-info-row"><span class="user-info-label">계정명</span><span class="user-info-value">' + data.username + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">표시 이름</span><span class="user-info-value">' + (data.display_name || '-') + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">이메일</span><span class="user-info-value">' + (data.email || '-') + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">부서</span><span class="user-info-value">' + (data.department || '-') + '</span></div>';
                        html += '<div class="user-info-row"><span class="user-info-label">잘못된 비밀번호 시도</span><span class="user-info-value" style="color: ' + (data.bad_pwd_count > 0 ? '#ff9800' : '#4caf50') + '; font-weight: 600;">' + data.bad_pwd_count + '회</span></div>';
                        html += '</div>';
                        
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


@router.post("/api/unlock-account/check")
async def api_check_account_lock_status(
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
    
    return check_lock_status(ldap_config, username)


@router.post("/api/unlock-account/unlock")
async def api_unlock_account(
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
    
    return unlock_user_account(ldap_config, user_dn, username)
