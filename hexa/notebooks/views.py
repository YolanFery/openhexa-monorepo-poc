from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.app import get_hexa_app_configs
from hexa.notebooks.credentials import NotebooksCredentials


@require_POST
@csrf_exempt  # TODO: we should remove this
def credentials(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    notebooks_credentials = NotebooksCredentials(request.user)

    if request.user.is_authenticated:
        # Set "Git in notebooks" feature flag
        notebooks_credentials.update_env(
            {
                "GIT_EXTENSION_ENABLED": "true"
                if notebooks_credentials.user.has_feature_flag(
                    "notebooks_git_extension"
                )
                else "false"
            }
        )

        for app_config in get_hexa_app_configs(connector_only=True):
            credentials_functions = app_config.get_notebooks_credentials()
            for credentials_function in credentials_functions:
                credentials_function(notebooks_credentials)

    if notebooks_credentials.authenticated:
        return JsonResponse(
            notebooks_credentials.to_dict(),
            status=200,
        )

    return JsonResponse(
        {},
        status=401,
    )
