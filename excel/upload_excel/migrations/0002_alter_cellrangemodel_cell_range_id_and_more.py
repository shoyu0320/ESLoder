# Generated by Django 4.1.2 on 2022-11-07 08:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("upload_excel", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cellrangemodel",
            name="cell_range_id",
            field=models.UUIDField(
                default=uuid.UUID("50d6776b-433a-4212-9a71-43e79c4b1439"),
                help_text="An ID based on uuid4 is assigned by cell range randomly and automatically.",
                verbose_name="セル範囲ID",
            ),
        ),
        migrations.AlterField(
            model_name="excelsheetmodel",
            name="sheet_id",
            field=models.UUIDField(
                default=uuid.UUID("1a96cbd6-bf7a-4731-9bb2-025c76e7f584"),
                help_text="An ID based on uuid4 is assigned by sheet randomly and automatically.",
                verbose_name="シートID",
            ),
        ),
    ]
