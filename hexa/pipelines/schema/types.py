import base64

from ariadne import EnumType, ObjectType, UnionType
from django.urls import reverse
from sentry_sdk import capture_exception

from hexa.core.graphql import result_page
from hexa.databases.utils import get_table_definition
from hexa.files.api import get_storage
from hexa.files.basefs import NotFound
from hexa.pipelines.models import Pipeline, PipelineRun, PipelineVersion
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_permissions

pipeline_permissions = ObjectType("PipelinePermissions")
pipeline_version_permissions = ObjectType("PipelineVersionPermissions")
pipeline_parameter = ObjectType("PipelineParameter")
pipeline_run_status_enum = EnumType("PipelineRunStatus", PipelineRun.STATUS_MAPPINGS)
pipeline_run_order_by_enum = EnumType(
    "PipelineRunOrderBy",
    {
        "EXECUTION_DATE_DESC": "-execution_date",
        "EXECUTION_DATE_ASC": "execution_date",
    },
)
pipeline_object = ObjectType("Pipeline")
generic_output_object = ObjectType("GenericOutput")

pipeline_run_output_union = UnionType("PipelineRunOutput")


def get_bucket_object(bucket_name, file):
    return get_storage().get_bucket_object(bucket_name, file)


@workspace_permissions.field("createPipeline")
def resolve_workspace_permissions_create_pipeline(obj: Workspace, info, **kwargs):
    request = info.context["request"]

    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.create_pipeline", obj
    )


@pipeline_run_output_union.type_resolver
def resolve_run_output_type(obj, *_):
    if "columns" in obj:
        return "DatabaseTable"
    elif obj["type"] == "file" or obj["type"] == "directory":
        return "BucketObject"

    return "GenericOutput"


@pipeline_parameter.field("name")
def resolve_pipeline_parameter_code(parameter, info, **kwargs):
    name = parameter.get("name")
    if name is None:
        name = parameter["code"]
    return name


@pipeline_parameter.field("required")
def resolve_pipeline_parameter_required(parameter, info, **kwargs):
    return parameter.get("required", False)


@pipeline_parameter.field("multiple")
def resolve_pipeline_parameter_multiple(parameter, info, **kwargs):
    return parameter.get("multiple", False)


@pipeline_permissions.field("update")
def resolve_pipeline_permissions_update(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.update_pipeline", pipeline
    )


@pipeline_permissions.field("createVersion")
def resolve_pipeline_permissions_create_version(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.create_pipeline_version", pipeline
    )


@pipeline_permissions.field("delete")
def resolve_pipeline_permissions_delete(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.delete_pipeline", pipeline
    )


@pipeline_permissions.field("run")
def resolve_pipeline_permissions_run(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.run_pipeline", pipeline
    )


@pipeline_permissions.field("schedule")
def resolve_pipeline_permissions_schedule(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return (
        request.user.is_authenticated
        and request.user.has_perm("pipelines.run_pipeline", pipeline)
        and pipeline.last_version
        and pipeline.last_version.is_schedulable
    )


@pipeline_permissions.field("stopPipeline")
def resolve_pipeline_permissions_stop_pipeline(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.stop_pipeline", pipeline
    )


@pipeline_version_permissions.field("update")
def resolve_pipeline_version_permissions_update(
    version: PipelineVersion, info, **kwargs
):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.update_pipeline_version", version
    )


@pipeline_version_permissions.field("delete")
def resolve_pipeline_version_permissions_delete(
    version: PipelineVersion, info, **kwargs
):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.delete_pipeline_version", version
    )


@pipeline_object.field("webhookUrl")
def resolve_pipeline_webhook_url(pipeline: Pipeline, info):
    request = info.context["request"]
    if pipeline.webhook_enabled:
        return request.build_absolute_uri(reverse("pipelines:run", args=[pipeline.id]))


