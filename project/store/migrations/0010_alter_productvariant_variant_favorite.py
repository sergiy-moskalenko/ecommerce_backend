# Generated by Django 4.1.2 on 2022-12-15 19:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0009_productvariant_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='store.optionsvalue'),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='store.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites_m2m', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
