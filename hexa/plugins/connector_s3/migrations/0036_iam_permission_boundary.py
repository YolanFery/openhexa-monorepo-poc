# Generated by Django 4.1.3 on 2023-01-10 09:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_s3", "0035_credentials_endpoint_url_alter_bucket_region_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="credentials",
            name="permissions_boundary_policy_arn",
            field=models.CharField(default="arn:aws:iam::", max_length=200),
            preserve_default=False,
        ),
    ]
