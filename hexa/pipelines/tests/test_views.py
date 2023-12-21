import uuid
from urllib.parse import urlencode

from django.urls import reverse

from hexa.core.test import TestCase
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.pipelines.models import Pipeline, PipelineRunTrigger
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ViewsTest(TestCase):
    @classmethod
    @mock_gcp_storage
    def setUpTestData(cls):
        cls.WORKSPACE_FEATURE = Feature.objects.create(code="workspaces")
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
        )
        FeatureFlag.objects.create(feature=cls.WORKSPACE_FEATURE, user=cls.USER_JANE)

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com",
            "juliaspassword",
        )
        FeatureFlag.objects.create(feature=cls.WORKSPACE_FEATURE, user=cls.USER_JULIA)

        cls.USER_SUPERUSER = User.objects.create_user(
            "rebecca@bluesquarehub.com", "standardpassword", is_superuser=True
        )
        FeatureFlag.objects.create(
            feature=cls.WORKSPACE_FEATURE, user=cls.USER_SUPERUSER
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SUPERUSER,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
        )

        cls.WORKSPACE_MEMBERSHIP_SUPERUSER = WorkspaceMembership.objects.get(
            workspace=cls.WORKSPACE, user=cls.USER_SUPERUSER
        )

        cls.WORKSPACE_MEMBERSHIP_JULIA = WorkspaceMembership.objects.create(
            user=cls.USER_JULIA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
            webhook_enabled=True,
        )
        cls.PIPELINE.upload_new_version(cls.USER_JULIA, b"", [])

    def test_run_pipeline_not_enabled(self):
        self.PIPELINE.webhook_enabled = False
        self.PIPELINE.save()
        r = self.client.post(
            reverse(
                "pipelines:run",
                args=[self.PIPELINE.id],
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"error": "Pipeline has no webhook enabled"})

    def test_run_pipeline_valid(self):
        self.assertEqual(self.PIPELINE.last_run, None)
        response = self.client.post(
            reverse(
                "pipelines:run",
                args=[self.PIPELINE.id],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(self.PIPELINE.last_run.id), response.json()["run_id"])
        self.assertEqual(
            self.PIPELINE.last_run.trigger_mode, PipelineRunTrigger.WEBHOOK
        )

    def test_run_pipeline_invalid_pipeline(self):
        self.assertEqual(self.PIPELINE.last_run, None)
        response = self.client.post(
            reverse(
                "pipelines:run",
                args=[uuid.uuid4()],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Pipeline not found"})

    def test_run_pipeline_specific_version(self):
        response = self.client.post(
            reverse(
                "pipelines:run_with_version",
                args=[self.PIPELINE.id, self.PIPELINE.last_version.number],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.PIPELINE.last_run.pipeline_version, self.PIPELINE.last_version
        )

    def test_run_pipeline_invalid_version(self):
        self.assertEqual(self.PIPELINE.last_run, None)
        response = self.client.post(
            reverse("pipelines:run_with_version", args=[self.PIPELINE.id, 30]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Pipeline version not found"})

    def test_run_pipeline_with_multiple_config(self):
        self.assert200withConfig(
            [
                {
                    "code": "my_parameter",
                    "name": "My parameter",
                    "type": "int",
                    "required": False,
                    "multiple": True,
                }
            ],
            {},
            {},
        )
        self.assert200withConfig(
            [
                {
                    "code": "my_parameter",
                    "name": "My parameter",
                    "type": "int",
                    "required": False,
                    "multiple": True,
                }
            ],
            {"param": [1, 2]},
            {"param": [1, 2]},
        )

    def assert200withConfig(
        self, parameters, config, result_config, content_type="application/json"
    ):
        self.PIPELINE.upload_new_version(
            self.USER_JULIA,
            b"",
            parameters,
        )
        endpoint_url = reverse(
            "pipelines:run",
            args=[self.PIPELINE.id],
        )
        r = self.client.post(
            endpoint_url,
            content_type=content_type,
            data=config
            if "application/json" == content_type
            else urlencode(config, doseq=True),
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.config, result_config)

    def test_run_multiple_form_urlencoded(self):
        self.assert200withConfig(
            [
                {
                    "code": "my_parameter",
                    "name": "My parameter",
                    "type": "string",
                    "required": True,
                    "multiple": True,
                }
            ],
            {"my_parameter": ["foo", "bar"]},
            {"my_parameter": ["foo", "bar"]},
        )

    def test_urlencoded_int_parameter(self):
        # Empty value
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "required": False,
                }
            ],
            {"send_mail_notifications": True},
            {},
            content_type="application/x-www-form-urlencoded",
        )

        # Single value
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "required": True,
                }
            ],
            {"param": 1},
            {"param": 1},
            content_type="application/x-www-form-urlencoded",
        )

        # Multiple
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "multiple": True,
                }
            ],
            {"param": [1, 2]},
            {"param": [1, 2]},
            content_type="application/x-www-form-urlencoded",
        )

        # Multiple with empty value
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "multiple": True,
                }
            ],
            {"send_mail_notifications": "1"},
            {},
            content_type="application/x-www-form-urlencoded",
        )

    def test_urlencoded_default_parameter(self):
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "string",
                    "required": False,
                    "default": "foo",
                }
            ],
            {"send_mail_notifications": "1"},
            {},
            content_type="application/x-www-form-urlencoded",
        )

    def test_urlencoded_float_parameter(self):
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "float",
                    "required": True,
                }
            ],
            {"param": 1.5},
            {"param": 1.5},
            content_type="application/x-www-form-urlencoded",
        )

        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "float",
                    "multiple": True,
                }
            ],
            {"param": [1.5, 2.5]},
            {"param": [1.5, 2.5]},
            content_type="application/x-www-form-urlencoded",
        )

    def test_urlencoded_boolean_parameter(self):
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "boolean",
                    "required": True,
                }
            ],
            {"param": "true"},
            {"param": True},
            content_type="application/x-www-form-urlencoded",
        )
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "boolean",
                    "required": True,
                }
            ],
            {"param": 1},
            {"param": True},
            content_type="application/x-www-form-urlencoded",
        )

        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "boolean",
                }
            ],
            {"param": "false"},
            {"param": False},
            content_type="application/x-www-form-urlencoded",
        )
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "boolean",
                }
            ],
            {"param": 0},
            {"param": False},
            content_type="application/x-www-form-urlencoded",
        )

    def test_send_mail_notifications(self):
        endpoint_url = reverse(
            "pipelines:run",
            args=[self.PIPELINE.id],
        )
        r = self.client.post(
            endpoint_url,
            data=urlencode({"send_mail_notifications": True}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, True)

        r = self.client.post(
            endpoint_url,
            data=urlencode({"send_mail_notifications": False}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, False)

        r = self.client.post(
            endpoint_url,
            data=urlencode({"send_mail_notifications": 0}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, False)

        # And in application/json
        r = self.client.post(
            endpoint_url + "?send_mail_notifications=1",
            data={},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, True)
