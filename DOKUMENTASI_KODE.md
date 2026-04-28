# 📚 Dokumentasi Kode Backend SmartNeighbour

> **Dokumentasi lengkap** yang menjelaskan setiap bagian kode backend, gunanya untuk apa, dan cara kerjanya.  
> **✨ NEW: Section 10** - Panduan lengkap cara pakai setiap endpoint di Frontend (React/Next.js)!

## 🎯 Apa yang Ada di Dokumentasi Ini?

### **Backend (Section 1-9)**
- 📁 Struktur project & arsitektur
- 🗄️ Database models & relationships
- 🔄 Serializers & validation
- 🌐 API endpoints & views
- 🔐 Authentication system (JWT)
- ⚙️ Configuration & settings

### **Frontend Integration (Section 10)** ⭐
- 📱 **Di mana endpoint digunakan** (file & page)
- 💻 **Cara pakai endpoint** di React/Next.js
- 📝 **Contoh code lengkap** dari frontend
- 🔄 **Flow penggunaan** step-by-step
- ⚡ **Best practices** & error handling
- 🎨 **UI patterns** (loading, search, filter)

---

## 📖 Daftar Isi

1. [Arsitektur & Struktur Project](#1-arsitektur--struktur-project)
2. [Models - Database Schema](#2-models---database-schema)
3. [Serializers - Data Validation](#3-serializers---data-validation)
4. [Views - API Endpoints](#4-views---api-endpoints)
5. [Authentication System](#5-authentication-system)
6. [Admin Panel](#6-admin-panel)
7. [Settings & Configuration](#7-settings--configuration)
8. [URL Routing](#8-url-routing)
9. [Flow Diagram](#9-flow-diagram)
10. [Frontend Integration - Cara Pakai Endpoint](#10-frontend-integration---cara-pakai-endpoint-di-reactnextjs) ⭐ NEW!

---

## 1. Arsitektur & Struktur Project

### 📂 Struktur Folder

```
smartneighbour_backend/
├── core/                          # App utama yang berisi semua logic bisnis
│   ├── models.py                  # Database models (User, RW, RT, Resident, dll)
│   ├── serializers.py             # Validasi & transformasi data API
│   ├── views.py                   # Logic endpoint API (login, CRUD, dll)
│   ├── authentication.py          # Custom JWT authentication
│   ├── backends.py                # Custom auth backend (login dengan email)
│   ├── admin.py                   # Interface admin Django
│   ├── urls.py                    # Routing URL untuk API
│   └── migrations/                # Database migration files
│
├── smartneighbour_api/            # Project settings
│   ├── settings.py                # Konfigurasi project (database, JWT, CORS, dll)
│   ├── urls.py                    # Main URL routing
│   ├── wsgi.py                    # WSGI server untuk production
│   └── asgi.py                    # ASGI server (untuk async/websocket)
│
├── manage.py                      # Django management command
├── requirements.txt               # Python dependencies
├── Procfile                       # Config untuk Railway deployment
├── runtime.txt                    # Python version untuk Railway
└── db.sqlite3                     # SQLite database (development)
```

### 🎯 Tujuan Arsitektur

**Kenapa pakai arsitektur ini?**
- **Django REST Framework**: Framework mature untuk bikin REST API yang scalable
- **JWT Token**: Stateless authentication, cocok untuk mobile/web app modern
- **Custom User Model**: Fleksibilitas penuh untuk manage user dengan role RW/RT/Warga
- **Modular**: Semua logic di app `core`, mudah di-maintain dan di-extend

---

## 2. Models - Database Schema

> **File**: `core/models.py`  
> **Fungsi**: Define struktur database dan relationship antar tabel

### 2.1 User Model

**Untuk apa?**
- Model utama untuk **authentication** semua user (RW, RT, Warga)
- Custom model (bukan pakai Django User default) biar bisa disesuaikan dengan kebutuhan

**Fields:**
```python
email           # Login identifier (unique)
password        # Hashed password (PBKDF2 + salt)
name            # Nama lengkap user
role            # Choices: 'rw', 'rt', 'warga'
is_active       # Status aktif/nonaktif
created_at      # Timestamp pembuatan
updated_at      # Timestamp update terakhir
```

**Methods penting:**
- `set_password(raw_password)` - Hash password sebelum disimpan
- `check_password(raw_password)` - Verifikasi password saat login

**Kenapa custom?**
- Django User default pakai username, kita butuh email
- Butuh field `role` untuk differentiate RW/RT/Warga
- Lebih simple, ga perlu field yang ga kepake

---

### 2.2 RW Model (Rukun Warga)

**Untuk apa?**
- Menyimpan **profile lengkap RW** (level tertinggi dalam hierarki)
- One-to-One relationship dengan User yang role-nya 'rw'

**Fields:**
```python
name            # Nama RW (contoh: "RW 01")
user            # Link ke User model (OneToOne)
area            # Wilayah yang dikelola
phone           # Nomor telepon
address         # Alamat kantor RW
```

**Relationship:**
- **Has Many RT**: Satu RW punya banyak RT
- **Has Many SecuritySchedule**: RW yang bikin jadwal keamanan
- **Has Many SecurityPersonnel**: RW yang manage data petugas

**Use Case:**
- RW login → Bisa manage semua RT di bawahnya
- RW bisa create RT baru
- RW bisa buat jadwal keamanan
- RW bisa lihat semua data warga di wilayahnya

---

### 2.3 RT Model (Rukun Tetangga)

**Untuk apa?**
- Menyimpan **profile lengkap RT** (level menengah)
- One-to-One dengan User role 'rt'
- Many-to-One dengan RW (RT belongs to RW)

**Fields:**
```python
name            # Nama RT (contoh: "RT 01")
user            # Link ke User model (OneToOne)
rw              # Link ke RW (ForeignKey)
area            # Wilayah RT
phone           # Nomor telepon
address         # Alamat kantor RT
```

**Relationship:**
- **Belongs to RW**: RT terikat ke satu RW
- **Has Many Residents**: Satu RT punya banyak warga
- **Has Many Feedbacks**: Warga di RT ini bisa kasih feedback
- **Has Many Announcements**: RT bisa bikin pengumuman

**Use Case:**
- RT login → Bisa manage warga di RT-nya
- RT bisa create resident baru
- RT bisa reply feedback
- RT bisa buat pengumuman

---

### 2.4 Resident Model (Warga)

**Untuk apa?**
- Menyimpan **data lengkap warga** perumahan
- Bisa linked ke User (kalau warga punya akun) atau stand-alone

**Fields Dasar:**
```python
name            # Nama lengkap warga
address         # Alamat rumah
phone           # Nomor telepon
email           # Email warga
status          # 'aktif' atau 'tidak aktif'
```

**Fields Tambahan (Data Kependudukan):**
```python
ktp                 # NIK (16 digit)
kk                  # Nomor Kartu Keluarga
jumlah_keluarga     # Jumlah anggota keluarga
kepala_keluarga     # Nama kepala keluarga
```

**Relationship:**
```python
user            # Optional: Link ke User (kalau punya akun)
rt              # Belongs to RT
```

**Use Case:**
- Data master warga untuk administrasi
- Warga yang punya akun bisa login & submit feedback
- RT bisa manage data warga di wilayahnya

---

### 2.5 Feedback Model

**Untuk apa?**
- Sistem **keluhan/feedback** dari warga ke RT/RW
- Include **rating system** (1-5 stars)
- RT/RW bisa **reply** feedback

**Fields:**
```python
user            # User yang submit feedback
rt              # RT tujuan feedback
author          # Nama pembuat (display name)
title           # Judul feedback
content         # Isi feedback
rating          # Rating 1-5 (optional)
date            # Tanggal submit
reply           # Balasan dari RT/RW (optional)
replied_at      # Timestamp balasan
replied_by      # Nama yang reply
```

**Use Case:**
- Warga submit keluhan/saran
- RT/RW bisa lihat semua feedback
- RT/RW bisa reply feedback
- Transparansi: semua warga di RT bisa lihat feedback (public)

---

### 2.6 Announcement Model

**Untuk apa?**
- Sistem **pengumuman** dari RT/RW ke warga
- Include **priority level** (high/medium/low)

**Fields:**
```python
user            # User yang bikin (RT/RW)
rt              # RT tujuan announcement
title           # Judul pengumuman
content         # Isi pengumuman
author          # Nama pembuat
date            # Tanggal publish
priority        # 'high', 'medium', 'low'
```

**Priority System:**
- **High**: Urgent (contoh: mati listrik, keamanan)
- **Medium**: Normal (contoh: iuran bulanan)
- **Low**: Info biasa (contoh: acara santai)

**Use Case:**
- RT/RW announce informasi penting
- Warga bisa lihat pengumuman di wilayahnya
- Frontend bisa highlight pengumuman high priority

---

### 2.7 SecuritySchedule Model

**Untuk apa?**
- Sistem **jadwal jaga keamanan** (satpam/hansip)
- Support **3 tipe jadwal**: daily, weekly, monthly
- Link ke data petugas keamanan

**Fields Umum:**
```python
user            # User yang bikin jadwal (RW)
rw              # RW yang punya jadwal
personnel       # Link ke petugas (optional)
name            # Nama petugas
shift           # 'Pagi', 'Siang', 'Malam'
schedule_type   # 'daily', 'weekly', 'monthly'
time            # Jam kerja (contoh: "08:00 - 16:00")
status          # 'aktif' atau 'tidak aktif'
notes           # Catatan tambahan
```

**Fields untuk Daily Schedule:**
```python
date            # Tanggal spesifik (contoh: 2026-05-01)
```

**Fields untuk Weekly Schedule:**
```python
start_date      # Tanggal mulai range
end_date        # Tanggal akhir range
weekday         # Hari dalam seminggu (0=Senin, 6=Minggu)
```

**Fields untuk Monthly Schedule:**
```python
start_date      # Tanggal mulai range
end_date        # Tanggal akhir range
month_day       # Tanggal dalam bulan (1-31)
```

**Use Case:**
- RW bikin jadwal jaga rutin
- Support jadwal harian, mingguan, atau bulanan
- Frontend bisa tampilkan jadwal dalam calendar view
- Link otomatis ke master data petugas

---

### 2.8 SecurityPersonnel Model

**Untuk apa?**
- **Master data** petugas keamanan
- Database petugas yang bisa di-assign ke jadwal

**Fields:**
```python
rw              # RW yang punya petugas
name            # Nama petugas
phone           # Nomor telepon
email           # Email petugas (optional)
address         # Alamat petugas
area            # Area bertugas
status          # 'aktif' atau 'tidak aktif'
notes           # Catatan (contoh: shift preference)
```

**Relationship:**
- **Belongs to RW**: Petugas milik satu RW
- **Has Many Schedules**: Satu petugas bisa ada di banyak jadwal

**Use Case:**
- RW maintain database petugas
- Saat bikin jadwal, pilih dari master data
- Bisa track petugas aktif/nonaktif

---

## 3. Serializers - Data Validation

> **File**: `core/serializers.py`  
> **Fungsi**: Transform data antara JSON (API) dan Python object (Model)

### Kenapa Butuh Serializer?

**3 Fungsi Utama:**
1. **Validation**: Cek data yang masuk valid atau ngga
2. **Serialization**: Convert Python object → JSON (untuk response API)
3. **Deserialization**: Convert JSON → Python object (dari request API)

---

### 3.1 UserSerializer

**Untuk apa?**
- CRUD User dengan auto-hash password

**Fitur Khusus:**
```python
# Password write_only (tidak pernah di-return ke client)
password = {'write_only': True}

# Override create() - auto-hash password
def create(self, validated_data):
    user.set_password(validated_data['password'])

# Override update() - re-hash kalau password diubah
def update(self, instance, validated_data):
    if 'password' in validated_data:
        instance.set_password(validated_data['password'])
```

**Kenapa penting?**
- Password TIDAK PERNAH disimpan dalam plaintext
- Password TIDAK PERNAH di-return di API response

---

### 3.2 RWSerializer & RTSerializer

**Untuk apa?**
- Serializer untuk profile RW dan RT
- Include data relasi (email user, nama RW)

**Fitur Display:**
```python
user_email = source='user.email', read_only=True  # Show email user
rw_name = source='rw.name', read_only=True        # Show nama RW (untuk RT)
```

**Kenapa?**
- Frontend butuh data relasi tanpa perlu request lagi
- Simplify frontend logic

---

### 3.3 ResidentSerializer

**Untuk apa?**
- CRUD Resident dengan data lengkap
- Include data user dan RT

**Fields Display:**
```python
user_email      # Email user (kalau linked)
rt_name         # Nama RT
```

---

### 3.4 FeedbackSerializer

**Untuk apa?**
- CRUD Feedback dengan validasi rating

**Validasi Khusus:**
```python
def validate_rating(self, value):
    if value is not None and (value < 1 or value > 5):
        raise ValidationError('Rating harus antara 1-5')
```

**Display Fields:**
```python
user_email      # Email pembuat
user_role       # Role pembuat
rt_name         # Nama RT tujuan
```

---

### 3.5 FeedbackReplySerializer

**Untuk apa?**
- Serializer khusus untuk RT/RW reply feedback
- Cuma butuh 2 field: reply dan replied_by

**Kenapa pisah?**
- Reply dan create feedback beda use case
- Validasi berbeda
- Cleaner code

---

### 3.6 RTCreateSerializer

**Untuk apa?**
- Serializer khusus untuk RW create RT baru
- **Auto-create User + RT profile** sekaligus

**Flow:**
```python
1. RW kirim data: name, email, phone, area, address
2. Serializer create User baru:
   - email dari input
   - role = 'rt'
   - password = 'passw0rd' (default)
3. Serializer create RT profile:
   - user = user yang baru dibuat
   - rw = RW yang create
   - data lainnya dari input
4. Return RT + credentials
```

**Validasi:**
```python
def validate_email(self, value):
    if User.objects.filter(email=value).exists():
        raise ValidationError('Email sudah terdaftar')
```

**Kenapa penting?**
- Proses create RT yang kompleks jadi simple
- RW tidak perlu manual create User dulu
- Password auto-generate, aman

---

### 3.7 ResidentCreateSerializer

**Untuk apa?**
- Serializer khusus untuk RT create Resident baru
- **Auto-create User + Resident profile** sekaligus

**Flow:**
```python
1. RT kirim data lengkap warga
2. Create User:
   - role = 'warga'
   - password = 'passw0rd' (default)
3. Create Resident:
   - user = user baru
   - rt = RT yang create
   - data lengkap (KTP, KK, dll)
4. Return Resident + credentials
```

**Fields Tambahan:**
```python
ktp, kk, jumlah_keluarga, kepala_keluarga
```

---

### 3.8 AnnouncementSerializer

**Untuk apa?**
- CRUD Announcement dengan auto-set author

**Auto Fields:**
```python
user    # Auto dari request.user
rt      # Auto dari role user
author  # Auto dari user.name atau user.email
```

---

### 3.9 SecurityScheduleSerializer

**Untuk apa?**
- CRUD Jadwal Keamanan
- Include data petugas untuk display

**Display Fields:**
```python
personnel_name      # Nama petugas
personnel_phone     # Telp petugas
personnel_email     # Email petugas
```

**Kenapa?**
- Frontend bisa langsung tampilkan info petugas
- Không perlu request lagi ke API personnel

---

### 3.10 SecurityPersonnelSerializer

**Untuk apa?**
- CRUD Master Data Petugas
- Simple serializer, no special logic

---

## 4. Views - API Endpoints

> **File**: `core/views.py`  
> **Fungsi**: Handle semua logic API endpoints

### 4.1 Authentication Views

#### `login_view()`

**Endpoint**: `POST /api/auth/login/`

**Fungsi**: Login user dan return JWT tokens

**Flow:**
```
1. Terima email & password
2. Cari user by email
3. Verify password dengan check_password()
4. Cek user is_active
5. Generate JWT tokens:
   - access_token (valid 24 jam)
   - refresh_token (valid 7 hari)
6. Token payload: user_id, email, role
7. Return tokens + user data
```

**Response Success:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "rw@example.com",
    "name": "RW 01",
    "role": "rw",
    "is_active": true
  },
  "message": "Login berhasil"
}
```

**Error Handling:**
- User not found → 404
- Wrong password → 401
- User not active → 403

---

#### `current_user()`

**Endpoint**: `GET /api/auth/me/`

**Fungsi**: Get data user yang sedang login

**Flow:**
```
1. Extract token dari header Authorization
2. Decode JWT token
3. Get user_id dari token payload
4. Query user by ID
5. Return user data
```

**Headers Required:**
```
Authorization: Bearer <access_token>
```

---

#### `verify_token()`

**Endpoint**: `GET /api/auth/verify/` atau `POST /api/auth/verify/`

**Fungsi**: Cek apakah token masih valid

**Response:**
```json
{
  "valid": true,
  "user": { ... },
  "token_payload": {
    "user_id": 1,
    "email": "rw@example.com",
    "role": "rw",
    "exp": 1714320000
  }
}
```

**Use Case:**
- Frontend cek token saat app load
- Redirect ke login kalau token expired

---

#### `refresh_token_view()`

**Endpoint**: `POST /api/auth/refresh/`

**Fungsi**: Generate access_token baru dari refresh_token

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "Token berhasil di-refresh"
}
```

**Kenapa?**
- Access token valid 24 jam (security)
- Refresh token valid 7 hari (convenience)
- User ga perlu login ulang tiap hari

---

### 4.2 UserViewSet

**Endpoints**:
- `GET /api/users/` - List all users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user detail
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `GET /api/users/stats/` - User statistics

**Custom Action: stats()**

**Endpoint**: `GET /api/users/stats/`

**Fungsi**: Return statistik user

**Response:**
```json
{
  "total": 100,
  "active": 95,
  "by_role": {
    "rw": 2,
    "rt": 10,
    "warga": 88
  }
}
```

---

### 4.3 RWViewSet

**Custom get_queryset()**

**Fungsi**: Filter data RW berdasarkan role user

**Logic:**
```python
if user.role == 'rw':
    # RW cuma lihat profile sendiri
    return RW.objects.filter(user=user)
elif user.role == 'rt':
    # RT bisa lihat RW-nya
    return RW.objects.filter(id=rt.rw.id)
else:
    return none
```

---

#### Custom Action: `create_rt()`

**Endpoint**: `POST /api/rw/create_rt/`

**Fungsi**: RW create RT baru lengkap dengan User

**Request:**
```json
{
  "name": "RT 01",
  "email": "rt01@example.com",
  "phone": "081234567890",
  "area": "Blok A",
  "address": "Jl. Mawar No. 1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "RT berhasil dibuat",
  "data": {
    "rt_id": 1,
    "rt_name": "RT 01",
    "user_email": "rt01@example.com",
    "generated_password": "passw0rd",
    "note": "Berikan email dan password ini ke RT untuk login"
  }
}
```

**Security:**
- Cuma user role 'rw' yang bisa akses
- Email harus unique
- Password auto-generate

---

#### Custom Action: `reset_password()`

**Endpoint**: `POST /api/rw/{id}/reset_password/`

**Fungsi**: RW reset password RT kalau lupa

**Response:**
```json
{
  "success": true,
  "message": "Password RT berhasil direset",
  "data": {
    "rt_id": 1,
    "rt_name": "RT 01",
    "user_email": "rt01@example.com",
    "new_password": "passw0rd",
    "note": "Berikan password baru ini ke RT untuk login"
  }
}
```

---

### 4.4 RTViewSet

**Custom get_queryset()**

**Logic:**
```python
if user.role == 'rw':
    # RW lihat semua RT dibawahnya
    return RT.objects.filter(rw=rw)
elif user.role == 'rt':
    # RT cuma lihat profile sendiri
    return RT.objects.filter(id=rt.id)
```

---

#### Custom Action: `create_resident()`

**Endpoint**: `POST /api/rt/create_resident/`

**Fungsi**: RT daftarkan warga baru lengkap dengan User

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "081234567890",
  "address": "Blok A No. 10",
  "ktp": "1234567890123456",
  "kk": "1234567890123456",
  "jumlah_keluarga": 4,
  "kepala_keluarga": "John Doe",
  "status": "aktif"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Warga berhasil didaftarkan",
  "data": {
    "resident_id": 1,
    "resident_name": "John Doe",
    "user_email": "john@example.com",
    "generated_password": "passw0rd",
    "note": "Berikan email dan password ini ke Warga untuk login"
  }
}
```

---

### 4.5 ResidentViewSet

**Custom get_queryset()**

**Logic Role-Based:**
```python
if user.role == 'rw':
    # RW lihat semua warga di semua RT-nya
    return Resident.objects.filter(rt__rw=rw)
    
elif user.role == 'rt':
    # RT lihat warga di RT-nya aja
    return Resident.objects.filter(rt=rt)
    
elif user.role == 'warga':
    # Warga cuma lihat data diri sendiri
    return Resident.objects.filter(user=user)
```

**Query Params:**
```
GET /api/residents/?status=aktif
```

---

#### Custom Action: `stats()`

**Endpoint**: `GET /api/residents/stats/`

**Response:**
```json
{
  "total": 500,
  "active": 480,
  "inactive": 20
}
```

---

### 4.6 FeedbackViewSet

**Custom get_queryset()**

**Logic:**
```python
if user.role == 'warga':
    # Warga lihat semua feedback di RT-nya (transparansi)
    return Feedback.objects.filter(rt=resident.rt)
    
elif user.role == 'rt':
    # RT lihat feedback dari warga di RT-nya
    return Feedback.objects.filter(rt=rt)
    
elif user.role == 'rw':
    # RW lihat semua feedback dari semua RT-nya
    return Feedback.objects.filter(rt__rw=rw)
```

---

#### Custom Action: `reply()`

**Endpoint**: `POST /api/feedbacks/{id}/reply/`

**Fungsi**: RT/RW reply feedback

**Request:**
```json
{
  "reply": "Terima kasih atas feedback-nya. Akan kami tindaklanjuti.",
  "replied_by": "RT 01"
}
```

**Auto-set:**
- `replied_at` = timezone.now()

---

#### Custom Action: `stats()`

**Response:**
```json
{
  "total": 150,
  "replied": 120,
  "unreplied": 30,
  "average_rating": 4.2
}
```

---

### 4.7 AnnouncementViewSet

**Custom get_queryset()**

**Logic:**
```python
if user.role == 'warga':
    # Warga lihat pengumuman dari RT-nya
    return Announcement.objects.filter(rt=resident.rt)
    
elif user.role == 'rt':
    # RT lihat pengumuman di RT-nya
    return Announcement.objects.filter(rt=rt)
    
elif user.role == 'rw':
    # RW lihat semua pengumuman dari semua RT-nya
    return Announcement.objects.filter(rt__rw=rw)
```

**Query Params:**
```
GET /api/announcements/?priority=high
```

---

#### Custom Action: `stats()`

**Response:**
```json
{
  "total": 80,
  "by_priority": {
    "high": 15,
    "medium": 50,
    "low": 15
  }
}
```

---

### 4.8 SecurityScheduleViewSet

**Custom perform_create()**

**Validasi:**
1. Cek ada petugas aktif atau tidak
2. Validasi date range untuk weekly/monthly
3. Auto-link petugas by name

**Custom perform_update()**

**Fungsi**: Re-link petugas kalau nama diubah

---

#### Custom Action: `stats()`

**Response:**
```json
{
  "total": 90,
  "active": 85,
  "by_shift": {
    "Pagi": 30,
    "Siang": 30,
    "Malam": 30
  }
}
```

**Query Params:**
```
GET /api/security-schedules/?shift=Pagi&date=2026-05-01
```

---

### 4.9 SecurityPersonnelViewSet

**Custom get_queryset()**

**Logic:**
```python
if user.role == 'rw':
    # RW lihat petugas mereka
    return SecurityPersonnel.objects.filter(rw=rw)
    
elif user.role == 'rt':
    # RT bisa lihat petugas dari RW-nya (read-only)
    return SecurityPersonnel.objects.filter(rw=rt.rw)
    
elif user.role == 'warga':
    # Warga bisa lihat petugas (read-only)
    return SecurityPersonnel.objects.filter(rw=resident.rt.rw)
```

**Custom perform_create()**

**Security**: Cuma RW yang bisa create/edit petugas

---

## 5. Authentication System

### 5.1 CustomJWTAuthentication

> **File**: `core/authentication.py`

**Untuk apa?**
- Custom JWT authentication untuk support User model sendiri

**Flow:**
```
1. Extract token dari header Authorization  
2. Validate token signature & expiry
3. Get user_id dari token payload
4. Query User by ID
5. Return User object
```

**Kenapa butuh custom?**
- JWT Simple default pakai Django User
- Kita pakai custom User model
- Need custom `get_user()` method

---

### 5.2 CustomUserBackend

> **File**: `core/backends.py`

**Untuk apa?**
- Backend authentication untuk login dengan email (bukan username)

**Methods:**

#### `authenticate(email, password)`

**Flow:**
```
1. Query User by email
2. Check password dengan check_password()
3. Return User object atau None
```

#### `get_user(user_id)`

**Flow:**
```
1. Query User by ID
2. Return User object atau None
```

**Kenapa?**
- Django default pakai username
- Kita butuh email-based authentication

---

### 5.3 JWT Token Structure

**Access Token Payload:**
```json
{
  "user_id": 1,
  "email": "rw@example.com",
  "role": "rw",
  "exp": 1714320000,
  "iat": 1714233600
}
```

**Refresh Token Payload:**
```json
{
  "user_id": 1,
  "email": "rw@example.com",
  "role": "rw",
  "exp": 1714838400,
  "iat": 1714233600
}
```

**Lifetime:**
- Access Token: 24 jam
- Refresh Token: 7 hari

**Security:**
- Token signed dengan SECRET_KEY
- Token dapat di-verify tanpa query database
- Stateless (tidak perlu session storage)

---

## 6. Admin Panel

> **File**: `core/admin.py`  
> **URL**: `/admin/`

### Untuk apa?

**Django Admin** adalah web interface untuk manage data secara manual.

**Use Case:**
- Debugging: lihat data langsung
- Manual data entry
- Bulk operations
- User management

---

### 6.1 UserAdmin

**Features:**
- List display: email, name, role, is_active
- Search: by email, name
- Filter: by role, is_active
- **Auto-hash password** saat save

**Custom save_model():**
```python
def save_model(self, request, obj, form, change):
    if not change or 'password' in form.changed_data:
        if not obj.password.startswith('pbkdf2_'):
            obj.set_password(obj.password)
```

**Kenapa?**
- Admin bisa input password plaintext
- Otomatis di-hash sebelum save

---

### 6.2 RWAdmin, RTAdmin, ResidentAdmin

**Features:**
- List all data
- Search by name, email, phone
- Filter by status, created date
- Read-only: created_at, updated_at

---

### 6.3 FeedbackAdmin

**Custom Field: has_reply**

**Fungsi**: Show indicator apakah feedback sudah dibalas

```python
def has_reply(self, obj):
    return obj.reply is not None
has_reply.boolean = True  # Show as icon
```

---

## 7. Settings & Configuration

> **File**: `smartneighbour_api/settings.py`

### 7.1 Database Configuration

**Priority:**
```python
1. DATABASE_URL (Railway/Heroku) → PostgreSQL production
2. DB_NAME env vars → PostgreSQL local
3. SQLite fallback → Development
```

**Kenapa?**
- Fleksibel: support production dan development
- Railway auto-inject DATABASE_URL
- Developer bisa pakai SQLite tanpa install PostgreSQL

---

### 7.2 JWT Configuration

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
}
```

**Kenapa:**
- 24 jam: balance antara security dan convenience
- 7 hari refresh: user ga perlu login tiap hari
- No blacklist: simplify architecture (stateless)

---

### 7.3 CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',    # Next.js development
    'http://localhost:8100',    # Ionic development
    # Production URLs here
]
```

**Untuk apa?**
- Allow frontend (beda domain) akses API
- Security: cuma domain tertentu yang bisa akses

---

### 7.4 Authentication Backends

```python
AUTHENTICATION_BACKENDS = [
    'core.backends.CustomUserBackend',        # Email-based auth
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]
```

---

### 7.5 REST Framework Config

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.CustomJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

**Kenapa AllowAny?**
- Permission di-set per view/endpoint
- Login endpoint harus AllowAny
- Lebih fleksibel

---

### 7.6 Static Files (WhiteNoise)

```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Untuk apa?**
- Serve static files (CSS, JS, images) di production
- No need Nginx/Apache untuk static files
- Auto compression & caching

---

### 7.7 Timezone & Localization

```python
LANGUAGE_CODE = 'id-id'
TIME_ZONE = 'Asia/Jakarta'
USE_TZ = True
```

**Untuk apa?**
- Semua timestamp dalam WIB (UTC+7)
- Format tanggal Indonesia

---

## 8. URL Routing

> **File**: `core/urls.py`

### Router Structure

```python
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'rw', RWViewSet)
router.register(r'rt', RTViewSet)
router.register(r'residents', ResidentViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'security-schedules', SecurityScheduleViewSet)
router.register(r'security-personnel', SecurityPersonnelViewSet)
```

**Auto-generate endpoints:**
- `GET /api/users/` - List
- `POST /api/users/` - Create
- `GET /api/users/{id}/` - Detail
- `PUT /api/users/{id}/` - Update
- `PATCH /api/users/{id}/` - Partial Update
- `DELETE /api/users/{id}/` - Delete

---

### Manual Routes

```python
urlpatterns = [
    path('auth/login/', views.login_view),
    path('auth/refresh/', views.refresh_token_view),
    path('auth/me/', views.current_user),
    path('auth/verify/', views.verify_token),
    path('', include(router.urls)),
]
```

---

## 9. Flow Diagram

### 9.1 Authentication Flow

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │
       │ POST /api/auth/login/
       │ {email, password}
       ▼
┌─────────────────────┐
│   login_view()      │
│                     │
│ 1. Get user by email│
│ 2. Check password   │
│ 3. Generate JWT     │
└──────┬──────────────┘
       │
       │ {access, refresh, user}
       ▼
┌─────────────┐
│   Frontend  │
│ Store tokens│ 
│ in localStorage
└─────────────┘
```

---

### 9.2 RW Create RT Flow

```
┌─────────────┐
│   RW Login  │
└──────┬──────┘
       │
       │ POST /api/rw/create_rt/
       │ {name, email, phone}
       ▼
┌───────────────────────────┐
│  RWViewSet.create_rt()    │
│                           │
│ 1. Verify user role = rw  │
│ 2. Validate email unique  │
│ 3. Create User (role=rt)  │
│ 4. Set password default   │
│ 5. Create RT profile      │
│ 6. Link RT to RW          │
└──────┬────────────────────┘
       │
       │ {rt_id, email, password}
       ▼
┌─────────────┐
│   RW        │
│ Give creds  │
│ to RT       │
└─────────────┘
```

---

### 9.3 Warga Submit Feedback Flow

```
┌─────────────┐
│ Warga Login │
└──────┬──────┘
       │
       │ POST /api/feedbacks/
       │ {title, content, rating}
       ▼
┌──────────────────────────────┐
│ FeedbackViewSet.create()     │
│                              │
│ 1. Get user from token       │
│ 2. Auto-set user & RT        │
│ 3. Save feedback             │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────┐
│ RT Dashboard │
│ Sees new     │
│ feedback     │
└──────┬───────┘
       │
       │ POST /api/feedbacks/{id}/reply/
       │ {reply, replied_by}
       ▼
┌──────────────────────────────┐
│ FeedbackViewSet.reply()      │
│                              │
│ 1. Get feedback              │
│ 2. Set reply & replied_at    │
│ 3. Save                      │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│   Warga     │
│ Sees reply  │
└─────────────┘
```

---

### 9.4 Role-Based Data Access

```
┌─────────────┐
│ User Login  │
└──────┬──────┘
       │
       ├─ role = 'rw' ──────────────┐
       │                            │
       ├─ role = 'rt' ──────────┐   │
       │                        │   │
       └─ role = 'warga' ──┐    │   │
                           │    │   │
                           ▼    ▼   ▼
                    ┌──────────────────────┐
                    │  get_queryset()      │
                    │                      │
                    │  Filter data based   │
                    │  on user role        │
                    └──────┬───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Warga:       │   │ RT:          │   │ RW:          │
│ See own data │   │ See RT data  │   │ See all data │
│ only         │   │ only         │   │ in wilayah   │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 🎯 Summary - Kenapa Kode Didesain Seperti Ini?

### 1. **Security First**
- Password selalu di-hash (PBKDF2 + salt)
- JWT token dengan expiry
- Role-based access control
- CORS protection

### 2. **Scalability**
- Django REST Framework mature & proven
- PostgreSQL untuk production (handle millions records)
- Stateless JWT (easy horizontal scaling)
- Pagination built-in

### 3. **Developer Experience**
- Clear separation of concerns
- Custom serializers untuk complex operations
- Auto-documentation (Django REST Framework browser)
- Django Admin untuk debugging

### 4. **User Experience**
- Fast response (optimized queries)
- Mobile-friendly (REST API)
- Offline capability (JWT tokens)
- Real-time (PWA ready)

### 5. **Maintainability**
- Models terpisah per concern
- Reusable serializers
- DRY (Don't Repeat Yourself)
- Clear naming conventions

### 6. **Flexibility**
- Support multiple databases
- Environment-based config
- Easy deployment (Railway, Heroku, VPS)
- Docker ready

---

---

## 10. Frontend Integration - Cara Pakai Endpoint di React/Next.js

> Panduan lengkap cara menggunakan setiap endpoint di frontend  
> **Stack Frontend**: Next.js 14 (App Router), TypeScript, Axios

---

### 📋 Quick Reference - Endpoint Usage Map

| Endpoint | Service File | Page/Component | Digunakan Oleh |
|----------|--------------|----------------|----------------|
| `POST /auth/login/` | `authService.ts` | `app/login/page.tsx` | Semua role |
| `GET /auth/me/` | `authService.ts` | All protected pages | Semua role |
| `POST /rw/create_rt/` | `rtService.ts` | `app/rt-management/page.tsx` | RW only |
| `POST /rw/{id}/reset_password/` | `rtService.ts` | `app/rt-management/page.tsx` | RW only |
| `GET /rt/` | `rtService.ts` | `app/rt-management/page.tsx` | RW, RT |
| `POST /rt/create_resident/` | `wargaService.ts` | `app/warga-management/page.tsx` | RT only |
| `GET /residents/` | `residentService.ts` | `app/warga-management/page.tsx` | RW, RT, Warga |
| `GET /residents/stats/` | `residentService.ts` | `app/dashboard/page.tsx` | RW, RT |
| `POST /feedbacks/` | `feedbackService.ts` | `app/feedback/page.tsx` | Warga |
| `POST /feedbacks/{id}/reply/` | `feedbackService.ts` | `app/feedback/page.tsx` | RT, RW |
| `GET /feedbacks/` | `feedbackService.ts` | `app/feedback/page.tsx` | Semua role |
| `POST /announcements/` | `announcementService.ts` | `app/announcements/page.tsx` | RT, RW |
| `GET /announcements/` | `announcementService.ts` | `app/announcements/page.tsx` | Semua role |
| `POST /security-schedules/` | `securityScheduleService.ts` | `app/security-schedule/page.tsx` | RW only |
| `GET /security-schedules/` | `securityScheduleService.ts` | `app/jadwal-jaga/page.tsx` | Semua role |
| `POST /security-personnel/` | `securityPersonnelService.ts` | `app/security-personnel/page.tsx` | RW only |
| `GET /security-personnel/` | `securityPersonnelService.ts` | `app/security-personnel/page.tsx` | Semua role |

---

### 10.1 Struktur Frontend

```
smartneighbour/
├── services/
│   ├── api.ts                      # Axios client dengan interceptor
│   └── modules/
│       ├── authService.ts          # Auth endpoints wrapper
│       ├── feedbackService.ts      # Feedback endpoints wrapper
│       ├── rtService.ts            # RT endpoints wrapper
│       ├── residentService.ts      # Resident endpoints wrapper
│       └── ...
├── app/
│   ├── login/page.tsx              # Login page
│   ├── feedback/page.tsx           # Feedback management
│   ├── rt-management/page.tsx      # RW manage RT
│   ├── warga-management/page.tsx   # RT manage warga
│   └── ...
└── lib/
    └── tokenManager.ts             # Token management & refresh
```

---

### 10.2 Authentication Endpoints

#### **POST /api/auth/login/**

**📍 Digunakan di:**
- File: `services/modules/authService.ts`
- Page: `app/login/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/authService.ts
export const authService = {
  async login(email: string, password: string): Promise<any> {
    return postData<any>('/auth/login/', { email, password });
  },
}

// app/login/page.tsx
const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    // ✅ Call API
    const response = await authService.login(email, password);
    
    // ✅ Response: { access, refresh, user, message }
    
    // ✅ Save tokens
    tokenManager.setTokens(response.access, response.refresh);
    tokenManager.setUser(response.user);
    
    // ✅ Redirect berdasarkan role
    const redirectPath = getRedirectByRole(response.user.role);
    router.replace(redirectPath);
    
  } catch (err: any) {
    const errorMessage = err?.response?.data?.error || 'Login gagal';
    setError(errorMessage);
  }
};
```

**🔄 Flow:**
1. User input email & password
2. Call `authService.login()`
3. Backend return JWT tokens + user data
4. Frontend save ke localStorage via `tokenManager`
5. Auto-redirect sesuai role (RW → RT Management, RT → Warga Management, Warga → Announcements)

---

#### **GET /api/auth/me/**

**📍 Digunakan di:**
- File: `services/modules/authService.ts`
- Semua protected pages (via middleware/useEffect)

**📝 Cara Pakai:**

```typescript
// services/modules/authService.ts
export const authService = {
  async getProfile(): Promise<any> {
    return getData<any>('/auth/me/');
  },
}

// Example di page component
useEffect(() => {
  const checkAuth = async () => {
    try {
      const user = await authService.getProfile();
      setUser(user);
    } catch (error) {
      router.push('/login');
    }
  };
  
  checkAuth();
}, []);
```

**🔄 Auto Token Refresh:**

Frontend punya **interceptor** di `services/api.ts`:

```typescript
// Request interceptor - auto attach token
client.interceptors.request.use(async (config) => {
  // Check if token needs refresh
  if (tokenManager.needsRefresh()) {
    await tokenManager.refreshAccessToken();
  }
  
  const token = tokenManager.getToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  return config;
});

// Response interceptor - handle 401
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try refresh token
      const refreshed = await tokenManager.refreshAccessToken();
      if (refreshed) {
        // Retry request dengan token baru
        return client(originalRequest);
      }
      // Kalau gagal, redirect ke login
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

**✨ Benefit:**
- Token otomatis di-attach ke setiap request
- Auto-refresh kalau hampir expired
- Auto-redirect kalau token invalid

---

### 10.3 RW Endpoints

#### **POST /api/rw/create_rt/**

**📍 Digunakan di:**
- File: `services/modules/rtService.ts`
- Page: `app/rt-management/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/rtService.ts
export const rtService = {
  create: async (data: RTCreateData) => {
    try {
      const response = await client.post('/rw/create_rt/', data);
      return response.data;
    } catch (error: any) {
      throw error.response?.data || error;
    }
  },
};

// app/rt-management/page.tsx
const handleCreateRT = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    // ✅ Call API dengan data RT
    const response = await rtService.create({
      name: 'RT 01',
      email: 'rt01@example.com',
      phone: '081234567890',
      area: 'Blok A',
      address: 'Jl. Mawar No. 1'
    });
    
    // ✅ Response berisi credentials
    // {
    //   success: true,
    //   data: {
    //     rt_id: 1,
    //     user_email: 'rt01@example.com',
    //     generated_password: 'passw0rd'
    //   }
    // }
    
    // ✅ Show credentials ke RW
    await Swal.fire({
      title: 'RT Berhasil Dibuat!',
      html: `
        <p><strong>Email:</strong> ${response.data.user_email}</p>
        <p><strong>Password:</strong> ${response.data.generated_password}</p>
        <p class="text-sm">Berikan credentials ini ke RT untuk login</p>
      `,
      icon: 'success'
    });
    
    // ✅ Refresh list RT
    fetchRTs();
    
  } catch (error: any) {
    await showErrorAlert('Error', error.error || 'Gagal membuat RT');
  }
};
```

**🎯 Use Case:**
- RW login → Buka RT Management page
- Click "Tambah RT"
- Isi form (nama, email, dll)
- Submit → Backend create User + RT
- Modal show credentials
- RW kasih credentials ke RT baru

---

#### **POST /api/rw/{id}/reset_password/**

**📍 Digunakan di:**
- File: `services/modules/rtService.ts`
- Page: `app/rt-management/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/rtService.ts
export const rtService = {
  resetPassword: async (id: number) => {
    try {
      const response = await client.post(`/rw/${id}/reset_password/`);
      return response.data;
    } catch (error: any) {
      throw error.response?.data || error;
    }
  },
};

// app/rt-management/page.tsx
const handleResetPassword = async (rtId: number) => {
  // ✅ Confirm dialog
  const confirmed = await showConfirmAlert(
    'Reset Password?',
    'Password RT akan direset ke default'
  );
  
  if (!confirmed) return;
  
  try {
    // ✅ Call API
    const response = await rtService.resetPassword(rtId);
    
    // ✅ Show new password
    await Swal.fire({
      title: 'Password Berhasil Direset!',
      html: `
        <p><strong>Password Baru:</strong> ${response.data.new_password}</p>
        <p class="text-sm">Berikan password ini ke RT</p>
      `,
      icon: 'success'
    });
    
  } catch (error: any) {
    await showErrorAlert('Error', 'Gagal reset password');
  }
};
```

---

#### **GET /api/rt/**

**📍 Digunakan di:**
- File: `services/modules/rtService.ts`
- Page: `app/rt-management/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/rtService.ts
export const rtService = {
  getAll: async () => {
    try {
      const response = await client.get('/rt/');
      return response.data;
    } catch (error: any) {
      throw error.response?.data || error;
    }
  },
};

// app/rt-management/page.tsx
const fetchRTs = async () => {
  try {
    setIsLoading(true);
    const response = await rtService.getAll();
    
    // ✅ Backend auto-filter by role
    // RW → lihat semua RT dibawahnya
    // RT → lihat profile sendiri
    
    const data = (response.results || response.data || []) as RT[];
    setRts(data);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal memuat data RT');
  } finally {
    setIsLoading(false);
  }
};

useEffect(() => {
  fetchRTs();
}, []);
```

**✨ Auto-filtering by Backend:**
- Kalau RW login → return semua RT di RW-nya
- Kalau RT login → return profile RT sendiri
- Frontend tidak perlu logic filter

---

### 10.4 RT Endpoints

#### **POST /api/rt/create_resident/**

**📍 Digunakan di:**
- File: `services/modules/wargaService.ts`
- Page: `app/warga-management/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/wargaService.ts
export const wargaService = {
  create: async (data: WargaCreateData) => {
    try {
      const response = await client.post('/rt/create_resident/', data);
      return response.data;
    } catch (error: any) {
      throw error.response?.data || error;
    }
  },
};

// app/warga-management/page.tsx
const handleCreateWarga = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    const response = await wargaService.create({
      name: 'John Doe',
      email: 'john@example.com',
      phone: '081234567890',
      address: 'Blok A No. 10',
      ktp: '1234567890123456',
      kk: '1234567890123456',
      jumlah_keluarga: 4,
      kepala_keluarga: 'John Doe',
      status: 'aktif'
    });
    
    // ✅ Show credentials
    await Swal.fire({
      title: 'Warga Berhasil Didaftarkan!',
      html: `
        <p><strong>Email:</strong> ${response.data.user_email}</p>
        <p><strong>Password:</strong> ${response.data.generated_password}</p>
      `,
      icon: 'success'
    });
    
    fetchWarga();
    
  } catch (error: any) {
    await showErrorAlert('Error', error.error || 'Gagal mendaftarkan warga');
  }
};
```

**🎯 Use Case:**
- RT login → Buka Warga Management
- Click "Tambah Warga"
- Isi form lengkap (KTP, KK, dll)
- Submit → Backend create User + Resident
- Show credentials ke RT
- RT kasih credentials ke warga baru

---

### 10.5 Resident Endpoints

#### **GET /api/residents/**

**📍 Digunakan di:**
- File: `services/modules/residentService.ts`
- Page: `app/residents/page.tsx`, `app/warga-management/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/residentService.ts
export const residentService = {
  async getAll(params?: {
    page?: number;
    limit?: number;
    search?: string;
    status?: string;
  }): Promise<ApiResponse<Resident[]>> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.status) queryParams.append('status', params.status);

    const endpoint = `/residents/${queryParams.toString() ? `?${queryParams}` : ''}`;
    return getData<ApiResponse<Resident[]>>(endpoint);
  },
};

// app/warga-management/page.tsx
const fetchWarga = async () => {
  try {
    setIsLoading(true);
    
    // ✅ Call dengan optional params
    const response = await residentService.getAll({
      page: 1,
      limit: 50,
      status: 'aktif',  // Filter by status
      search: searchTerm  // Search by name/email
    });
    
    const data = response.results || response.data || [];
    setWarga(data);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal memuat data warga');
  } finally {
    setIsLoading(false);
  }
};

// ✅ Auto-filter by role (backend)
// RW → lihat semua warga di semua RT-nya
// RT → lihat warga di RT-nya saja
// Warga → lihat data diri sendiri
```

**🔍 Search & Filter:**

```typescript
// Search handler
const handleSearch = (value: string) => {
  setSearchTerm(value);
  
  // Debounce untuk performance
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchWarga();
  }, 500);
};

