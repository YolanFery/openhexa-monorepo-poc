# Generated by Django 4.0.6 on 2022-09-06 16:32

import django.db.models.deletion
import django.db.models.expressions
from django.db import migrations, models

import hexa.data_collections.models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("data_collections", "0003_collectionelement_object_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectionelement",
            name="collection",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="elements",
                to="data_collections.collection",
            ),
        ),
        migrations.AlterField(
            model_name="collectionelement",
            name="object_type",
            field=models.ForeignKey(
                limit_choices_to=hexa.data_collections.models.limit_data_source_types,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddConstraint(
            model_name="collectionelement",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("collection_id"),
                django.db.models.expressions.F("object_type"),
                django.db.models.expressions.F("object_id"),
                name="collection_element_unique_object",
            ),
        ),
    ]
