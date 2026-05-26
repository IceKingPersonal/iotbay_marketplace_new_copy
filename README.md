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

### Terminal 1 — Backend

```powershell
cd backend
python app.py
```

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

Then open the frontend in your browser:

```text
http://localhost:5173
```

---

## Database Note

The SQLite database file is not included in the repository.

After cloning the project, each user must create their own local database by running:

```powershell
cd backend
python init_db.py
```

This creates the required database tables and sample data.

---
