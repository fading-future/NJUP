# Generated by Django 5.1.4 on 2024-12-11 17:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="administrator",
            name="user",
        ),
        migrations.RemoveField(
            model_name="student",
            name="user",
        ),
        migrations.RemoveField(
            model_name="teacher",
            name="user",
        ),
    ]
