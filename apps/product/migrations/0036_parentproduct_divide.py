# Generated by Django 2.0.3 on 2018-06-27 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0035_auto_20180625_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentproduct',
            name='divide',
            field=models.BooleanField(default=True),
        ),
    ]
