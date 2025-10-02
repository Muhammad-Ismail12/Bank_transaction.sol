## Clinic App (FastAPI)

A simple full-stack clinic management app built with FastAPI, SQLAlchemy (SQLite), and Jinja2 templates. Includes authentication (JWT in HttpOnly cookies), and CRUD for Patients, Doctors, and Appointments with a basic schedule view.

### Features
- Authentication with JWT cookies (seeded admin account)
- Patients CRUD
- Doctors CRUD
- Appointments CRUD
- Weekly schedule view by doctor

### Requirements
- Python 3.10+

### Setup
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

If you prefer running via Python module:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Default Admin
- Username: `admin`
- Password: `admin123`

Change these via environment variables in a `.env` file at the project root:
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
SECRET_KEY=please-change-this
```

### Project Structure
```
app/
  main.py
  database.py
  models.py
  core/
    config.py
  auth/
    security.py
  routers/
    auth.py
    patients.py
    doctors.py
    appointments.py
  templates/
    base.html
    login.html
    patients/
      list.html
      form.html
    doctors/
      list.html
      form.html
    appointments/
      list.html
      form.html
      schedule.html
  static/
    css/
      styles.css
```

### Notes
- This project uses SQLite for simplicity. You can switch to Postgres/MySQL by updating `app/database.py` and installing the appropriate driver.
- JWT is stored in an HttpOnly cookie named `access_token`.
