import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User

users = User.objects.all()
print(f'Total akun pengguna: {users.count()}\n')
print('=' * 50)

for user in users:
    print(f'Email: {user.email}')
    print(f'Nama: {user.name}')
    print(f'Role: {user.role}')
    print(f'Status: {"Aktif" if user.is_active else "Tidak Aktif"}')
    print(f'Dibuat: {user.created_at}')
    print('-' * 50)
