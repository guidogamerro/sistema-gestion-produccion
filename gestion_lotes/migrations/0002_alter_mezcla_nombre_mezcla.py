# Generated by Django 4.0.1 on 2024-11-11 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_lotes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mezcla',
            name='nombre_mezcla',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
