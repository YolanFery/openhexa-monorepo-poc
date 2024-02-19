# Generated by Django 4.1.3 on 2022-11-15 08:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_s3", "0034_remove_object_collections_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="credentials",
            name="endpoint_url",
            field=models.CharField(
                blank=True,
                help_text="The URL of your MinIO server. Let it blank when using real Amazon S3",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="bucket",
            name="region",
            field=models.CharField(
                choices=[
                    ("us-east-1", "us-east-1"),
                    ("us-east-2", "us-east-2"),
                    ("us-west-1", "us-west-1"),
                    ("us-west-2", "us-west-2"),
                    ("ca-central-1", "ca-central-1"),
                    ("eu-north-1", "eu-north-1"),
                    ("eu-west-3", "eu-west-3"),
                    ("eu-west-2", "eu-west-2"),
                    ("eu-west-1", "eu-west-1"),
                    ("eu-central-1", "eu-central-1"),
                    ("eu-south-1", "eu-south-1"),
                    ("ap-south-1", "ap-south-1"),
                    ("ap-northeast-1", "ap-northeast-1"),
                    ("ap-northeast-2", "ap-northeast-2"),
                    ("ap-northeast-3", "ap-northeast-3"),
                    ("ap-southeast-1", "ap-southeast-1"),
                    ("ap-southeast-2", "ap-southeast-2"),
                    ("ap-east-1", "ap-east-1"),
                    ("sa-east-1", "sa-east-1"),
                    ("cn-north-1", "cn-north-1"),
                    ("cn-northwest-1", "cn-northwest-1"),
                    ("me-south-1", "me-south-1"),
                    ("af-south-1", "af-south-1"),
                    ("ap-south-2", "ap-south-2"),
                    ("eu-east-1", "eu-east-1"),
                    ("eu-central-2", "eu-central-2"),
                    ("ap-southeast-3", "ap-southeast-3"),
                    ("me-south-2", "me-south-2"),
                    ("me-west-1", "me-west-1"),
                    ("minio", "minio"),
                ],
                default="eu-central-1",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="credentials",
            name="default_region",
            field=models.CharField(
                choices=[
                    ("us-east-1", "us-east-1"),
                    ("us-east-2", "us-east-2"),
                    ("us-west-1", "us-west-1"),
                    ("us-west-2", "us-west-2"),
                    ("ca-central-1", "ca-central-1"),
                    ("eu-north-1", "eu-north-1"),
                    ("eu-west-3", "eu-west-3"),
                    ("eu-west-2", "eu-west-2"),
                    ("eu-west-1", "eu-west-1"),
                    ("eu-central-1", "eu-central-1"),
                    ("eu-south-1", "eu-south-1"),
                    ("ap-south-1", "ap-south-1"),
                    ("ap-northeast-1", "ap-northeast-1"),
                    ("ap-northeast-2", "ap-northeast-2"),
                    ("ap-northeast-3", "ap-northeast-3"),
                    ("ap-southeast-1", "ap-southeast-1"),
                    ("ap-southeast-2", "ap-southeast-2"),
                    ("ap-east-1", "ap-east-1"),
                    ("sa-east-1", "sa-east-1"),
                    ("cn-north-1", "cn-north-1"),
                    ("cn-northwest-1", "cn-northwest-1"),
                    ("me-south-1", "me-south-1"),
                    ("af-south-1", "af-south-1"),
                    ("ap-south-2", "ap-south-2"),
                    ("eu-east-1", "eu-east-1"),
                    ("eu-central-2", "eu-central-2"),
                    ("ap-southeast-3", "ap-southeast-3"),
                    ("me-south-2", "me-south-2"),
                    ("me-west-1", "me-west-1"),
                    ("minio", "minio"),
                ],
                default="eu-central-1",
                max_length=50,
            ),
        ),
    ]
