# Generated by Django 4.0.2 on 2022-06-22 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_rename_monederosaleitem_saleitem_monedero'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleitem',
            name='monedero',
        ),
    ]
