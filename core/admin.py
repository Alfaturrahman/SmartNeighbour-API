from django.contrib import admin
from .models import User, Resident, Feedback, Announcement, SecuritySchedule


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('email', 'name', 'role', 'is_active')
        }),
        ('Password', {
            'fields': ('password',),
            'description': 'Password akan di-hash otomatis saat disimpan'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            # Only hash password if it's a new user or password was changed
            if not obj.password.startswith('pbkdf2_'):
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Warga', {
            'fields': ('name', 'email', 'phone', 'address', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'rating', 'date', 'has_reply', 'created_at']
    list_filter = ['rating', 'date', 'created_at']
    search_fields = ['title', 'author', 'content']
    readonly_fields = ['date', 'created_at', 'updated_at', 'replied_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Feedback', {
            'fields': ('user', 'author', 'title', 'content', 'rating', 'date')
        }),
        ('Balasan', {
            'fields': ('reply', 'replied_by', 'replied_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_reply(self, obj):
        return obj.reply is not None and obj.reply != ''
    has_reply.boolean = True
    has_reply.short_description = 'Sudah Dibalas'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'priority', 'date', 'created_at']
    list_filter = ['priority', 'date', 'created_at']
    search_fields = ['title', 'author', 'content']
    readonly_fields = ['date', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Pengumuman', {
            'fields': ('user', 'title', 'content', 'author', 'priority', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SecuritySchedule)
class SecurityScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'shift', 'date', 'time', 'status', 'created_at']
    list_filter = ['shift', 'status', 'date', 'created_at']
    search_fields = ['name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['date', 'shift']
    
    fieldsets = (
        ('Informasi Jadwal', {
            'fields': ('user', 'name', 'shift', 'date', 'time', 'status')
        }),
        ('Catatan', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
