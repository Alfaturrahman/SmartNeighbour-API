# Generated migration to fix foreign key constraint issues
# This migration makes FK fields nullable to allow existing data without valid references
# This is necessary because migration 0002 added FK constraints with default=1 
# but RT(1) may not exist in production databases

from django.db import migrations, models
import django.db.models.deletion


def set_orphan_feedbacks_to_null(apps, schema_editor):
    """Set feedbacks with invalid RT references to NULL"""
    Feedback = apps.get_model('core', 'Feedback')
    RT = apps.get_model('core', 'RT')
    
    # Get all RT IDs  
    valid_rt_ids = set(RT.objects.values_list('id', flat=True))
    
    # Set invalid references to NULL (will be fixed after RT data is properly set up)
    if valid_rt_ids:
        Feedback.objects.exclude(rt_id__in=valid_rt_ids).update(rt_id=None)
    else:
        # If no valid RTs, set all to NULL temporarily
        Feedback.objects.all().update(rt_id=None)


def set_orphan_schedules_to_null(apps, schema_editor):
    """Set security schedules with invalid RW references to NULL"""
    SecuritySchedule = apps.get_model('core', 'SecuritySchedule')
    RW = apps.get_model('core', 'RW')
    
    # Get all RW IDs
    valid_rw_ids = set(RW.objects.values_list('id', flat=True))
    
    # Set invalid references to NULL
    if valid_rw_ids:
        SecuritySchedule.objects.exclude(rw_id__in=valid_rw_ids).update(rw_id=None)
    else:
        # If no valid RWs, set all to NULL temporarily
        SecuritySchedule.objects.all().update(rw_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_securityschedule_end_date_and_more'),
    ]

    operations = [
        # Run cleanup functions first
        migrations.RunPython(set_orphan_feedbacks_to_null, migrations.RunPython.noop),
        migrations.RunPython(set_orphan_schedules_to_null, migrations.RunPython.noop),
        
        # Make Feedback.rt nullable to allow data without valid RT references
        migrations.AlterField(
            model_name='feedback',
            name='rt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='core.rt'),
        ),
        
        # Make SecuritySchedule.rw nullable to allow data without valid RW references
        migrations.AlterField(
            model_name='securityschedule',
            name='rw',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='security_schedules', to='core.rw'),
        ),
    ]
