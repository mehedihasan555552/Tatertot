# Generated by Django 5.0.1 on 2025-03-22 19:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background_image_url', models.URLField(blank=True, max_length=500)),
                ('splash_video_url', models.URLField(blank=True, max_length=500)),
                ('last_roku_publish', models.DateTimeField(blank=True, null=True)),
                ('last_firetv_publish', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'App Settings',
            },
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('m3u8_url', models.URLField(max_length=500)),
                ('thumbnail_url', models.URLField(max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='base.show')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
