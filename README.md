# Python Web Server

FastAPI 기반의 Python 웹 서버 프로젝트입니다.

## 시작하기

### 1. 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python main.py
# 또는
uvicorn main:app --reload
```

### 4. 접속

- 메인 페이지: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 메인 페이지 |
| GET | `/api/health` | 헬스 체크 |
| GET | `/api/hello/{name}` | 인사 API |

## 기술 스택

- Python 3.9+
- FastAPI
- Uvicorn
