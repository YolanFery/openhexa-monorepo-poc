# Generated by Django 3.2.6 on 2021-08-23 09:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("connector_dhis2", "0012_alter_instancepermission_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dataelement",
            options={"ordering": ("dhis2_name",), "verbose_name": "DHIS2 Data Element"},
        ),
        migrations.AlterModelOptions(
            name="indicator",
            options={"ordering": ("dhis2_name",), "verbose_name": "DHIS2 Indicator"},
        ),
        migrations.AlterModelOptions(
            name="indicatortype",
            options={
                "ordering": ("dhis2_name",),
                "verbose_name": "DHIS2 Indicator type",
            },
        ),
        migrations.AlterModelOptions(
            name="instance",
            options={"ordering": ("url",), "verbose_name": "DHIS2 Instance"},
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="countries",
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="description",
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="locale",
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="name",
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="short_name",
        ),
        migrations.RemoveField(
            model_name="dataelement",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="countries",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="description",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="locale",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="name",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="short_name",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="countries",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="description",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="locale",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="name",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="short_name",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="active_from",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="active_to",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="countries",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="description",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="locale",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="name",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="public",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="short_name",
        ),
        migrations.RemoveField(
            model_name="instance",
            name="tags",
        ),
    ]
