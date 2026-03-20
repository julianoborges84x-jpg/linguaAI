# LinguaAI / Mentor Lingua

SaaS de aprendizado de idiomas com backend FastAPI, frontend React/Vite, PostgreSQL, JWT, onboarding persistido e billing `FREE/PRO` com Stripe.

## Estrutura ativa

- `app/`: backend FastAPI, models SQLAlchemy, rotas e servicos.
- `alembic/`: migrations oficiais do banco.
- `frontend/`: frontend principal em React + TypeScript + Vite.
- `tests/`: testes automatizados do backend com pytest.

`frontend_backup/` e o frontend legado em JSX foram mantidos apenas como historico; a base ativa e deployavel e `frontend/`.

## Setup local

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Backend esperado: `http://127.0.0.1:8000/docs`

Frontend esperado: `http://127.0.0.1:3000`

## Variaveis de ambiente

### Backend `.env`

- `APP_ENV`
- `API_URL`
- `FRONTEND_URL`
- `DATABASE_URL`
- `DB_AUTO_CREATE`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXP_MINUTES`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`
- `OPENAI_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PAYMENT_METHOD_TYPES`
- `STRIPE_ALLOW_FAKE_CHECKOUT`

### Frontend `frontend/.env`

- `VITE_API_URL`

## Fluxos suportados

- Criacao de conta em `POST /users`
- Login JWT em `POST /auth/login`
- Sessao autenticada em `GET /users/me`
- Onboarding persistido em `PATCH /users/me`
- Lesson com persistencia em `/sessions/start` e `/sessions/{id}/finish`
- Chat real em `/mentor/chat`
- Billing Stripe em `/billing/create-checkout-session`
- Webhook Stripe em `/billing/webhook`
- Status de plano em `/billing/status`
- Verificacao de email via token
- Jornada pedagogica com trilha e aulas em `/pedagogy/*`

## Seed pedagogico (conteudo)

Para garantir o conteudo original da trilha `English Foundations A1` (24 aulas), execute:

```powershell
.\.venv\Scripts\python -m app.scripts.seed_pedagogy
```

Observacao:
- O seed tambem e autoexecutado pelos endpoints pedagogicos quando necessario.
- Idiomas suportados no seed atual: `en`, `es`, `fr`, `it`.

## Endpoints pedagogicos principais

- `GET /pedagogy/track/current`
- `GET /pedagogy/modules`
- `GET /pedagogy/modules/{id}`
- `GET /pedagogy/lessons/{id}`
- `POST /pedagogy/lessons/{id}/step`
- `POST /pedagogy/lessons/{id}/submit`
- `GET /pedagogy/review/today`
- `POST /pedagogy/review/submit`
- `GET /pedagogy/recommendations`
- `GET /pedagogy/progress/summary`

## Testes e validacao

### Backend

```powershell
.\.venv\Scripts\python -m pytest -q
```

### Smoke flow (aprendizagem visivel)

Valida o fluxo real: login -> home pedagogica -> modulo -> licao -> submit -> resumo.

```powershell
.\.venv\Scripts\python scripts/smoke_learning_flow.py --base-url http://127.0.0.1:8000
```

### Frontend

```powershell
cd frontend
npm run lint
npm run test:run
npm run build
```

## Banco e migrations

- A fonte de verdade do schema e o Alembic.
- O comando oficial de bootstrap e `python -m alembic upgrade head`.
- A migration `0006_users_verification_fields` alinha `users` com o modelo atual e adiciona `is_verified` e `verification_token`.
- As migrations `0002` a `0005` foram deixadas idempotentes para recuperar ambientes que estavam em `0001_initial` mas com schema parcialmente alterado.

## Stripe

Eventos esperados no webhook:

- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`

Em `development/test`, o fallback fake pode ser usado com `STRIPE_ALLOW_FAKE_CHECKOUT=true`. Em producao, deixe `false`.

## Deploy

### Backend

Comando de start:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Passos:

1. Definir variaveis de ambiente de producao.
2. Executar `python -m alembic upgrade head`.
3. Configurar webhook Stripe apontando para `/billing/webhook`.
4. Configurar `FRONTEND_URL`, `API_URL`, `CORS_ALLOWED_ORIGINS` e `TRUSTED_HOSTS`.

### Frontend

Build:

```powershell
npm run build
```

Output:

- `frontend/dist`

Variavel obrigatoria:

- `VITE_API_URL=https://seu-backend-publico`

## Checklist de lancamento

- Banco migrado com `alembic upgrade head`
- Stripe checkout e webhook configurados
- SMTP configurado ou conscientemente desativado
- `JWT_SECRET` rotacionado e forte
- `OPENAI_API_KEY` configurada
- CORS/hosts revisados para dominio final
- Healthcheck validado
- Frontend buildado e backend com `/docs` acessivel

## Seguranca

- O `.env` atual do workspace continha segredos reais e deve ser rotacionado antes do lancamento publico.
- Nao mantenha chaves Stripe, OpenAI, JWT e credenciais do Neon versionadas.
