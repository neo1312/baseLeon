from django.db import migrations


def repair_purchaseitem_sequence(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT setval(
                pg_get_serial_sequence('scm_purchaseitem', 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM scm_purchaseitem
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ('scm', '0009_alter_provider_options'),
    ]

    operations = [
        migrations.RunPython(repair_purchaseitem_sequence, migrations.RunPython.noop),
    ]
