from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = 'Hash passwords for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        
        for user in users:
            # Jika password belum di-hash (tidak dimulai dengan pbkdf2_sha256)
            if not user.password.startswith('pbkdf2_sha256'):
                self.stdout.write(f'Hashing password for {user.email}...')
                # Set password dengan method yang akan hash otomatis
                user.set_password('admin123')  # Default password
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Password hashed for {user.email}'))
            else:
                self.stdout.write(f'Password already hashed for {user.email}')
        
        self.stdout.write(self.style.SUCCESS('\nAll passwords processed!'))
        self.stdout.write('Default password for all users: admin123')
