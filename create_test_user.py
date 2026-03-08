import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User

# Create admin user
try:
    user = User.objects.get(email='admin@test.com')
    print(f'User already exists: {user.email}')
except User.DoesNotExist:
    user = User(
        email='admin@test.com',
        name='Admin Test',
        role='admin',
        is_active=True
    )
    user.set_password('admin123')
    user.save()
    print(f'✓ Admin user created: {user.email}')
    print(f'  Password: admin123')
    print(f'  Role: {user.role}')

# Create security user
try:
    sec_user = User.objects.get(email='security@test.com')
    print(f'User already exists: {sec_user.email}')
except User.DoesNotExist:
    sec_user = User(
        email='security@test.com',
        name='Security Test',
        role='security',
        is_active=True
    )
    sec_user.set_password('security123')
    sec_user.save()
    print(f'✓ Security user created: {sec_user.email}')
    print(f'  Password: security123')
    print(f'  Role: {sec_user.role}')

# Create resident user
try:
    res_user = User.objects.get(email='resident@test.com')
    print(f'User already exists: {res_user.email}')
except User.DoesNotExist:
    res_user = User(
        email='resident@test.com',
        name='Resident Test',
        role='resident',
        is_active=True
    )
    res_user.set_password('resident123')
    res_user.save()
    print(f'✓ Resident user created: {res_user.email}')
    print(f'  Password: resident123')
    print(f'  Role: {res_user.role}')

print('\n✓ All test users created successfully!')
