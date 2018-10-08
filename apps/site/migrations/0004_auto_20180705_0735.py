# Generated by Django 2.0.3 on 2018-07-05 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site', '0003_auto_20180629_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='note',
            field=models.CharField(default='', max_length=256, verbose_name='note'),
        ),
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('submitted', 'submitted'), ('accepted', 'accepted'), ('rejected', 'rejected'), ('deleted', 'deleted'), ('initialed', 'initialed')], default='submitted', max_length=16, verbose_name='status'),
        ),
    ]