// Filter by status
const handleFilterStatus = (status: string) => {
  setStatusFilter(status);
  fetchWarga();
};
```

---

#### **GET /api/residents/stats/**

**📍 Digunakan di:**
- File: `services/modules/residentService.ts`
- Page: `app/dashboard/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/residentService.ts
export const residentService = {
  async getStats(): Promise<ApiResponse<{
    total: number;
    active: number;
    inactive: number;
  }>> {
    return getData<ApiResponse<any>>('/residents/stats/');
  },
};

// app/dashboard/page.tsx
const fetchStats = async () => {
  try {
    const stats = await residentService.getStats();
    
    // ✅ Display di dashboard cards
    setStats({
      totalWarga: stats.total,
      wargaAktif: stats.active,
      wargaTidakAktif: stats.inactive
    });
    
  } catch (error) {
    console.error('Error fetching stats:', error);
  }
};
```

---

### 10.6 Feedback Endpoints

#### **POST /api/feedbacks/**

**📍 Digunakan di:**
- File: `services/modules/feedbackService.ts`
- Page: `app/feedback/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/feedbackService.ts
export const feedbackService = {
  async create(data: FeedbackFormData): Promise<ApiResponse<Feedback>> {
    return postData<ApiResponse<Feedback>>('/feedbacks/', data);
  },
};

