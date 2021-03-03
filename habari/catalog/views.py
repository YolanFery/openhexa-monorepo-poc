from time import sleep

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from .connectors import get_connector_app_configs
from .models import Datasource


def index(request):
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasources = Datasource.objects.all()

    return render(
        request,
        "catalog/index.html",
        {
            "datasources": datasources,
            "breadcrumbs": breadcrumbs,
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    try:
        sync_result = datasource.sync()
        messages.success(request, sync_result, extra_tags="green")
    except Datasource.NoConnector as e:
        messages.error(request, e, extra_tags="red")

    return redirect(request.META.get("HTTP_REFERER"))


def quick_search(request):
    query = request.GET.get("query", "")
    results = Datasource.objects.search(query)

    connector_app_configs = get_connector_app_configs()
    for app_config in connector_app_configs:
        results += app_config.connector.objects.search(query)

    return JsonResponse(
        {
            "results": [
                result.to_dict()
                for result in sorted(results, key=lambda r: r.rank, reverse=True)[:10]
            ]
        }
    )


def search(request):
    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (_("Search"),),
    ]

    return render(request, "catalog/search.html", {"breadcrumbs": breadcrumbs})
