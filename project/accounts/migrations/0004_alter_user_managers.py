# Generated by Django 4.1.2 on 2023-08-21 11:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_email_verify_token_alter_user_date_of_birth"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[],
        ),
    ]