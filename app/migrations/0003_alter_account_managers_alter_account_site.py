# Generated by Django 4.2.3 on 2023-07-16 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_account_user_account'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='account',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='account',
            name='site',
            field=models.URLField(unique=True),
        ),
    ]
