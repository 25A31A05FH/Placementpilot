# PLACEMENTPILOT
## URL Routes, Testing, Deployment and Future Scope

## 1. Main Application Routes

This project uses Django page routes rather than a separate REST API as its primary interface.

| Route | Purpose | Access |
|---|---|---|
| `/` | Public landing page | Public |
| `/register/` | Student registration | Public |
| `/login/` | Login portal chooser | Public |
| `/student-login/` | Student sign-in | Public |
| `/admin-login/` | Administrator sign-in | Public |
| `/recruiter-login/` | Recruiter sign-in | Public |
| `/dashboard/` | Role-specific dashboard | Authenticated |
| `/profile/` | Update profile and academic details | Authenticated |
| `/drives/` | Browse open drives | Authenticated |
| `/eligible-drives/` | List drives matching the student's profile | Authenticated |
| `/drives/<id>/` | Drive details and eligibility information | Authenticated |
| `/drives/<id>/apply/` | Submit an application | Student, POST |
| `/applications/` | Student applications or recruiter/admin review | Authenticated |
| `/applications/<id>/status/` | Update an application status | Admin or owning recruiter |
| `/resume-analyzer/` | Resume extraction and keyword analysis | Authenticated |
| `/notifications/` | View notifications | Authenticated |
| `/manage/students/` | Manage student records | Administrator |
| `/manage/companies/` | Manage companies | Administrator |
| `/manage/drives/` | Manage placement drives | Admin or recruiter (own drives for recruiter) |
| `/manage/recruiters/` | Recruiter account management | Administrator |
| `/django-admin/` | Django admin interface | Staff/superuser |

## 2. Validation and Access Control
- Login uses Django authentication.
- Passwords are managed by Django's password-hashing system.
- Role-based decorators restrict administrative and recruiter operations.
- Recruiters are restricted to drives they own for sensitive applicant and application operations.
- Application submission is restricted to students and rechecks eligibility on the server.
- Django CSRF middleware protects form submissions.
- Duplicate applications are prevented by a database unique constraint.
- The Remember me feature extends the session and stores a remembered username cookie; it does not store the password.

## 3. Testing

The repository includes Django tests covering several important workflows, including:
- Eligible and ineligible CGPA cases
- LeetCode threshold evaluation
- Required-skill eligibility
- Eligible drive listing
- Remember-me and browser-session behavior
- Student application submission and duplicate prevention
- Separate portal role access
- Administrator drive management and applicant visibility
- Student restrictions from administrator-only views
- Profile URL validation
- Administrator promotion command behavior

Run tests in the project virtual environment:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Run Django's configuration checks:

```powershell
.\.venv\Scripts\python.exe manage.py check
```

## 4. Local Setup

The repository's README documents the following Windows setup pattern:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

SQLite is the default for local development. MySQL can be enabled using the database environment variables documented in the repository.

## 5. Deployment Overview

The repository includes a Railway deployment guide for Django with MySQL.

High-level deployment steps:
1. Connect the GitHub repository to a Railway web service.
2. Add a MySQL database service.
3. Configure a strong `DJANGO_SECRET_KEY` and set `DJANGO_DEBUG=0`.
4. Configure allowed hosts and trusted HTTPS origins.
5. Set MySQL connection environment variables.
6. Run database migrations and collect static files.
7. Start the application with Gunicorn.
8. Mount persistent storage for uploaded resumes.
9. Create the first administrator and test the deployed application.

The repository's documented start command is:

```bash
python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Check the live platform's pricing and current deployment requirements before using a hosted database or application service.

## 6. Current Limitations and Notes
- Resume analysis uses a predefined keyword list, not semantic AI understanding.
- Scanned/image-only PDFs may not produce extractable text.
- LeetCode solved counts are self-reported and can be marked for placement-office verification. The current eligibility helper checks the stored count against the drive threshold; it does not require the verification flag to be true before returning eligible.
- The application currently creates in-portal notifications; external email/SMS delivery is not described as an implemented feature.
- Production use with real student data requires careful review of privacy, access, backups, resume file access, retention, and operational policies.

## 7. Future Enhancements
1. Add an audit trail for administrator and recruiter actions.
2. Add configurable email notifications.
3. Add stronger resume upload validation, malware scanning, and controlled file delivery.
4. Add analytics for placement drives, departments, application conversion, and hiring outcomes.
5. Add a formal coding-platform verification workflow with clear evidence and review history.
6. Add more comprehensive tests for edge cases and recruiter ownership.
7. Add data export and institution-level reporting with access controls.
8. Add backup automation and documented data-retention procedures.

## 8. Conclusion
PlacementPilot provides a unified platform for campus placement workflows. Its role-based dashboards, configurable eligibility rules, application tracking, notifications, and resume keyword analysis reduce fragmentation between students, placement administrators, and recruiters. The project establishes a practical foundation that can be extended with stronger analytics, verification, communication, and production governance features.
