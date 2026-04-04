from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db import models as db_models
from .models import User, RW, RT, Resident, Feedback, Announcement, SecuritySchedule, SecurityPersonnel
from .serializers import (
    UserSerializer, RWSerializer, RTSerializer, LoginSerializer, ResidentSerializer,
    FeedbackSerializer, FeedbackReplySerializer,
    AnnouncementSerializer, SecurityScheduleSerializer, SecurityPersonnelSerializer, RTCreateSerializer, ResidentCreateSerializer
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reset_password(self, request, pk=None):
        """Reset RT password - RW endpoint to generate new password for RT"""
        # Verify user is RW
        if request.user.role != 'rw':
            return Response(
                {'error': 'Hanya RW yang dapat reset password RT'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            rw = request.user.rw_profile
        except RW.DoesNotExist:
            return Response(
                {'error': 'RW profile tidak ditemukan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rt = RT.objects.get(id=pk, rw=rw)
        except RT.DoesNotExist:
            return Response(
                {'error': 'RT tidak ditemukan atau bukan milik RW ini'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate new password
        new_password = 'passw0rd'
        
        # Set new password to user
        rt.user.set_password(new_password)
        rt.user.save()
        
        return Response({
            'success': True,
            'message': 'Password RT berhasil direset',
            'data': {
                'rt_id': rt.id,
                'rt_name': rt.name,
                'user_email': rt.user.email,
                'new_password': new_password,
                'note': 'Berikan password baru ini ke RT untuk login'
            }
        }, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reset_password(self, request, pk=None):
        """Reset Resident password - RT endpoint to generate new password for Resident"""
        # Verify user is RT
        if request.user.role != 'rt':
            return Response(
                {'error': 'Hanya RT yang dapat reset password Warga'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            rt = request.user.rt_profile
        except RT.DoesNotExist:
            return Response(
                {'error': 'RT profile tidak ditemukan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resident = Resident.objects.get(id=pk, rt=rt)
        except Resident.DoesNotExist:
            return Response(
                {'error': 'Warga tidak ditemukan atau bukan milik RT ini'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate new password
        new_password = 'passw0rd'
        
        # Set new password to user
        resident.user.set_password(new_password)
        resident.user.save()
        
        return Response({
            'success': True,
            'message': 'Password Warga berhasil direset',
            'data': {
                'resident_id': resident.id,
                'resident_name': resident.name,
                'user_email': resident.user.email,
                'new_password': new_password,
                'note': 'Berikan password baru ini ke Warga untuk login'
            }
        }, status=status.HTTP_200_OK)


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
    
    def perform_update(self, serializer):
        """Override update to check if user can edit this resident"""
        user = self.request.user
        resident = serializer.instance
        
        # RT can only update residents in their own RT
        if user.role == 'rt':
            try:
                rt = user.rt_profile
                if resident.rt != rt:
                    raise serializers.ValidationError("Anda hanya dapat mengedit warga di RT Anda sendiri.")
            except RT.DoesNotExist:
                raise serializers.ValidationError("User does not have an RT profile.")
        elif user.role == 'rw':
            # RW can update residents in their RTs
            try:
                rw = user.rw_profile
                if resident.rt.rw != rw:
                    raise serializers.ValidationError("Anda hanya dapat mengedit warga di RW Anda.")
            except Exception as e:
                raise serializers.ValidationError(f"Error: {str(e)}")
        
        serializer.save()
    
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
            # Warga sees all feedback from their RT (for transparency)
            try:
                resident = user.resident_profile
                queryset = queryset.filter(rt=resident.rt)
            except Resident.DoesNotExist:
                queryset = queryset.none()
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
    
    def perform_create(self, serializer):
        """Override create to auto-set user and rt"""
        user = self.request.user
        
        # Auto-set RT based on user role if not provided
        rt = serializer.validated_data.get('rt')
        if not rt:
            if user.role == 'rt':
                # RT creates feedback for their own RT
                try:
                    rt = user.rt_profile
                except RT.DoesNotExist:
                    pass
            elif user.role == 'warga':
                # For warga, find their RT from resident record
                try:
                    resident = Resident.objects.filter(email=user.email).first()
                    if resident:
                        rt = resident.rt
                except Exception:
                    pass
        
        # Save with user and rt
        if rt:
            serializer.save(user=user, rt=rt)
        else:
            serializer.save(user=user)
    
    def perform_update(self, serializer):
        """Override update to check if user is the creator"""
        user = self.request.user
        feedback = serializer.instance
        
        # Check if user is the creator of this feedback
        if feedback.user != user:
            raise serializers.ValidationError("Anda hanya dapat mengedit feedback yang Anda buat sendiri.")
        
        serializer.save()


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Override create to auto-set user, rt, and author from current user"""
        user = self.request.user
        rt = None
        
        if user.role == 'rt':
            # RT creates announcements for their own RT
            try:
                rt = user.rt_profile
            except RT.DoesNotExist:
                raise serializers.ValidationError("User does not have an RT profile. Cannot create announcement.")
        elif user.role == 'rw':
            # RW can create announcements for any of their RTs
            try:
                rw = user.rw_profile
                rt_id = self.request.data.get('rt_id')
                
                if not rt_id:
                    raise serializers.ValidationError("RW must specify which RT this announcement is for (rt_id is required).")
                
                # Verify RT belongs to this RW
                rt = RT.objects.get(id=rt_id, rw=rw)
            except RT.DoesNotExist:
                raise serializers.ValidationError("RT tidak ditemukan atau tidak termasuk dalam RW Anda.")
            except Exception as e:
                raise serializers.ValidationError(f"Error: {str(e)}")
        else:
            raise serializers.ValidationError("Only RW and RT staff can create announcements.")
        
        # Auto-set author from user's name
        serializer.save(user=user, rt=rt, author=user.name or user.email)
    
    def perform_update(self, serializer):
        """Override update to maintain user, rt, and author - only creator can edit"""
        user = self.request.user
        announcement = serializer.instance
        rt = announcement.rt  # Keep existing RT by default
        author = announcement.author  # Keep original author
        
        # Check if user is the creator of this announcement
        if announcement.user != user:
            raise serializers.ValidationError("Anda hanya dapat mengedit pengumuman yang Anda buat sendiri.")
        
        if user.role == 'rt':
            try:
                rt = user.rt_profile
            except RT.DoesNotExist:
                raise serializers.ValidationError("User does not have an RT profile.")
        elif user.role == 'rw':
            # RW can update announcements for their RTs
            try:
                rw = user.rw_profile
                # Verify current announcement belongs to their RT
                if announcement.rt.rw != rw:
                    raise serializers.ValidationError("Anda tidak memiliki akses untuk mengubah pengumuman ini.")
            except Exception as e:
                raise serializers.ValidationError(f"Error: {str(e)}")
        
        serializer.save(user=user, rt=rt, author=author)
    
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
    
    def perform_create(self, serializer):
        """Auto-set RW from current user and link personnel by name"""
        user = self.request.user
        rw = None
        
        if user.role == 'rw':
            try:
                rw = user.rw_profile
            except:
                raise serializers.ValidationError("User does not have an RW profile.")
        else:
            raise serializers.ValidationError("Only RW staff can create security schedules.")
        
        # Check if there are any active personnel
        active_personnel_count = SecurityPersonnel.objects.filter(rw=rw, status='aktif').count()
        if active_personnel_count == 0:
            raise serializers.ValidationError("Tidak ada petugas keamanan aktif. Tambahkan petugas di Master Data Keamanan terlebih dahulu.")
        
        # Link personnel by name if exists
        personnel = None
        personnel_name = serializer.validated_data.get('name')
        if personnel_name:
            try:
                personnel = SecurityPersonnel.objects.get(rw=rw, name=personnel_name, status='aktif')
            except SecurityPersonnel.DoesNotExist:
                raise serializers.ValidationError(f"Petugas '{personnel_name}' tidak ditemukan atau tidak aktif.")
        
        # Validate date ranges for weekly and monthly schedules
        schedule_type = serializer.validated_data.get('schedule_type', 'daily')
        if schedule_type in ['weekly', 'monthly']:
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            if not start_date or not end_date:
                raise serializers.ValidationError("Tanggal mulai dan tanggal berakhir harus diisi untuk jadwal mingguan dan bulanan.")
            
            if start_date > end_date:
                raise serializers.ValidationError("Tanggal mulai harus lebih kecil atau sama dengan tanggal berakhir.")
            
            # Removed weekday validation for weekly schedules - now it's just a date range
            if schedule_type == 'monthly':
                if serializer.validated_data.get('month_day') is None:
                    raise serializers.ValidationError("Tanggal bulan harus diisi untuk jadwal bulanan.")
        
        serializer.save(user=user, rw=rw, personnel=personnel)
    
    def perform_update(self, serializer):
        """Update schedule and re-link personnel by name"""
        rw = serializer.instance.rw
        
        # Link personnel by name if exists
        personnel = None
        personnel_name = serializer.validated_data.get('name', serializer.instance.name)
        if personnel_name:
            try:
                personnel = SecurityPersonnel.objects.get(rw=rw, name=personnel_name, status='aktif')
            except SecurityPersonnel.DoesNotExist:
                pass  # Name doesn't match any active personnel, that's OK
        
        # Validate date ranges for weekly and monthly schedules
        schedule_type = serializer.validated_data.get('schedule_type', serializer.instance.schedule_type)
        if schedule_type in ['weekly', 'monthly']:
            start_date = serializer.validated_data.get('start_date', serializer.instance.start_date)
            end_date = serializer.validated_data.get('end_date', serializer.instance.end_date)
            
            if not start_date or not end_date:
                raise serializers.ValidationError("Tanggal mulai dan tanggal berakhir harus diisi untuk jadwal mingguan dan bulanan.")
            
            if start_date > end_date:
                raise serializers.ValidationError("Tanggal mulai harus lebih kecil atau sama dengan tanggal berakhir.")
            
            # Removed weekday validation for weekly schedules - now it's just a date range
            if schedule_type == 'monthly':
                month_day = serializer.validated_data.get('month_day', serializer.instance.month_day)
                if month_day is None:
                    raise serializers.ValidationError("Tanggal bulan harus diisi untuk jadwal bulanan.")
        
        serializer.save(personnel=personnel)
    
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


class SecurityPersonnelViewSet(viewsets.ModelViewSet):
    queryset = SecurityPersonnel.objects.all()
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Auto-set RW from current user"""
        user = self.request.user
        rw = None
        
        if user.role == 'rw':
            try:
                rw = user.rw_profile
            except:
                raise serializers.ValidationError("User does not have an RW profile.")
        else:
            raise serializers.ValidationError("Only RW staff can create security personnel records.")
        
        serializer.save(rw=rw)
    
    def get_queryset(self):
        """Only allow RW to see their own security personnel"""
        user = self.request.user
        queryset = SecurityPersonnel.objects.all()
        
        if user.role == 'rw':
            try:
                rw = user.rw_profile
                queryset = queryset.filter(rw=rw)
            except:
                queryset = queryset.none()
        else:
            # RT and Warga can view security personnel but from their RW
            try:
                if user.role == 'rt':
                    rt = user.rt_profile
                    queryset = queryset.filter(rw=rt.rw)
                elif user.role == 'warga':
                    resident = user.resident_profile
                    queryset = queryset.filter(rw=resident.rt.rw)
                else:
                    queryset = queryset.none()
            except:
                queryset = queryset.none()
        
        # Filter by status if provided in query params
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset.order_by('name')
