# Generated by Django 4.1.2 on 2022-11-10 09:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("upload_excel", "0002_cellrangemodel_is_dev_exp_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cellrangemodel",
            name="include_title",
            field=models.BooleanField(default=False, verbose_name="タイトルかどうか"),
        ),
        migrations.AlterField(
            model_name="cellrangemodel",
            name="cell_range_id",
            field=models.UUIDField(
                default=uuid.UUID("071622a7-4aae-4cee-b28a-5e1ee4b676f7"),
                help_text="An ID based on uuid4 is assigned by cell range randomly and automatically.",
                verbose_name="セル範囲ID",
            ),
        ),
        migrations.AlterField(
            model_name="excelsheetmodel",
            name="sheet_id",
            field=models.UUIDField(
                default=uuid.UUID("676a9965-319a-4c03-b618-73e8542dac10"),
                help_text="An ID based on uuid4 is assigned by sheet randomly and automatically.",
                primary_key=True,
                serialize=False,
                verbose_name="シートID",
            ),
        ),
    ]