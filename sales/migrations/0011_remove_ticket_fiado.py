# Generated by Django 5.1.2 on 2024-11-16 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0010_pago_ticket"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ticket",
            name="fiado",
        ),
    ]
