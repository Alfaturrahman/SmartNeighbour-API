from rest_framework import serializers
from .models import User, RW, RT, Resident, Feedback, Announcement, SecuritySchedule
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name', 'role', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class RWSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = RW
        fields = ['id', 'name', 'user', 'user_email', 'area', 'phone', 'address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RTSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    rw_name = serializers.CharField(source='rw.name', read_only=True)
    
    class Meta:
        model = RT
        fields = ['id', 'name', 'user', 'user_email', 'rw', 'rw_name', 'area', 'phone', 'address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ResidentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, required=False)
    rt_name = serializers.CharField(source='rt.name', read_only=True)
    
    class Meta:
        model = Resident
        fields = ['id', 'name', 'address', 'phone', 'email', 'status', 'user', 'user_email', 'rt', 'rt_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, required=False)
    rt_name = serializers.CharField(source='rt.name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_email', 'rt', 'rt_name', 'author', 'title', 'content', 'rating', 'date', 'reply', 'replied_at', 'replied_by', 'created_at', 'updated_at']
        read_only_fields = ['date', 'replied_at', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating harus antara 1-5')
        return value


class FeedbackReplySerializer(serializers.Serializer):
    reply = serializers.CharField()
    replied_by = serializers.CharField()


class AnnouncementSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, required=False)
    rt_name = serializers.CharField(source='rt.name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'user', 'user_email', 'rt', 'rt_name', 'title', 'content', 'author', 'date', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['date', 'created_at', 'updated_at']


class SecurityScheduleSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, required=False)
    rw_name = serializers.CharField(source='rw.name', read_only=True)
    
    class Meta:
        model = SecuritySchedule
        fields = ['id', 'user', 'user_email', 'rw', 'rw_name', 'name', 'shift', 'date', 'time', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RTCreateSerializer(serializers.Serializer):
    """Serializer untuk RW membuat akun RT baru"""
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    area = serializers.CharField(max_length=255, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email sudah terdaftar')
        return value
    
    def create(self, validated_data):
        """Auto-create User dan RT profile"""
        import secrets
        import string
        
        # Generate random password (8 chars: mix of letters, numbers, symbols)
        alphabet = string.ascii_letters + string.digits + '!@#$%'
        generated_password = ''.join(secrets.choice(alphabet) for i in range(8))
        
        # Create User
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            role='rt',
            is_active=True
        )
        user.set_password(generated_password)
        user.save()
        
        # Get RW from request (injected by view)
        rw = self.context.get('rw')
        
        # Create RT profile
        rt = RT(
            name=validated_data['name'],
            user=user,
            rw=rw,
            phone=validated_data.get('phone', ''),
            area=validated_data.get('area', ''),
            address=validated_data.get('address', '')
        )
        rt.save()
        
        # Store password in context for response
        self.context['generated_password'] = generated_password
        
        return rt


class ResidentCreateSerializer(serializers.Serializer):
    """Serializer untuk RT membuat akun Warga baru"""
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=['aktif', 'tidak aktif'], default='aktif')
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email sudah terdaftar')
        return value
    
    def create(self, validated_data):
        """Auto-create User dan Resident profile"""
        import secrets
        import string
        
        # Generate random password
        alphabet = string.ascii_letters + string.digits + '!@#$%'
        generated_password = ''.join(secrets.choice(alphabet) for i in range(8))
        
        # Create User
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            role='warga',
            is_active=True
        )
        user.set_password(generated_password)
        user.save()
        
        # Get RT from request (injected by view)
        rt = self.context.get('rt')
        
        # Create Resident profile
        resident = Resident(
            name=validated_data['name'],
            user=user,
            rt=rt,
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            status=validated_data.get('status', 'aktif')
        )
        resident.save()
        
        # Store password in context for response
        self.context['generated_password'] = generated_password
        
        return resident
