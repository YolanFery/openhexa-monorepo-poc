# Generated by Django 4.2.6 on 2023-11-02 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("visualizations", "0004_permissions_next"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="externaldashboardpermission",
            name="external_dashboard",
        ),
        migrations.RemoveField(
            model_name="externaldashboardpermission",
            name="team",
        ),
        migrations.RemoveField(
            model_name="externaldashboardpermission",
            name="user",
        ),
        migrations.RemoveField(
            model_name="index",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="index",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="index",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="indexpermission",
            name="index",
        ),
        migrations.RemoveField(
            model_name="indexpermission",
            name="permission_type",
        ),
        migrations.RemoveField(
            model_name="indexpermission",
            name="team",
        ),
        migrations.DeleteModel(
            name="ExternalDashboard",
        ),
        migrations.DeleteModel(
            name="ExternalDashboardPermission",
        ),
        migrations.DeleteModel(
            name="Index",
        ),
        migrations.DeleteModel(
            name="IndexPermission",
        ),
    ]