// app/feedback/page.tsx
const handleSubmitFeedback = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    // ✅ Call API
    await feedbackService.create({
      title: formData.title,
      content: formData.content,
      rating: 5,  // Optional rating 1-5
      author: user?.name || 'User',
    });
    
    await showSuccessAlert('Berhasil', 'Feedback berhasil dikirim');
    
    // ✅ Refresh list
    fetchFeedbacks();
    setModalOpen(false);
    
  } catch (error: any) {
    await showErrorAlert('Error', 'Gagal mengirim feedback');
  }
};
```

**🎯 Use Case:**
- Warga submit keluhan/feedback
- Backend auto-set user & RT dari token
- RT/RW bisa lihat feedback masuk

---

#### **POST /api/feedbacks/{id}/reply/**

**📍 Digunakan di:**
- File: `services/modules/feedbackService.ts`
- Page: `app/feedback/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/feedbackService.ts
export const feedbackService = {
  async reply(id: number, reply: string, replied_by?: string): Promise<ApiResponse<Feedback>> {
    return postData<ApiResponse<Feedback>>(`/feedbacks/${id}/reply/`, { 
      reply,
      replied_by: replied_by || 'Admin'
    });
  },
};

// app/feedback/page.tsx
const handleReplyFeedback = async (feedbackId: number) => {
  try {
    // ✅ Call API
    await feedbackService.reply(
      feedbackId,
      replyText,
      user?.name || 'RT'
    );
    
    await showSuccessAlert('Berhasil', 'Balasan berhasil dikirim');
    
    // ✅ Refresh untuk update UI
    fetchFeedbacks();
    setReplyModalOpen(false);
    
  } catch (error: any) {
    await showErrorAlert('Error', 'Gagal mengirim balasan');
  }
};
```

**🔄 Flow:**
1. Warga submit feedback
2. RT/RW lihat di list feedback
3. Click "Balas"
4. Isi reply text
5. Submit → Backend save reply + timestamp
6. Warga bisa lihat reply

---

#### **GET /api/feedbacks/**

**📍 Digunakan di:**
- File: `services/modules/feedbackService.ts`
- Page: `app/feedback/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/feedbackService.ts
export const feedbackService = {
  async getAll(params?: {
    page?: number;
    limit?: number;
    rating?: number;
  }): Promise<ApiResponse<Feedback[]>> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.rating) queryParams.append('rating', params.rating.toString());

    const endpoint = `/feedbacks/${queryParams.toString() ? `?${queryParams}` : ''}`;
    return getData<ApiResponse<Feedback[]>>(endpoint);
  },
};

