from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField()),  # استخدم `appointment_date` بدلاً من `date`
                ('appointment_time', models.TimeField()),  # استخدم `appointment_time` بدلاً من `time`
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='المبلغ')),  # احتفظ بـ `amount` من التغييرات المحلية
                ('purpose', models.CharField(choices=[('consultation', 'استشارة'), ('surgery', 'جراحة'), ('checkup', 'فحص دوري'), ('emergency', 'طوارئ')], max_length=20, verbose_name='الغرض')),  # احتفظ بـ `purpose` من التغييرات المحلية
                ('type', models.CharField(choices=[('new', 'جديد'), ('followup', 'متابع')], max_length=20, verbose_name='نوع الحجز')),  # احتفظ بـ `type` من التغييرات المحلية
                ('is_online', models.BooleanField(default=False)),  # استخدم `is_online` من التغييرات البُعدية
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),  # استخدم `status` من التغييرات البُعدية
                ('created_at', models.DateTimeField(auto_now_add=True)),  # استخدم `created_at` من التغييرات البُعدية
                ('updated_at', models.DateTimeField(auto_now=True)),  # استخدم `updated_at` من التغييرات البُعدية
                ('notes', models.TextField(blank=True, null=True)),  # استخدم `notes` من التغييرات البُعدية
            ],
            options={
                'verbose_name': 'Booking',
                'verbose_name_plural': 'Bookings',
                'ordering': ['-appointment_date', '-appointment_time'],
            },
        ),
    ]
