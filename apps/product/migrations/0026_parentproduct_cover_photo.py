# Generated by Django 2.0.3 on 2018-05-21 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_auto_20180512_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentproduct',
            name='cover_photo',
            field=models.CharField(default='', max_length=128, verbose_name='Cover Photo'),
        ),
    ]
