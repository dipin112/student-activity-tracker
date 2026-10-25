# Student Activity Tracker

A simple activity tracker for students, built with React and Django. Students can record activities and hours, while admins can review the log and summary.

## Run locally

Open two terminals from this project folder:

```powershell
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver
```

```powershell
cd clientapp
npm.cmd install
npm.cmd run dev
```

Visit the URL printed by Vite (normally `http://localhost:5173`) to use the tracker. The admin sign-in page is at `http://127.0.0.1:8000/`; the dashboard opens after signing in. The Django API runs at `http://127.0.0.1:8000/api/`.

## Django superuser

Create a superuser to sign in to Django Admin at `http://127.0.0.1:8000/admin/`:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

Follow the prompts to set the username, email, and password. The `Activity` model is available in Django Admin after signing in.

## API

- `GET /api/activities/` lists all activities.
- `POST /api/activities/` accepts JSON: `name`, `activity`, `hours`.
- `GET`, `PUT`, `PATCH`, and `DELETE /api/activities/<id>/` retrieve, edit, or remove one activity.
- `GET /api/summary/` returns total entries, total hours, and the most active student.

Run the backend test suite with:

```powershell
.\venv\Scripts\python.exe manage.py test
```
