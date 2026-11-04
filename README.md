# PlacementPilot — Python / Django edition

PlacementPilot is a campus placement management portal built with Python, Django templates, HTML/CSS/JavaScript and a database backend. It has three role-based workspaces: student, administrator and recruiter.

## Included modules

- Student registration and login (username or email), profile and academic details
- Role-based dashboards for students, administrators and recruiters
- Company and placement-drive management
- Eligibility checks using CGPA, department, backlogs, drive deadline, listed skills, LeetCode solved problems
- Student LeetCode username, public profile link and self-reported solved count
- Placement-office verification flags for coding-platform counts (managed in Django admin)
- A dedicated eligible-drives list, plus per-drive eligibility reasons
- A "Remember me" option for the PlacementPilot account (14-day session); passwords remain Django-hashed and are never stored in plain text
- Student applications and status updates (pending, shortlisted, rejected, selected)
- Notifications for application submission and status changes
- Resume text extraction for PDF, DOCX, TXT and Markdown files
- Skill keyword matching and comparison against active placement drives
- Django admin at `/django-admin/`
- Optional fictional demo data command

## 1. Requirements

- Python 3.10 or newer (Python 3.11/3.12 recommended)
- Windows 10/11, macOS or Linux
- SQLite for the quickest local run, or MySQL 8+ if required by your project setup

## 2. Install and run on Windows PowerShell

Open PowerShell in the extracted `PlacementPilot-Python` folder (the folder containing `manage.py`).

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations portal
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Open **http://127.0.0.1:8000/**.

You do not need to activate the virtual environment, and these commands avoid PowerShell's `Activate.ps1` execution-policy issue. If `py -3` is not recognised, use `python -m venv .venv` in its place.

## 3. Administrator and recruiter access

Create the administrator with `createsuperuser`. Sign in at `/login/` to use the main admin dashboard. Staff/superuser accounts receive administrator access automatically. The Django admin interface is available at `/django-admin/`.

An administrator can create recruiter accounts from **Recruiters** in the main portal. Recruiters can create and manage their own drives and review applications for those drives.

For a quick demonstration with sample logins, instead of (or in addition to) the normal `seed_demo` command, run:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo --with-users
```

This creates fictional demo accounts:

- Student: `student_demo` / `DemoPass123!`
- Recruiter: `recruiter_demo` / `DemoPass123!`

Change or delete these accounts before any deployment. Sample company and drive data is fictional.

## 4. MySQL configuration

The project starts with SQLite by default so the first run does not require a MySQL server. To use MySQL 8+, create a database named `placementpilot` with `utf8mb4`, then set these environment variables in the same PowerShell window before running `manage.py migrate` and `runserver`:

```powershell
$env:DB_ENGINE = "mysql"
$env:DB_NAME = "placementpilot"
$env:DB_USER = "root"
$env:DB_PASSWORD = "YOUR_MYSQL_PASSWORD"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
```

Then run the `makemigrations` (if not already created) and `migrate` commands. `PyMySQL` is used as the pure-Python MySQL driver to avoid compiling `mysqlclient` on Windows. Keep the DB environment variables set in the terminal used to start Django.

## 5. Main routes

| Route | Purpose |
|---|---|
| `/` | Public landing page |
| `/register/` | Student registration |
| `/login/` | Sign in |
| `/dashboard/` | Role-based dashboard |
| `/profile/` | Student academic profile |
| `/drives/` | Browse placement drives and see eligibility badges |
| `/eligible-drives/` | Show only drives matching the student's current profile |
| `/applications/` | Application tracking / candidate review |
| `/resume-analyzer/` | Resume text and skill-gap analysis |
| `/manage/students/` | Administrator student directory |
| `/manage/companies/` | Company management |
| `/manage/drives/` | Admin/recruiter drive management |
| `/manage/recruiters/` | Admin recruiter account creation |
| `/django-admin/` | Django's built-in admin |

## 6. Resume analysis notes

Supported files are PDF, DOCX, TXT and MD, with a 5 MB upload limit. The analyzer extracts text and matches a curated keyword list. Scanned/image-only PDFs may not contain extractable text. This is an assistive keyword tool, not an AI assessment or proof of proficiency.

## 7. Important project notes

- The placement eligibility logic is based on criteria stored on each drive: minimum CGPA, maximum backlogs, eligible departments, active status/deadline, required skills, minimum LeetCode solved count. A threshold of 0 means LeetCode is not required for that drive.
- Students enter their LeetCode usernames, public profile URLs and completion counts in **My profile**. Counts are self-reported and visibly marked as such until the placement office verifies them in `/django-admin/`. Any profile edit resets the LeetCode verification flag.
- The project does not automatically scrape LeetCode. LeetCode's terms prohibit crawling/scraping. For this college-project build, manual counts + profile links + staff verification avoid collecting third-party credentials or relying on unofficial endpoints.
- Never enter LeetCode passwords in PlacementPilot. The Remember me option only keeps the PlacementPilot login session active for 14 days; Django stores the PlacementPilot password using its password-hashing system. Browser password managers can be used for autofill if desired.
- Status changes notify the student in the portal.
- The fictional sample drives include example LeetCode thresholds to demonstrate the eligibility engine. Adjust these requirements from Manage drives for your own demo.
- Django CSRF protection, password hashing and authentication are enabled.
- For public deployment, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=0`, configure `DJANGO_ALLOWED_HOSTS`, serve static/media files safely, enable HTTPS and review upload/storage policies.
- This is a college-project starter. Add audit logging, email delivery, automated tests, backups and stronger operational controls before real institutional use.

