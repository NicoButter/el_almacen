# Generated by Django 5.1.2 on 2024-11-16 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas_corrientes", "0002_alter_cuentacorriente_cliente_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cuentacorriente",
            name="saldo",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
