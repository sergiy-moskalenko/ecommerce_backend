# Generated by Django 4.1.2 on 2023-08-07 16:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0015_product_discount_price_alter_product_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="discount_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=7, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name="productfilter",
            name="position",
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                check=models.Q(("price__gt", 0)),
                name="store_product_price_not_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("discount_price__gt", 0),
                    ("discount_price__isnull", True),
                    _connector="OR",
                ),
                name="store_product_discount_price_not_zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                check=models.Q(("price__gt", models.F("discount_price"))),
                name="store_product_price_more_than_discount_price",
            ),
        ),
    ]
