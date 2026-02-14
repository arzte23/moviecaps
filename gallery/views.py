from django.shortcuts import render

from .models import Screencap


def home(request):
    screencaps = Screencap.objects.select_related("title").all()
    return render(request, "gallery/home.html", {"screencaps": screencaps})


def search(request):
    query = request.GET.get("q")
    if query:
        screencaps = (
            Screencap.objects.filter(tags__name__icontains=query)
            .select_related("title")
            .distinct()
        )
    else:
        screencaps = Screencap.objects.none()

    return render(
        request, "gallery/search.html", {"screencaps": screencaps, "query": query}
    )
