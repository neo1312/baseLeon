# Generated by Django 4.0.2 on 2022-02-10 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_saleitem_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleitem',
            name='cost',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
