from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def verify_token_plain(request):
    """Plain Django view tanpa DRF - untuk debug"""
    if request.method not in ['GET', 'POST']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header.startswith('Bearer '):
        return JsonResponse({
            'error': 'No Bearer token',
            'headers': dict(request.META),
            'step': '1'
        }, status=401)
    
    token_string = auth_header.split(' ')[1]
    
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from .models import User
        from .serializers import UserSerializer
        
        token = AccessToken(token_string)
        user_id = token.get('user_id')
        
        user = User.objects.get(id=user_id)
        
        return JsonResponse({
            'success': True,
            'user': UserSerializer(user).data,
            'debug': f'User ID: {user_id}, Email: {user.email}'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'error': f'User {user_id} not found in database',
            'step': '3'
        }, status=404)
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'step': '2'
        }, status=401)