// app/feedback/page.tsx
const fetchFeedbacks = async () => {
  try {
    setIsLoading(true);
    const response = await feedbackService.getAll();
    
    // ✅ Backend auto-filter by role & RT
    // Warga → lihat feedback di RT-nya (transparansi)
    // RT → lihat feedback dari warga di RT-nya
    // RW → lihat semua feedback
    
    const data = response.results || response.data || [];
    setFeedbacks(data);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal memuat data feedback');
  } finally {
    setIsLoading(false);
  }
};
```

---

### 10.7 Announcement Endpoints

#### **POST /api/announcements/**

**📍 Digunakan di:**
- File: `services/modules/announcementService.ts`
- Page: `app/announcements/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/announcementService.ts
export const announcementService = {
  async create(data: AnnouncementFormData): Promise<ApiResponse<Announcement>> {
    return postData<ApiResponse<Announcement>>('/announcements/', data);
  },
};

// app/announcements/page.tsx (RT/RW only)
const handleCreateAnnouncement = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await announcementService.create({
      title: formData.title,
      content: formData.content,
      priority: 'high',  // 'high', 'medium', 'low'
    });
    
    await showSuccessAlert('Berhasil', 'Pengumuman berhasil dipublikasikan');
    
    fetchAnnouncements();
    setModalOpen(false);
    
  } catch (error: any) {
    await showErrorAlert('Error', 'Gagal membuat pengumuman');
  }
};
```

**🎯 Priority System:**

```typescript
// Priority badge component
const getPriorityBadge = (priority: string) => {
  const styles = {
    high: 'bg-red-100 text-red-800 border-red-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-green-100 text-green-800 border-green-300'
  };
  
  return (
    <span className={`px-2 py-1 rounded ${styles[priority]}`}>
      {priority === 'high' ? '🔴 Urgent' : 
       priority === 'medium' ? '🟡 Penting' : 
       '🟢 Info'}
    </span>
  );
};
```

---

#### **GET /api/announcements/**

**📍 Digunakan di:**
- File: `services/modules/announcementService.ts`
- Page: `app/announcements/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/announcementService.ts
export const announcementService = {
  async getAll(params?: {
    page?: number;
    limit?: number;
    priority?: string;
  }): Promise<ApiResponse<Announcement[]>> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.priority) queryParams.append('priority', params.priority);

    const endpoint = `/announcements/${queryParams.toString() ? `?${queryParams}` : ''}`;
    return getData<ApiResponse<Announcement[]>>(endpoint);
  },
};

