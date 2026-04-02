import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User

# Reset passwords for test users
users_to_reset = [
    ('rw@test.com', 'rw123'),
    ('rt@test.com', 'rt123'),
    ('warga@test.com', 'warga123'),
]

for email, password in users_to_reset:
    try:
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        print(f'✓ Password reset: {email} -> {password}')
    except User.DoesNotExist:
        print(f'✗ User not found: {email}')

print('\n✓ All passwords reset successfully!')
