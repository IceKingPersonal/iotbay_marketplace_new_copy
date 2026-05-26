## Backend Installation and Setup

Open a terminal in the main project folder.

Go into the backend folder:

```powershell
cd backend
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

Create the SQLite database:

```powershell
python init_db.py
```

Run the backend server:

```powershell
python app.py
```

The backend should now be running at:

```text
http://127.0.0.1:5000
```

---

## Frontend Installation and Setup

Open a second terminal in the main project folder.

Go into the frontend folder:

```powershell
cd frontend
```

Install the frontend dependencies:

```powershell
npm install
```

Run the frontend development server:

```powershell
npm run dev
```

The frontend should now be running at:

```text
http://localhost:5173
```

---

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
