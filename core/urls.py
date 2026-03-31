from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import plain_views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'rw', views.RWViewSet)
router.register(r'rt', views.RTViewSet)
router.register(r'residents', views.ResidentViewSet)
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'announcements', views.AnnouncementViewSet)
router.register(r'security-schedules', views.SecurityScheduleViewSet)

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', views.refresh_token_view, name='refresh-token'),
    path('auth/me/', views.current_user, name='current-user'),
    path('auth/verify/', views.verify_token, name='verify-token'),
    path('auth/test/', plain_views.verify_token_plain, name='test-plain'),
    path('', include(router.urls)),
]