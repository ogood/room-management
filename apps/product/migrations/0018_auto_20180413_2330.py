# Generated by Django 2.0.3 on 2018-04-13 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_auto_20180413_0000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='payment',
        ),
        migrations.AddField(
            model_name='product',
            name='upfront',
            field=models.IntegerField(blank=True, default=1, verbose_name='Pay Upfront'),
        ),
    ]
