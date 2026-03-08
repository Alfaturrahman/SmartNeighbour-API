from rest_framework import serializers
from .models import User, Resident, Feedback, Announcement, SecuritySchedule
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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resident
        fields = ['id', 'name', 'address', 'phone', 'email', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_email', 'author', 'title', 'content', 'rating', 'date', 'reply', 'replied_at', 'replied_by', 'created_at', 'updated_at']
        read_only_fields = ['date', 'replied_at', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating harus antara 1-5')
        return value


class FeedbackReplySerializer(serializers.Serializer):
    reply = serializers.CharField()
    replied_by = serializers.CharField()


class AnnouncementSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'user', 'user_email', 'title', 'content', 'author', 'date', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['date', 'created_at', 'updated_at']


class SecurityScheduleSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SecuritySchedule
        fields = ['id', 'user', 'user_email', 'name', 'shift', 'date', 'time', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
