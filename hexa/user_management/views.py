from django.http import JsonResponse
from django.shortcuts import render

from hexa.catalog.connectors import get_connector_app_configs
from hexa.notebooks.credentials import NotebooksCredentials


def account(request):
    return render(request, "user_management/account.html", {"user": request.user})


def credentials(request):
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    notebooks_credentials = NotebooksCredentials(request.user)

    if request.user.is_authenticated:
        for app_config in get_connector_app_configs():
            credentials_functions = app_config.get_notebooks_credentials()
            for credentials_function in credentials_functions:
                credentials_function(notebooks_credentials, request.user)

    return JsonResponse(
        notebooks_credentials.to_dict(),
        status=200 if notebooks_credentials.authenticated else 401,
    )
