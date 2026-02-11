# ⚡ AutoFill-GForm Pro

**Intelligent Google Form Auto Filling Platform**

A production-ready system that automatically fills Google Forms using your stored profile data and an AI agent for missing answers.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | JWT + bcrypt based signup/login with auto-login |
| 👤 **Profile Management** | Store all personal data used for form filling |
| 🤖 **AI Agent** | Generates realistic answers for unknown questions |
| 🧠 **Smart Matching** | Sentence embeddings match questions to profile fields |
| 📝 **Auto Form Filler** | Playwright engine detects & fills all field types |
| 📋 **History & Logs** | Full audit trail of every form fill operation |
| 💡 **Learned Mappings** | System remembers answers for future re-use |
| 🌐 **Web Dashboard** | Premium dark-mode UI for all operations |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   FastAPI Backend │────▶│  SQLite Database│
│   (HTML/JS/CSS) │     │                  │     │                 │
└─────────────────┘     │  ┌─────────────┐ │     └─────────────────┘
                        │  │ Auth (JWT)   │ │
                        │  ├─────────────┤ │     ┌─────────────────┐
                        │  │ AI Agent     │ │────▶│ Sentence        │
                        │  │ (NLP Match)  │ │     │ Transformers    │
                        │  ├─────────────┤ │     └─────────────────┘
                        │  │ Form Filler  │ │
                        │  │ (Playwright) │ │────▶ Google Forms
                        │  └─────────────┘ │
                        └──────────────────┘
```

---

## 📂 Folder Structure

```
form_filler/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # All configuration
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT authentication
│   │   ├── routes/
│   │   │   ├── auth_routes.py   # Auth endpoints
│   │   │   ├── profile_routes.py# Profile CRUD
│   │   │   └── form_routes.py   # Form fill endpoints
│   │   ├── services/
│   │   │   ├── ai_agent.py      # AI answer generation
│   │   │   ├── question_matcher.py  # Embedding-based matching
│   │   │   └── form_filler.py   # Playwright automation
│   │   └── utils/
│   │       └── security.py      # bcrypt hashing
│   ├── data/                    # SQLite database
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Login / Signup
│   ├── dashboard.html           # Form filling dashboard
│   ├── profile.html             # Profile management
│   ├── history.html             # Fill history
│   ├── css/
│   │   └── style.css            # Design system
│   └── js/
│       ├── api.js               # API client
│       ├── auth.js              # Auth logic
│       ├── dashboard.js         # Dashboard logic
│       ├── profile.js           # Profile logic
│       └── history.js           # History logic
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- pip
- Internet connection (for downloading models)

### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 4: Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 5: Open in Browser

Navigate to: **http://localhost:8000**

---

## 🔄 Example Workflow

### 1. Sign Up
Create an account with username, email, and password.

### 2. Set Up Profile
Fill in all your personal details:
- Name, Register Number, Department, Year
- Email, Phone, Gender, College
- **Skills, Interests, Bio** ← Critical for AI!

### 3. Fill a Form
1. Copy a Google Form link
2. Paste it in the dashboard
3. Toggle "Auto-submit" if desired
4. Click **⚡ Auto Fill**

### 4. Watch it Work
The system will:
- Open the form in a headless browser
- Detect all questions and field types
- Match questions to your profile fields using sentence embeddings
- Generate AI answers for unmatched questions
- Fill all fields automatically
- Optionally submit the form

### 5. Review Results
- Real-time status updates on the dashboard
- Detailed log showing each question, answer, and source
- Full history available on the History page

---

## 🤖 How AI Fills Missing Answers

### Smart Question Matching (Sentence Embeddings)

The system uses `all-MiniLM-L6-v2` sentence transformer model to compute embeddings:

1. Each profile field has multiple description phrases
2. Incoming form questions are encoded as embeddings
3. Cosine similarity is computed between question and all field descriptions
4. Best match above threshold (0.45) is selected

**Example:**
```
Question: "What is your registration number?"
→ Matches "register_number" field (similarity: 0.87)
→ Fills with stored register number
```

### AI Agent for Unknown Questions

When no profile field matches:

1. The agent reads your full profile + bio
2. Classifies the question type (motivation, about, skills, etc.)
3. Generates a contextual answer using your data
4. Saves the answer as a "learned mapping" for future use

**Example:**
```
Question: "Why do you want to join this club?"
→ No profile field match
→ AI reads: interests="AI/ML, Web Dev", bio="Passionate CS student..."
→ Generates: "I am deeply interested in AI/ML and Web Development.
   As a Computer Science student, I believe this club aligns
   perfectly with my goals and interests."
```

### AI Modes

| Mode | Config | Description |
|------|--------|-------------|
| **Local** (default) | `AI_MODE=local` | Template-based generation using profile context |
| **OpenAI** | `AI_MODE=openai` | Uses GPT API for richer generation |

To use OpenAI, set environment variables:
```bash
set AI_MODE=openai
set OPENAI_API_KEY=sk-your-key-here
```

---

## 🔐 Security Best Practices

1. **Password Hashing**: All passwords are hashed with bcrypt (never stored in plain text)
2. **JWT Tokens**: Stateless authentication with configurable expiration (default: 7 days)
3. **User Isolation**: Each user can only access their own data
4. **Input Validation**: Pydantic schemas validate all inputs
5. **CORS Policy**: Configurable cross-origin settings
6. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
7. **No Hardcoded Credentials**: All secrets via environment variables

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | auto-generated | JWT signing key |
| `AI_MODE` | `local` | AI mode: `local` or `openai` |
| `OPENAI_API_KEY` | ` ` | OpenAI API key (if using openai mode) |
| `HEADLESS` | `true` | Run browser headless |
| `SLOW_MO` | `100` | Playwright slow motion (ms) |

---

## 📡 API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Verify token |

### Profile
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/profile/` | Get profile |
| POST | `/api/profile/` | Create/update profile |
| PUT | `/api/profile/` | Update profile |

### Forms
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/forms/fill` | Start form fill |
| GET | `/api/forms/status/{id}` | Check fill status |
| GET | `/api/forms/history` | Get fill history |
| GET | `/api/forms/mappings` | Get learned mappings |
| DELETE | `/api/forms/mappings/{id}` | Delete mapping |

---

## ⚠️ Disclaimer

This tool is designed for **personal use** to fill forms with your **own data**. 
- Do NOT use to spam or abuse Google Forms
- Do NOT use to submit false information
- Respect Google's Terms of Service
- Use responsibly

---

## 📄 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python + FastAPI |
| Database | SQLite + SQLAlchemy |
| Auth | JWT + bcrypt |
| Automation | Playwright |
| AI/NLP | Sentence Transformers (all-MiniLM-L6-v2) |
| Frontend | HTML + CSS + JavaScript |

---

**Built with ❤️ — AutoFill-GForm Pro v1.0.0**
