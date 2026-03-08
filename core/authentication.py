from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from core.models import User


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for custom User model
    """
    
    def get_user(self, validated_token):
        """
        Get user from validated token
        """
        try:
            user_id = validated_token.get('user_id')
            user = User.objects.get(id=user_id, is_active=True)
            return user
        except User.DoesNotExist:
            raise InvalidToken('User not found')
