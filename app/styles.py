"""
공통 CSS 스타일 및 네비게이션
"""

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


def get_top_nav(current_page: str = "") -> str:
    """상단 네비게이션 바 HTML 생성"""
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
