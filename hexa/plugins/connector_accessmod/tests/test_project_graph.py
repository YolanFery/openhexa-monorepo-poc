import uuid

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    Project,
)
from hexa.user_management.models import User


class AccessmodProjectGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janesthebest",
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
            crs=4326,
        )
        cls.OTHER_PROJECT = Project.objects.create(
            name="Other project",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
            crs=4326,
        )
        cls.SLOPE_ROLE = FilesetRole.objects.create(
            name="Slope",
            code=FilesetRoleCode.SLOPE,
            format=FilesetFormat.RASTER,
        )
        cls.SLOPE_FILESET = Fileset.objects.create(
            name="A wonderful slope",
            role=cls.SLOPE_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.SLOPE_FILE = File.objects.create(
            fileset=cls.SLOPE_FILESET, uri="afile.tiff", mime_type="image/tiff"
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="A random accessibility analysis",
            slope=cls.SLOPE_FILESET,
            priority_land_cover=[1, 2],
        )

    def test_accessmod_project_owner(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProject($id: String!) {
                  accessmodProject(id: $id) {
                    id
                    name
                    spatialResolution
                    country {
                        code
                    }
                    owner {
                        email
                    }
                  }
                }
            """,
            {"id": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodProject"],
            {
                "id": str(self.SAMPLE_PROJECT.id),
                "name": "Sample project",
                "spatialResolution": 100,
                "country": {"code": "BE"},
                "owner": {"email": "jim@bluesquarehub.com"},
            },
        )

    def test_accessmod_project_not_owner(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodProject($id: String!) {
                  accessmodProject(id: $id) {
                    id
                  }
                }
            """,
            {"id": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodProject"],
            None,
        )

    def test_accessmod_projects(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
        )

    def test_accessmod_projects_with_term(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects(term: "samp", page: 1, perPage: 10) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
        )

    def test_accessmod_projects_with_pagination(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects(page: 1, perPage: 10) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
        )

    def test_accessmod_projects_empty(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 0,
                "items": [],
            },
        )

    def test_create_accessmod_project(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput) {
                  createAccessmodProject(input: $input) {
                    success
                    project {
                        name
                        spatialResolution
                        crs
                        country {
                            code
                        }
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["createAccessmodProject"],
            {
                "success": True,
                "project": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                },
                "errors": [],
            },
        )

    def test_create_accessmod_project_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput) {
                  createAccessmodProject(input: $input) {
                    success
                    project {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "name": self.SAMPLE_PROJECT.name,
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["createAccessmodProject"],
            {"success": False, "project": None, "errors": ["NAME_DUPLICATE"]},
        )

    def test_update_accessmod_project(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                        name
                        country {
                            code
                        }
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodProject"],
            {
                "success": True,
                "project": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
                    "country": {"code": "CD"},
                },
                "errors": [],
            },
        )

    def test_update_accessmod_project_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": self.OTHER_PROJECT.name,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodProject"],
            {
                "success": False,
                "project": {"id": str(self.SAMPLE_PROJECT.id)},
                "errors": ["NAME_DUPLICATE"],
            },
        )

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(uuid.uuid4()),
                    "name": "YOLO",
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            {"success": False, "project": None, "errors": ["NOT_FOUND"]},
            r["data"]["updateAccessmodProject"],
        )

    def test_delete_accessmod_project(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation deleteAccessmodProject($input: DeleteAccessmodProjectInput) {
                  deleteAccessmodProject(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                }
            },
        )

        self.assertEqual(
            r["data"]["deleteAccessmodProject"],
            {"success": True, "errors": []},
        )
        self.assertIsNone(Project.objects.filter(id=self.SAMPLE_PROJECT.id).first())

    def test_delete_accessmod_project_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation deleteAccessmodProject($input: DeleteAccessmodProjectInput) {
                  deleteAccessmodProject(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(uuid.uuid4()),
                }
            },
        )

        self.assertEqual(
            r["data"]["deleteAccessmodProject"],
            {"success": False, "errors": ["NOT_FOUND"]},
        )
        self.assertIsNotNone(Project.objects.filter(id=self.SAMPLE_PROJECT.id).first())
