from ariadne import MutationType
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from hexa.workspaces.models import Workspace

from ..api import generate_download_url, generate_upload_url, get_blob
from ..models import Dataset, DatasetLink, DatasetVersion, DatasetVersionFile

mutations = MutationType()


@mutations.field("createDataset")
def resolve_create_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspaceSlug"]
        )
        dataset = Dataset.objects.create_if_has_perm(
            principal=request.user,
            workspace=workspace,
            name=mutation_input["name"],
            description=mutation_input["description"],
        )
        link = DatasetLink.objects.get(dataset=dataset, workspace=workspace)

        return {
            "success": True,
            "errors": [],
            "link": link,
            "dataset": dataset,
        }
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("updateDataset")
def resolve_update_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["datasetId"]
        )

        dataset.update_if_has_perm(
            principal=request.user,
            **mutation_input,
        )

        return {"success": True, "errors": [], "dataset": dataset}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("deleteDataset")
def resolve_delete_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["id"]
        )

        dataset.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("createDatasetVersion")
def resolve_create_dataset_version(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["datasetId"]
        )

        version = DatasetVersion.objects.create_if_has_perm(
            principal=request.user,
            dataset=dataset,
            name=mutation_input["name"],
            description=mutation_input.get("description"),
        )

        return {"success": True, "errors": [], "version": version}
    except IntegrityError:
        return {"success": False, "errors": ["DUPLICATE_NAME"]}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("deleteDatasetVersion")
def resolve_delete_dataset_version(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        version = DatasetVersion.objects.filter_for_user(request.user).get(
            id=mutation_input["versionId"]
        )

        version.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except DatasetVersion.DoesNotExist:
        return {"success": False, "errors": ["VERSION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("linkDataset")
def resolve_link_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["datasetId"]
        )
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspaceSlug"]
        )

        if not request.user.has_perm("datasets.link_dataset", (dataset, workspace)):
            raise PermissionDenied

        link = dataset.link(principal=request.user, workspace=workspace)

        return {"success": True, "errors": [], "link": link}
    except IntegrityError:
        return {"success": False, "errors": ["ALREADY_LINKED"]}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("deleteDatasetLink")
def resolve_delete_dataset_share(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        link = DatasetLink.objects.filter_for_user(request.user).get(
            id=mutation_input["id"]
        )

        link.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except DatasetLink.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("createDatasetVersionFile")
def resolve_create_version_file(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        version = DatasetVersion.objects.filter_for_user(request.user).get(
            id=mutation_input["versionId"]
        )

        if not request.user.has_perm(
            "datasets.create_dataset_version", version.dataset
        ):
            raise PermissionDenied

        with transaction.atomic():
            file = None
            try:
                file = version.get_file_by_name(mutation_input["uri"])
                if get_blob(file) is not None:
                    return {"success": False, "errors": ["ALREADY_EXISTS"]}
            except DatasetVersionFile.DoesNotExist:
                file = DatasetVersionFile.objects.create(
                    dataset_version=version,
                    uri=version.get_full_uri(mutation_input["uri"]),
                    content_type=mutation_input["contentType"],
                    created_by=request.user,
                )
            upload_url = generate_upload_url(file)
            return {
                "success": True,
                "errors": [],
                "file": file,
                "upload_url": upload_url,
            }
    except ValidationError:
        return {"success": False, "errors": ["INVALID_URI"]}
    except DatasetVersion.DoesNotExist:
        return {"success": False, "errors": ["VERSION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("prepareVersionFileDownload")
def resolve_version_file_download(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        file = DatasetVersionFile.objects.filter_for_user(request.user).get(
            id=mutation_input["fileId"]
        )

        if not request.user.has_perm(
            "datasets.download_dataset", file.dataset_version.dataset
        ):
            raise PermissionDenied

        download_url = generate_download_url(file)
        if download_url is None:
            return {"success": False, "errors": ["FILE_NOT_UPLOADED"]}

        return {"success": True, "errors": [], "download_url": download_url}
    except DatasetVersionFile.DoesNotExist:
        return {"success": False, "errors": ["FILE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("pinDataset")
def resolve_pin_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        link = DatasetLink.objects.get(id=mutation_input["linkId"])

        if not request.user.has_perm("datasets.pin_dataset", link):
            raise PermissionDenied

        link.is_pinned = mutation_input["pinned"]
        link.save()

        return {"success": True, "errors": [], "link": link}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except DatasetLink.DoesNotExist:
        return {"success": False, "errors": ["LINK_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


bindables = [mutations]
