# Capacity Connect

Capacity Connect is a Django learning and capacity-building portal. The current stage provides learner registration and authentication, separate administrator sign-in, role-protected dashboards, coding and professional-development courses with introductory lessons, and administrator-managed learner enrollment.

## Stage 4: course lessons and learning materials

### What this stage includes

- Includes the existing account, course catalogue, enrollment, and dashboard features.
- Adds ordered lessons with readable introductory material to the sample courses, including Leadership, Digital skills, Communication, and Wellbeing.
- Lets administrators edit lesson titles, order, estimated reading time, and content inline on each Course in Django admin.
- Shows the course outline publicly, while protecting full lesson text so only enrolled learners and administrators can read it.
- Adds previous/next lesson navigation for learners.
- Seeds or updates ten sample courses and their 30 lessons using one repeatable command.

### Requirements

- Python 3.10 or newer
- pip

### Exact setup commands (Windows PowerShell)

Run these commands from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py seed_coding_courses
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that PowerShell window, then activate again.

On macOS or Linux, the equivalent commands are:

```sh
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py seed_coding_courses
python manage.py runserver
```

The development settings use a clearly development-only fallback secret so the project runs locally. Do not use that fallback for a public deployment. To create a private local key, run `python -c "import secrets; print(secrets.token_urlsafe(50))"` and set the result as `DJANGO_SECRET_KEY` in `.env`.

To create an administrator account for course management, run:

```powershell
python manage.py createsuperuser
```

### Project structure

```text
CAPACITY CONNECT/
├── accounts/
│   ├── migrations/
│   ├── templates/accounts/
│   │   ├── auth_base.html
│   │   ├── login.html
│   │   ├── password_change_done.html
│   │   ├── password_reset_complete.html
│   │   ├── password_reset_done.html
│   │   ├── password_reset_email.txt
│   │   ├── password_reset_subject.txt
│   │   └── register.html
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   └── __init__.py
├── capacity_connect/
│   ├── __init__.py
│   ├── settings.py  # backward-compatible development settings import
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── migrations/
│   ├── templates/core/
│   │   ├── base.html
│   │   ├── course_detail.html
│   │   ├── course_list.html
│   │   ├── lesson_detail.html
│   │   ├── dashboard_base.html
│   │   ├── admin_course_form.html
│   │   └── dashboards/
│   │       ├── administrator.html
│   │       ├── learner.html
│   │       └── trainer.html
│   │   └── home.html
│   ├── admin.py
│   ├── forms.py
│   ├── mixins.py
│   ├── models.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/css/site.css
├── .gitignore
├── .env.example
├── manage.py
├── README.md
└── requirements.txt
```

### Database migrations

Stage 2's account backfill migration preserves existing Django users, password hashes, profiles, and unrelated group memberships. Course capacity adds an enrollment limit to existing courses (defaulting to 30 seats) and creates an Enrollment table with database constraints. Existing courses are not deleted. Apply migrations with:

```powershell
python manage.py migrate
```

Course lessons add a `CourseLesson` database table. The migration file is included in the project; when setting up or updating your local database, run:

```powershell
python manage.py migrate
```

Use `python manage.py makemigrations core` only after you change Django models. Do not delete or rewrite migrations that have already been applied to a shared or deployed database.

The `seed_coding_courses` management command creates or updates ten published courses and three starter lessons per course in the current database. It is safe to run more than once:

```powershell
python manage.py seed_coding_courses
```

The ten courses include coding, Leadership, Digital skills, Communication, and Wellbeing topics. The four professional-development courses are Everyday Leadership, Digital Confidence at Work, Clear and Confident Communication, and Everyday Wellbeing and Resilience.

## Environment and production settings

Copy `.env.example` to `.env` for local use. `.env` is ignored by Git; never commit it or paste a real secret into source code. Environment variables supplied by your hosting provider can override the `.env` file values.

| Variable | Development use | Production requirement |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Optional; a local-only fallback is used if empty. | Required; use a unique, private random value. |
| `DJANGO_DEBUG` | Defaults to `true` in `config.settings.dev`. | Production settings always force `false`. |
| `DJANGO_ALLOWED_HOSTS` | Defaults to `127.0.0.1,localhost`. | Required comma-separated public hostnames, without URL schemes. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Optional comma-separated origins including `https://`. | Set when the deployment's legitimate POST origin differs from the host configuration. |
| `DJANGO_SECURE_SSL_REDIRECT` | Not enabled by development settings. | Defaults to `true` in production; set up HTTPS at the host/proxy first. |

For production, set `DJANGO_SETTINGS_MODULE=config.settings.prod` in the hosting environment and configure `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` as appropriate. Production settings reject missing secret/host configuration and enable secure session/CSRF cookies, HTTPS redirects, and HSTS. Before deploying behind a TLS-terminating proxy, configure Django's secure-proxy handling only for a proxy you control, and verify HTTPS redirects to avoid redirect loops.

Run the production configuration checks after supplying safe temporary values in your local shell:

```powershell
$env:DJANGO_SECRET_KEY = "Temporary-Production-Check-Key-Not-For-Deployment-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
$env:DJANGO_ALLOWED_HOSTS = "example.com"
python manage.py check --deploy --settings=config.settings.prod
```

```sh
DJANGO_SECRET_KEY=Temporary-Production-Check-Key-Not-For-Deployment-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ \
DJANGO_ALLOWED_HOSTS=example.com \
python manage.py check --deploy --settings=config.settings.prod
```

This check may report Django's `security.W021` warning because HSTS preload is intentionally not enabled by default. Only enable preload after confirming every subdomain is permanently HTTPS-capable and you intend to submit the domain to browser preload lists.

