# Arcade Hub - Python Backend (FastAPI)

A ready-to-deploy backend for the Arcade Hub web app. Auth with **auto email
verification**, JWT, virtual-coin wallet, game score submission, leaderboards,
and an admin dashboard API.

> Virtual coins only. This is **not** a real-money / gambling platform.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # edit if you want SMTP
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive API.

The app uses **SQLite** by default — no database setup needed. Switch to Postgres by setting `DATABASE_URL`.

If `SMTP_*` env vars are blank, verification emails are printed to the server console (so signup still works for local dev). Click the link in the console to verify.

## File layout

```
.
├── main.py                     # FastAPI entry point
├── requirements.txt
├── Dockerfile                  # docker build -t arcade-api . && docker run -p 8000:8000 arcade-api
├── render.yaml                 # one-click deploy on Render
├── Procfile                    # for Heroku-style PaaS
├── .env.example
└── app/
    ├── config.py               # env-driven settings
    ├── database.py             # SQLAlchemy engine + session
    ├── schemas.py              # Pydantic request/response models
    ├── security.py             # passwords + JWT + auth dependencies
    ├── models/
    │   ├── user_model.py
    │   ├── wallet_model.py
    │   └── game_model.py
    ├── routers/
    │   ├── health_router.py    # GET /health
    │   ├── auth_router.py      # /api/auth/*
    │   ├── wallet_router.py    # /api/wallet/*
    │   ├── games_router.py     # /api/games/*
    │   └── admin_router.py     # /api/admin/*
    └── services/
        ├── email_service.py    # SMTP with console fallback
        └── wallet_service.py
```

Filenames are distinct (no two files share the same name) per the spec.

## Email verification (automatic, one-click)

1. User signs up → backend creates a token, stores it on the user row, and emails a verify link.
2. Link points to `GET /api/auth/verify?token=...` → instantly flips `is_verified` and redirects to `FRONTEND_URL/verified`.
3. Frontend can also call `POST /api/auth/verify?token=...` to verify in-place.
4. `POST /api/auth/resend-verification` triggers a new email.

### Free SMTP providers that work out of the box

| Provider     | Host                       | Port | Notes                            |
|--------------|----------------------------|------|----------------------------------|
| Gmail        | `smtp.gmail.com`           | 587  | Use an **App Password**          |
| Brevo        | `smtp-relay.brevo.com`     | 587  | 300 free emails/day              |
| Mailtrap     | `sandbox.smtp.mailtrap.io` | 587  | Dev sandbox (does not send real) |
| Mailgun      | `smtp.mailgun.org`         | 587  | Free sandbox domain              |

## Auth flow

```
POST /api/auth/signup    { email, username, password }   → 201 { access_token, user }   + verification email
POST /api/auth/login     { email, password }             → 200 { access_token, user }
GET  /api/auth/verify?token=...                          → redirect to /verified
POST /api/auth/resend-verification  { email }            → 200
GET  /api/auth/me                  (Bearer token)        → current user
```

## Wallet

```
GET /api/wallet/balance
GET /api/wallet/transactions
```

## Games + leaderboard

```
GET  /api/games/list
POST /api/games/score             { game_key, score, duration_seconds? }   (verified users only)
GET  /api/games/leaderboard/{game_key}
GET  /api/games/my-scores
```

Supported `game_key` values: `fruit_slice`, `memory_match`, `tic_tac_toe`, `2048`.

## Admin

The first user who signs up with the email in `ADMIN_EMAIL` becomes admin.

```
GET  /api/admin/stats
GET  /api/admin/users
POST /api/admin/users/{id}/toggle-active
POST /api/admin/users/{id}/force-verify
POST /api/admin/wallet/adjust       { user_id, amount, note? }
```

## Deploy to Render (free tier)

1. Push this folder to a GitHub repo.
2. Render → New → Blueprint → pick the repo. Render reads `render.yaml`, provisions a free web service + free Postgres, and wires `DATABASE_URL` automatically.
3. Set the `sync: false` env vars in the Render dashboard (admin email, SMTP creds, frontend URL, etc.).
4. Deploy. Your API is live at `https://arcade-hub-api.onrender.com`.

## Deploy with Docker

```bash
docker build -t arcade-api .
docker run -p 8000:8000 --env-file .env arcade-api
```

## Security checklist before going live

- [ ] Set a long random `SECRET_KEY`
- [ ] Set `CORS_ORIGINS` to your actual frontend domain (not `*`)
- [ ] Configure real SMTP and set `EMAIL_CONSOLE_FALLBACK=false`
- [ ] Use Postgres (not SQLite) for production
- [ ] Put the API behind HTTPS (Render does this automatically)
