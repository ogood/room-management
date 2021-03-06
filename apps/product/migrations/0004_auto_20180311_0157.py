# Generated by Django 2.0.3 on 2018-03-11 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_auto_20180310_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentproduct',
            name='status',
            field=models.CharField(choices=[('default', 'default'), ('private', 'private'), ('public', 'public'), ('deleted', 'deleted')], default='', max_length=64, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('private', 'private'), ('public', 'public'), ('rented', 'rented'), ('deleted', 'deleted')], default='', max_length=64, verbose_name='Status'),
        ),
    ]
