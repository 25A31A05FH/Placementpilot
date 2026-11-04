# Deploy PlacementPilot on Railway (Django + MySQL)

This project is configured for Railway's Django-compatible Python build and Railway MySQL. Review current Railway usage and billing before deploying; hosting and database use may incur charges.

## A. Prepare GitHub

1. Create a new repository on GitHub.
2. From this folder (the one containing `manage.py`), run:

```powershell
git init
git add .
git commit -m "Prepare PlacementPilot for deployment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Do not commit `.env`, `db.sqlite3`, `media/`, `.venv/`, or real student data. These are covered by `.gitignore`.

## B. Create the Railway services

1. In Railway, create a project and deploy the GitHub repository as a service.
2. Add a MySQL database service in the same Railway project. Name that service **MySQL** so the variable references below work.
3. Connect the web service to the MySQL service using Railway's variable references.

## C. Set web-service variables

Set these variables in the Django web service:

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | A unique long random secret; never commit it |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_ALLOWED_HOSTS` | Your Railway domain only, e.g. `placementpilot-production.up.railway.app` (no scheme) |
| `CSRF_TRUSTED_ORIGINS` | `https://placementpilot-production.up.railway.app` |
| `DB_ENGINE` | `mysql` |
| `DB_NAME` | `${{MySQL.MYSQLDATABASE}}` |
| `DB_USER` | `${{MySQL.MYSQLUSER}}` |
| `DB_PASSWORD` | `${{MySQL.MYSQLPASSWORD}}` |
| `DB_HOST` | `${{MySQL.MYSQLHOST}}` |
| `DB_PORT` | `${{MySQL.MYSQLPORT}}` |
| `MEDIA_ROOT` | `/app/media` |

If you named the database service something other than `MySQL`, change the prefix in each reference to match that service name. Railway's MySQL service exposes the `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD` and `MYSQLDATABASE` variables.

To generate a secret locally, run this in your project virtual environment and copy the output into Railway (do not share it in chat or commit it):

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

After Railway generates your public domain, update `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to that exact hostname.

## D. Configure the web service

- Build command: leave Railway's Python/Railpack default, which installs `requirements.txt`.
- Start command:

```bash
python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

The repository also includes a `Procfile` with this command.

Generate a public domain in the service's Networking settings. Django uses the `RAILWAY_PUBLIC_DOMAIN` environment variable automatically as an allowed host and trusted HTTPS origin as a fallback, but still set the values above explicitly for clarity.

## E. Persist uploaded resumes

Application containers can be replaced during deploys. Add a Railway volume to the web service with mount path:

```text
/app/media
```

The `MEDIA_ROOT=/app/media` variable makes uploaded resumes write to that mounted volume. Without persistent media storage, uploaded files may be lost when the app container is replaced.

## F. Create the first administrator

After the first successful deployment, open the Railway service shell and run:

```bash
python manage.py createsuperuser
```

Then sign in to PlacementPilot using the account you created. The Django admin is at `/django-admin/`.

## G. Verify before sharing the URL

Run these checks from the Railway service shell:

```bash
python manage.py check --deploy
python manage.py showmigrations
```

Also test student registration, login/logout, profile save, LeetCode eligibility, drive applications, recruiter status updates, resume upload and file access. Use fictional/demo records until backups, privacy controls and upload policies are in place.

## Keep in mind

- Do not use the Django development server for public deployment; Railway starts Gunicorn through the command above.
- Static files are collected into `staticfiles/` and served by WhiteNoise.
- MySQL stores application records; the mounted volume stores resume files.
- Configure database backups before adding genuine student records.
- Hosting and database usage may be billable. Review Railway's current pricing and usage dashboard before leaving the application online.
