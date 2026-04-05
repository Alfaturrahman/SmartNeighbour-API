"""
Fix warga users without resident profiles - PRODUCTION VERSION
Direct connection to Railway PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:CmAfDwLtIMtOYscAjsvOPYWntlastOdP@maglev.proxy.rlwy.net:13709/railway"

def fix_production_warga():
    print("\n" + "=" * 70)
    print("FIXING WARGA RESIDENT PROFILES - PRODUCTION")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        print("✓ Connected to Railway PostgreSQL\n")
        
        # Get warga users without resident profile
        cur.execute("""
            SELECT u.id, u.email, u.name
            FROM users u
            LEFT JOIN residents r ON r.user_id = u.id
            WHERE u.role = 'warga' AND r.id IS NULL;
        """)
        warga_without_profile = cur.fetchall()
        
        if not warga_without_profile:
            print("✓ All warga users already have resident profiles!")
            return
        
        print(f"Found {len(warga_without_profile)} warga without resident profile:")
        for w in warga_without_profile:
            print(f"  - {w['name']} ({w['email']})")
        
        # Get first RT as default
        cur.execute("SELECT id, name FROM rt ORDER BY id LIMIT 1;")
        default_rt = cur.fetchone()
        
        if not default_rt:
            print("\n✗ ERROR: No RT found! Create RT first.")
            return
        
        print(f"\nDefault RT: {default_rt['name']} (ID: {default_rt['id']})")
        print("\nCreating resident profiles...")
        
        created = 0
        for warga in warga_without_profile:
            try:
                cur.execute("""
                    INSERT INTO residents 
                    (user_id, rt_id, name, email, phone, address, status, 
                     ktp, kk, jumlah_keluarga, kepala_keluarga, created_at, updated_at)
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s, %s, NOW(), NOW());
                """, (
                    warga['id'],
                    default_rt['id'],
                    warga['name'],
                    warga['email'],
                    '000000000000',  # Default phone
                    'Alamat belum diisi',  # Default address
                    'aktif',
                    1,  # jumlah_keluarga default
                    warga['name']  # kepala_keluarga
                ))
                
                print(f"  ✓ Created profile for {warga['name']}")
                created += 1
                
            except Exception as e:
                print(f"  ✗ Failed for {warga['name']}: {e}")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Resident profiles created: {created}/{len(warga_without_profile)}")
        print("\n✓ All warga can now access the system!")
        print("\nNext steps:")
        print("1. RT should update resident details (phone, address, KTP, KK)")
        print("2. Test warga login and verify they can see jadwal keamanan")
        print("=" * 70 + "\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_production_warga()
