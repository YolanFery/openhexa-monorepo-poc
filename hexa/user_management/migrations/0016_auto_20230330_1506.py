# Generated by Django 4.1.7 on 2023-03-30 15:06

from django.db import migrations


def add_openhexa_legacy_flag(apps, schema_editor):
    User = apps.get_model("user_management", "User")
    Feature = apps.get_model("user_management", "Feature")
    FeatureFlag = apps.get_model("user_management", "FeatureFlag")

    feature = None
    try:
        feature = Feature.objects.get(code="openhexa_legacy")
    except Feature.DoesNotExist:
        feature = Feature.objects.create(code="openhexa_legacy")

    for user in User.objects.all():
        FeatureFlag.objects.create(feature=feature, user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0015_featureflag_cascade"),
    ]

    operations = [
        migrations.RunPython(add_openhexa_legacy_flag),
    ]