// app/announcements/page.tsx
const fetchAnnouncements = async () => {
  try {
    setIsLoading(true);
    
    const response = await announcementService.getAll({
      priority: priorityFilter  // Optional filter
    });
    
    // ✅ Backend auto-filter by role
    // Warga → lihat pengumuman dari RT-nya
    // RT → lihat pengumuman di RT-nya
    // RW → lihat semua pengumuman
    
    const data = response.results || response.data || [];
    setAnnouncements(data);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal memuat pengumuman');
  } finally {
    setIsLoading(false);
  }
};
```

---

### 10.8 Security Schedule Endpoints

#### **POST /api/security-schedules/**

**📍 Digunakan di:**
- File: `services/modules/securityScheduleService.ts`
- Page: `app/jadwal-jaga/page.tsx`, `app/security-schedule/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/securityScheduleService.ts
export const securityScheduleService = {
  async create(data: ScheduleFormData): Promise<ApiResponse<SecuritySchedule>> {
    return postData<ApiResponse<SecuritySchedule>>('/security-schedules/', data);
  },
};

// app/security-schedule/page.tsx
const handleCreateSchedule = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await securityScheduleService.create({
      name: 'Budi Santoso',  // Nama petugas
      shift: 'Pagi',  // 'Pagi', 'Siang', 'Malam'
      schedule_type: 'weekly',  // 'daily', 'weekly', 'monthly'
      start_date: '2026-05-01',
      end_date: '2026-05-31',
      weekday: 1,  // 0=Senin, 6=Minggu (untuk weekly)
      time: '08:00 - 16:00',
      status: 'aktif'
    });
    
    await showSuccessAlert('Berhasil', 'Jadwal berhasil dibuat');
    
    fetchSchedules();
    setModalOpen(false);
    
  } catch (error: any) {
    await showErrorAlert('Error', error.error || 'Gagal membuat jadwal');
  }
};
```

**📅 Schedule Types:**

```typescript
// Daily Schedule
{
  schedule_type: 'daily',
  date: '2026-05-15',  // Tanggal spesifik
}

