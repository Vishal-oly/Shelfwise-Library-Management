# Shelfwise — Library Desk

A small Django + SQLite library tracker inspired by the reference project, with a little extra catalogue and lending functionality.

## Included
- Staff signup, sign-in and sign-out
- Overview dashboard with books, loans and overdue counts
- Book catalogue: add, edit, remove, search by title/author/category/ISBN
- Copy count and live availability
- Issue book with borrower and due date; mark returned
- Django admin and SQLite database
- Responsive interface; no front-end framework required

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo  # optional sample books/loans
python manage.py runserver
```

Open http://127.0.0.1:8000/ and create a staff account. The included demo data is shared by authenticated staff users.

To use the Django admin, first create a superuser with `python manage.py createsuperuser`, then open `/admin/`.

## Notes
- SQLite is suitable for a small demo/local deployment. Use a persistent database/storage plan before hosting important records.
- Set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS` before deploying publicly.
- Do not commit a real `db.sqlite3` file or credentials to a public repository.
