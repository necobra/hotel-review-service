# Generated by Django 5.0.7 on 2024-07-18 15:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_review_service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='hotel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='hotel_review_service.hotel'),
        ),
    ]
