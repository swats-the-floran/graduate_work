# Generated by Django 4.0 on 2022-09-05 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0005_createa_assignment_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['-created_at'], 'verbose_name': 'Поручение', 'verbose_name_plural': 'Поручения'},
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='transport',
            field=models.CharField(blank=True, choices=[('email', 'email'), ('sms', 'sms')], default='email', max_length=20, verbose_name='transport'),
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='notification_type',
            field=models.CharField(blank=True, choices=[('like', 'like'), ('mass_mail', 'mass_mail'), ('welcome', 'welcome'), ('new_movie', 'new_movie'), ('assignment', 'assignment'), ('delayed', 'delayed'), ('birthday', 'birthday')], default='', max_length=20, verbose_name='notification_type'),
        ),
    ]