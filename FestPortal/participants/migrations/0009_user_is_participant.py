# Generated by Django 5.2 on 2025-04-12 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0008_alter_user_is_active_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_participant',
            field=models.BooleanField(default=True),
        ),
    ]
