# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_securityschedule_end_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resident',
            name='ktp',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Nomor KTP'),
        ),
        migrations.AddField(
            model_name='resident',
            name='kk',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Nomor Kartu Keluarga'),
        ),
        migrations.AddField(
            model_name='resident',
            name='jumlah_keluarga',
            field=models.IntegerField(blank=True, default=1, null=True, verbose_name='Jumlah Anggota Keluarga'),
        ),
        migrations.AddField(
            model_name='resident',
            name='kepala_keluarga',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Nama Kepala Keluarga'),
        ),
    ]
