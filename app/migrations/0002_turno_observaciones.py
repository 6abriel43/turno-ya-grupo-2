# Generated for historial clinico.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="turno",
            name="observaciones",
            field=models.TextField(blank=True),
        ),
    ]
