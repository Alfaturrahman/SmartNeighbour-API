from django.contrib.auth.backends import BaseBackend
from core.models import User


class CustomUserBackend(BaseBackend):
    """
    Custom authentication backend for custom User model
    """
    # Backend authentication buat login dengan email & password (bukan username)
    
    def authenticate(self, request, email=None, password=None):
        # Verifikasi login user pakai email dan password
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        # Ambil user by ID, dipanggil sama Django untuk maintain session
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
