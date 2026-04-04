# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_resident_additional_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
