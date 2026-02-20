# LinguaAI Backend

Backend FastAPI + SQLAlchemy + PostgreSQL (psycopg3) com JWT.

## 1) Configuracao de ambiente

```powershell
Copy-Item .env.example .env
```

`.env.example`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/mentorlingua
JWT_SECRET=troque_isto
JWT_EXPIRES_MINUTES=60
OPENAI_API_KEY=coloque_sua_chave_aqui
```

- Pode deixar `OPENAI_API_KEY` vazio durante setup inicial.
- O app so retorna erro quando um endpoint de IA for chamado sem chave.

## 2) Rodar em dev local (Windows + venv)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 3) Rodar em producao com Docker Compose

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

## 4) Verificacao rapida

- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Colecao REST Client: `requests.http`

## 5) Endpoints principais

- `POST /users`
- `POST /auth/login`
- `GET /me`
- `GET /health`
