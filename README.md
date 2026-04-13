# 💳 NovaPay — Banking Management System

A full-stack banking management system built with **FastAPI**, **PostgreSQL**, and **React (Vite)**. Features JWT authentication, secure password hashing, account management, and transaction tracking.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, CSS Modules |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT (python-jose), bcrypt 5.x |
| Validation | Pydantic v2 |

---

## 📁 Project Structure

```
bank-fastapi/
├── backend/
│   ├── main.py           # FastAPI routes and app entry point
│   ├── models.py         # SQLAlchemy database models
│   ├── auth.py           # JWT + bcrypt authentication logic
│   ├── migrations/       # Alembic migration files
│   │   └── versions/
│   ├── alembic.ini       # Alembic configuration
│   ├── .env              # Environment variables (never commit!)
│   └── requirements.txt  # Python dependencies
│
└── frontend/
    └── src/
        ├── App.jsx           # Main app + all page components
        ├── App.css           # Buttons, forms, table, modal styles
        ├── index.css         # Global variables, fonts, reset
        ├── Sidebar.css       # Sidebar + navigation styles
        ├── Auth.css          # Login / Register page styles
        └── Accounts.css      # Stat cards + account card styles
```

---

## ⚙️ Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- pip
- npm

---

## 🛠️ Backend Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/bank-fastapi.git
cd bank-fastapi/backend
```

### 2. Create and activate virtual environment

```bash
python -m venv myenv

# Windows
myenv\Scripts\activate

# macOS / Linux
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic \
            bcrypt python-jose[cryptography] python-dotenv pydantic
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL database

```sql
CREATE DATABASE banking_db;
```

### 5. Configure environment variables

Create a `.env` file in the `backend/` directory:

```env
SECRET_KEY=your_generated_secret_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/banking_db
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the backend server

```bash
uvicorn main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

API Docs available at: `http://127.0.0.1:8000/docs`

---

## 🎨 Frontend Setup

### 1. Navigate to frontend directory

```bash
cd ../frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the development server

```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🔐 Authentication Flow

```
POST /auth/register   →  Create new user (bcrypt hashed password)
POST /auth/login      →  Returns JWT access token (valid 8 hours)
GET  /auth/verify     →  Verify token validity + expiry in IST
```

All account and transaction routes require:
```
Authorization: Bearer <your_token>
```

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login and get token | ❌ |
| GET | `/auth/verify` | Verify token | ✅ |

### Accounts
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/accounts` | List all accounts | ✅ |
| POST | `/accounts` | Create new account | ✅ |
| GET | `/accounts/{id}` | Get account by ID | ✅ |
| PUT | `/accounts/{id}` | Update account | ✅ |
| DELETE | `/accounts/{id}` | Delete account | ✅ |

### Transactions
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/transactions` | List all transactions | ✅ |
| POST | `/transactions` | Create transaction | ✅ |
| GET | `/transactions/{account_id}` | Get by account | ✅ |
| DELETE | `/transactions/{id}` | Delete transaction | ✅ |

---

## 🗄️ Database Schema

```
users
├── id              VARCHAR(36)   PRIMARY KEY
├── username        VARCHAR(255)  UNIQUE NOT NULL
└── hashed_password VARCHAR(255)  NOT NULL

accounts
├── id              VARCHAR(36)   PRIMARY KEY
├── account_number  VARCHAR(20)   UNIQUE NOT NULL  ← auto-generated 12-digit
├── name            VARCHAR(255)  NOT NULL
└── balance         FLOAT         NOT NULL

transactions
├── id              VARCHAR(36)   PRIMARY KEY
├── account_id      VARCHAR(36)   FK → accounts.id
├── amount          FLOAT         NOT NULL  ← negative for withdrawals
└── description     VARCHAR(255)
```

---

## 🔒 Security Features

- **bcrypt 5.x** password hashing with SHA-256 pre-processing to handle 72-byte limit
- **JWT tokens** signed with HS256 algorithm
- **SECRET_KEY** loaded from `.env` — never hardcoded
- **OAuth2 password flow** for Swagger UI authorization
- **Protected routes** via `get_current_user` dependency
- **CORS** configured for frontend origin only

---

## 🗃️ Alembic Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

---

## 🌐 Frontend Features

- 🔐 Login / Register with JWT token management
- 🏠 Dashboard with total balance, accounts, deposits stats
- 🏦 Accounts — create, edit, delete with auto account numbers
- 🔄 Transactions — create, delete, filter by account
- 📱 Responsive sidebar (collapses on mobile)
- 🔔 Toast notifications for all actions
- 💰 Indian Rupee (₹) formatting with `en-IN` locale

---

## 📦 requirements.txt

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
alembic
bcrypt==5.0.0
python-jose[cryptography]
python-dotenv
pydantic
```

---

## 🚫 .gitignore

```
# Environment
.env
myenv/
__pycache__/
*.pyc

# Node
node_modules/
dist/

# Database
*.db
*.sqlite
```

---

## 👨‍💻 Author

**Raaghav**
- GitHub: [@yourusername](https://github.com/yourusername)

---

## 📄 License

This project is licensed under the MIT License.