// Weekly Schedule  
{
  schedule_type: 'weekly',
  start_date: '2026-05-01',
  end_date: '2026-05-31',
  weekday: 1,  // Setiap Selasa dalam range
}

// Monthly Schedule
{
  schedule_type: 'monthly',
  start_date: '2026-05-01',
  end_date: '2026-12-31',
  month_day: 15,  // Tanggal 15 setiap bulan
}
```

---

#### **GET /api/security-schedules/**

**📍 Digunakan di:**
- File: `services/modules/securityScheduleService.ts`
- Page: `app/jadwal-jaga/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/securityScheduleService.ts
export const securityScheduleService = {
  async getAll(params?: {
    shift?: string;
    date?: string;
  }): Promise<ApiResponse<SecuritySchedule[]>> {
    const queryParams = new URLSearchParams();
    if (params?.shift) queryParams.append('shift', params.shift);
    if (params?.date) queryParams.append('date', params.date);

    const endpoint = `/security-schedules/${queryParams.toString() ? `?${queryParams}` : ''}`;
    return getData<ApiResponse<SecuritySchedule[]>>(endpoint);
  },
};

// app/jadwal-jaga/page.tsx
const fetchSchedules = async () => {
  try {
    setIsLoading(true);
    
    const response = await securityScheduleService.getAll({
      shift: shiftFilter,  // Filter by shift
      date: selectedDate   // Filter by date
    });
    
    const data = response.results || response.data || [];
    setSchedules(data);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal memuat jadwal');
  } finally {
    setIsLoading(false);
  }
};
```

**📊 Display di Calendar:**

```typescript
// Group schedules by date for calendar view
const groupSchedulesByDate = (schedules: SecuritySchedule[]) => {
  const grouped: Record<string, SecuritySchedule[]> = {};
  
  schedules.forEach(schedule => {
    const dateKey = schedule.date || 'recurring';
    if (!grouped[dateKey]) {
      grouped[dateKey] = [];
    }
    grouped[dateKey].push(schedule);
  });
  
  return grouped;
};
```

---

### 10.9 Security Personnel Endpoints

#### **POST /api/security-personnel/**

**📍 Digunakan di:**
- File: `services/modules/securityPersonnelService.ts`
- Page: `app/security-personnel/page.tsx`

**📝 Cara Pakai:**

```typescript
// services/modules/securityPersonnelService.ts
export const securityPersonnelService = {
  async create(data: PersonnelFormData): Promise<ApiResponse<SecurityPersonnel>> {
    return postData<ApiResponse<SecurityPersonnel>>('/security-personnel/', data);
  },
};

