# SaveIt

https://saveit-frontend.onrender.com/login

**From Reel to Reminder — Never Miss an Opportunity Again**

A deadline-aware opportunity tracker that turns Instagram reels, Telegram messages, and shared links into structured, reminder-synced tracked opportunities — plus a curated feed of Government of India schemes via MyBharat, NSP, and PM Internship Scheme.

---

## What it does

- **My Tracker** — share a reel, link, or message to our Telegram bot; a three-stage AI extraction pipeline (media → linked page → live web search fallback) pulls out the title, deadline, eligibility, and stipend, and tracks it for you with reminders.
- **Govt Radar** — a browsable, curated feed of government opportunities (MyBharat, NSP, PM Internship Scheme) that anyone can browse without signing in.
- **Confidence-aware extraction** — low-confidence deadline extractions are flagged for a one-tap user confirmation instead of being silently trusted.
- **Account linking** — sign up on the web, then link your Telegram account with a short code so anything you send the bot shows up on your dashboard.

## Tech stack

**Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
**Backend:** FastAPI, SQLAlchemy, SQLite (dev), JWT auth
**Extraction pipeline:** Claude API (structured extraction), Whisper (speech-to-text), Tesseract/Cloud Vision (OCR), Tavily (search fallback)


## Getting started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env           # fill in your own API keys
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Check `http://localhost:8000/health` to confirm it's up.

> **Note:** Use Python 3.11 or 3.12. Some dependencies (Pillow, pydantic-core) don't yet have pre-built wheels for very new Python versions on Windows.

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
NEXT_PUBLIC_API_URL=http://localhost:8000


```bash
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Environment variables (backend)

See `backend/.env.example` for the full list. Minimum to run locally:
- `DATABASE_URL` (defaults to local SQLite, no setup needed)
- `JWT_SECRET_KEY` (any random string)

Optional (features degrade gracefully without them):
- `ANTHROPIC_API_KEY` — LLM extraction
- `OPENAI_API_KEY` — Whisper transcription
- `TAVILY_API_KEY` — Stage 3 search fallback
- `TELEGRAM_BOT_TOKEN` — Telegram intake bot

