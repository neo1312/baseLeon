# Generated by Django 4.0.2 on 2022-02-10 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_alter_saleitem_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleitem',
            name='cost',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]