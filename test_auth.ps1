# Test JWT Authentication
# Usage: .\test_auth.ps1

$baseUrl = "http://localhost:8000/api"

Write-Host "`n=== SmartNeighbour API Authentication Test ===" -ForegroundColor Cyan

# Test 1: Login
Write-Host "`n[1] Testing Login..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@smartneighbour.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login/" -Method Post -Body $loginBody -ContentType "application/json"
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "User: $($loginResponse.user.name) ($($loginResponse.user.role))" -ForegroundColor Green
    
    $accessToken = $loginResponse.access
    $refreshToken = $loginResponse.refresh
    
    Write-Host "Access Token: $($accessToken.Substring(0, 50))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Get Current User
Write-Host "`n[2] Testing Get Current User (/api/auth/me/)..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $accessToken"
}

try {
    $meResponse = Invoke-RestMethod -Uri "$baseUrl/auth/me/" -Method Get -Headers $headers
    Write-Host "✓ Current user retrieved successfully!" -ForegroundColor Green
    Write-Host "User: $($meResponse.name) - $($meResponse.email)" -ForegroundColor Green
} catch {
    Write-Host "✗ Get current user failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 3: Verify Token
Write-Host "`n[3] Testing Verify Token..." -ForegroundColor Yellow
try {
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/auth/verify/" -Method Get -Headers $headers
    Write-Host "✓ Token verified successfully!" -ForegroundColor Green
    Write-Host "Valid: $($verifyResponse.valid)" -ForegroundColor Green
    Write-Host "Token Expiry: $($verifyResponse.token_payload.exp)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Token verification failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 4: Refresh Token
Write-Host "`n[4] Testing Refresh Token..." -ForegroundColor Yellow
$refreshBody = @{
    refresh = $refreshToken
} | ConvertTo-Json

try {
    $refreshResponse = Invoke-RestMethod -Uri "$baseUrl/auth/refresh/" -Method Post -Body $refreshBody -ContentType "application/json"
    Write-Host "✓ Token refreshed successfully!" -ForegroundColor Green
    
    $newAccessToken = $refreshResponse.access
    Write-Host "New Access Token: $($newAccessToken.Substring(0, 50))..." -ForegroundColor Gray
    
    # Test new token
    $newHeaders = @{
        "Authorization" = "Bearer $newAccessToken"
    }
    $testResponse = Invoke-RestMethod -Uri "$baseUrl/auth/me/" -Method Get -Headers $newHeaders
    Write-Host "✓ New token works!" -ForegroundColor Green
} catch {
    Write-Host "✗ Token refresh failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 5: Test Protected Endpoints
Write-Host "`n[5] Testing Protected Endpoints..." -ForegroundColor Yellow

# Users endpoint
try {
    $usersResponse = Invoke-RestMethod -Uri "$baseUrl/users/" -Method Get -Headers $headers
    Write-Host "✓ Users endpoint accessible!" -ForegroundColor Green
    Write-Host "Total users: $($usersResponse.count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Users endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Residents endpoint
try {
    $residentsResponse = Invoke-RestMethod -Uri "$baseUrl/residents/" -Method Get -Headers $headers
    Write-Host "✓ Residents endpoint accessible!" -ForegroundColor Green
    Write-Host "Total residents: $($residentsResponse.count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Residents endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor White
Write-Host "  - Login: ✓" -ForegroundColor Green
Write-Host "  - Get Current User: Check output above" -ForegroundColor Yellow
Write-Host "  - Verify Token: Check output above" -ForegroundColor Yellow
Write-Host "  - Refresh Token: Check output above" -ForegroundColor Yellow
Write-Host "  - Protected Endpoints: Check output above" -ForegroundColor Yellow
Write-Host ""
