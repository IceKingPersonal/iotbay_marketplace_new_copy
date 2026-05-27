# IoT Bay — Marketplace prototype (R0)

Software prototype for the IoT Bay marketplace: a React (Vite) frontend and a Flask API with SQLite. Login and Register still perform **browser-side format checks**, then call **`POST /api/v1/users/bootstrap`** so the UI receives a **`user_uid`** for cart and order API calls (prototype auth uses the **`X-User-Id`** header, not production-grade sessions).

## Target branch

Use the "main" branch for this prototype.

## Dependencies

### Prerequisites

- Python 3.10 or newer
- pip (bundled with Python)
- Node.js 18+ and npm (frontend only)

### Frontend dependencies (`frontend/package.json`)

- `react`
- `react-dom`
- `react-router-dom`
- `vite`
- `eslint`

Install with:

```bash
cd frontend
npm install
```

### Backend dependencies (`backend/requirements.txt`)

- `flask`
- `flask-cors`
- SQLite is provided by Python's built-in `sqlite3` module (no extra package required)

Install with:

```bash
cd backend
python -m pip install -r requirements.txt
```

### Project structure

| Area        | Stack                                      |
| ----------- | ------------------------------------------ |
| Frontend    | React 19, Vite 7, React Router |
| Backend     | Flask 3, Python 3.10+, `sqlite3` (stdlib)  |
| Database    | SQLite (file `backend/data/iotbay.db`)     |

Install dependencies separately for each app (see below).

## Run on localhost

### 1. Clone and checkout

```bash
git clone "github.com/isd-2026/project-assignment-iotbay-marketplace-workshop04-group1"
cd project-assignment-iotbay-marketplace-workshop04-group1
git checkout main
```

### 2. Frontend (browser UI)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Run the **backend** at the same time so Login/Register can bootstrap a user. **Vite proxies** `/api` → `http://localhost:3001` during `npm run dev` (see `frontend/vite.config.ts`). Use **Shop** → add to cart → **Cart** → checkout → **Orders** → open an order to try **PATCH**/**PUT** status updates.

### 3. Backend (API + database)

In a **second** terminal:

```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

- API base: **http://localhost:3001**
- Health: `GET http://localhost:3001/health`
- DB check: `GET http://localhost:3001/api/db-check` — returns SQLite version when the file DB is connected

On first run, the server creates `backend/data/` and `iotbay.db`, seeds demo products if the catalog is empty, then initializes schema tables from `backend/db.py`.

### 4. Status / cart / orders API (summary)

| Method | Path | Purpose |
| ------ | ---- | ------- |
| POST | `/api/v1/users/bootstrap` | Create or return `user_uid` for an email |
| GET | `/api/v1/products` | Demo catalog |
| GET | `/api/v1/cart` | Current open cart + lines (`X-User-Id`) |
| POST | `/api/v1/cart/items` | Add / merge line (`X-User-Id`) |
| PATCH | `/api/v1/cart/items/:id` | Update line quantity |
| DELETE | `/api/v1/cart/items/:id` | Remove line |
| PATCH | `/api/v1/cart/:cartId` | Update cart `status` (`open` \| `checked_out` \| `abandoned`) |
| POST | `/api/v1/cart/checkout` | Place order (`Saved` status, stock decremented) |
| GET | `/api/v1/orders` | List orders for user |
| GET | `/api/v1/orders/:orderId` | Order + device line items |
| PATCH | `/api/v1/orders/:orderId` | Update status (`Saved` \| `Paid` \| `Cancelled`) |
| PUT | `/api/v1/orders/:orderId` | Full replace: `shipping_address`, `total_price`, `currency`, `status` |

Order `status` values: **Saved** (on placement), **Paid**, **Cancelled** (restores stock). Devices with 0 stock cannot be added to cart or ordered.

### Ports

| Service   | Port |
| --------- | ---- |
| Vite dev  | 5173 |
| Flask     | 3001 |

Override the API port with `PORT` (PowerShell: `$env:PORT=4000; python app.py` in `backend`). If you change the backend port, update `frontend/vite.config.ts` proxy `target` or set `VITE_API_BASE` to the full API origin.

## Running the Application

To run the full application, both the backend and frontend servers must be running at the same time.

### Terminal 1 - Backend

```powershell
cd backend
python app.py
```

### Terminal 2 - Frontend

```powershell
cd frontend
npm run dev
```

Then open the frontend in your browser:

```text
http://localhost:5173
```

### Feature 02 - IoT Device Catalogue

After logging in, open the dashboard and select `Feature 02 - IoT Device Catalogue Management`, or use the navbar link named `Devices`. If a user is not logged in, the page shows a login-required message. If the backend returns an unauthorized response because the session has expired, the frontend clears the device page state and returns the user to the login page.

The device catalogue page is available at:

```text
http://localhost:5173/devices
```

The page uses the backend device catalogue API:

```text
GET http://localhost:5000/api/devices
```

Staff users can create, update, archive, and audit device records through the protected `/api/devices` endpoints. Device records require a name, category/type, brand, model, price, stock quantity, condition, and status. The backend validates device categories, numeric price and stock ranges, condition values, and status values before saving records.

Run the backend database setup before using Feature 02 so the device catalogue tables exist:

```powershell
cd backend
python init_db.py
```

---

## Database Note

The SQLite database file is not included in the repository.

After cloning the project, each user must create their own local database by running:

```powershell
cd backend
python init_db.py
```

This creates the required database tables and sample data, including dummy
Feature 02 device catalogue records. The seeded devices cover every supported
device category, condition, and status value used by the backend validation.

---

## Test Scripts

The Python test scripts are located in the root-level test folder:

```text
tests
```

Run tests from a new third terminal after the backend and frontend are already
running in their own terminals.

### Terminal 3 - Tests

From the main project folder, activate the local virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the full test suite:

```powershell
python -m pytest tests
```

Run the original Feature 01 test script:

```powershell
python -m pytest tests/test_feature01.py
```

Run the original combined Feature 02 test script:

```powershell
python -m pytest tests/test_feature02.py
```

Run only the Feature 02 user-story tests:

```powershell
python -m pytest tests/test_feature02_story01_create_devices.py
python -m pytest tests/test_feature02_story02_browse_catalogue.py
python -m pytest tests/test_feature02_story03_search_devices.py
python -m pytest tests/test_feature02_story04_update_devices.py
python -m pytest tests/test_feature02_story05_delete_devices.py
```

Run one individual test function by adding `::test_name` to the script path:

```powershell
python -m pytest tests/test_feature02_story01_create_devices.py::test_api_staff_can_create_device
```

Each Feature 02 story test script includes unit tests, API tests, and an E2E-style
Flask client workflow for its user story and acceptance criteria.

---
