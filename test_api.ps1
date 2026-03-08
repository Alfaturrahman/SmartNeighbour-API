# Smart Neighbourhood API Test Script
$baseUrl = "http://127.0.0.1:8000/api"
$token = ""

Write-Host "=== SMART NEIGHBOURHOOD API TESTING ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Login
Write-Host "[1] Testing Login..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@smartneighbour.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $response.access
    Write-Host "✓ Login Success!" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0,20))..." -ForegroundColor Gray
    Write-Host "  User: $($response.user.name) ($($response.user.role))" -ForegroundColor Gray
} catch {
    Write-Host "✗ Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host ""

# Test 2: Get Current User
Write-Host "[2] Testing Get Current User..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/me/" -Headers $headers
    Write-Host "✓ Success! User: $($response.name)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Get Users
Write-Host "[3] Testing Get Users..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/users/" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) users" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Get Users Stats
Write-Host "[4] Testing Get Users Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/users/stats/" -Headers $headers
    Write-Host "✓ Success! Total: $($response.total), Active: $($response.active)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 5: Get Residents
Write-Host "[5] Testing Get Residents..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/residents/" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) residents" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 6: Get Residents Stats
Write-Host "[6] Testing Get Residents Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/residents/stats/" -Headers $headers
    Write-Host "✓ Success! Total: $($response.total), Active: $($response.active), Inactive: $($response.inactive)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 7: Create Resident
Write-Host "[7] Testing Create Resident..." -ForegroundColor Yellow
$newResident = @{
    name = "Test User"
    address = "Jl. Test No. 123"
    phone = "08123456789"
    email = "test@example.com"
    status = "aktif"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/residents/" -Method POST -Body $newResident -Headers $headers
    $newResidentId = $response.id
    Write-Host "✓ Success! Created resident ID: $newResidentId" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    $newResidentId = 1
}

Write-Host ""

# Test 8: Get Feedbacks
Write-Host "[8] Testing Get Feedbacks..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/feedbacks/" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) feedbacks" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 9: Get Feedbacks Stats
Write-Host "[9] Testing Get Feedbacks Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/feedbacks/stats/" -Headers $headers
    Write-Host "✓ Success! Total: $($response.total), Replied: $($response.replied), Avg Rating: $($response.average_rating)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 10: Get Announcements
Write-Host "[10] Testing Get Announcements..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/announcements/" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) announcements" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 11: Get Announcements Stats
Write-Host "[11] Testing Get Announcements Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/announcements/stats/" -Headers $headers
    Write-Host "✓ Success! Total: $($response.total)" -ForegroundColor Green
    Write-Host "  High: $($response.by_priority.high), Medium: $($response.by_priority.medium), Low: $($response.by_priority.low)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 12: Get Security Schedules
Write-Host "[12] Testing Get Security Schedules..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/security-schedules/" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) schedules" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 13: Get Security Schedules Stats
Write-Host "[13] Testing Get Security Schedules Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/security-schedules/stats/" -Headers $headers
    Write-Host "✓ Success! Total: $($response.total), Active: $($response.active)" -ForegroundColor Green
    Write-Host "  Pagi: $($response.by_shift.Pagi), Siang: $($response.by_shift.Siang), Malam: $($response.by_shift.Malam)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 14: Filter Residents by Status
Write-Host "[14] Testing Filter Residents (status=aktif)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/residents/?status=aktif" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) active residents" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 15: Filter Announcements by Priority
Write-Host "[15] Testing Filter Announcements (priority=high)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/announcements/?priority=high" -Headers $headers
    Write-Host "✓ Success! Found $($response.count) high priority announcements" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== TESTING COMPLETED ===" -ForegroundColor Cyan