// app/security-personnel/page.tsx
const handleCreatePersonnel = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await securityPersonnelService.create({
      name: 'Budi Santoso',
      phone: '081234567890',
      email: 'budi@example.com',
      address: 'Jl. Merdeka No. 1',
      area: 'Blok A-C',
      status: 'aktif',
      notes: 'Tersedia shift malam'
    });
    
    await showSuccessAlert('Berhasil', 'Petugas berhasil ditambahkan');
    
    fetchPersonnel();
    setModalOpen(false);
    
  } catch (error: any) {
    await showErrorAlert('Error', 'Gagal menambahkan petugas');
  }
};
```

**🎯 Use Case:**
- RW maintain master data petugas
- Saat buat jadwal, pilih dari master data
- Auto-link by name

---

### 10.10 Error Handling Pattern

**Global Error Handler:**

```typescript
// services/api.ts
client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      
      // ✅ 401 Unauthorized → Try refresh, then logout
      if (status === 401) {
        const refreshed = await tokenManager.refreshAccessToken();
        if (refreshed) {
          // Retry request
          return client(originalRequest);
        }
        // Redirect to login
        tokenManager.clearAuth();
        window.location.href = '/login';
      }
      
      // ✅ 403 Forbidden
      else if (status === 403) {
        await showErrorAlert('Akses Ditolak', 'Anda tidak memiliki izin');
      }
      
      // ✅ 500 Server Error
      else if (status >= 500) {
        await showErrorAlert('Server Error', 'Terjadi kesalahan server');
      }
    }
    
    // ✅ Network Error
    else if (error.request) {
      await showErrorAlert('Network Error', 'Tidak dapat terhubung ke server');
    }
    
    return Promise.reject(error);
  }
);
```

**Local Error Handler:**

```typescript
// Component level
try {
  await someService.create(data);
  await showSuccessAlert('Berhasil', 'Data berhasil disimpan');
} catch (error: any) {
  const errorMessage = 
    error?.response?.data?.error ||         // Backend error message
    error?.response?.data?.detail ||        // Backend detail
    error?.message ||                       // JS error
    'Terjadi kesalahan';                    // Fallback
  
  await showErrorAlert('Error', errorMessage);
}
```

---

### 10.11 Best Practices Frontend

#### **1. Loading States**

```typescript
const [isLoading, setIsLoading] = useState(false);

const fetchData = async () => {
  try {
    setIsLoading(true);
    const data = await someService.getAll();
    setData(data);
  } catch (error) {
    // Handle error
  } finally {
    setIsLoading(false);  // Always set loading false
  }
};
```

#### **2. Debounce Search**

```typescript
let searchTimeout: NodeJS.Timeout;

