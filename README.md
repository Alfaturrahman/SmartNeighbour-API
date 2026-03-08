# SmartNeighbour Backend API

Backend API untuk sistem manajemen perumahan SmartNeighbour menggunakan Django REST Framework.

## 🚀 Fitur

- ✅ Autentikasi JWT dengan refresh tokens
- ✅ CRUD untuk User, Resident, Feedback, Announcement, Security Schedule
- ✅ Role-based access (Admin, Security, Resident)
- ✅ Django Admin panel lengkap
- ✅ PostgreSQL database
- ✅ CORS configured untuk frontend

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip

## 🛠️ Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd smartneighbour_backend
```

2. **Buat virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
# Copy env.example ke .env
cp env.example .env
# Edit .env sesuai konfigurasi Anda
```

5. **Setup database PostgreSQL**
```sql
CREATE DATABASE smartneighbour_db;
CREATE USER smartneighbour_user WITH PASSWORD 'smartneighbour2026!';
GRANT ALL PRIVILEGES ON DATABASE smartneighbour_db TO smartneighbour_user;
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser untuk Django Admin**
```bash
python manage.py createsuperuser
```

8. **Hash existing passwords (jika ada data lama)**
```bash
python manage.py hash_passwords
```

9. **Run development server**
```bash
python manage.py runserver
```

Server akan berjalan di `http://localhost:8000`

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login dan dapatkan JWT token
- `GET /api/auth/me/` - Get current user info
- `GET /api/auth/verify/` - Verify JWT token

### Users
- `GET /api/users/` - List semua users
- `POST /api/users/` - Create user baru
- `GET /api/users/{id}/` - Get user detail
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `GET /api/users/stats/` - User statistics

### Residents
- `GET /api/residents/` - List semua warga
- `POST /api/residents/` - Create warga baru
- `GET /api/residents/{id}/` - Get warga detail
- `PUT /api/residents/{id}/` - Update warga
- `DELETE /api/residents/{id}/` - Delete warga
- `GET /api/residents/stats/` - Resident statistics

### Feedbacks
- `GET /api/feedbacks/` - List semua feedback
- `POST /api/feedbacks/` - Create feedback baru
- `GET /api/feedbacks/{id}/` - Get feedback detail
- `PUT /api/feedbacks/{id}/` - Update feedback
- `DELETE /api/feedbacks/{id}/` - Delete feedback
- `POST /api/feedbacks/{id}/reply/` - Reply to feedback
- `GET /api/feedbacks/stats/` - Feedback statistics

### Announcements
- `GET /api/announcements/` - List semua pengumuman
- `POST /api/announcements/` - Create pengumuman baru
- `GET /api/announcements/{id}/` - Get pengumuman detail
- `PUT /api/announcements/{id}/` - Update pengumuman
- `DELETE /api/announcements/{id}/` - Delete pengumuman
- `GET /api/announcements/stats/` - Announcement statistics

### Security Schedules
- `GET /api/security-schedules/` - List semua jadwal
- `POST /api/security-schedules/` - Create jadwal baru
- `GET /api/security-schedules/{id}/` - Get jadwal detail
- `PUT /api/security-schedules/{id}/` - Update jadwal
- `DELETE /api/security-schedules/{id}/` - Delete jadwal
- `GET /api/security-schedules/stats/` - Schedule statistics

## 🔐 Authentication

Gunakan JWT token untuk autentikasi:

```bash
# Login untuk mendapatkan token
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}

# Gunakan token di header untuk request lain
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🔧 Django Admin

Akses Django Admin panel di `http://localhost:8000/admin/`

Features:
- Manage semua models (User, Resident, Feedback, dll)
- Search & filter functionality
- Custom fieldsets untuk better UX
- Auto password hashing untuk User model

## 📝 Environment Variables

Lihat `env.example` untuk daftar lengkap environment variables yang diperlukan.

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run dengan coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Project Structure

```
smartneighbour_backend/
├── core/                       # Main app
│   ├── models.py              # Database models
│   ├── views.py               # API views
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # URL routing
│   ├── admin.py               # Django admin config
│   └── management/
│       └── commands/
│           └── hash_passwords.py
├── smartneighbour_api/        # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── env.example
```

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG=False` di `.env`
2. Generate strong `SECRET_KEY`
3. Update `ALLOWED_HOSTS` dengan domain production
4. Setup production database (PostgreSQL)
5. Collect static files: `python manage.py collectstatic`
6. Use production server (gunicorn): `gunicorn smartneighbour_api.wsgi:application`
7. Setup reverse proxy (nginx)
8. Enable HTTPS/SSL

## 📄 License

MIT License

## 👥 Contributors

- Rahman

## 🐛 Bug Reports

Laporkan bug melalui issue tracker atau hubungi tim development.
