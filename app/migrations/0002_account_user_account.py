# Generated by Django 4.2.3 on 2023-07-09 16:06

from django.db import migrations, models
import django.db.models.deletion
import django_multitenant.mixins
import django_multitenant.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('site', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
            managers=[
                ('objects', django_multitenant.models.TenantManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='app.account'),
        ),
    ]