const handleSearch = (value: string) => {
  setSearchTerm(value);
  
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchData();  // Call API after 500ms idle
  }, 500);
};
```

#### **3. Optimistic UI Updates**

```typescript
const handleDelete = async (id: number) => {
  // Show loading immediately
  const optimisticData = data.filter(item => item.id !== id);
  setData(optimisticData);
  
  try {
    await someService.delete(id);
    await showSuccessAlert('Berhasil', 'Data berhasil dihapus');
  } catch (error) {
    // Revert on error
    fetchData();
    await showErrorAlert('Error', 'Gagal menghapus data');
  }
};
```

#### **4. Role-Based Access Control**

```typescript
// lib/rolePermissions.ts
export const getPermissions = (role: UserRole) => {
  const permissions = {
    rw: {
      canCreateRT: true,
      canManageSchedule: true,
      canViewAllData: true,
    },
    rt: {
      canCreateResident: true,
      canReplyFeedback: true,
      canCreateAnnouncement: true,
    },
    warga: {
      canSubmitFeedback: true,
      canViewAnnouncements: true,
    }
  };
  
  return permissions[role];
};

// Usage in component
const permissions = getPermissions(userRole);

if (permissions.canCreateRT) {
  // Show "Tambah RT" button
}
```

---

### 10.12 Deployment & Environment

**Environment Variables:**

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

```env
# .env.production
NEXT_PUBLIC_API_URL=https://api.smartneighbour.com/api
```

**Auto-switch berdasarkan environment:**

```typescript
// services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
```

---

### 10.13 Complete Flow Diagram - Frontend ↔ Backend

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Request (Axios)
                              │ Header: Authorization: Bearer <token>
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           API Client Interceptor (services/api.ts)          │
│                                                             │
│  1. Check if token needs refresh                           │
│  2. Auto-attach Authorization header                       │
│  3. Handle 401 → Refresh → Retry                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (Django REST Framework)            │
│                                                             │
│  Middleware Stack:                                          │
│  1. CORS Middleware ✓                                      │
│  2. JWT Authentication ✓                                   │
│  3. Permission Classes ✓                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ViewSet / API View                         │
│                                                             │
│  1. get_queryset() → Filter by role                        │
│  2. Serializer validation                                   │
│  3. Business logic                                          │
│  4. Database operations                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Query Result
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Serializer Transform                      │
│                                                             │
│  Python Object → JSON                                       │
│  Include related data (user_email, rt_name, etc)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ JSON Response
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Response Interceptor (services/api.ts)         │
│                                                             │
│  - Handle errors globally                                   │
│  - Show error alerts                                        │
│  - Redirect on 401                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND Component                        │
│                                                             │
│  1. Update state                                            │
│  2. Re-render UI                                            │
│  3. Show success/error alert                                │
└─────────────────────────────────────────────────────────────┘
```

---

### 10.14 Troubleshooting Guide

#### **Problem: Token expired / 401 Error**

**Solution:**
```typescript
// Check token validity
const token = tokenManager.getToken();
const isValid = tokenManager.isTokenValid();

if (!isValid) {
  // Try refresh
  const refreshed = await tokenManager.refreshAccessToken();
  
  if (!refreshed) {
    // Redirect to login
    router.push('/login');
  }
}
```

---

#### **Problem: CORS Error**

**Check Backend:**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Add your frontend URL
]
```

**Check Frontend:**
```typescript
// services/api.ts
const API_URL = 'http://localhost:8000/api';  // Make sure URL is correct
```

---

#### **Problem: 403 Forbidden**

**Check Permissions:**
```typescript
// Frontend - Check if user has permission
const permissions = getPermissions(userRole);

if (!permissions.canCreateRT) {
  showErrorAlert('Akses Ditolak', 'Anda tidak memiliki izin');
  return;
}
```

```python
# Backend - Check permission in view
if request.user.role != 'rw':
    return Response({'error': 'Hanya RW yang bisa akses'}, status=403)
```

---

#### **Problem: Data tidak muncul / Empty array**

**Debug Steps:**
```typescript
// 1. Check API response
const response = await someService.getAll();
console.log('API Response:', response);

// 2. Check data structure
const data = response.results || response.data || [];
console.log('Data:', data);

// 3. Check backend filter
// Backend auto-filter by role, pastikan user role benar
console.log('User Role:', user.role);
```

---

#### **Problem: Network Error / Timeout**

**Solution:**
```typescript
// Increase timeout
const client = axios.create({
  timeout: 30000,  // 30 seconds
});

// Add retry logic
const retry = async (fn: Function, retries = 3) => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return retry(fn, retries - 1);
    }
    throw error;
  }
};
```

---

### 10.15 Performance Optimization Tips

#### **1. Use React Query / SWR for Caching**

```typescript
import useSWR from 'swr';

const { data, error, isLoading } = useSWR(
  '/residents/',
  () => residentService.getAll(),
  {
    revalidateOnFocus: false,
    dedupingInterval: 60000,  // Cache 1 minute
  }
);
```

---

#### **2. Implement Pagination**

```typescript
const [page, setPage] = useState(1);
const [hasMore, setHasMore] = useState(true);

const loadMore = async () => {
  const response = await residentService.getAll({ 
    page: page + 1,
    limit: 20 
  });
  
  if (response.results.length === 0) {
    setHasMore(false);
  } else {
    setData([...data, ...response.results]);
    setPage(page + 1);
  }
};
```

---

#### **3. Debounce Heavy Operations**

```typescript
import { debounce } from 'lodash';

const debouncedSearch = debounce((value: string) => {
  fetchData({ search: value });
}, 500);

const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
  setSearchTerm(e.target.value);
  debouncedSearch(e.target.value);
};
```

---

#### **4. Lazy Load Routes**

```typescript
// app/layout.tsx
import dynamic from 'next/dynamic';

const FeedbackPage = dynamic(() => import('./feedback/page'), {
  loading: () => <Loading />,
});
```

---

### 10.16 Testing Examples

#### **Test API Service**

```typescript
// __tests__/services/authService.test.ts
import { authService } from '@/services/modules/authService';

describe('Auth Service', () => {
  it('should login successfully', async () => {
    const response = await authService.login(
      'test@example.com',
      'password123'
    );
    
    expect(response).toHaveProperty('access');
    expect(response).toHaveProperty('refresh');
    expect(response.user.email).toBe('test@example.com');
  });
  
  it('should handle login error', async () => {
    await expect(
      authService.login('wrong@email.com', 'wrongpass')
    ).rejects.toThrow();
  });
});
```

---

#### **Test Component**

```typescript
// __tests__/app/login/page.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '@/app/login/page';

describe('Login Page', () => {
  it('should submit login form', async () => {
    render(<LoginPage />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/berhasil/i)).toBeInTheDocument();
    });
  });
});
```

---

### 10.17 Security Checklist

#### **Frontend Security**

- ✅ **Never log sensitive data** (passwords, tokens)
- ✅ **Sanitize user input** before display
- ✅ **Use HTTPS** in production
- ✅ **Validate on both client & server**
- ✅ **Implement CSRF protection**
- ✅ **Set secure HTTP headers**
- ✅ **Use Content Security Policy**
- ✅ **Store tokens securely** (httpOnly cookies atau localStorage with encryption)

```typescript
// Bad - Don't log tokens
console.log('Token:', token);

// Good - Log without sensitive data
console.log('Login successful');

// Bad - Direct innerHTML
element.innerHTML = userInput;

// Good - Use React (auto-escapes)
<div>{userInput}</div>
```

---

### 10.18 Summary - Frontend Integration

**✨ Apa yang Sudah Dijelaskan:**

1. **Service Layer** - Wrapper untuk semua API calls
2. **Auto Authentication** - Token auto-attach & refresh
3. **Error Handling** - Global & local error handlers
4. **Role-Based Access** - Frontend filter by permissions
5. **Loading States** - Better UX dengan loading indicators
6. **Search & Filter** - Debounced search, query params
7. **CRUD Operations** - Create, Read, Update, Delete patterns
8. **File & Page Mapping** - Tahu endpoint dipakai dimana
9. **Code Examples** - Real code dari aplikasi
10. **Best Practices** - Performance, security, testing

**🎯 Key Takeaways:**

✅ **Frontend tidak perlu logic kompleks** - Backend sudah filter by role  
✅ **Token management otomatis** - Interceptor handle semua  
✅ **Error handling global** - Consistent error messages  
✅ **Type-safe** - TypeScript untuk prevent bugs  
✅ **Reusable** - Service layer bisa dipake di mana aja  
✅ **Scalable** - Easy to add new endpoints  

**📚 Dokumentasi Lengkap:**
- Backend API: Section 1-9
- Frontend Integration: Section 10
- Flow Diagrams: Throughout
- Troubleshooting: Section 10.14
- Best Practices: Section 10.11, 10.15, 10.17

Dokumentasi ini **living document** - akan di-update seiring development! 🚀

---

## 📞 Kontak & Support

Untuk pertanyaan lebih lanjut tentang kode ini, silakan hubungi tim development.

---

**Last Updated**: April 29, 2026  
**Version**: 2.0.0  
**Author**: SmartNeighbour Development Team
