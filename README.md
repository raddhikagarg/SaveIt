# SaveIt

https://saveit-frontend.onrender.com/login

### Problem Statement:

Application Development for AI-powered Opportunity Tracking from Social Media & Government Platforms

### Problem statement description :

Students discover internships, scholarships, hackathons, and government schemes every day through Instagram Reels, Telegram, WhatsApp, and websites. However, these opportunities are often lost due to scattered bookmarks, forgotten deadlines, and unstructured information.

SaveIt provides a unified platform that automatically extracts, organizes, and reminds users about important opportunities before they expire.

---

### Idea Description :

SaveIt is an AI-powered opportunity tracker designed for students and young professionals. Users can simply share an Instagram Reel, Telegram message, or any opportunity link, and SaveIt automatically extracts the title, deadline, eligibility, stipend, and organizer using a multi-stage AI pipeline.

The platform also features **Govt Radar**, a curated feed of verified opportunities from MyBharat, National Scholarship Portal, and PM Internship Scheme, ensuring users never miss important government initiatives.

---

### Abstract / Summary :

SaveIt solves the problem of opportunity overload by transforming unstructured social media content into a personalized deadline-aware dashboard. Instead of manually saving posts or remembering dates, users receive structured opportunity cards, confidence-based deadline verification, and timely reminders.

By combining AI extraction with verified government opportunity aggregation, SaveIt becomes a single destination for discovering and tracking career opportunities.

---

### Status :

We have implemented the following features:

- User authentication using JWT
- Personal opportunity tracker dashboard
- Government opportunity feed (Govt Radar)
- AI-powered extraction pipeline for reels, links & messages
- Deadline confirmation for low-confidence extractions
- Opportunity detail pages with structured information
- Telegram account linking infrastructure

---

## Tech Stacks Used :

### ⦿ Frontend :

- Next.js (App Router)
- TypeScript
- Tailwind CSS

### ⦿ Backend :

- FastAPI
- SQLAlchemy
- Pydantic

### ⦿ Database :

- SQLite (Development)

### ⦿ AI & APIs :

- Claude API
- Whisper
- Tesseract OCR
- Tavily Search

---

## Important URLs :

### Live Application

https://saveit-frontend.onrender.com/login

### Local Development

**Frontend:**  
http://localhost:3000

**Backend:**  
http://localhost:8000

**Backend Health Check:**  
http://localhost:8000/health

---

## Project Structure

```text
SaveIt/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── tracker/
│   │   ├── govt-radar/
│   │   ├── opportunity/[id]/
│   │   └── components/
│   ├── lib/
│   └── package.json
│
└── README.md
```

---

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/simarjitwaves/saveit.git
cd saveit
```

### Run the Backend

```bash
cd backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000**

### Run the Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

---

## Future Scope

- Push & email deadline reminders
- Duplicate opportunity detection
- AI-powered personalized opportunity recommendations
- Multi-language extraction support

