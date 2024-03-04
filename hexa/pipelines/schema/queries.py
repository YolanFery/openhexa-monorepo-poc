from ariadne import QueryType
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineVersion,
)
from hexa.workspaces.models import Workspace

pipelines_query = QueryType()


@pipelines_query.field("pipelines")
def resolve_pipelines(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if kwargs.get("workspaceSlug", None):
        try:
            ws = Workspace.objects.filter_for_user(request.user).get(
                slug=kwargs.get("workspaceSlug")
            )
            qs = (
                Pipeline.objects.filter_for_user(request.user)
                .filter(workspace=ws)
                .order_by("name", "id")
            )
        except Workspace.DoesNotExist:
            qs = Pipeline.objects.none()
    else:
        qs = Pipeline.objects.filter_for_user(request.user).order_by("name", "id")

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@pipelines_query.field("pipeline")
def resolve_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        return Pipeline.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Pipeline.DoesNotExist:
        return None


@pipelines_query.field("pipelineByCode")
def resolve_pipeline_by_code(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            workspace__slug=kwargs["workspaceSlug"], code=kwargs["code"]
        )
    except Pipeline.DoesNotExist:
        pipeline = None

    return pipeline


@pipelines_query.field("pipelineRun")
def resolve_pipeline_run(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if not request.user.is_authenticated:
        return None

    run_id = kwargs["id"]
    try:
        if isinstance(request.user, PipelineRunUser):
            qs = PipelineRun.objects.filter(id=request.user.pipeline_run.id).exclude(
                state__in=[PipelineRunState.SUCCESS, PipelineRunState.FAILED]
            )
        else:
            qs = PipelineRun.objects.filter_for_user(request.user)

        return qs.get(id=run_id)

    except PipelineRun.DoesNotExist:
        return None


@pipelines_query.field("pipelineVersion")
def resolve_pipeline_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        version = PipelineVersion.objects.get(id=kwargs["id"])
        if request.user.has_perm("pipelines.view_pipeline_version", version):
            return version
    except PipelineVersion.DoesNotExist:
        return None


bindables = [
    pipelines_query,
]
