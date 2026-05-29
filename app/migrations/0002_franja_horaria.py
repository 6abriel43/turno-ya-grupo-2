# Generated for integrante 2.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FranjaHoraria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "dia",
                    models.CharField(
                        choices=[
                            ("LUN", "Lunes"),
                            ("MAR", "Martes"),
                            ("MIE", "Miercoles"),
                            ("JUE", "Jueves"),
                            ("VIE", "Viernes"),
                            ("SAB", "Sabado"),
                            ("DOM", "Domingo"),
                        ],
                        max_length=3,
                    ),
                ),
                ("hora_inicio", models.TimeField()),
                ("hora_fin", models.TimeField()),
                ("medicos", models.ManyToManyField(blank=True, related_name="franjas", to="app.medico")),
            ],
            options={
                "ordering": ["dia", "hora_inicio"],
                "verbose_name_plural": "franjas horarias",
            },
        ),
    ]
