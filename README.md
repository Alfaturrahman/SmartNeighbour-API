# SmartNeighbour — Backend API

Backend API untuk sistem manajemen perumahan SmartNeighbour, dibangun dengan Django REST Framework.

## Ringkasan
- Autentikasi JWT, role-based access, CRUD untuk user/resident/feedback/announcement, dan admin panel.

## Prerequisites
- Python 3.10+
- pip
- (Opsional untuk production) PostgreSQL

## Quickstart (development)
1. Clone repository
```bash
git clone <repository-url>
cd SmartNeighbour-API
```
2. Virtualenv & install
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```
3. Copy `.env` and edit jika perlu (untuk dev, SQLite digunakan jika `DATABASE_URL` kosong)
```bash
copy env.example .env
# edit .env sesuai kebutuhan
```
4. Run migrations & create superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```
5. Run dev server
```bash
python manage.py runserver
```

Server: http://127.0.0.1:8000

## Environment notes
- Set `SECRET_KEY`, `DEBUG`, dan `DATABASE_URL` via environment in production; do not commit secrets.

## Important endpoints (short)
- `POST /api/auth/login/` — Login, returns `access` + `refresh` tokens
- `GET /api/auth/me/` — Current user (requires Bearer token)
- Standard REST endpoints: `/api/users/`, `/api/residents/`, `/api/feedbacks/`, `/api/announcements/`, `/api/security-schedules/`

## Security checklist (high level)
- Ensure `DEBUG=False` and a strong `SECRET_KEY` in production.
- Use HTTPS and secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`).
- Keep `CORS_ALLOWED_ORIGINS` specific (avoid wildcard when credentials are allowed).
- Use proper permission classes (`IsAuthenticated`) by default and limit `AllowAny` to auth endpoints.

## Testing
```bash
python manage.py test
```

## Docker (optional)
Tidak ada Dockerfile di repo saat ini — disarankan menambahkan `Dockerfile` untuk backend dan `docker-compose.yml` untuk dev reproducibility.

## Contributing & License
- Kontributor: Rahman
- License: MIT

---
Untuk dokumentasi teknis lebih lengkap dan cheat-sheet endpoint lihat file dokumentasi lain di repo.
