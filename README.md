# shin-woo.com - portfolio + Job Search Command Center (Django on Heroku)

Django 5.2 site with three areas:

| Area | URLs | Who sees it |
|---|---|---|
| Public portfolio | `/`, `/experience/`, `/projects/`, `/case-studies/`, `/about/`, `/contact/`, `/writing/` | Everyone |
| Accounts | `/accounts/login/`, `register/`, `profile/`, `password-change/`, `password-reset/` | Everyone / signed-in users |
| JSCC (private) | `/jscc/` dashboard, `applications/`, `roadmap/`, `checklist/`, `contacts/`, `settings/` | Signed-in users, each sees only their own data |

Site content (Projects, Case Studies, Writing) and incoming Contact messages are managed in the Django admin at `/admin/`.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations --check   # should report "No changes detected"
python manage.py migrate
python manage.py createsuperuser          # your login for the site, JSCC and the admin
python manage.py seed_content             # optional: starter projects + draft case studies
python manage.py test                     # automated checks
python manage.py runserver
```

## Deploying to Heroku

The existing `Procfile` already runs migrations on release. Then set these config vars:

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | **Required.** Keeps logins and reset links valid across restarts. |
| `ALLOW_REGISTRATION` | `true` to let anyone create a JSCC account. Default in production: closed. |
| `CSRF_TRUSTED_ORIGINS` | e.g. `https://shin-woo.com,https://www.shin-woo.com` |
| `ADMIN_URL` | Optional, e.g. `my-secret-admin/` to move the admin off `/admin/`. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Optional SMTP details so password-reset emails really send. Without them emails print to the log. |

After the first deploy: `heroku run python manage.py createsuperuser` then optionally `heroku run python manage.py seed_content`.

## Project layout

```
my-profile/
  models.py            Comment, Project, CaseStudy, Post, ContactMessage + JSCC models
  views.py             public pages
  views_accounts.py    login / register / password / profile
  views_jscc.py        private JSCC pages (all queries filtered to request.user)
  forms.py             Bootstrap-styled forms
  admin.py             admin setup
  context_processors.py  SITE details + active nav item for every template
  templates/
    base.html          global layout (navbar, messages, footer)
    base_jscc.html     app shell with sidebar
    base_account.html  centered card layout
    components/        reusable pieces (see below)
    jscc/  accounts/   private and account pages
  static/site.css      design system
```

### Reusable components (`templates/components/`)

`navbar`, `footer`, `messages`, `page_header`, `form_field`, `form_body`, `tag_list`, `status_badge`, `stat_card`, `empty_state`, `project_card`, `case_study_card`, `post_card`, `jscc_sidebar`. Each file starts with a comment showing how to `{% include %}` it.

### Design system (`static/site.css`)

All colours, type sizes, spacing, radii and shadows are CSS variables at the top of the file (`--color-primary`, `--text-xl`, `--space-4`, `--radius-lg`, ...). Change a value there and the whole site follows. Status colours for applications/roadmap come from the `.status-<value>` classes.

## Notes

- Writing posts are plain text; blank lines become paragraphs.
- Public comments on the About page are stored but not displayed (unchanged behaviour).
- Static files: Heroku runs `collectstatic` on deploy. Locally, run `python manage.py collectstatic --no-input` if you test with `DEBUG` off.
- Never commit database credentials, passwords or hostnames to this repository.
