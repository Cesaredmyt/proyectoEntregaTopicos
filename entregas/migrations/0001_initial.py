from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UltimoFolio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("folio", models.CharField(max_length=50)),
                ("consultado_en", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