The old `capacity_connect.settings` module continues to load development settings for compatibility. New production deployments should explicitly use `config.settings.prod`; do not rely on the compatibility module for deployment.

### Accounts and dashboards

- Register at `/accounts/register/`; public registration always creates a Learner account.
- Sign in at `/accounts/login/`. Administrators can select **Use administrator sign in** or visit `/accounts/admin-login/`; this route does not grant admin rights to normal accounts.
- An administrator dashboard user must have an Administrator Profile, the matching Administrator Django Group, and `is_staff=True`. A Django superuser receives these automatically.
- Change a password at `/accounts/password-change/`; request a reset at `/accounts/password-reset/`.
- `/dashboard/` sends the signed-in user to the dashboard matching their profile role.
- Explicit dashboard paths are `/dashboard/learner/`, `/dashboard/trainer/`, and `/dashboard/administrator/`. A logged-in user with the wrong role or missing matching role group receives HTTP 403.
- Use Django admin at `/admin/` to manage account Profiles and assign Trainer/Learner roles. Django admin still requires Django staff permissions; creating a superuser automatically creates an Administrator profile.
- From the Administrator dashboard, select **Add a course**, enter the enrollment limit, and publish the course. The dashboard lists each course's actual enrolled count and available seats.
- To assign a course to a learner, open `/admin/core/enrollment/add/` (or open a course in admin and use its Enrollments section), select a learner and a published course, then save. The learner will see that course under **My courses** at `/dashboard/learner/`.
- To add the six example coding courses and their 18 starter lessons to your database, run `python manage.py seed_coding_courses`. Courses appear in Django admin and the published course catalogue, and lessons can be edited inline on each course's admin page.
- Course pages show a learning path and lesson titles. Enroll in or get assigned to a course to open its lesson materials. Signed-in learners who are not enrolled receive HTTP 403 if they try to access a lesson directly.
- Learners can enroll on a published course detail page. The available seat count reflects successful enrollments; a learner cannot enroll twice, non-learners cannot enroll, and a full course rejects new enrollments.
- Lesson progress, quiz results, and course completion statistics will be added in later stages; no placeholder data is shown.

In local development, password reset emails print in the server terminal. For production, configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` (or `EMAIL_USE_SSL`), and `DEFAULT_FROM_EMAIL` as secret/environment settings with your email provider. Do not commit SMTP credentials.

### Run the checks and tests

With the virtual environment activated:

```powershell
python manage.py check
python manage.py test core accounts
```

The tests check public course pages, protected lesson content, course seeding, administrator course assignment, learner dashboard privacy, registration and role assignment, login/logout, password-flow pages, role-group synchronization, dashboard routing, and denial of cross-role dashboard access.

### Manual demonstration checklist

1. Register a new account and confirm it is signed in as a Learner.
2. On `/accounts/login/`, confirm the administrator sign-in option appears. Test it with a learner account; it must reject the login and not create a session.
3. Sign in with the designated administrator account via the administrator option and confirm it opens the administrator dashboard.
4. Run `python manage.py seed_coding_courses` and confirm six courses with three lessons each appear in `/courses/` and Django admin.
5. In Django admin, assign one published course to a learner using `/admin/core/enrollment/add/`.
6. Open the course in admin and edit a lesson title or content, then save.
7. Sign in as the assigned learner and confirm the course appears under **My courses** on `/dashboard/learner/`.
8. Open the course and read a lesson; use the next/previous links to move through the course.
9. Sign in as another learner who is not enrolled and try opening the same lesson URL; confirm access is denied.
10. Try assigning a course to a Trainer in Django admin; the form must reject that account.
11. Try `/dashboard/trainer/` and `/dashboard/administrator/` as a Learner; each should return 403.
12. Confirm `/`, `/courses/`, and published course details still work after signing in and out.
13. Request a password reset and confirm its email appears in the development server terminal.
14. Resize to a phone viewport; confirm the dashboard menu can collapse and the page remains readable.
15. Try visiting a dashboard when logged out; confirm redirection to `/accounts/login/`.

### Common errors

- **`No module named django`**: activate `.venv`, then run `python -m pip install -r requirements.txt`.
- **`py` or `python` is not recognized**: install Python and enable its PATH option, then reopen PowerShell.
- **Port 8000 is already in use**: run `python manage.py runserver 8001` and visit `http://127.0.0.1:8001/`.
- **Static CSS is missing**: confirm `static/css/site.css` exists and restart the development server. Django serves project static files automatically in development when `DEBUG=True`.
- **PowerShell refuses to activate the environment**: use the process-scoped execution-policy command above; it does not change the machine-wide policy.
- **Password reset email is not received locally**: development uses the console email backend; inspect the `runserver` terminal for the reset message.
- **A user is denied access to their assigned dashboard**: confirm both their Profile role and its matching Django Group are correct. Saving the Profile in Django admin synchronizes the role group.

## Configuration and security

SQLite is for local development in this stage. Production uses `config.settings.prod`, which forces debug mode off and requires a secret key and allowed hostnames. Do not commit real keys or place provider credentials in templates or JavaScript.

Bootstrap and the web fonts are loaded from public CDNs in this first-stage layout, so those visual resources require an internet connection. The Django page itself does not depend on an external API.

## Planned development stages

1. Settings split, homepage, course catalogue/details, and administrator course management
2. Authentication, profiles, role-based dashboard shells, and enrollment capacity (current)
3. Course categories, trainer-owned course management, and enrollment dashboards
4. Lessons, resources, progress, and competencies
5. Quizzes, scoring, and assessment reports
6. Knowledge sharing, announcements, and notifications
7. Server-side AI learning assistant
8. Administration dashboard and reporting
9. Validation, authorization, security checks, and testing
10. MySQL migration guidance, GitHub workflow, and deployment preparation
