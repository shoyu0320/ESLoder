# Generated by Django 4.1.2 on 2022-11-09 08:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CellRangeModel",
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
                (
                    "sheet_create_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Define when a sheet has created.",
                        verbose_name="セル範囲作成日時",
                    ),
                ),
                (
                    "sheet_update_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Define when a sheet has updated.",
                        verbose_name="セル範囲作成日時",
                    ),
                ),
                (
                    "cell_range_id",
                    models.UUIDField(
                        default=uuid.UUID("f59cb19e-945b-4db8-8902-c9acbf458a74"),
                        help_text="An ID based on uuid4 is assigned by cell range randomly and automatically.",
                        verbose_name="セル範囲ID",
                    ),
                ),
                (
                    "cell_range_id_by_order",
                    models.IntegerField(
                        default=None,
                        help_text="An ID based on merged order is assigned by cell range.",
                        verbose_name="順序付きセル範囲ID",
                    ),
                ),
                (
                    "effective_cell_width",
                    models.IntegerField(default=1, verbose_name="有効セル幅"),
                ),
                (
                    "effective_cell_height",
                    models.IntegerField(default=1, verbose_name="有効セル高さ"),
                ),
                ("has_parent", models.BooleanField(default=True, verbose_name="親の有無")),
            ],
            options={"db_table": "cell_range",},
        ),
        migrations.CreateModel(
            name="ESTemplateNamesModel",
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
                (
                    "name",
                    models.CharField(
                        default="profile", max_length=20, verbose_name="シートタイプ"
                    ),
                ),
            ],
            options={"db_table": "template_names",},
        ),
        migrations.CreateModel(
            name="ExcelSheetModel",
            fields=[
                (
                    "sheet_create_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Define when a sheet has created.",
                        verbose_name="シート作成日時",
                    ),
                ),
                (
                    "sheet_update_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Define when a sheet has updated.",
                        verbose_name="シート作成日時",
                    ),
                ),
                (
                    "sheet_id",
                    models.UUIDField(
                        default=uuid.UUID("5f45a265-6d45-43b2-bc61-93eb0e9347fe"),
                        help_text="An ID based on uuid4 is assigned by sheet randomly and automatically.",
                        primary_key=True,
                        serialize=False,
                        verbose_name="シートID",
                    ),
                ),
                (
                    "sheet_type",
                    models.CharField(
                        choices=[(1, "profile"), (2, "project")],
                        default="profile",
                        help_text="Set a name of template sheet.'profile' that is default sheet type is a template we designed as typical profile in our officeEven before you don't generate your custom template, you can use two template types of 'profile' and 'project'",
                        max_length=10,
                        verbose_name="シートタイプ",
                    ),
                ),
                (
                    "col_size",
                    models.PositiveIntegerField(default=1, verbose_name="シートのカラムサイズ"),
                ),
                (
                    "row_size",
                    models.PositiveIntegerField(default=1, verbose_name="シートのローサイズ"),
                ),
            ],
            options={"db_table": "excel_sheet",},
        ),
        migrations.CreateModel(
            name="RowModel",
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
                (
                    "cell_start",
                    models.CharField(
                        default="A1", max_length=10, verbose_name="セルのロー初期位置"
                    ),
                ),
                (
                    "cell_end",
                    models.CharField(
                        default="A1", max_length=10, verbose_name="セルのロー終端位置"
                    ),
                ),
                (
                    "cell_size",
                    models.PositiveIntegerField(default=1, verbose_name="セルの行方向サイズ"),
                ),
                (
                    "cell_range_id_by_order",
                    models.IntegerField(
                        default=None,
                        help_text="An ID based on merged order is assigned by cell range.",
                        verbose_name="順序付きセル範囲ID",
                    ),
                ),
                (
                    "cell_range",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rows",
                        to="upload_excel.cellrangemodel",
                    ),
                ),
            ],
            options={"db_table": "row",},
        ),
        migrations.CreateModel(
            name="ContentModel",
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
                ("cell_content", models.TextField(default="", verbose_name="セルの内容")),
                (
                    "cell_range_id_by_order",
                    models.IntegerField(
                        default=None,
                        help_text="An ID based on merged order is assigned by cell range.",
                        verbose_name="順序付きセル範囲ID",
                    ),
                ),
                (
                    "cell_range",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="content",
                        to="upload_excel.cellrangemodel",
                    ),
                ),
            ],
            options={"db_table": "content",},
        ),
        migrations.CreateModel(
            name="ColumnModel",
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
                (
                    "cell_start",
                    models.CharField(
                        default="A1", max_length=10, verbose_name="セルのカラム初期位置"
                    ),
                ),
                (
                    "cell_end",
                    models.CharField(
                        default="A1", max_length=10, verbose_name="セルのカラム終端位置"
                    ),
                ),
                (
                    "cell_size",
                    models.PositiveIntegerField(default=1, verbose_name="セルの列方向サイズ"),
                ),
                (
                    "cell_range_id_by_order",
                    models.IntegerField(
                        default=None,
                        help_text="An ID based on merged order is assigned by cell range.",
                        verbose_name="順序付きセル範囲ID",
                    ),
                ),
                (
                    "cell_range",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="columns",
                        to="upload_excel.cellrangemodel",
                    ),
                ),
            ],
            options={"db_table": "column",},
        ),
        migrations.AddField(
            model_name="cellrangemodel",
            name="excel_sheet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cell_ranges",
                to="upload_excel.excelsheetmodel",
            ),
        ),
    ]
