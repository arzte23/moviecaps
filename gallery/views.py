from django.shortcuts import get_object_or_404, render

from .models import Screencap, Title


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


def title_detail(request, slug):
    title = get_object_or_404(Title.objects.prefetch_related("caps"), slug=slug)
    return render(request, "gallery/title_detail.html", {"title": title})
