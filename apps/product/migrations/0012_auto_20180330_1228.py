# Generated by Django 2.0.3 on 2018-03-30 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_auto_20180328_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupbill',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='original_bills', to='product.ParentProduct', verbose_name='Product'),
        ),
    ]