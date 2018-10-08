# Generated by Django 2.0.3 on 2018-03-10 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parentproduct',
            old_name='owner',
            new_name='owners',
        ),
        migrations.AlterField(
            model_name='parentproduct',
            name='status',
            field=models.CharField(choices=[('private', 'private'), ('public', 'public'), ('deleted', 'deleted')], default='', max_length=64, verbose_name='Status'),
        ),
    ]
