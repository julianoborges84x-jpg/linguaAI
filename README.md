# LinguaAI SaaS (FastAPI + React/Vite)

Projeto full stack pronto para operacao como SaaS com plano `FREE/PRO`, Stripe real, landing page, paginas legais e fluxo de deploy.

## Stack

- Backend: FastAPI + SQLAlchemy
- Frontend: React + Vite + Tailwind
- Banco: PostgreSQL
- Billing: Stripe Checkout + Billing Portal + Webhook

## Variaveis de ambiente

1. Copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

2. Configure no backend (`.env`):

- `API_URL`
- `FRONTEND_URL`
- `DATABASE_URL`
- `JWT_SECRET`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`
- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`

3. Configure no frontend (`frontend/.env`):

```powershell
Copy-Item frontend\.env.example frontend\.env
```

- `VITE_API_URL` (URL publica do backend)

## Rodar localmente

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Testes

### Backend (unitarios + integracao)

```powershell
pytest -q
```

### Frontend build de producao

```powershell
cd frontend
npm run build
```

## Endpoints Stripe

- `POST /billing/create-checkout-session`
- `POST /billing/create-portal-session`
- `POST /billing/webhook`
- `GET /billing/status`
- `POST /billing/cancel-subscription`

Fluxo:

1. Checkout criado em `/billing/create-checkout-session`.
2. Stripe conclui pagamento.
3. Webhook `checkout.session.completed` promove usuario para `PRO`.
4. Webhook `customer.subscription.updated/deleted` sincroniza status e volta para `FREE` quando cancelado.

## Deploy frontend (Vercel)

1. Importar pasta `frontend` no Vercel.
2. Build command: `npm run build`.
3. Output: `dist`.
4. Definir env:
   - `VITE_API_URL=https://SEU_BACKEND_PUBLICO`
5. Arquivo pronto: `frontend/vercel.json`.

## Deploy backend (Render)

1. Criar Web Service apontando para este repositorio.
2. Build command:
   - `pip install -r requirements.txt`
3. Start command:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Definir envs de producao (`APP_ENV=production`, `DATABASE_URL`, `JWT_SECRET`, Stripe etc.).
5. Arquivo pronto: `render.yaml`.

## Deploy backend (Railway)

1. Criar projeto e conectar repositorio.
2. Configurar envs de producao.
3. Start command:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Arquivos prontos: `Procfile` e `railway.json`.

## Stripe em producao

1. Criar produto/price no Stripe e copiar `price_id`.
2. Configurar:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PRICE_ID`
   - `STRIPE_WEBHOOK_SECRET`
3. Criar endpoint de webhook no Dashboard Stripe:
   - `https://SEU_BACKEND/billing/webhook`
4. Eventos recomendados:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`

## Dominio e CORS

1. Defina dominio frontend e backend (ex.: Vercel + Render).
2. Atualize no backend:
   - `FRONTEND_URL`
   - `API_URL`
   - `CORS_ALLOWED_ORIGINS` (localhost + dominio real)
   - `TRUSTED_HOSTS`
3. Atualize no frontend:
   - `VITE_API_URL`

## Observacoes de operacao

- Em `dev/test`, o fallback fake pode ser habilitado com `STRIPE_ALLOW_FAKE_CHECKOUT=true`.
- Em producao, use Stripe real e mantenha `STRIPE_ALLOW_FAKE_CHECKOUT=false`.
