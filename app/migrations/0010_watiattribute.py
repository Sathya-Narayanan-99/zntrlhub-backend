# Generated by Django 4.1 on 2023-08-20 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_segmentation'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatiAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_endpoint', models.URLField(max_length=2000)),
                ('api_key', models.CharField(max_length=1000)),
                ('connected', models.BooleanField(default=False)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Wati_attribute', to='app.account')),
            ],
        ),
    ]
