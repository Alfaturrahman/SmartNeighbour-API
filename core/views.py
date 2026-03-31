from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db import models as db_models
from .models import User, RW, RT, Resident, Feedback, Announcement, SecuritySchedule
from .serializers import (
    UserSerializer, RWSerializer, RTSerializer, LoginSerializer, ResidentSerializer,
    FeedbackSerializer, FeedbackReplySerializer,
    AnnouncementSerializer, SecurityScheduleSerializer, RTCreateSerializer, ResidentCreateSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint - returns JWT tokens"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            
            # Verify password
            if not user.check_password(password):
                return Response({
                    'error': 'Password salah',
                    'detail': 'Email atau password tidak valid'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is active
            if not user.is_active:
                return Response({
                    'error': 'User tidak aktif',
                    'detail': 'Akun Anda telah dinonaktifkan. Hubungi administrator.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate JWT tokens with proper user context
            refresh = RefreshToken()
            refresh['user_id'] = user.id
            refresh['email'] = user.email
            refresh['role'] = user.role
            
            # Get access token from refresh token
            access = refresh.access_token
            access['user_id'] = user.id
            access['email'] = user.email
            access['role'] = user.role
            
            return Response({
                'access': str(access),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
                'message': 'Login berhasil'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User tidak ditemukan',
                'detail': 'Email tidak terdaftar dalam sistem'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    """Get current authenticated user from JWT token"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return Response({
            'error': 'Token tidak ditemukan',
            'detail': 'Authorization header harus format: Bearer <token>'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token_string = auth_header.split(' ')[1]
    except IndexError:
        return Response({
            'error': 'Format token salah',
            'detail': 'Authorization header harus format: Bearer <token>'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
        
        token = AccessToken(token_string)
        user_id = token.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'Token tidak valid',
                'detail': 'user_id tidak ditemukan dalam token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response({
                'error': 'User tidak ditemukan',
                'detail': f'User dengan ID {user_id} tidak ada atau tidak aktif'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except (TokenError, InvalidToken) as e:
        return Response({
            'error': 'Token tidak valid atau expired',
            'detail': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        import traceback
        return Response({
            'error': 'Internal server error',
            'detail': str(e),
            'traceback': traceback.format_exc() if request.GET.get('debug') else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """Verify JWT token validity and return user data"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return Response({
            'valid': False,
            'error': 'Token tidak ditemukan',
            'detail': 'Authorization header harus format: Bearer <token>'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token_string = auth_header.split(' ')[1]
    except IndexError:
        return Response({
            'valid': False,
            'error': 'Format token salah'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
        
        token = AccessToken(token_string)
        user_id = token.get('user_id')
        
        if not user_id:
            return Response({
                'valid': False,
                'error': 'user_id tidak ditemukan dalam token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return Response({
                'valid': True,
                'user': UserSerializer(user).data,
                'token_payload': {
                    'user_id': user_id,
                    'email': token.get('email'),
                    'role': token.get('role'),
                    'exp': token.get('exp')
                }
            })
        except User.DoesNotExist:
            return Response({
                'valid': False,
                'error': f'User ID {user_id} tidak ditemukan atau tidak aktif'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except (TokenError, InvalidToken) as e:
        return Response({
            'valid': False,
            'error': 'Token tidak valid atau expired',
            'detail': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        import traceback
        return Response({
            'valid': False,
            'error': str(e),
            'traceback': traceback.format_exc() if request.GET.get('debug') else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Refresh access token using refresh token"""
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token tidak ditemukan',
            'detail': 'Field "refresh" diperlukan dalam request body'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
        
        # Validate refresh token
        token = RefreshToken(refresh_token)
        user_id = token.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'Token tidak valid',
                'detail': 'user_id tidak ditemukan dalam token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verify user exists and is active
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({
                'error': 'User tidak ditemukan atau tidak aktif'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new access token
        access = token.access_token
        access['user_id'] = user.id
        access['email'] = user.email
        access['role'] = user.role
        
        return Response({
            'access': str(access),
            'message': 'Token berhasil di-refresh'
        }, status=status.HTTP_200_OK)
        
    except (TokenError, InvalidToken) as e:
        return Response({
            'error': 'Refresh token tidak valid atau expired',
            'detail': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc() if request.data.get('debug') else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = User.objects.count()
        active = User.objects.filter(is_active=True).count()
        by_role = {
            'rw': User.objects.filter(role='rw').count(),
            'rt': User.objects.filter(role='rt').count(),
            'warga': User.objects.filter(role='warga').count(),
        }
        return Response({
            'total': total,
            'active': active,
            'by_role': by_role
        })


class RWViewSet(viewsets.ModelViewSet):
    queryset = RW.objects.all()
    serializer_class = RWSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'rw':
            # RW can only see their own profile
            try:
                return RW.objects.filter(user=user)
            except RW.DoesNotExist:
                return RW.objects.none()
        elif user.role == 'rt':
            # RT can see their RW
            try:
                rt = user.rt_profile
                return RW.objects.filter(id=rt.rw.id)
            except (RT.DoesNotExist, AttributeError):
                return RW.objects.none()
        return RW.objects.none()
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_rt(self, request):
        """Endpoint untuk RW membuat akun RT baru"""
        # Verify user is RW
        if request.user.role != 'rw':
            return Response(
                {'error': 'Hanya RW yang dapat membuat akun RT'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            rw = request.user.rw_profile
        except RW.DoesNotExist:
            return Response(
                {'error': 'RW profile tidak ditemukan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RTCreateSerializer(
            data=request.data,
            context={'rw': rw, 'request': request}
        )
        
        if serializer.is_valid():
            rt = serializer.save()
            generated_password = serializer.context.get('generated_password')
            
            return Response({
                'success': True,
                'message': 'RT berhasil dibuat',
                'data': {
                    'rt_id': rt.id,
                    'rt_name': rt.name,
                    'user_email': rt.user.email,
                    'generated_password': generated_password,
                    'note': 'Berikan email dan password ini ke RT untuk login'
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RTViewSet(viewsets.ModelViewSet):
    queryset = RT.objects.all()
    serializer_class = RTSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'rw':
            # RW can see all RT under them
            try:
                rw = user.rw_profile
                return RT.objects.filter(rw=rw)
            except RW.DoesNotExist:
                return RT.objects.none()
        elif user.role == 'rt':
            # RT can only see their own profile
            try:
                rt = user.rt_profile
                return RT.objects.filter(id=rt.id)
            except RT.DoesNotExist:
                return RT.objects.none()
        return RT.objects.none()
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_resident(self, request):
        """Endpoint untuk RT membuat akun Warga baru"""
        # Verify user is RT
        if request.user.role != 'rt':
            return Response(
                {'error': 'Hanya RT yang dapat membuat akun Warga'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            rt = request.user.rt_profile
        except RT.DoesNotExist:
            return Response(
                {'error': 'RT profile tidak ditemukan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ResidentCreateSerializer(
            data=request.data,
            context={'rt': rt, 'request': request}
        )
        
        if serializer.is_valid():
            resident = serializer.save()
            generated_password = serializer.context.get('generated_password')
            
            return Response({
                'success': True,
                'message': 'Warga berhasil didaftarkan',
                'data': {
                    'resident_id': resident.id,
                    'resident_name': resident.name,
                    'user_email': resident.user.email,
                    'generated_password': generated_password,
                    'note': 'Berikan email dan password ini ke Warga untuk login'
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = Resident.objects.all()
    serializer_class = ResidentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Resident.objects.all()
        user = self.request.user
        
        # Data scoping based on user role
        if user.role == 'rw':
            # RW sees all residents under all their RTs
            try:
                rw = user.rw_profile
                rt_ids = RT.objects.filter(rw=rw).values_list('id', flat=True)
                queryset = queryset.filter(rt_id__in=rt_ids)
            except RT.DoesNotExist:
                queryset = queryset.none()
        elif user.role == 'rt':
            # RT only sees their own residents
            try:
                rt = user.rt_profile
                queryset = queryset.filter(rt=rt)
            except RT.DoesNotExist:
                queryset = queryset.none()
        elif user.role == 'warga':
            # Warga only sees themselves
            try:
                resident = user.resident_profile
                queryset = queryset.filter(id=resident.id)
            except Resident.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
        
        # Apply filters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Resident.objects.count()
        active = Resident.objects.filter(status='aktif').count()
        inactive = Resident.objects.filter(status='tidak aktif').count()
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive
        })


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Feedback.objects.all()
        
        # Data scoping based on user role
        if user.role == 'warga':
            # Warga only sees their own feedback
            queryset = queryset.filter(user=user)
        elif user.role == 'rt':
            # RT sees feedback from their residents
            try:
                rt = user.rt_profile
                queryset = queryset.filter(rt=rt)
            except RT.DoesNotExist:
                queryset = queryset.none()
        elif user.role == 'rw':
            # RW sees all feedback from their RTs
            try:
                rw = user.rw_profile
                rt_ids = RT.objects.filter(rw=rw).values_list('id', flat=True)
                queryset = queryset.filter(rt_id__in=rt_ids)
            except RT.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        feedback = self.get_object()
        serializer = FeedbackReplySerializer(data=request.data)
        
        if serializer.is_valid():
            feedback.reply = serializer.validated_data['reply']
            feedback.replied_by = serializer.validated_data['replied_by']
            feedback.replied_at = timezone.now()
            feedback.save()
            return Response(FeedbackSerializer(feedback).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Feedback.objects.count()
        replied = Feedback.objects.filter(reply__isnull=False).count()
        unreplied = Feedback.objects.filter(reply__isnull=True).count()
        avg_rating = Feedback.objects.aggregate(db_models.Avg('rating'))['rating__avg'] or 0
        return Response({
            'total': total,
            'replied': replied,
            'unreplied': unreplied,
            'average_rating': round(avg_rating, 2)
        })


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.all()
        
        # Data scoping based on user role
        if user.role == 'warga':
            # Warga sees announcements from their RT
            try:
                resident = user.resident_profile
                queryset = queryset.filter(rt=resident.rt)
            except Resident.DoesNotExist:
                queryset = queryset.none()
        elif user.role == 'rt':
            # RT sees announcements for their area
            try:
                rt = user.rt_profile
                # See their own announcements and RW announcements for their RW
                queryset = queryset.filter(rt=rt)
            except RT.DoesNotExist:
                queryset = queryset.none()
        elif user.role == 'rw':
            # RW sees all announcements from their RTs
            try:
                rw = user.rw_profile
                rt_ids = RT.objects.filter(rw=rw).values_list('id', flat=True)
                queryset = queryset.filter(rt_id__in=rt_ids)
            except RT.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
        
        # Apply priority filter
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Announcement.objects.count()
        by_priority = {
            'high': Announcement.objects.filter(priority='high').count(),
            'medium': Announcement.objects.filter(priority='medium').count(),
            'low': Announcement.objects.filter(priority='low').count(),
        }
        return Response({
            'total': total,
            'by_priority': by_priority
        })


class SecurityScheduleViewSet(viewsets.ModelViewSet):
    queryset = SecuritySchedule.objects.all()
    serializer_class = SecurityScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = SecuritySchedule.objects.all()
        
        # Data scoping based on user role
        if user.role == 'warga':
            # Warga sees schedules from their RT's RW
            try:
                resident = user.resident_profile
                rw = resident.rt.rw
                queryset = queryset.filter(rw=rw)
            except (Resident.DoesNotExist, AttributeError):
                queryset = queryset.none()
        elif user.role == 'rt':
            # RT sees schedules from their RW
            try:
                rt = user.rt_profile
                queryset = queryset.filter(rw=rt.rw)
            except RT.DoesNotExist:
                queryset = queryset.none()
        elif user.role == 'rw':
            # RW sees only their own schedules
            try:
                rw = user.rw_profile
                queryset = queryset.filter(rw=rw)
            except RT.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
        
        # Apply filters
        shift = self.request.query_params.get('shift', None)
        date = self.request.query_params.get('date', None)
        
        if shift:
            queryset = queryset.filter(shift=shift)
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset.order_by('date', 'shift')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = SecuritySchedule.objects.count()
        active = SecuritySchedule.objects.filter(status='aktif').count()
        by_shift = {
            'Pagi': SecuritySchedule.objects.filter(shift='Pagi').count(),
            'Siang': SecuritySchedule.objects.filter(shift='Siang').count(),
            'Malam': SecuritySchedule.objects.filter(shift='Malam').count(),
        }
        return Response({
            'total': total,
            'active': active,
            'by_shift': by_shift
        })
