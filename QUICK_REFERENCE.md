# 🚀 Quick Reference - SmartNeighbour API

> Cheat sheet untuk developer - cara cepat pakai API

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [RW Endpoints](#rw-endpoints-rukun-warga)
- [RT Endpoints](#rt-endpoints-rukun-tetangga)
- [Resident Endpoints](#resident-endpoints-warga)
- [Feedback Endpoints](#feedback-endpoints)
- [Announcement Endpoints](#announcement-endpoints)
- [Security Schedule Endpoints](#security-schedule-endpoints)
- [Error Codes](#error-codes)

---

## Authentication

### Login
```typescript
// Request
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}

// Response
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "role": "rw"
  }
}

// Frontend Usage
const response = await authService.login(email, password);
tokenManager.setTokens(response.access, response.refresh);
```

### Get Current User
```typescript
// Request
GET /api/auth/me/
Headers: Authorization: Bearer <access_token>

// Response
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "role": "rw"
}

// Frontend Usage
const user = await authService.getProfile();
```

### Refresh Token
```typescript
// Request
POST /api/auth/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}

// Response
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "message": "Token berhasil di-refresh"
}

// Auto-handled by interceptor
```

---

## RW Endpoints (Rukun Warga)

### Create RT
```typescript
// Request
POST /api/rw/create_rt/
Headers: Authorization: Bearer <access_token>
{
  "name": "RT 01",
  "email": "rt01@example.com",
  "phone": "081234567890",
  "area": "Blok A",
  "address": "Jl. Mawar No. 1"
}

// Response
{
  "success": true,
  "message": "RT berhasil dibuat",
  "data": {
    "rt_id": 1,
    "user_email": "rt01@example.com",
    "generated_password": "passw0rd"
  }
}

// Frontend Usage
const response = await rtService.create(formData);
```

### Reset RT Password
```typescript
// Request
POST /api/rw/{rt_id}/reset_password/
Headers: Authorization: Bearer <access_token>

// Response
{
  "success": true,
  "message": "Password RT berhasil direset",
  "data": {
    "rt_id": 1,
    "user_email": "rt01@example.com",
    "new_password": "passw0rd"
  }
}

// Frontend Usage
const response = await rtService.resetPassword(rtId);
```

### Get All RT
```typescript
// Request
GET /api/rt/
Headers: Authorization: Bearer <access_token>

// Response (Auto-filtered by role)
{
  "results": [
    {
      "id": 1,
      "name": "RT 01",
      "user_email": "rt01@example.com",
      "rw": 1,
      "rw_name": "RW 01",
      "area": "Blok A",
      "phone": "081234567890"
    }
  ]
}

// Frontend Usage
const rts = await rtService.getAll();
```

---

## RT Endpoints (Rukun Tetangga)

### Create Resident
```typescript
// Request
POST /api/rt/create_resident/
Headers: Authorization: Bearer <access_token>
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

// Response
{
  "success": true,
  "message": "Warga berhasil didaftarkan",
  "data": {
    "resident_id": 1,
    "user_email": "john@example.com",
    "generated_password": "passw0rd"
  }
}

// Frontend Usage
const response = await wargaService.create(formData);
```

---

## Resident Endpoints (Warga)

### Get All Residents
```typescript
// Request
GET /api/residents/?status=aktif&search=john
Headers: Authorization: Bearer <access_token>

// Response (Auto-filtered by role)
{
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "081234567890",
      "address": "Blok A No. 10",
      "rt": 1,
      "rt_name": "RT 01",
      "status": "aktif",
      "ktp": "1234567890123456",
      "kk": "1234567890123456"
    }
  ]
}

// Frontend Usage
const residents = await residentService.getAll({
  status: 'aktif',
  search: 'john'
});
```

### Get Resident Stats
```typescript
// Request
GET /api/residents/stats/
Headers: Authorization: Bearer <access_token>

// Response
{
  "total": 500,
  "active": 480,
  "inactive": 20
}

// Frontend Usage
const stats = await residentService.getStats();
```

### Update Resident
```typescript
// Request
PUT /api/residents/{id}/
Headers: Authorization: Bearer <access_token>
{
  "name": "John Doe Updated",
  "phone": "081234567899"
}

// Response
{
  "id": 1,
  "name": "John Doe Updated",
  "email": "john@example.com",
  ...
}

// Frontend Usage
const updated = await residentService.update(id, formData);
```

### Delete Resident
```typescript
// Request
DELETE /api/residents/{id}/
Headers: Authorization: Bearer <access_token>

// Response
204 No Content

// Frontend Usage
await residentService.delete(id);
```

---

## Feedback Endpoints

### Submit Feedback
```typescript
// Request
POST /api/feedbacks/
Headers: Authorization: Bearer <access_token>
{
  "title": "Complaint Title",
  "content": "Complaint details...",
  "rating": 3,
  "author": "John Doe"
}

// Response
{
  "id": 1,
  "title": "Complaint Title",
  "content": "Complaint details...",
  "rating": 3,
  "author": "John Doe",
  "date": "2026-04-29",
  "reply": null,
  "replied_at": null
}

// Frontend Usage
await feedbackService.create(formData);
```

### Reply to Feedback
```typescript
// Request
POST /api/feedbacks/{id}/reply/
Headers: Authorization: Bearer <access_token>
{
  "reply": "Terima kasih atas feedback-nya...",
  "replied_by": "RT 01"
}

// Response
{
  "id": 1,
  "title": "Complaint Title",
  "reply": "Terima kasih atas feedback-nya...",
  "replied_by": "RT 01",
  "replied_at": "2026-04-29T10:30:00Z"
}

// Frontend Usage
await feedbackService.reply(feedbackId, replyText, user.name);
```

### Get All Feedbacks
```typescript
// Request
GET /api/feedbacks/?rating=5
Headers: Authorization: Bearer <access_token>

// Response (Auto-filtered by role)
{
  "results": [
    {
      "id": 1,
      "title": "Complaint Title",
      "content": "Details...",
      "rating": 3,
      "author": "John Doe",
      "user_email": "john@example.com",
      "rt_name": "RT 01",
      "reply": "Response...",
      "replied_by": "RT 01",
      "date": "2026-04-29"
    }
  ]
}

// Frontend Usage
const feedbacks = await feedbackService.getAll({ rating: 5 });
```

### Get Feedback Stats
```typescript
// Request
GET /api/feedbacks/stats/
Headers: Authorization: Bearer <access_token>

// Response
{
  "total": 150,
  "replied": 120,
  "unreplied": 30,
  "average_rating": 4.2
}

// Frontend Usage
const stats = await feedbackService.getStats();
```

---

## Announcement Endpoints

### Create Announcement
```typescript
// Request
POST /api/announcements/
Headers: Authorization: Bearer <access_token>
{
  "title": "Important Notice",
  "content": "Announcement details...",
  "priority": "high"
}

// Response
{
  "id": 1,
  "title": "Important Notice",
  "content": "Announcement details...",
  "priority": "high",
  "author": "RT 01",
  "date": "2026-04-29"
}

// Frontend Usage
await announcementService.create(formData);
```

### Get All Announcements
```typescript
// Request
GET /api/announcements/?priority=high
Headers: Authorization: Bearer <access_token>

// Response (Auto-filtered by role)
{
  "results": [
    {
      "id": 1,
      "title": "Important Notice",
      "content": "Details...",
      "priority": "high",
      "author": "RT 01",
      "rt_name": "RT 01",
      "date": "2026-04-29"
    }
  ]
}

// Frontend Usage
const announcements = await announcementService.getAll({
  priority: 'high'
});
```

---

## Security Schedule Endpoints

### Create Schedule
```typescript
// Request
POST /api/security-schedules/
Headers: Authorization: Bearer <access_token>

// Daily Schedule
{
  "name": "Budi Santoso",
  "shift": "Pagi",
  "schedule_type": "daily",
  "date": "2026-05-15",
  "time": "08:00 - 16:00",
  "status": "aktif"
}

// Weekly Schedule
{
  "name": "Budi Santoso",
  "shift": "Pagi",
  "schedule_type": "weekly",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "weekday": 1,  // 0=Senin, 6=Minggu
  "time": "08:00 - 16:00",
  "status": "aktif"
}

// Monthly Schedule
{
  "name": "Budi Santoso",
  "shift": "Pagi",
  "schedule_type": "monthly",
  "start_date": "2026-05-01",
  "end_date": "2026-12-31",
  "month_day": 15,  // Tanggal 15 setiap bulan
  "time": "08:00 - 16:00",
  "status": "aktif"
}

// Response
{
  "id": 1,
  "name": "Budi Santoso",
  "shift": "Pagi",
  "schedule_type": "weekly",
  "personnel_name": "Budi Santoso",
  "personnel_phone": "081234567890"
}

// Frontend Usage
await securityScheduleService.create(formData);
```

### Get All Schedules
```typescript
// Request
GET /api/security-schedules/?shift=Pagi&date=2026-05-15
Headers: Authorization: Bearer <access_token>

// Response
{
  "results": [
    {
      "id": 1,
      "name": "Budi Santoso",
      "shift": "Pagi",
      "schedule_type": "daily",
      "date": "2026-05-15",
      "time": "08:00 - 16:00",
      "personnel_name": "Budi Santoso",
      "personnel_phone": "081234567890",
      "status": "aktif"
    }
  ]
}

// Frontend Usage
const schedules = await securityScheduleService.getAll({
  shift: 'Pagi',
  date: '2026-05-15'
});
```

### Create Security Personnel
```typescript
// Request
POST /api/security-personnel/
Headers: Authorization: Bearer <access_token>
{
  "name": "Budi Santoso",
  "phone": "081234567890",
  "email": "budi@example.com",
  "address": "Jl. Merdeka No. 1",
  "area": "Blok A-C",
  "status": "aktif",
  "notes": "Tersedia shift malam"
}

// Response
{
  "id": 1,
  "name": "Budi Santoso",
  "phone": "081234567890",
  "email": "budi@example.com",
  "rw_name": "RW 01",
  "status": "aktif"
}

// Frontend Usage
await securityPersonnelService.create(formData);
```

---

## Error Codes

### Common HTTP Status Codes

| Code | Meaning | Handling |
|------|---------|----------|
| **200** | OK | Success |
| **201** | Created | Resource created successfully |
| **204** | No Content | Delete successful |
| **400** | Bad Request | Validation error, check request data |
| **401** | Unauthorized | Token invalid/expired, refresh or login |
| **403** | Forbidden | No permission to access resource |
| **404** | Not Found | Resource not found |
| **500** | Server Error | Backend error, contact admin |

### Backend Error Response Format

```json
{
  "error": "Error title",
  "detail": "Detailed error message"
}
```

### Frontend Error Handling

```typescript
try {
  await someService.create(data);
} catch (error: any) {
  const errorMessage = 
    error?.response?.data?.error ||
    error?.response?.data?.detail ||
    error?.message ||
    'Terjadi kesalahan';
  
  await showErrorAlert('Error', errorMessage);
}
```

---

## Role-Based Access

| Role | Permissions |
|------|------------|
| **RW** | • Create/manage RT<br>• View all residents<br>• Create security schedules<br>• View all feedback & announcements |
| **RT** | • Create/manage residents<br>• Reply feedback<br>• Create announcements<br>• View residents in RT |
| **Warga** | • Submit feedback<br>• View announcements<br>• View own data |

---

## Auto-Filtering by Backend

✅ **Semua GET endpoints** otomatis filter data berdasarkan role user:

- `GET /api/residents/` → RW lihat semua, RT lihat di RT-nya, Warga lihat diri sendiri
- `GET /api/feedbacks/` → Filter by RT & role
- `GET /api/announcements/` → Filter by RT & role
- `GET /api/security-schedules/` → Filter by RW

**Frontend tidak perlu logic filter!** Backend sudah handle.

---

## Token Management

### Auto-Refresh Flow

```
1. Request sent
2. Interceptor checks token expiry
3. If < 5 mins remaining → Auto refresh
4. Attach new token
5. Send request
```

### Manual Refresh

```typescript
const refreshed = await tokenManager.refreshAccessToken();
if (refreshed) {
  // Token refreshed, retry request
} else {
  // Refresh failed, redirect to login
  router.push('/login');
}
```

---

## Query Parameters

### Pagination
```
GET /api/residents/?page=2&limit=20
```

### Search
```
GET /api/residents/?search=john
```

### Filter by Status
```
GET /api/residents/?status=aktif
```

### Multiple Filters
```
GET /api/residents/?status=aktif&search=john&page=1&limit=20
```

---

## Tips & Best Practices

### ✅ DO's
- Always handle errors with try-catch
- Use loading states for better UX
- Debounce search inputs (500ms)
- Cache data when possible (SWR/React Query)
- Validate input on frontend before API call
- Show success/error alerts to user

### ❌ DON'Ts
- Don't log sensitive data (tokens, passwords)
- Don't fetch data on every render
- Don't ignore error handling
- Don't hardcode API URLs
- Don't expose tokens in URL params

---

## Environment Setup

### Development
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Production
```env
NEXT_PUBLIC_API_URL=https://api.smartneighbour.com/api
```

---

## Quick Commands

### Backend (Django)
```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access admin
http://localhost:8000/admin/
```

### Frontend (Next.js)
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start
```

---

**📚 Lihat dokumentasi lengkap di**: `DOKUMENTASI_KODE.md`

**Last Updated**: April 29, 2026  
**Version**: 1.0.0
