# Generated by Django 2.0.3 on 2018-03-27 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_product_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.IntegerField(blank=True, default=1, verbose_name='quantity'),
        ),
    ]