@pipeline_object.field("currentVersion")
def resolve_pipeline_current_version(pipeline: Pipeline, info, **kwargs):
    return pipeline.last_version


@pipeline_object.field("permissions")
def resolve_pipeline_permissions(pipeline: Pipeline, info, **kwargs):
    return pipeline


@pipeline_object.field("versions")
def resolve_pipeline_versions(pipeline: Pipeline, info, **kwargs):
    qs = pipeline.versions.all()
    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@pipeline_object.field("runs")
def resolve_pipeline_runs(pipeline: Pipeline, info, **kwargs):
    qs = PipelineRun.objects.filter(pipeline=pipeline)

    order_by = kwargs.get("orderBy", None)
    if order_by is not None:
        qs = qs.order_by(order_by)
    else:
        qs = qs.order_by("-execution_date")

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@pipeline_object.field("recipients")
def resolve_pipeline_recipients(pipeline: Pipeline, info, **kwargs):
    return pipeline.pipelinerecipient_set.all()


pipeline_run_object = ObjectType("PipelineRun")


@pipeline_run_object.field("triggerMode")
def resolve_pipeline_run_trigger_mode(run: PipelineRun, info, **kwargs):
    return run.trigger_mode


@pipeline_run_object.field("duration")
def resolve_pipeline_run_duration(run: PipelineRun, info, **kwargs):
    return int(run.duration.total_seconds()) if run.duration is not None else 0


@pipeline_run_object.field("config")
def resolve_pipeline_run_config(run: PipelineRun, info, **kwargs):
    return run.config


@pipeline_run_object.field("code")
def resolve_pipeline_run_code(run: PipelineRun, info, **kwargs):
    return base64.b64encode(run.get_code()).decode("ascii")


pipeline_run_object.set_alias("progress", "current_progress")
pipeline_run_object.set_alias("logs", "run_logs")
pipeline_run_object.set_alias("version", "pipeline_version")


pipeline_version_object = ObjectType("PipelineVersion")


@pipeline_version_object.field("isLatestVersion")
def resolve_pipeline_version_is_latest(version: PipelineVersion, info, **kwargs):
    return version.is_latest_version


@pipeline_version_object.field("zipfile")
def resolve_pipeline_version_zipfile(version: PipelineVersion, info, **kwargs):
    return base64.b64encode(version.zipfile).decode("ascii")


@pipeline_version_object.field("permissions")
def resolve_pipeline_version_permissions(version: PipelineVersion, info, **kwargs):
    return version


@pipeline_run_object.field("outputs")
def resolve_pipeline_run_outputs(run: PipelineRun, info, **kwargs):
    result = []
    workspace = run.pipeline.workspace
    for output in run.outputs:
        try:
            if output["type"] == "file":
                result.append(
                    get_bucket_object(
                        workspace.bucket_name,
                        output["uri"][len(f"gs://{workspace.bucket_name}/") :],
                    )
                )
            elif output["type"] == "db":
                table_data = get_table_definition(workspace, output["name"])
                if table_data:
                    result.append(table_data)
                else:
                    raise Exception(
                        f"Table {output['name']} not found or connection error"
                    )
            else:
                result.append(output)
        except NotFound:
            # File object might be deleted
            continue
        except Exception as e:
            # Table or Bucket object might be deleted
            capture_exception(e)

    return result


@pipeline_run_object.field("datasetVersions")
def resolve_pipeline_run_dataset_version(run: PipelineRun, info, **kwargs):
    return run.dataset_versions.all()


# FIXME: This is an alias to still support the deprecated "number" field
pipeline_version_object.set_alias("number", "name")


bindables = [
    pipeline_permissions,
    pipeline_parameter,
    pipeline_object,
    pipeline_run_object,
    pipeline_run_status_enum,
    pipeline_run_order_by_enum,
    pipeline_version_object,
    pipeline_version_permissions,
    generic_output_object,
    pipeline_run_output_union,
]
