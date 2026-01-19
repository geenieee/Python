from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Python Web Server",
    description="FastAPI 기반 웹 서버",
    version="1.0.0"
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python Web Server</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            p { font-size: 1.2em; opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐍 Python Web Server</h1>
            <p>FastAPI 서버가 정상적으로 실행 중입니다!</p>
            <p><a href="/docs" style="color: #fff;">API 문서 보기 →</a></p>
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
