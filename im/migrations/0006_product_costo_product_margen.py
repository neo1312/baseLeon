# Generated by Django 4.0.2 on 2022-02-11 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('im', '0005_alter_product_barcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='costo',
            field=models.CharField(default=0, max_length=100, verbose_name='costo'),
        ),
        migrations.AddField(
            model_name='product',
            name='margen',
            field=models.CharField(default=0, max_length=100, verbose_name='margen'),
        ),
    ]
