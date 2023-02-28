from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
        )

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
        )

        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )

        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_JULIA
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_JULIA,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER_REBECCA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.WORKSPACE_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            user=cls.USER_JULIA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.WORKSPACE_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="DB",
            description="Connection's description",
            connection_type=ConnectionType.POSTGRESQL,
        )

        cls.WORKSPACE_CONNECTION.set_fields(
            cls.USER_JULIA,
            [{"code": "field_1", "value": "value_1", "secret": False}],
        )

    def test_workspace_credentials_404(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse(
                "workspaces:credentials", kwargs={"workspace_slug": self.WORKSPACE.slug}
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_workspace_credentials_401(self):
        self.client.force_login(self.USER_REBECCA)
        response = self.client.post(
            reverse(
                "workspaces:credentials", kwargs={"workspace_slug": self.WORKSPACE.slug}
            )
        )
        self.assertEqual(response.status_code, 401)

    def test_workspace_credentials_200(self):
        self.client.force_login(self.USER_JULIA)
        response = self.client.post(
            reverse(
                "workspaces:credentials", kwargs={"workspace_slug": self.WORKSPACE.slug}
            )
        )

        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["env"], {"DB_field_1": "value_1"})
