# COMPREHENSIVE API TESTING WITH AUTHENTICATION
# SmartNeighbour Backend - Full API Test Suite

$baseUrl = "http://127.0.0.1:8000/api"
$global:accessToken = $null
$global:refreshToken = $null

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SMARTNEIGHBOUR COMPREHENSIVE API TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Statistics
$script:totalTests = 0
$script:passedTests = 0
$script:failedTests = 0

function Test-API {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null,
        [bool]$RequireAuth = $false,
        [int[]]$ExpectedStatus = @(200, 201)
    )
    
    $script:totalTests++
    Write-Host "`n[$script:totalTests] $Name" -ForegroundColor Cyan
    Write-Host "    Method: $Method | URL: $Url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
            ErrorAction = 'Stop'
        }
        
        # Add authentication if required
        if ($RequireAuth -and $global:accessToken) {
            $params.Headers = @{
                "Authorization" = "Bearer $global:accessToken"
            }
            Write-Host "    Auth: Using Bearer Token" -ForegroundColor Gray
        }
        
        # Add body if provided
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -in $ExpectedStatus) {
            Write-Host "    ✓ PASS - Status: $($response.StatusCode)" -ForegroundColor Green
            $script:passedTests++
            
            # Try to parse and display response
            try {
                $json = $response.Content | ConvertFrom-Json
                if ($json.count -ne $null) {
                    Write-Host "    Response: $($json.count) items" -ForegroundColor Gray
                } elseif ($json.total -ne $null) {
                    Write-Host "    Response: Stats - Total: $($json.total)" -ForegroundColor Gray
                } elseif ($json.access) {
                    Write-Host "    Response: Token received" -ForegroundColor Gray
                } else {
                    Write-Host "    Response: Success" -ForegroundColor Gray
                }
            } catch {}
            
            return @{
                Success = $true
                StatusCode = $response.StatusCode
                Content = $response.Content
            }
        } else {
            Write-Host "    ✗ FAIL - Unexpected Status: $($response.StatusCode)" -ForegroundColor Red
            $script:failedTests++
            return @{ Success = $false; StatusCode = $response.StatusCode }
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        # Check if this is expected (like 401 for unauthenticated requests)
        if ($statusCode -in $ExpectedStatus) {
            Write-Host "    ✓ PASS - Expected Status: $statusCode" -ForegroundColor Green
            $script:passedTests++
            return @{ Success = $true; StatusCode = $statusCode }
        } else {
            Write-Host "    ✗ FAIL - Status: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
            $script:failedTests++
            return @{ Success = $false; StatusCode = $statusCode; Error = $_.Exception.Message }
        }
    }
}

# ==========================================
# PHASE 1: AUTHENTICATION TESTS (No Auth)
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host " PHASE 1: AUTHENTICATION & AUTHORIZATION  " -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

# Test 1: Login with valid credentials
Write-Host "`n--- Testing Login ---" -ForegroundColor Yellow
$loginResult = Test-API -Name "Login with Admin User" `
    -Url "$baseUrl/auth/login/" `
    -Method POST `
    -Body @{ email = "admin@test.com"; password = "admin123" } `
    -ExpectedStatus @(200)

if ($loginResult.Success) {
    $loginData = $loginResult.Content | ConvertFrom-Json
    $global:accessToken = $loginData.access
    $global:refreshToken = $loginData.refresh
    Write-Host "    ✓ Access Token: $($global:accessToken.Substring(0, 20))..." -ForegroundColor Green
    Write-Host "    ✓ User: $($loginData.user.email) | Role: $($loginData.user.role)" -ForegroundColor Green
}

# Test 2: Login with invalid credentials
Test-API -Name "Login with Invalid Password" `
    -Url "$baseUrl/auth/login/" `
    -Method POST `
    -Body @{ email = "admin@test.com"; password = "wrongpassword" } `
    -ExpectedStatus @(401)

# Test 3: Verify token
Test-API -Name "Verify Valid Token" `
    -Url "$baseUrl/auth/verify/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Test 4: Get current user
Test-API -Name "Get Current User" `
    -Url "$baseUrl/auth/me/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Test 5: Refresh token
