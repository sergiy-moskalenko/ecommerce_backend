# Generated by Django 4.1.2 on 2023-01-17 15:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_productfilter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productfilter',
            options={'ordering': ['position']},
        ),
        migrations.AlterField(
            model_name='productfilter',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(999)]),
        ),
        migrations.AlterUniqueTogether(
            name='productfilter',
            unique_together={('category', 'option')},
        ),
    ]
