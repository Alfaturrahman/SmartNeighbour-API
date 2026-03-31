from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    ROLE_CHOICES = [
        ('rw', 'Rukun Warga'),
        ('rt', 'Rukun Tetangga'),
        ('warga', 'Warga/Resident'),
    ]
    
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    # Required for Django authentication system compatibility
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_authenticated(self):
        return True


class RW(models.Model):
    """Rukun Warga - Community Head"""
    name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rw_profile')
    area = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rw'
    
    def __str__(self):
        return f"RW: {self.name}"


class RT(models.Model):
    """Rukun Tetangga - Smaller unit head under RW"""
    name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rt_profile')
    rw = models.ForeignKey(RW, on_delete=models.CASCADE, related_name='rts')
    area = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rt'
    
    def __str__(self):
        return f"RT: {self.name} (under {self.rw.name})"


class Resident(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak aktif', 'Tidak Aktif'),
    ]
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resident_profile')
    rt = models.ForeignKey(RT, on_delete=models.CASCADE, related_name='residents', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'residents'
        
    def __str__(self):
        return self.name


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks', db_column='user_id')
    rt = models.ForeignKey(RT, on_delete=models.CASCADE, related_name='feedbacks')
    author = models.CharField(max_length=200)
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    reply = models.TextField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feedbacks'
        
    def __str__(self):
        return self.title


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements', db_column='user_id')
    rt = models.ForeignKey(RT, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        
    def __str__(self):
        return self.title


class SecuritySchedule(models.Model):
    SHIFT_CHOICES = [
        ('Pagi', 'Pagi'),
        ('Siang', 'Siang'),
        ('Malam', 'Malam'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak aktif', 'Tidak Aktif'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_schedules', db_column='user_id')
    rw = models.ForeignKey(RW, on_delete=models.CASCADE, related_name='security_schedules')
    name = models.CharField(max_length=200)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    date = models.DateField()
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_schedules'
        
    def __str__(self):
        return f'{self.name} - {self.shift} ({self.date})'
