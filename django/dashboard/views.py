
import json
import requests

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .data_sources.npb import fetch_gold

@require_http_methods(["GET", "POST"])
def index(request):
    
    context = {}

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "fetch_gold":
            try:
                data = fetch_gold()

                print("Dane zlota: ", flush=True)
                print(
                    json.dumps(data, ensure_ascii=False, indent=2)
                )

                context["gold_data"] = data
                context["message"]   = (
                    f"pobrano {len(data)} notowań"
                )
            except (requests.exceptions.RequestException, ValueError) as exc:
                print(f"Błąd: {exc}", flush=True)

                context["error"] = ("dupa 1")
        else:
            context["error"] = "dupa 2"

    return render(request, "M:/repos_new/Data-engineering/django/dashboard/templates/index.html", context)