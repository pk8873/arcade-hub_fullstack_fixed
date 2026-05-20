# Arcade Hub — Full Stack (FastAPI + React)

A complete, free-to-deploy arcade web app. Backend in Python (FastAPI),
frontend in React + Vite + TanStack Router. Auth with auto email
verification, JWT, virtual-coin wallet, game leaderboards, admin dashboard.

> **Virtual coins only — not a real-money / gambling platform.**

```
arcade-hub/
├── render.yaml          ← one-click deploy (backend + frontend + Postgres)
├── arcade-backend/      ← FastAPI (Python)
└── arcade-frontend/     ← Vite + React + TanStack Router (TypeScript)
```

## 1. Run locally (zero config)

### Backend
```bash
cd arcade-backend
python -m venv .venv && source .venv/bin/activate   # win: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```
- API: http://localhost:8000 · Docs: http://localhost:8000/docs
- Default admin auto-created on first boot: **admin@gmail.com / admin123**
- No SMTP configured? Verification links are printed to the server console.

### Frontend
```bash
cd arcade-frontend
cp .env.example .env       # VITE_API_URL defaults to http://localhost:8000
npm install
npm run dev
```
Open http://localhost:5173. Sign up, log in as admin, play games, view wallet.

## 2. One-click deploy to Render (free tier)

1. Push this whole folder to a GitHub repo.
2. https://dashboard.render.com → **New +** → **Blueprint** → pick the repo.
3. Render reads `render.yaml`, provisions:
   - `arcade-hub-api` — FastAPI web service
   - `arcade-hub-web` — Vite static site
   - `arcade-hub-db` — free Postgres
4. Click **Apply**. After ~3 minutes the URLs are live.
5. (Optional but recommended) In the Render dashboard:
   - Change `ADMIN_PASSWORD` from `admin123` to something real.
   - Fill SMTP env vars (Gmail App Password, Brevo, etc.) for real emails.
   - Restrict `CORS_ORIGINS` from `*` to your frontend URL.

## 3. 100% free stack — no paid services required

| Layer       | Free option used                                  |
|-------------|---------------------------------------------------|
| Backend     | Render free web service (sleeps when idle)        |
| Frontend    | Render static site (or Netlify / Vercel / Cloudflare Pages) |
| Database    | Render free Postgres, or SQLite (file)            |
| Email       | Gmail App Password / Brevo 300-free-per-day / Mailtrap sandbox |
| Auth        | JWT (no external auth provider needed)            |

## 4. Auto email verification

1. User signs up → backend mails a one-click verify link automatically.
2. Link points at `GET /api/auth/verify?token=...` → flips `is_verified`,
   redirects to `FRONTEND_URL/verified`.
3. Frontend also exposes `/verify?token=...` which calls the JSON endpoint
   so you can stay inside the app.
4. `POST /api/auth/resend-verification` triggers a new email at any time.

If `SMTP_HOST` is empty, the verification email is printed to the server
console — copy the link from the logs and click it to verify in local dev.

## 5. Free SMTP providers that work out of the box

| Provider     | Host                       | Port | Notes                          |
|--------------|----------------------------|------|--------------------------------|
| Gmail        | `smtp.gmail.com`           | 587  | Use an **App Password**        |
| Brevo        | `smtp-relay.brevo.com`     | 587  | 300 free emails/day            |
| Mailtrap     | `sandbox.smtp.mailtrap.io` | 587  | Dev sandbox, no real delivery  |
| Mailgun      | `smtp.mailgun.org`         | 587  | Free sandbox domain            |

Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
in the backend env.

## 6. Frontend pages

| Route        | What it does                                    |
|--------------|-------------------------------------------------|
| `/`          | Landing page                                    |
| `/signup`    | Create account (auto-sends verify email)        |
| `/login`     | Log in                                          |
| `/verify`    | Frontend verify page (reads `?token=`)          |
| `/verified`  | Success page after backend redirect             |
| `/dashboard` | Profile, wallet balance, resend-verify          |
| `/games`     | Submit demo scores, view leaderboards           |
| `/wallet`    | Balance + full transaction history              |
| `/admin`     | (admin only) users, stats, coin adjustments     |

## 7. Hard limits (be aware)

- **Demo game logic only.** "Play" submits a random score so you can see
  scores, coins, and leaderboards working end-to-end. Real playable game
  engines (Ludo, Rummy, multiplayer matchmaking) are a separate, much larger
  build.
- **No real money / payments / KYC / RBI compliance.** Coins are virtual.
- **Default admin password is `admin123` — change it before going public.**
- **Render free tier sleeps the backend after inactivity** (~50s cold start
  on first hit). Upgrade or use a keep-alive ping for production.

## 8. Security checklist before going public

- [ ] Change `ADMIN_PASSWORD` env var on Render
- [ ] Set `CORS_ORIGINS` to your actual frontend URL (not `*`)
- [ ] Set a long random `SECRET_KEY` (Render's `generateValue` does this)
- [ ] Configure real SMTP and set `EMAIL_CONSOLE_FALLBACK=false`
- [ ] Use Postgres (Render does this automatically via `render.yaml`)
