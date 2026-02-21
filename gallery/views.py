from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Screencap, Title


def home(request):
    screencaps = Screencap.objects.select_related("title").all()
    paginator = Paginator(screencaps, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    custom_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    return render(
        request,
        "gallery/home.html",
        {"page_obj": page_obj, "custom_range": custom_range},
    )


def search(request):
    query = request.GET.get("q")
    if query:
        screencaps = (
            Screencap.objects.filter(
                Q(tags__name__icontains=query)
                | Q(title__name__icontains=query)
                | Q(title__description__icontains=query)
            )
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
    screencaps = title.caps.all()
    paginator = Paginator(screencaps, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    custom_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    return render(
        request,
        "gallery/title_detail.html",
        {"title": title, "page_obj": page_obj, "custom_range": custom_range},
    )
