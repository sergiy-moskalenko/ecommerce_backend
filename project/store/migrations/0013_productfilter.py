# Generated by Django 4.1.2 on 2023-01-16 08:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_category_options_productimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(999)])),
                ('hide', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_filter', to='store.category')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_filter', to='store.option')),
            ],
        ),
    ]
