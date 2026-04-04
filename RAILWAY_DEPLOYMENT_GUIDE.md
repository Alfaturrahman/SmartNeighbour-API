# Railway Deployment Guide - RT & Warga Features Update

## 📋 What's New in This Update

### Backend Changes:
1. **Migration 0007**: Added resident fields (KTP, KK, jumlah_keluarga, kepala_keluarga)
2. **Migration 0008**: Made feedback rating optional
3. **Serializers**: Added personnel contact info to SecuritySchedule
4. **Views**: Updated warga permissions to view all RT feedback
5. **Bug Fixes**: Fixed warga data scoping for feedback and schedules

### Frontend Changes:
1. RT dashboard features completed
2. Warga can view all feedback from their RT
3. Security schedule view for all roles
4. Reply hierarchy system (RW > RT)
5. Improved UI/UX across all pages

---

## 🚀 Deployment Steps

### 1. Backup Production Data (IMPORTANT!)

```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Backup database
railway run python manage.py dumpdata > railway_backup_$(date +%Y%m%d).json
```

### 2. Push Backend to Railway

```powershell
cd C:\Users\Rahman\Desktop\smartneighbour_backend

# Check git status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Add RT dashboard: resident fields, feedback improvements, security schedule, warga permissions"

# Push to main branch (Railway auto-deploys)
git push origin main
```

**Railway will automatically:**
- Run migrations (from Procfile)
- Apply 0007_resident_additional_fields
- Apply 0008_feedback_rating_optional
- Restart the service

### 3. Verify Deployment

Wait 2-3 minutes for deployment to complete, then:

```bash
# Check deployment status
railway status

# Verify migrations
railway run python verify_railway_deployment.py
```

### 4. Fix Warga Resident Profiles

If verification shows warga users without resident profiles:

```bash
# Run the fix script
railway run python fix_warga_residents.py
```

This will:
- Create resident profiles for all warga users
- Link them to default RT
- Set default values for phone/address
- RT can update details later via UI

### 5. Test Critical Features

Login to your Railway backend URL and test:

- **RW Login**: Create RT, manage security, view all feedback
- **RT Login**: Manage residents, reply to feedback, view schedules
- **Warga Login**: 
  - Can view jadwal keamanan (should see today's guards)
  - Can view feedback from RT (including others' feedback)
  - Can create and delete own feedback

### 6. Push Frontend to Vercel/Railway

```powershell
cd C:\Users\Rahman\Downloads\Frontend\Frontend\smartneighbour

git add .
git commit -m "Complete RT and Warga dashboard features"
git push origin main
```

Vercel will auto-deploy. Wait for build to complete.

---

## 🔧 Troubleshooting

### Migration Errors

If migrations fail:

```bash
# Check migration status
railway run python manage.py showmigrations

# If stuck, try fake the migration (CAREFUL!)
railway run python manage.py migrate core 0007 --fake
railway run python manage.py migrate core 0008 --fake

# Then run sync
railway run python manage.py migrate
```

### Warga Can't See Schedules

```bash
# Check if user has resident profile
railway shell
>>> from core.models import User, Resident
>>> warga = User.objects.get(email='warga@example.com')
>>> warga.resident_profile  # Should NOT raise DoesNotExist
>>> exit()

# If error, run fix script
railway run python fix_warga_residents.py
```

### 500 Errors After Deploy

```bash
# Check logs
railway logs

# Common issues:
# 1. Missing environment variables
# 2. Warga without resident profile
# 3. CORS_ORIGINS not updated
```

### Database Column Missing

If you see `no such column` errors:

```bash
# Force run migrations
railway run python manage.py migrate --run-syncdb
```

---

## 📊 Post-Deployment Checklist

- [ ] Migrations 0007 and 0008 applied successfully
- [ ] All warga users have resident profiles
- [ ] Security schedules visible to all roles
- [ ] Feedback system working with reply hierarchy
- [ ] RT can manage residents with new fields
- [ ] Warga can see jadwal keamanan
- [ ] CORS configured for frontend domain
- [ ] No 500 errors in logs
- [ ] Test login for all 3 roles (RW, RT, Warga)

---

## 🛡️ Rollback Plan

If deployment fails critically:

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or rollback in Railway dashboard
# Project → Deployments → Select previous → Rollback
```

Restore database from backup:

```bash
railway run python manage.py loaddata railway_backup_YYYYMMDD.json
```

---

## 📞 Support Scripts

All scripts are in the backend folder:

- `fix_warga_residents.py` - Create missing resident profiles
- `verify_railway_deployment.py` - Check deployment health
- `list_users.py` - List all users in system
- `create_test_user.py` - Create test accounts

---

## 🎯 Expected Behavior After Deploy

### Warga Users:
- Can see all feedback from their RT (not just own)
- Can see security schedule from RW
- Can create/delete own feedback
- Cannot reply to feedback

### RT Users:
- Can manage residents with new fields (KTP, KK, family info)
- Can reply to feedback (green background)
- Can view security schedules
- Cannot override RW replies

### RW Users:
- Full access (unchanged)
- Can override RT replies (blue background)
- Can manage all data

---

**Deployment Date**: ____________
**Deployed By**: ____________
**Backend Version**: ____________
**Frontend Version**: ____________

