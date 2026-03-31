# Generated migration for role and hierarchy changes

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Add RW model
        migrations.CreateModel(
            name='RW',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('area', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rw_profile', to='core.user')),
            ],
            options={
                'db_table': 'rw',
            },
        ),
        
        # Add RT model
        migrations.CreateModel(
            name='RT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('area', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rw', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rts', to='core.rw')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rt_profile', to='core.user')),
            ],
            options={
                'db_table': 'rt',
            },
        ),
        
        # Update User model - change role choices
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('rw', 'Rukun Warga'), ('rt', 'Rukun Tetangga'), ('warga', 'Warga/Resident')], max_length=20),
        ),
        
        # Update Resident model - add user and rt fields
        migrations.AddField(
            model_name='resident',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resident_profile', to='core.user'),
        ),
        migrations.AddField(
            model_name='resident',
            name='rt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residents', to='core.rt'),
        ),
        
        # Update Feedback model - add rt field and update user field
        migrations.AddField(
            model_name='feedback',
            name='rt',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='core.rt'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedbacks', to='core.user'),
        ),
        
        # Update Announcement model - add rt field and update user field
        migrations.AddField(
            model_name='announcement',
            name='rt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='core.rt'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='announcements', to='core.user'),
        ),
        
        # Update SecuritySchedule model - change rw field
        migrations.RemoveField(
            model_name='securityschedule',
            name='user',
        ),
        migrations.AddField(
            model_name='securityschedule',
            name='rw',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='security_schedules', to='core.rw'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='securityschedule',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='security_schedules', to='core.user'),
        ),
    ]
