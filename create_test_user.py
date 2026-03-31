import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, RW, RT, Resident

# Create RW user
try:
    rw_user = User.objects.get(email='rw@test.com')
    print(f'User already exists: {rw_user.email}')
except User.DoesNotExist:
    rw_user = User(
        email='rw@test.com',
        name='RW Test',
        role='rw',
        is_active=True
    )
    rw_user.set_password('rw123')
    rw_user.save()
    
    # Create RW profile
    rw_profile = RW(
        name='RW Test',
        user=rw_user,
        area='Area Test',
        phone='085123456789'
    )
    rw_profile.save()
    
    print(f'✓ RW user created: {rw_user.email}')
    print(f'  Password: rw123')
    print(f'  Role: {rw_user.role}')

# Create RT user
try:
    rt_user = User.objects.get(email='rt@test.com')
    print(f'User already exists: {rt_user.email}')
except User.DoesNotExist:
    # Get RW first
    rw = RW.objects.first()
    if rw:
        rt_user = User(
            email='rt@test.com',
            name='RT Test',
            role='rt',
            is_active=True
        )
        rt_user.set_password('rt123')
        rt_user.save()
        
        # Create RT profile
        rt_profile = RT(
            name='RT Test',
            user=rt_user,
            rw=rw,
            area='Area Test - RT',
            phone='085987654321'
        )
        rt_profile.save()
        
        print(f'✓ RT user created: {rt_user.email}')
        print(f'  Password: rt123')
        print(f'  Role: {rt_user.role}')
    else:
        print('⚠️  No RW found. Create RW first!')

# Create warga user
try:
    warga_user = User.objects.get(email='warga@test.com')
    print(f'User already exists: {warga_user.email}')
except User.DoesNotExist:
    warga_user = User(
        email='warga@test.com',
        name='Warga Test',
        role='warga',
        is_active=True
    )
    warga_user.set_password('warga123')
    warga_user.save()
    
    # Create resident profile (optional)
    rt = RT.objects.first()
    if rt:
        resident = Resident(
            name='Warga Test',
            email='warga@test.com',
            phone='082123456789',
            address='Jalan Test No. 1',
            user=warga_user,
            rt=rt,
            status='aktif'
        )
        resident.save()
    
    print(f'✓ Warga user created: {warga_user.email}')
    print(f'  Password: warga123')
    print(f'  Role: {warga_user.role}')

print('\n✓ All test users created successfully!')
