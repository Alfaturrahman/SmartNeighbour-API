# Comprehensive API Testing Script
# SmartNeighbour Backend API Tests

$baseUrl = "http://127.0.0.1:8000/api"
$results = @()

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  SMARTNEIGHBOUR API TESTING   " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Function to test endpoint
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [hashtable]$Headers = $null
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    Write-Host "  URL: $Url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
        }
        
        if ($Headers) { $params.Headers = $Headers }
        if ($Body) { 
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        Write-Host "  ✓ Status: $($response.StatusCode)" -ForegroundColor Green
        
        return @{
            Name = $Name
            Status = "PASS"
            StatusCode = $response.StatusCode
            Response = $response.Content
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "  ✗ Status: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
        
        return @{
            Name = $Name
            Status = "FAIL"
            StatusCode = $statusCode
            Error = $_.Exception.Message
        }
    }
}

# ========================================
# 1. AUTHENTICATION TESTS
# ========================================
Write-Host "`n[1] AUTHENTICATION ENDPOINTS" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Magenta

# Test Login (will fail if no user exists, but we can check endpoint works)
$results += Test-Endpoint -Name "Login Endpoint" -Url "$baseUrl/auth/login/" -Method POST -Body @{
    email = "test@example.com"
    password = "test123"
}

# Test Verify Token (without token - should fail properly)
$results += Test-Endpoint -Name "Verify Token (No Auth)" -Url "$baseUrl/auth/verify/" -Method GET

# Test Current User (without token - should fail properly)
$results += Test-Endpoint -Name "Current User (No Auth)" -Url "$baseUrl/auth/me/" -Method GET

# Test Refresh Token
$results += Test-Endpoint -Name "Refresh Token (Invalid)" -Url "$baseUrl/auth/refresh/" -Method POST -Body @{
    refresh = "invalid_token"
}

# ========================================
# 2. USERS ENDPOINTS
# ========================================
Write-Host "`n[2] USERS ENDPOINTS" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Magenta

$results += Test-Endpoint -Name "List Users (No Auth)" -Url "$baseUrl/users/" -Method GET
$results += Test-Endpoint -Name "User Stats (No Auth)" -Url "$baseUrl/users/stats/" -Method GET

# ========================================
# 3. RESIDENTS ENDPOINTS
# ========================================
Write-Host "`n[3] RESIDENTS ENDPOINTS" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Magenta

$results += Test-Endpoint -Name "List Residents (No Auth)" -Url "$baseUrl/residents/" -Method GET
$results += Test-Endpoint -Name "Residents Stats (No Auth)" -Url "$baseUrl/residents/stats/" -Method GET
$results += Test-Endpoint -Name "Filter Residents (status=aktif)" -Url "$baseUrl/residents/?status=aktif" -Method GET

# ========================================
# 4. FEEDBACKS ENDPOINTS
# ========================================
Write-Host "`n[4] FEEDBACKS ENDPOINTS" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Magenta

$results += Test-Endpoint -Name "List Feedbacks (No Auth)" -Url "$baseUrl/feedbacks/" -Method GET
$results += Test-Endpoint -Name "Feedbacks Stats (No Auth)" -Url "$baseUrl/feedbacks/stats/" -Method GET

# ========================================
# 5. ANNOUNCEMENTS ENDPOINTS
# ========================================
Write-Host "`n[5] ANNOUNCEMENTS ENDPOINTS" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Magenta

$results += Test-Endpoint -Name "List Announcements (No Auth)" -Url "$baseUrl/announcements/" -Method GET
$results += Test-Endpoint -Name "Announcements Stats (No Auth)" -Url "$baseUrl/announcements/stats/" -Method GET
$results += Test-Endpoint -Name "Filter Announcements (priority=high)" -Url "$baseUrl/announcements/?priority=high" -Method GET

# ========================================
# 6. SECURITY SCHEDULES ENDPOINTS
# ========================================
Write-Host "`n[6] SECURITY SCHEDULES ENDPOINTS" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Magenta

$results += Test-Endpoint -Name "List Security Schedules (No Auth)" -Url "$baseUrl/security-schedules/" -Method GET
$results += Test-Endpoint -Name "Security Stats (No Auth)" -Url "$baseUrl/security-schedules/stats/" -Method GET
$results += Test-Endpoint -Name "Filter Schedules (shift=Pagi)" -Url "$baseUrl/security-schedules/?shift=Pagi" -Method GET

# ========================================
# SUMMARY
# ========================================
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "       TEST SUMMARY             " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$passed = ($results | Where-Object { $_.StatusCode -in @(200, 201) }).Count
$unauthorized = ($results | Where-Object { $_.StatusCode -in @(401, 403) }).Count
$failed = ($results | Where-Object { $_.StatusCode -notin @(200, 201, 401, 403) }).Count
$total = $results.Count

Write-Host "`nTotal Tests: $total" -ForegroundColor White
Write-Host "✓ Success (200-201): $passed" -ForegroundColor Green
Write-Host "⚠ Unauthorized (401/403): $unauthorized" -ForegroundColor Yellow
Write-Host "✗ Failed (Other): $failed" -ForegroundColor Red

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "      DETAILED RESULTS          " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

foreach ($result in $results) {
    $status = switch ($result.StatusCode) {
        { $_ -in @(200, 201) } { "✓ PASS" ; $color = "Green" }
        { $_ -in @(401, 403) } { "⚠ AUTH" ; $color = "Yellow" }
        default { "✗ FAIL" ; $color = "Red" }
    }
    
    Write-Host "`n$($result.Name)" -ForegroundColor White
    Write-Host "  Status: $status ($($result.StatusCode))" -ForegroundColor $color
    
    if ($result.Error) {
        Write-Host "  Error: $($result.Error)" -ForegroundColor Red
    }
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host ""
