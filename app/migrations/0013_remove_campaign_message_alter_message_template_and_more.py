# Generated by Django 4.1 on 2023-08-29 04:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_campaign_message_alter_watitemplate_managers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='message',
        ),
        migrations.AlterField(
            model_name='message',
            name='template',
            field=models.CharField(max_length=1024),
        ),
        migrations.CreateModel(
            name='VisitorSegmentationMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('segmentation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.segmentation')),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.visitor')),
            ],
            options={
                'unique_together': {('visitor', 'segmentation')},
            },
        ),
    ]