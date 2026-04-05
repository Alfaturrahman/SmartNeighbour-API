"""
Check Railway Production Database
Direct connection to verify data after deployment
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:CmAfDwLtIMtOYscAjsvOPYWntlastOdP@maglev.proxy.rlwy.net:13709/railway"

def check_production():
    print("\n" + "=" * 70)
    print("RAILWAY PRODUCTION DATABASE CHECK")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        print("✓ Connected to Railway PostgreSQL\n")
        
        # 1. Check tables exist
        print("1. CHECKING TABLES")
        print("-" * 70)
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        print(f"Total tables: {len(tables)}")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        # 2. Check migrations
        print("\n2. APPLIED MIGRATIONS")
        print("-" * 70)
        cur.execute("""
            SELECT app, name, applied 
            FROM django_migrations 
            WHERE app = 'core'
            ORDER BY id DESC
            LIMIT 5;
        """)
        migrations = cur.fetchall()
        for mig in migrations:
            print(f"  ✓ {mig['name']} - {mig['applied']}")
        
        # Check if 0007 and 0008 applied
        cur.execute("""
            SELECT COUNT(*) as count FROM django_migrations 
            WHERE app = 'core' AND name IN (
                '0007_resident_additional_fields',
                '0008_feedback_rating_optional'
            );
        """)
        new_migrations = cur.fetchone()
        if new_migrations['count'] == 2:
            print("\n  ✓✓ NEW MIGRATIONS 0007 & 0008 APPLIED!")
        else:
            print(f"\n  ⚠ Only {new_migrations['count']}/2 new migrations applied")
        
        # 3. Check users
        print("\n3. USERS")
        print("-" * 70)
        cur.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role;")
        users = cur.fetchall()
        for user in users:
            print(f"  {user['role'].upper()}: {user['count']}")
        
        # 4. Check warga without resident profile
        print("\n4. WARGA RESIDENT PROFILES")
        print("-" * 70)
        cur.execute("""
            SELECT u.email, u.name, 
                   CASE WHEN r.id IS NOT NULL THEN 'YES' ELSE 'NO' END as has_profile
            FROM users u
            LEFT JOIN residents r ON r.user_id = u.id
            WHERE u.role = 'warga';
        """)
        warga_users = cur.fetchall()
        
        with_profile = sum(1 for w in warga_users if w['has_profile'] == 'YES')
        without_profile = sum(1 for w in warga_users if w['has_profile'] == 'NO')
        
        print(f"  Total warga: {len(warga_users)}")
        print(f"  With profile: {with_profile}")
        print(f"  Without profile: {without_profile}")
        
        if without_profile > 0:
            print(f"\n  ⚠ Users WITHOUT resident profile:")
            for w in warga_users:
                if w['has_profile'] == 'NO':
                    print(f"    - {w['name']} ({w['email']})")
            print(f"\n  👉 Run: railway run python fix_warga_residents.py")
        else:
            print(f"  ✓ All warga have resident profiles!")
        
        # 5. Check resident table columns (0007 migration)
        print("\n5. RESIDENT TABLE COLUMNS (Migration 0007)")
        print("-" * 70)
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'residents'
            AND column_name IN ('ktp', 'kk', 'jumlah_keluarga', 'kepala_keluarga')
            ORDER BY column_name;
        """)
        columns = cur.fetchall()
        
        expected_cols = ['ktp', 'kk', 'jumlah_keluarga', 'kepala_keluarga']
        found_cols = [col['column_name'] for col in columns]
        
        for col in expected_cols:
            if col in found_cols:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING!")
        
        # 6. Check feedback table (0008 migration)
        print("\n6. FEEDBACK TABLE (Migration 0008)")
        print("-" * 70)
        cur.execute("""
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'feedbacks'
            AND column_name = 'rating';
        """)
        rating_col = cur.fetchone()
        if rating_col and rating_col['is_nullable'] == 'YES':
            print(f"  ✓ rating column is nullable (optional)")
        else:
            print(f"  ⚠ rating column issue")
        
        # 7. Check RW and RT structure
        print("\n7. RW & RT STRUCTURE")
        print("-" * 70)
        cur.execute("""
            SELECT rw.name as rw_name, 
                   COUNT(rt.id) as rt_count,
                   COUNT(DISTINCT r.id) as resident_count
            FROM rw
            LEFT JOIN rt ON rt.rw_id = rw.id
            LEFT JOIN residents r ON r.rt_id = rt.id
            GROUP BY rw.id, rw.name;
        """)
        rw_structure = cur.fetchall()
        for rw in rw_structure:
            print(f"  {rw['rw_name']}")
            print(f"    - RTs: {rw['rt_count']}")
            print(f"    - Residents: {rw['resident_count']}")
        
        # 8. Check security schedules
        print("\n8. SECURITY SCHEDULES")
        print("-" * 70)
        cur.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'aktif' THEN 1 ELSE 0 END) as active,
                   SUM(CASE WHEN personnel_id IS NOT NULL THEN 1 ELSE 0 END) as with_personnel
            FROM security_schedules;
        """)
        schedules = cur.fetchone()
        print(f"  Total: {schedules['total']}")
        print(f"  Active: {schedules['active']}")
        print(f"  Linked to personnel: {schedules['with_personnel']}")
        
        # Check today's schedules
        today = date.today()
        cur.execute("""
            SELECT shift, name, start_date, end_date
            FROM security_schedules
            WHERE status = 'aktif'
            AND start_date <= %s
            AND end_date >= %s;
        """, (today, today))
        today_guards = cur.fetchall()
        
        print(f"\n  Schedules active today ({today}):")
        if today_guards:
            for guard in today_guards:
                print(f"    - {guard['shift']}: {guard['name']}")
        else:
            print(f"    ⚠ No guards scheduled for today")
        
        # 9. Check feedback
        print("\n9. FEEDBACK")
        print("-" * 70)
        cur.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN reply IS NOT NULL THEN 1 ELSE 0 END) as with_reply,
                   SUM(CASE WHEN rating IS NULL THEN 1 ELSE 0 END) as no_rating
            FROM feedbacks;
        """)
        feedback = cur.fetchone()
        print(f"  Total: {feedback['total']}")
        print(f"  With reply: {feedback['with_reply']}")
        print(f"  Without rating: {feedback['no_rating']}")
        
        # 10. Final summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        issues = []
        
        if new_migrations['count'] < 2:
            issues.append("New migrations not fully applied")
        
        if without_profile > 0:
            issues.append(f"{without_profile} warga without resident profile")
        
        if len(found_cols) < 4:
            issues.append("Resident table missing columns")
        
        if not today_guards:
            issues.append("No security guards scheduled for today")
        
        if issues:
            print("⚠ ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✓✓ ALL CHECKS PASSED!")
            print("\nProduction database is ready to use!")
        
        print("=" * 70 + "\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_production()