## 8. Run tests

```powershell
.\.venv\Scripts\python.exe manage.py test
```

## 9. Landing page design integration

The public landing page in `templates/portal/home.html` has been adapted from the supplied dark SaaS landing-page reference into native Django templates and CSS. It includes a responsive blurred navigation bar, centered hero, working Sign in / Get started links, a CSS-built dashboard preview, feature cards, workflow steps and live opportunity cards. The dashboard illustration is only a visual preview; real student/admin/recruiter data is shown after signing in.

This project intentionally remains a Django application. The supplied `.tsx` component cannot be rendered directly by Django templates, and the current project does not use React, shadcn/ui, Tailwind or TypeScript. The visual design and interactions were ported to `templates/portal/home.html` and `static/css/app.css` so the project keeps one server and the Python-only setup remains unchanged. The login and registration actions link to the existing Django routes.

## 10. LeetCode profile and eligibility matching

Students can save their LeetCode username, public profile URL and solved-problem count in **My profile**. The count is self-reported until a placement administrator verifies it in `/django-admin/`. Placement drives can set a minimum LeetCode solved count; a value of `0` means LeetCode is not part of that drive's eligibility rules.

Eligibility is calculated separately for each open drive and checks minimum CGPA, maximum backlogs, eligible department, drive deadline, required skills and (when configured) minimum LeetCode solved count. The app does not collect LeetCode passwords or scrape the platform.

## 11. Public deployment (Railway + MySQL)

A step-by-step deployment checklist is in [`DEPLOY-RAILWAY.md`](DEPLOY-RAILWAY.md). The project includes `Procfile`, Gunicorn, WhiteNoise, production security settings and environment-based MySQL settings for Railway. In Railway, name the database service `MySQL` to use the variable references below; if you choose another service name, update the reference prefixes accordingly. Recommended sequence:

1. Push this folder to a private or public GitHub repository (do not commit `.env`, `db.sqlite3`, `media/` or `.venv/`).
2. In Railway, create a project and deploy the GitHub repository as a web service.
3. Add a **MySQL** database service to the same Railway project. Railway exposes `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD` and `MYSQLDATABASE`; use service-variable references in the web service.
4. Set these variables on the web service:
   - `DJANGO_SECRET_KEY` = a long random secret (never commit this value)
   - `DJANGO_DEBUG` = `0`
   - `DJANGO_ALLOWED_HOSTS` = your generated Railway domain (host only, no `https://`)
   - `CSRF_TRUSTED_ORIGINS` = `https://your-generated-domain`
   - `DB_ENGINE` = `mysql`
   - `DB_NAME` = `${{MySQL.MYSQLDATABASE}}`
   - `DB_USER` = `${{MySQL.MYSQLUSER}}`
   - `DB_PASSWORD` = `${{MySQL.MYSQLPASSWORD}}`
   - `DB_HOST` = `${{MySQL.MYSQLHOST}}`
   - `DB_PORT` = `${{MySQL.MYSQLPORT}}`
   - `MEDIA_ROOT` = `/app/media`
5. Set the service start command to `python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
6. Generate a public domain in Railway Networking. Update `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to match it.
7. Attach a Railway volume to the web service mounted at `/app/media` so uploaded resumes survive app redeploys. Create the first administrator from the Railway service shell with `python manage.py createsuperuser`.

Keep the MySQL service and web service in the same Railway project so they can communicate over Railway's private network. Configure MySQL backups before using real student records. Check Railway's current usage and billing before deploying: hosting and database usage may incur charges.

### Updating an existing local installation

When using a newer PlacementPilot ZIP over an existing project, stop the server first and replace the project source files. Keep your existing `.venv` folder, `db.sqlite3`, `.env`/environment settings and `media` folder. Then run:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

The included `0003_remove_hackerrank` migration removes the retired HackerRank profile and drive-criteria columns from an existing database. Student accounts, LeetCode details, companies, drives and applications are preserved; any HackerRank-only values are discarded.
