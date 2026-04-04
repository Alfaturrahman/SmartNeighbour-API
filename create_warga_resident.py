import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, Resident, RT

# Get warga user
warga = User.objects.get(email='warga@test.com')
print(f'Found user: {warga.name} ({warga.email})')

# Get the first RT (RT Test under RW Test)
rt = RT.objects.first()
print(f'Found RT: {rt.name} under {rt.rw.name}')

# Check if resident already exists
existing = Resident.objects.filter(user=warga).first()
if existing:
    print(f'Resident profile already exists: {existing}')
else:
    # Create resident profile
    resident = Resident.objects.create(
        user=warga,
        rt=rt,
        name=warga.name,
        email=warga.email,
        phone='081234567890',
        address='Jl. Test No. 123',
        status='aktif',
        ktp='1234567890123456',
        kk='1234567890123456',
        jumlah_keluarga=4,
        kepala_keluarga='Test Warga'
    )
    print(f'Created resident profile: {resident}')
    print(f'Linked to RT: {resident.rt}')
    print(f'Under RW: {resident.rt.rw}')
