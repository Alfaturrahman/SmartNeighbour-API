# Panduan Fix JWT Authentication Issue

## Masalah yang Diperbaiki

Error 401 Unauthorized pada `/api/auth/me/` setelah login berhasil disebabkan oleh:

1. **Token Generation**: Token JWT tidak dibuat dengan benar di login endpoint
2. **Error Handling**: Error handling tidak lengkap di endpoint autentikasi
3. **Missing Endpoints**: Tidak ada endpoint untuk refresh token

## Perubahan yang Dilakukan

### 1. Login Endpoint (`/api/auth/login/`)
- ✅ Fixed token generation - sekarang access token dibuat dengan custom claims yang benar
- ✅ Improved error messages dengan detail yang lebih jelas
- ✅ Tambah validasi user is_active sebelum generate token

### 2. Current User Endpoint (`/api/auth/me/`)
- ✅ Improved error handling untuk berbagai kasus error
- ✅ Tambah validasi token format yang lebih robust
- ✅ Tambah pengecekan user is_active
- ✅ Better error messages dengan detail spesifik

### 3. Verify Token Endpoint (`/api/auth/verify/`)
- ✅ Enhanced dengan response yang lebih lengkap
- ✅ Return token payload info (user_id, email, role, exp)
- ✅ Better error handling

### 4. Refresh Token Endpoint (NEW: `/api/auth/refresh/`)
- ✅ Endpoint baru untuk refresh access token
- ✅ Validasi refresh token dan user status
- ✅ Generate new access token dengan custom claims

## Testing

### Cara 1: Menggunakan Test Script
```powershell
# Jalankan test script
.\test_auth.ps1
```

### Cara 2: Manual Testing dengan PowerShell

```powershell
# 1. Login
$loginBody = @{
    email = "admin@smartneighbour.com"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" -Method Post -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access

# 2. Get Current User
$headers = @{ "Authorization" = "Bearer $token" }
$user = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me/" -Method Get -Headers $headers
Write-Host "User: $($user.name) - $($user.email)"

# 3. Verify Token
$verify = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/verify/" -Method Get -Headers $headers
Write-Host "Token valid: $($verify.valid)"

# 4. Refresh Token
$refreshBody = @{ refresh = $loginResponse.refresh } | ConvertTo-Json
$newToken = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/refresh/" -Method Post -Body $refreshBody -ContentType "application/json"
Write-Host "New Access Token: $($newToken.access.Substring(0, 50))..."
```

### Cara 3: Testing dari Frontend

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@smartneighbour.com',
    password: 'admin123'
  })
});
const { access, refresh, user } = await loginResponse.json();

// 2. Get Current User
const meResponse = await fetch('http://localhost:8000/api/auth/me/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
const currentUser = await meResponse.json();
console.log('Current User:', currentUser);

// 3. Verify Token
const verifyResponse = await fetch('http://localhost:8000/api/auth/verify/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
const verifyData = await verifyResponse.json();
console.log('Token Valid:', verifyData.valid);

// 4. Refresh Token (ketika access token expired)
const refreshResponse = await fetch('http://localhost:8000/api/auth/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh })
});
const { access: newAccess } = await refreshResponse.json();
```

## API Endpoints yang Tersedia

| Endpoint | Method | Auth | Deskripsi |
|----------|--------|------|-----------|
| `/api/auth/login/` | POST | ❌ No | Login dan dapatkan JWT tokens |
| `/api/auth/refresh/` | POST | ❌ No | Refresh access token |
| `/api/auth/me/` | GET | ✅ Yes | Get current user info |
| `/api/auth/verify/` | GET/POST | ✅ Yes | Verify token validity |
| `/api/users/` | GET/POST | ✅ Yes | Manage users |
| `/api/residents/` | GET/POST | ✅ Yes | Manage residents |
| `/api/feedbacks/` | GET/POST | ✅ Yes | Manage feedbacks |
| `/api/announcements/` | GET/POST | ✅ Yes | Manage announcements |
| `/api/security-schedules/` | GET/POST | ✅ Yes | Manage security schedules |

## Error Responses

Semua endpoint sekarang memberikan error response yang lebih informatif:

```json
{
  "error": "Token tidak valid atau expired",
  "detail": "Token has expired"
}
```

Untuk debugging, tambahkan `?debug=1` di URL untuk mendapatkan traceback lengkap.

## Troubleshooting

### Masalah: Masih mendapat 401 setelah login
**Solusi:**
1. Check apakah token disimpan dengan benar di frontend
2. Verify format Authorization header: `Bearer <token>`
3. Check token expiry dengan `/api/auth/verify/`
4. Gunakan test script untuk isolate masalah

### Masalah: Token expired
**Solusi:**
1. Gunakan refresh token di `/api/auth/refresh/` untuk mendapat access token baru
2. Access token lifetime: 24 jam (dapat diubah di settings.py)
3. Refresh token lifetime: 7 hari (dapat diubah di settings.py)

### Masalah: User not found
**Solusi:**
1. Pastikan user ada di database
2. Check apakah user is_active = True
3. Buat user baru atau update existing user

## Next Steps

1. ✅ Restart Django server untuk apply changes
2. ✅ Test dengan script: `.\test_auth.ps1`
3. ✅ Test dari frontend application
4. ✅ Update frontend untuk menggunakan endpoint `/api/auth/refresh/` untuk auto-refresh token
