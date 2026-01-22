from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
import gws_service

app = FastAPI(
    title="GWS User Management",
    description="Google Workspace 사용자 관리 시스템",
    version="1.0.0"
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GWS User Management</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .nav {
                background: rgba(0,0,0,0.2);
                padding: 15px 30px;
                display: flex;
                gap: 20px;
                align-items: center;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 8px;
                transition: background 0.3s;
            }
            .nav a:hover { background: rgba(255,255,255,0.2); }
            .nav a.active { background: rgba(255,255,255,0.3); }
            .nav .logo { font-weight: bold; font-size: 1.3em; margin-right: 20px; }
            .container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: calc(100vh - 60px);
                color: white;
            }
            .hero {
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            p { font-size: 1.2em; opacity: 0.9; }
            .btn {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: white;
                color: #667eea;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                transition: transform 0.2s;
            }
            .btn:hover { transform: scale(1.05); }
        </style>
    </head>
    <body>
        <nav class="nav">
            <span class="logo">🔐 GWS Admin</span>
            <a href="/" class="active">홈</a>
            <a href="/users">사용자 목록</a>
            <a href="/docs">API 문서</a>
        </nav>
        <div class="container">
            <div class="hero">
                <h1>🔐 GWS User Management</h1>
                <p>Google Workspace 사용자 관리 시스템</p>
                <p>2단계 인증 현황을 한눈에 확인하세요</p>
                <a href="/users" class="btn">사용자 목록 보기 →</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/users", response_class=HTMLResponse)
async def users_page():
    """사용자 목록 페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>사용자 목록 - GWS Admin</title>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                background: #f5f5f5;
                min-height: 100vh;
            }
            .nav {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px 30px;
                display: flex;
                gap: 20px;
                align-items: center;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 8px;
                transition: background 0.3s;
            }
            .nav a:hover { background: rgba(255,255,255,0.2); }
            .nav a.active { background: rgba(255,255,255,0.3); }
            .nav .logo { font-weight: bold; font-size: 1.3em; margin-right: 20px; color: white; }
            .content {
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            h1 { color: #333; margin: 0; }
            .stats {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                flex: 1;
            }
            .stat-card h3 { margin: 0 0 10px 0; color: #666; font-size: 0.9em; }
            .stat-card .value { font-size: 2em; font-weight: bold; color: #333; }
            .stat-card.success .value { color: #22c55e; }
            .stat-card.warning .value { color: #f59e0b; }
            .card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .search-box {
                padding: 20px;
                border-bottom: 1px solid #eee;
            }
            .search-box input {
                width: 100%;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 1em;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 15px 20px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            th {
                background: #f9f9f9;
                font-weight: 600;
                color: #666;
            }
            tr:hover { background: #f5f5f5; }
            .badge {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 500;
            }
            .badge.success { background: #dcfce7; color: #166534; }
            .badge.danger { background: #fee2e2; color: #991b1b; }
            .badge.warning { background: #fef3c7; color: #92400e; }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .error {
                text-align: center;
                padding: 40px;
                color: #991b1b;
                background: #fee2e2;
                border-radius: 8px;
                margin: 20px;
            }
        </style>
    </head>
    <body>
        <nav class="nav">
            <span class="logo">🔐 GWS Admin</span>
            <a href="/">홈</a>
            <a href="/users" class="active">사용자 목록</a>
            <a href="/docs">API 문서</a>
        </nav>
        <div class="content">
            <div class="header">
                <h1>👥 사용자 목록</h1>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <h3>전체 사용자</h3>
                    <div class="value" id="totalUsers">-</div>
                </div>
                <div class="stat-card success">
                    <h3>2단계 인증 활성화</h3>
                    <div class="value" id="users2sv">-</div>
                </div>
                <div class="stat-card warning">
                    <h3>2단계 인증 미설정</h3>
                    <div class="value" id="usersNo2sv">-</div>
                </div>
            </div>
            
            <div class="card">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="이름 또는 이메일로 검색..." onkeyup="filterTable()">
                </div>
                <div id="tableContainer">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>사용자 목록을 불러오는 중...</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let allUsers = [];
            
            async function loadUsers() {
                try {
                    const response = await fetch('/api/users');
                    if (!response.ok) {
                        throw new Error('API 호출 실패');
                    }
                    const data = await response.json();
                    allUsers = data.users;
                    
                    // 통계 업데이트
                    document.getElementById('totalUsers').textContent = data.total;
                    document.getElementById('users2sv').textContent = data.enrolled_2sv;
                    document.getElementById('usersNo2sv').textContent = data.not_enrolled_2sv;
                    
                    renderTable(allUsers);
                } catch (error) {
                    document.getElementById('tableContainer').innerHTML = `
                        <div class="error">
                            <p>⚠️ 사용자 목록을 불러오는데 실패했습니다.</p>
                            <p>${error.message}</p>
                            <p>credentials.json 파일이 있는지, 권한 설정이 올바른지 확인해주세요.</p>
                        </div>
                    `;
                }
            }
            
            function renderTable(users) {
                const html = `
                    <table>
                        <thead>
                            <tr>
                                <th>성</th>
                                <th>이름</th>
                                <th>이메일</th>
                                <th>2단계 인증</th>
                                <th>상태</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.map(user => `
                                <tr>
                                    <td>${user.familyName || '-'}</td>
                                    <td>${user.givenName || '-'}</td>
                                    <td>${user.email}</td>
                                    <td>
                                        ${user.isEnrolledIn2Sv 
                                            ? '<span class="badge success">✓ 활성화</span>' 
                                            : '<span class="badge danger">✗ 미설정</span>'}
                                    </td>
                                    <td>
                                        ${user.suspended 
                                            ? '<span class="badge warning">정지됨</span>' 
                                            : '<span class="badge success">활성</span>'}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
                document.getElementById('tableContainer').innerHTML = html;
            }
            
            function filterTable() {
                const query = document.getElementById('searchInput').value.toLowerCase();
                const filtered = allUsers.filter(user => 
                    (user.familyName && user.familyName.toLowerCase().includes(query)) ||
                    (user.givenName && user.givenName.toLowerCase().includes(query)) ||
                    user.email.toLowerCase().includes(query)
                );
                renderTable(filtered);
            }
            
            // 페이지 로드 시 사용자 목록 불러오기
            loadUsers();
        </script>
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


@app.get("/api/users")
async def get_users():
    """
    Google Workspace 사용자 목록 조회
    
    Returns:
        사용자 목록 (성, 이름, 이메일, 2단계 인증 여부)
    """
    try:
        users = gws_service.get_all_users()
        
        # 통계 계산
        total = len(users)
        enrolled_2sv = sum(1 for u in users if u.get("isEnrolledIn2Sv", False))
        not_enrolled_2sv = total - enrolled_2sv
        
        return {
            "users": users,
            "total": total,
            "enrolled_2sv": enrolled_2sv,
            "not_enrolled_2sv": not_enrolled_2sv
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="credentials.json 파일을 찾을 수 없습니다. 프로젝트 폴더에 파일이 있는지 확인해주세요."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 목록 조회 중 오류 발생: {str(e)}"
        )


@app.get("/api/users/{email}")
async def get_user(email: str):
    """
    특정 사용자 정보 조회
    
    Args:
        email: 사용자 이메일
    """
    try:
        user = gws_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 조회 중 오류 발생: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
