# Generated by Django 4.2.13 on 2024-05-30 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default=2, max_length=30),
            preserve_default=False,
        ),
    ]