if ($global:refreshToken) {
    $refreshResult = Test-API -Name "Refresh Access Token" `
        -Url "$baseUrl/auth/refresh/" `
        -Method POST `
        -Body @{ refresh = $global:refreshToken } `
        -ExpectedStatus @(200)
    
    if ($refreshResult.Success) {
        $refreshData = $refreshResult.Content | ConvertFrom-Json
        Write-Host "    ✓ New Access Token received" -ForegroundColor Green
    }
}

# Test 6: Test without authentication (should fail)
Test-API -Name "Access Protected Endpoint (No Auth)" `
    -Url "$baseUrl/users/" `
    -Method GET `
    -RequireAuth $false `
    -ExpectedStatus @(401)

# ==========================================
# PHASE 2: USERS CRUD OPERATIONS
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host " PHASE 2: USERS API                        " -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

# List users
Test-API -Name "List All Users" `
    -Url "$baseUrl/users/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Get user stats
Test-API -Name "Get User Statistics" `
    -Url "$baseUrl/users/stats/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Create new user
$newUserResult = Test-API -Name "Create New User" `
    -Url "$baseUrl/users/" `
    -Method POST `
    -Body @{
        email = "newuser@test.com"
        password = "password123"
        name = "New User Test"
        role = "resident"
        is_active = $true
    } `
    -RequireAuth $true `
    -ExpectedStatus @(201)

$newUserId = $null
if ($newUserResult.Success) {
    $newUserData = $newUserResult.Content | ConvertFrom-Json
    $newUserId = $newUserData.id
    Write-Host "    ✓ Created User ID: $newUserId" -ForegroundColor Green
}

# Get specific user
if ($newUserId) {
    Test-API -Name "Get User by ID ($newUserId)" `
        -Url "$baseUrl/users/$newUserId/" `
        -Method GET `
        -RequireAuth $true `
        -ExpectedStatus @(200)
    
    # Update user
    Test-API -Name "Update User (PATCH)" `
        -Url "$baseUrl/users/$newUserId/" `
        -Method PATCH `
        -Body @{ name = "Updated User Name" } `
        -RequireAuth $true `
        -ExpectedStatus @(200)
}

# ==========================================
# PHASE 3: RESIDENTS CRUD OPERATIONS
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host " PHASE 3: RESIDENTS API                    " -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

# List residents
Test-API -Name "List All Residents" `
    -Url "$baseUrl/residents/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Get resident stats
Test-API -Name "Get Resident Statistics" `
    -Url "$baseUrl/residents/stats/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Create new resident
$newResidentResult = Test-API -Name "Create New Resident" `
    -Url "$baseUrl/residents/" `
    -Method POST `
    -Body @{
        name = "John Doe"
        address = "Jl. Test No. 123"
        phone = "08123456789"
        email = "johndoe@test.com"
        status = "aktif"
    } `
    -RequireAuth $true `
    -ExpectedStatus @(201)

$residentId = $null
if ($newResidentResult.Success) {
    $residentData = $newResidentResult.Content | ConvertFrom-Json
    $residentId = $residentData.id
    Write-Host "    ✓ Created Resident ID: $residentId" -ForegroundColor Green
}

# Filter residents by status
Test-API -Name "Filter Residents (status=aktif)" `
    -Url "$baseUrl/residents/?status=aktif" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# ==========================================
# PHASE 4: FEEDBACKS CRUD OPERATIONS
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host " PHASE 4: FEEDBACKS API                    " -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

# List feedbacks
Test-API -Name "List All Feedbacks" `
    -Url "$baseUrl/feedbacks/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Get feedback stats
Test-API -Name "Get Feedback Statistics" `
    -Url "$baseUrl/feedbacks/stats/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Create new feedback
