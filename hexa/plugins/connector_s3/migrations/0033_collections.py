# Generated by Django 4.0.6 on 2022-07-29 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_collections", "0001_collections"),
        ("connector_s3", "0032_permission_mode_data_2"),
    ]

    operations = [
        migrations.CreateModel(
            name="ObjectCollectionElement",
            fields=[
                (
                    "collectionelement_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="data_collections.collectionelement",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("data_collections.collectionelement",),
        ),
        migrations.AddField(
            model_name="object",
            name="collections",
            field=models.ManyToManyField(
                related_name="+",
                through="connector_s3.ObjectCollectionElement",
                to="data_collections.collection",
            ),
        ),
        migrations.AddField(
            model_name="objectcollectionelement",
            name="element",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="connector_s3.object"
            ),
        ),
    ]
