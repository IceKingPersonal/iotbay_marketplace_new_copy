# IoTBay Marketplace

IoTBay Marketplace is a React and Flask prototype for user accounts, access logs,
device catalogue management, and customer orders. The active application uses a
React/Vite frontend, a Flask API, and a local SQLite database.

## Tech Stack

| Area | Stack |
| --- | --- |
| Frontend | React 19, Vite 8, React Router |
| Backend | Python, Flask, Flask-Cors, Werkzeug |
| Database | SQLite via Python `sqlite3` |
| Tests | pytest |

The active Flask app is `backend/app.py`. It registers these API families:

- `/api/auth`
- `/api/users`
- `/api/access-logs`
- `/api/devices`
- `/api/orders`

Some legacy R0 files remain in the repository for reference and structure
compatibility, but the active Flask app does not register the legacy cart,
products, or bootstrap-user blueprints.

## Setup

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- npm

### Backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python init_db.py
python app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

The SQLite database is created at:

```text
backend/iotbay.db
```

### Frontend

Open a second terminal in the project root:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

The frontend API client sends requests to:

```text
http://localhost:5000/api
```

## Frontend Routes

- `/` - login
- `/register` - registration
- `/dashboard` - feature dashboard
- `/profile` - view profile
- `/edit` - edit profile
- `/access-logs` - login/logout history
- `/devices` - device catalogue
- `/orders` - order list
- `/orders/:orderId` - order details

## Running The App

Run the backend and frontend at the same time:

```powershell
# Terminal 1
cd backend
python app.py
```

```powershell
# Terminal 2
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

Seed users created by `python init_db.py`:

| Role | Email | Password |
| --- | --- | --- |
| Customer | `customer@test.com` | `Password123` |
| Staff | `staff@test.com` | `Password123` |

## Tests

Run backend tests from the backend folder:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests
```

If you are using the backend-local virtual environment instead:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests
```

Run frontend checks from the frontend folder:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

## Feature Notes

Feature 01 covers user registration, login, profile, account cancellation, and
access logs.

Feature 02 covers device catalogue browsing, searching, creation, updates,
archiving, bulk deletion, and audit logs. Staff users can manage devices.

Feature 03 covers order listing, order creation through the backend API, order
detail viewing, and customer status updates for saved orders.
