# Generated by Django 4.1.2 on 2023-08-08 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0002_remove_order_phone_num_order_phone_number_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField()),
            ],
            options={
                "verbose_name": "Payment data",
                "verbose_name_plural": "Payment data",
            },
        ),
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ("-created_at",)},
        ),
        migrations.RemoveField(
            model_name="order",
            name="status",
        ),
        migrations.AddField(
            model_name="order",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("return", "Return"),
                    ("shipment", "Awaiting Shipment"),
                    ("pickup", "Awaiting Pickup"),
                    ("shipped", "Shipped"),
                    ("cancelled", "Cancelled"),
                    ("completed", "Completed"),
                ],
                default="pending",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_mode",
            field=models.CharField(
                choices=[
                    ("cash", "Payment upon receipt of goods"),
                    ("card", "Credit and debit card"),
                ],
                default="card",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[
                    (None, "Unknown"),
                    ("success", "Success"),
                    ("error", "Error"),
                    ("reversed", "Reversed"),
                    ("failure", "Failure"),
                    ("processing", "Processing"),
                ],
                default="Unknown",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_cost",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="cost",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="discount_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=7, null=True
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                check=models.Q(("price__gt", 0)),
                name="order_orderitem_price_not_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("discount_price__gt", 0),
                    ("discount_price__isnull", True),
                    _connector="OR",
                ),
                name="order_orderitem_discount_price_not_zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                check=models.Q(("price__gt", models.F("discount_price"))),
                name="order_orderitem_discount_price_less_than_price",
            ),
        ),
        migrations.AddField(
            model_name="paymentdata",
            name="order",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_data",
                to="order.order",
            ),
        ),
    ]
