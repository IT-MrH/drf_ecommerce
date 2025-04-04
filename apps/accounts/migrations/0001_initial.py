# Generated by Django 5.1.7 on 2025-03-27 06:37

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=25, null=True, verbose_name='First name')),
                ('last_name', models.CharField(max_length=25, null=True, verbose_name='Last name')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email address')),
                ('avatar', models.ImageField(default='avatars/default.jpg', null=True, upload_to='avatars/')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account_type', models.CharField(choices=[('SELLER', 'SELLER'), ('BUYER', 'BUYER')], default='BUYER', max_length=6)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