$newFeedbackResult = Test-API -Name "Create New Feedback" `
    -Url "$baseUrl/feedbacks/" `
    -Method POST `
    -Body @{
        author = "Test User"
        title = "Test Feedback"
        content = "This is a test feedback content"
        rating = 5
    } `
    -RequireAuth $true `
    -ExpectedStatus @(201)

$feedbackId = $null
if ($newFeedbackResult.Success) {
    $feedbackData = $newFeedbackResult.Content | ConvertFrom-Json
    $feedbackId = $feedbackData.id
    Write-Host "    ✓ Created Feedback ID: $feedbackId" -ForegroundColor Green
    
    # Reply to feedback
    Test-API -Name "Reply to Feedback" `
        -Url "$baseUrl/feedbacks/$feedbackId/reply/" `
        -Method POST `
        -Body @{
            reply = "Thank you for your feedback!"
            replied_by = "Admin"
        } `
        -RequireAuth $true `
        -ExpectedStatus @(200)
}

# ==========================================
# PHASE 5: ANNOUNCEMENTS CRUD OPERATIONS
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host " PHASE 5: ANNOUNCEMENTS API                " -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

# List announcements
Test-API -Name "List All Announcements" `
    -Url "$baseUrl/announcements/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Get announcement stats
Test-API -Name "Get Announcement Statistics" `
    -Url "$baseUrl/announcements/stats/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Create new announcement
$newAnnouncementResult = Test-API -Name "Create New Announcement" `
    -Url "$baseUrl/announcements/" `
    -Method POST `
    -Body @{
        title = "Test Announcement"
        content = "This is a test announcement"
        author = "Admin"
        priority = "high"
    } `
    -RequireAuth $true `
    -ExpectedStatus @(201)

$announcementId = $null
if ($newAnnouncementResult.Success) {
    $announcementData = $newAnnouncementResult.Content | ConvertFrom-Json
    $announcementId = $announcementData.id
    Write-Host "    ✓ Created Announcement ID: $announcementId" -ForegroundColor Green
}

# Filter announcements by priority
Test-API -Name "Filter Announcements (priority=high)" `
    -Url "$baseUrl/announcements/?priority=high" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# ==========================================
# PHASE 6: SECURITY SCHEDULES CRUD
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host " PHASE 6: SECURITY SCHEDULES API           " -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

# List security schedules
Test-API -Name "List All Security Schedules" `
    -Url "$baseUrl/security-schedules/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Get security stats
Test-API -Name "Get Security Schedule Statistics" `
    -Url "$baseUrl/security-schedules/stats/" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Create new security schedule
$newScheduleResult = Test-API -Name "Create New Security Schedule" `
    -Url "$baseUrl/security-schedules/" `
    -Method POST `
    -Body @{
        name = "Security Guard A"
        shift = "Pagi"
        date = "2026-02-15"
        time = "07:00 - 15:00"
        status = "aktif"
        notes = "Test schedule"
    } `
    -RequireAuth $true `
    -ExpectedStatus @(201)

$scheduleId = $null
if ($newScheduleResult.Success) {
    $scheduleData = $newScheduleResult.Content | ConvertFrom-Json
    $scheduleId = $scheduleData.id
    Write-Host "    ✓ Created Schedule ID: $scheduleId" -ForegroundColor Green
}

# Filter schedules by shift
Test-API -Name "Filter Schedules (shift=Pagi)" `
    -Url "$baseUrl/security-schedules/?shift=Pagi" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# Filter schedules by date
Test-API -Name "Filter Schedules (date=2026-02-15)" `
    -Url "$baseUrl/security-schedules/?date=2026-02-15" `
    -Method GET `
    -RequireAuth $true `
    -ExpectedStatus @(200)

# ==========================================
# FINAL SUMMARY
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "           FINAL TEST SUMMARY               " -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests:  $script:totalTests" -ForegroundColor White
Write-Host "✓ Passed:     $script:passedTests" -ForegroundColor Green
Write-Host "✗ Failed:     $script:failedTests" -ForegroundColor Red
Write-Host ""

$successRate = [math]::Round(($script:passedTests / $script:totalTests) * 100, 2)
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 90){'Green'}elseif($successRate -ge 70){'Yellow'}else{'Red'})

Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host ""

if ($script:failedTests -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! API is working perfectly!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Please review the results above." -ForegroundColor Yellow
}

Write-Host ""
